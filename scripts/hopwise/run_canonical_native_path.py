#!/usr/bin/env python3
"""Run a compact Hopwise native-path integration experiment."""

from __future__ import annotations

import argparse
import json
import math
from logging import getLogger
from pathlib import Path

import torch

from hopwise.config import Config
from hopwise.data import create_dataset, data_preparation
from hopwise.quick_start import run_hopwise
from hopwise.utils import get_model, get_trainer, init_logger, init_seed

from scripts.hopwise.canonical_config import build_kgglm_config, build_pearlm_config
from scripts.hopwise.smoke_prepare_native_path import (
    install_bounded_logits_mask_cache,
    install_cumulative_score_alignment,
    install_kgglm_serial_sampler,
    install_sparse_relation_lookup,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("PEARLM", "KGGLM"), required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-id", default="0")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--embedding-size", type=int, default=128)
    parser.add_argument("--num-heads", type=int, default=4)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--train-batch-size", type=int, default=128)
    parser.add_argument("--warmup-steps", type=int, default=0)
    parser.add_argument("--eval-step", type=int, default=0)
    parser.add_argument("--stopping-step", type=int, default=1)
    parser.add_argument("--validation-paths-per-user", type=int, default=1)
    parser.add_argument("--validation-num-beams", type=int, default=1)
    parser.add_argument(
        "--train-stage",
        choices=("pretrain", "finetune"),
        help="Required for KGGLM; ignored for PEARLM.",
    )
    parser.add_argument("--pre-model-path", type=Path)
    parser.add_argument("--pretrain-epochs", type=int, default=3)
    parser.add_argument("--save-step", type=int, default=1)
    parser.add_argument("--pretrain-paths", type=int, default=1)
    parser.add_argument(
        "--select-best-validation",
        action="store_true",
        help="Evaluate on the fixed validation split and save/load the best checkpoint.",
    )
    parser.add_argument(
        "--experiment-kind",
        default="compact integration smoke",
        help="Auditable label written to the result JSON.",
    )
    parser.add_argument(
        "--skip-test-evaluation",
        action="store_true",
        help=(
            "Train and save the checkpoint without Hopwise's built-in final "
            "test generation. Canonical cold-start test users are handled by "
            "the export adapter as empty recommendation rows."
        ),
    )
    return parser.parse_args()


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def run_train_only(
    *,
    model_name: str,
    dataset_name: str,
    config_dict: dict,
    select_best_validation: bool,
) -> dict:
    """Train a Hopwise path model without its unconditional final test pass."""

    config = Config(model=model_name, dataset=dataset_name, config_dict=config_dict)
    init_seed(config["seed"], config["reproducibility"])
    init_logger(config)
    logger = getLogger()
    logger.info(config)

    dataset = create_dataset(config)
    logger.info(dataset)
    train_data, valid_data, _ = data_preparation(config, dataset)

    init_seed(config["seed"] + config["local_rank"], config["reproducibility"])
    model = get_model(config["model"])(config, train_data.dataset)
    if isinstance(model, torch.nn.Module):
        model = model.to(device=config["device"], dtype=config["weight_precision"])
    logger.info(model)

    trainer = get_trainer(config["MODEL_TYPE"], config["model"])(config, model)
    best_valid_score, best_valid_result = trainer.fit(
        train_data,
        valid_data,
        saved=select_best_validation,
        show_progress=config["show_progress"],
    )
    return {
        "best_valid_score": best_valid_score,
        "valid_score_bigger": config["valid_metric_bigger"],
        "best_valid_result": best_valid_result,
        "test_result": None,
        "test_evaluation": "SKIPPED_FOR_CANONICAL_COLD_START_USERS",
    }


def main() -> None:
    args = parse_args()
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    install_sparse_relation_lookup()
    install_cumulative_score_alignment()
    install_bounded_logits_mask_cache()
    if args.model == "KGGLM":
        if args.train_stage is None:
            raise ValueError("--train-stage is required for KGGLM")
        install_kgglm_serial_sampler()
        config = build_kgglm_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            train_stage=args.train_stage,
            pre_model_path=args.pre_model_path,
            epochs=args.epochs,
            pretrain_epochs=args.pretrain_epochs,
            embedding_size=args.embedding_size,
            num_heads=args.num_heads,
            num_layers=args.num_layers,
            paths_per_user=args.validation_paths_per_user,
            num_beams=args.validation_num_beams,
            train_batch_size=args.train_batch_size,
            warmup_steps=args.warmup_steps,
            eval_step=args.eval_step,
            stopping_step=args.stopping_step,
            save_step=args.save_step,
            pretrain_paths=args.pretrain_paths,
        )
    else:
        if args.train_stage is not None or args.pre_model_path is not None:
            raise ValueError("KGGLM stage arguments cannot be used with PEARLM")
        config = build_pearlm_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            epochs=args.epochs,
            embedding_size=args.embedding_size,
            num_heads=args.num_heads,
            num_layers=args.num_layers,
            paths_per_user=args.validation_paths_per_user,
            num_beams=args.validation_num_beams,
            train_batch_size=args.train_batch_size,
            warmup_steps=args.warmup_steps,
            eval_step=args.eval_step,
            stopping_step=args.stopping_step,
        )

    if args.skip_test_evaluation:
        result = run_train_only(
            model_name=args.model,
            dataset_name=args.dataset,
            config_dict=config,
            select_best_validation=args.select_best_validation,
        )
    else:
        result = run_hopwise(
            model=args.model,
            dataset=args.dataset,
            config_dict=config,
            saved=False,
        )
    args.output.write_text(
        json.dumps(
            {
                "status": "PASS",
                "experiment_kind": args.experiment_kind,
                "model": args.model,
                "dataset": args.dataset,
                "epochs": args.epochs,
                "architecture": {
                    "embedding_size": args.embedding_size,
                    "num_heads": args.num_heads,
                    "num_layers": args.num_layers,
                },
                "train_batch_size": args.train_batch_size,
                "warmup_steps": args.warmup_steps,
                "eval_step": args.eval_step,
                "stopping_step": args.stopping_step,
                "select_best_validation": args.select_best_validation,
                "validation_paths_per_user": args.validation_paths_per_user,
                "validation_num_beams": args.validation_num_beams,
                "train_stage": args.train_stage,
                "pre_model_path": (
                    str(args.pre_model_path) if args.pre_model_path is not None else None
                ),
                "pretrain_epochs": args.pretrain_epochs if args.model == "KGGLM" else None,
                "pretrain_paths": args.pretrain_paths if args.model == "KGGLM" else None,
                "result": json_safe(result),
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
