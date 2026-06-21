#!/usr/bin/env python3
"""Train a RecBole accuracy-reference model and export canonical top-k items."""

from __future__ import annotations

import argparse
import csv
import json
import pickle
from logging import getLogger
from pathlib import Path

import numpy as np
import torch

from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.data.transform import construct_transform
from recbole.utils import (
    get_model,
    get_trainer,
    init_logger,
    init_seed,
)
from recbole.utils.case_study import full_sort_topk


SUPPORTED_MODELS = {"KGIN", "KGAT", "LightGCN"}


def load_labels(labels_dir: Path, split: str) -> dict[int, set[int]]:
    with open(labels_dir / f"{split}_label.pkl", "rb") as f:
        return {
            int(uid): {int(pid) for pid in pids}
            for uid, pids in pickle.load(f).items()
        }


def jsonable(value):
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def build_config(args) -> Config:
    config_dict = {
        "data_path": str(Path(args.data_path).resolve()),
        "benchmark_filename": ["train", "valid", "test"],
        "USER_ID_FIELD": "user_id",
        "ITEM_ID_FIELD": "item_id",
        "RATING_FIELD": "rating",
        "TIME_FIELD": "timestamp",
        "HEAD_ENTITY_ID_FIELD": "head_id",
        "TAIL_ENTITY_ID_FIELD": "tail_id",
        "RELATION_ID_FIELD": "relation_id",
        "ENTITY_ID_FIELD": "entity_id",
        "load_col": {
            "inter": ["user_id", "item_id", "rating", "timestamp"],
            "user": ["user_id"],
            "item": ["item_id"],
            "kg": ["head_id", "relation_id", "tail_id"],
            "link": ["item_id", "entity_id"],
        },
        "eval_args": {
            "split": None,
            "group_by": "user",
            "order": "RO",
            "mode": "full",
        },
        "repeatable": False,
        "metrics": ["Recall", "NDCG", "Hit", "Precision"],
        "topk": [args.topk],
        "valid_metric": f"NDCG@{args.topk}",
        "valid_metric_bigger": True,
        "epochs": args.epochs,
        "stopping_step": args.stopping_step,
        "eval_step": 1,
        "train_batch_size": args.train_batch_size,
        "eval_batch_size": args.eval_batch_size,
        "learning_rate": args.learning_rate,
        "checkpoint_dir": str(Path(args.checkpoint_dir).resolve()),
        "gpu_id": str(args.gpu_id),
        "use_gpu": not args.cpu,
        "worker": 0,
        "show_progress": args.show_progress,
        "save_dataset": False,
        "save_dataloaders": False,
        "seed": args.seed,
        "reproducibility": True,
        "log_wandb": False,
        "train_neg_sample_args": {
            "distribution": "uniform",
            "sample_num": 1,
            "alpha": 1.0,
            "dynamic": False,
            "candidate_num": 0,
        },
        "user_inter_num_interval": "[0,inf)",
        "item_inter_num_interval": "[0,inf)",
        "entity_kg_num_interval": "[0,inf)",
        "relation_kg_num_interval": "[0,inf)",
    }
    if args.model == "KGIN":
        config_dict.update(
            {
                "embedding_size": 64,
                "context_hops": 3,
                "n_factors": 4,
                "reg_weight": 1e-5,
                "learning_rate": args.learning_rate,
            }
        )
    elif args.model == "KGAT":
        config_dict.update(
            {
                "embedding_size": 64,
                "kg_embedding_size": 64,
                "layers": [64],
                "reg_weight": 1e-5,
            }
        )
    elif args.model == "LightGCN":
        config_dict.update(
            {
                "embedding_size": 64,
                "n_layers": 2,
                "reg_weight": 1e-5,
            }
        )
    return Config(model=args.model, dataset=args.dataset_token, config_dict=config_dict)


def export_topk(
    model,
    dataset,
    test_data,
    labels_dir: Path,
    output_path: Path,
    topk: int,
    batch_size: int,
    device,
) -> dict:
    test_labels = load_labels(labels_dir, "test")
    uid_tokens = sorted(test_labels)
    uid_internal = []
    for uid in uid_tokens:
        internal = int(dataset.token2id(dataset.uid_field, str(uid)))
        if internal == 0:
            raise ValueError(f"Canonical test uid={uid} is absent from RecBole dataset")
        uid_internal.append(internal)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    model.eval()
    for start in range(0, len(uid_internal), batch_size):
        end = min(start + batch_size, len(uid_internal))
        _, topk_iids = full_sort_topk(
            uid_internal[start:end],
            model,
            test_data,
            topk,
            device=device,
        )
        item_tokens = dataset.id2token(dataset.iid_field, topk_iids.cpu())
        for uid, tokens in zip(uid_tokens[start:end], item_tokens):
            pids = [int(token) for token in tokens]
            if len(pids) != topk or len(pids) != len(set(pids)):
                raise ValueError(f"Invalid RecBole top-k for uid={uid}: {pids}")
            rows.append((uid, pids))

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["uid", "top10"])
        for uid, pids in rows:
            writer.writerow([uid, " ".join(map(str, pids))])
    return {"users": len(rows), "topk": topk, "output": str(output_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=sorted(SUPPORTED_MODELS), required=True)
    parser.add_argument("--dataset-token", required=True)
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--stopping-step", type=int, default=10)
    parser.add_argument("--train-batch-size", type=int, default=2048)
    parser.add_argument("--eval-batch-size", type=int, default=1024)
    parser.add_argument("--export-batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2020)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--show-progress", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    Path(args.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    config = build_config(args)
    init_seed(config["seed"], config["reproducibility"])
    init_logger(config)
    logger = getLogger()
    logger.info(config)

    dataset = create_dataset(config)
    logger.info(dataset)
    train_data, valid_data, test_data = data_preparation(config, dataset)
    if args.prepare_only:
        init_seed(config["seed"] + config["local_rank"], config["reproducibility"])
        model = get_model(config["model"])(config, train_data._dataset).to(
            config["device"]
        )
        summary = {
            "status": "PREPARE_PASS",
            "model": args.model,
            "dataset": args.dataset_token,
            "users": dataset.user_num - 1,
            "items": dataset.item_num - 1,
            "entities": getattr(dataset, "entity_num", None),
            "relations": getattr(dataset, "relation_num", None),
            "parameters": sum(parameter.numel() for parameter in model.parameters()),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        (output_dir / "prepare_summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        return

    init_seed(config["seed"] + config["local_rank"], config["reproducibility"])
    model = get_model(config["model"])(config, train_data._dataset).to(config["device"])
    construct_transform(config)
    trainer = get_trainer(config["MODEL_TYPE"], config["model"])(config, model)
    best_valid_score, best_valid_result = trainer.fit(
        train_data,
        valid_data,
        saved=True,
        show_progress=config["show_progress"],
    )
    test_result = trainer.evaluate(
        test_data,
        load_best_model=True,
        show_progress=config["show_progress"],
    )
    export_summary = export_topk(
        trainer.model,
        dataset,
        test_data,
        Path(args.labels_dir),
        output_dir / "uid_topk.csv",
        args.topk,
        args.export_batch_size,
        config["device"],
    )
    summary = {
        "status": "TRAIN_AND_EXPORT_PASS",
        "model": args.model,
        "dataset": args.dataset_token,
        "checkpoint": trainer.saved_model_file,
        "best_valid_score": jsonable(best_valid_score),
        "best_valid_result": jsonable(best_valid_result),
        "test_result": jsonable(test_result),
        "export": export_summary,
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    (output_dir / "recbole_summary.json").write_text(rendered + "\n")


if __name__ == "__main__":
    main()
