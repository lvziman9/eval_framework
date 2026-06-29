#!/usr/bin/env python3
"""Run canonical TransE and TPRec preparation/training stages."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from logging import getLogger
from pathlib import Path

import torch

from hopwise.config import Config
from hopwise.data import create_dataset, data_preparation
from hopwise.utils import get_model, get_trainer, init_logger, init_seed

from scripts.hopwise.tprec_runtime import (
    build_tprec_config,
    build_transe_config,
    canonical_path_constraints,
    install_tprec_runtime_patches,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("preflight", "transe", "pretrain", "policy"), required=True)
    parser.add_argument(
        "--dataset",
        choices=(
            "canonical_ml1m_v1",
            "canonical_lastfm_v1",
            "canonical_amazon_book_kgat_v1",
        ),
        required=True,
    )
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-id", default="")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--embedding-size", type=int, default=100)
    parser.add_argument("--train-batch-size", type=int, default=1024)
    parser.add_argument("--eval-batch-size", type=int, default=16)
    parser.add_argument("--beam-search-hop", type=int, nargs=3, default=(25, 50, 1))
    parser.add_argument(
        "--pretrained-checkpoint",
        type=Path,
        help="TPRec pretrain checkpoint to install as the policy-stage input.",
    )
    parser.add_argument(
        "--transe-checkpoint",
        type=Path,
        help="Canonical TransE checkpoint used to initialize TPRec pretraining.",
    )
    return parser.parse_args()


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def prepare_model(stage: str, args: argparse.Namespace):
    if stage in {"preflight", "pretrain", "policy"}:
        model_name = "TPRec"
        train_stage = "pretrain" if stage in {"preflight", "pretrain"} else "policy"
        config_dict = build_tprec_config(
            dataset=args.dataset,
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            train_stage=train_stage,
            epochs=args.epochs,
            train_batch_size=args.train_batch_size,
            eval_batch_size=args.eval_batch_size,
            beam_search_hop=tuple(args.beam_search_hop),
            transe_checkpoint=args.transe_checkpoint,
        )
    else:
        model_name = "TransE"
        config_dict = build_transe_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            epochs=args.epochs,
            embedding_size=args.embedding_size,
            train_batch_size=args.train_batch_size,
        )

    config = Config(model=model_name, dataset=args.dataset, config_dict=config_dict)
    init_seed(config["seed"], config["reproducibility"])
    init_logger(config)
    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)
    init_seed(config["seed"] + config["local_rank"], config["reproducibility"])
    model = get_model(config["model"])(config, train_data.dataset)
    if isinstance(model, torch.nn.Module):
        model = model.to(device=config["device"], dtype=config["weight_precision"])
    return config, dataset, train_data, valid_data, test_data, model


def main() -> None:
    args = parse_args()
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    install_tprec_runtime_patches()

    if args.stage in {"preflight", "pretrain"}:
        if args.transe_checkpoint is None:
            raise ValueError("--transe-checkpoint is required for TPRec pretraining")
        if not args.transe_checkpoint.is_file():
            raise FileNotFoundError(args.transe_checkpoint)

    if args.stage == "policy":
        if args.pretrained_checkpoint is None:
            raise ValueError("--pretrained-checkpoint is required for the policy stage")
        if not args.pretrained_checkpoint.is_file():
            raise FileNotFoundError(args.pretrained_checkpoint)
        installed = args.checkpoint_dir / f"TPRec-{args.dataset}-pretrained.pth"
        if args.pretrained_checkpoint.resolve() != installed.resolve():
            shutil.copy2(args.pretrained_checkpoint, installed)

    config, dataset, train_data, valid_data, test_data, model = prepare_model(args.stage, args)
    logger = getLogger()
    logger.info(model)

    result = {
        "status": "PASS",
        "stage": args.stage,
        "model": config["model"],
        "dataset": args.dataset,
        "dataset_class": type(dataset).__name__,
        "users": dataset.user_num,
        "items": dataset.item_num,
        "entities": dataset.entity_num,
        "relations": dataset.relation_num,
        "train_batches": len(train_data),
        "valid_batches": len(valid_data),
        "test_batches": len(test_data),
        "path_constraints": canonical_path_constraints(args.dataset),
    }

    if args.stage == "preflight":
        result.update(
            {
                "trainable_parameters": sum(
                    parameter.numel() for parameter in model.parameters() if parameter.requires_grad
                ),
                "user_embedding_trainable": model.user_embedding.weight.requires_grad,
                "entity_embedding_trainable": model.entity_embedding.weight.requires_grad,
                "relation_embedding_trainable": model.relation_embedding.weight.requires_grad,
                "temporal_train_users": len(train_data.dataset.temporal_weights.uc_weight),
                "temporal_valid_users": len(valid_data.dataset.temporal_weights.uc_weight),
                "temporal_test_users": len(test_data.dataset.temporal_weights.uc_weight),
            }
        )
    else:
        trainer = get_trainer(config["MODEL_TYPE"], config["model"])(config, model)
        best_valid_score, best_valid_result = trainer.fit(
            train_data,
            valid_data,
            saved=True,
            show_progress=config["show_progress"],
        )
        result.update(
            {
                "epochs": args.epochs,
                "best_valid_score": json_safe(best_valid_score),
                "best_valid_result": json_safe(best_valid_result),
                "checkpoint": str(trainer.saved_model_file),
            }
        )

    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
