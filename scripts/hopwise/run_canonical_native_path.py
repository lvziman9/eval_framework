#!/usr/bin/env python3
"""Run a compact Hopwise native-path integration experiment."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from hopwise.quick_start import run_hopwise

from scripts.hopwise.smoke_prepare_native_path import install_sparse_relation_lookup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("PEARLM",), required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-id", default="0")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--embedding-size", type=int, default=128)
    parser.add_argument("--num-heads", type=int, default=4)
    parser.add_argument("--num-layers", type=int, default=2)
    return parser.parse_args()


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def main() -> None:
    args = parse_args()
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    install_sparse_relation_lookup()
    config = {
        "gpu_id": args.gpu_id,
        "use_gpu": True,
        "data_path": str(args.data_root),
        "checkpoint_dir": str(args.checkpoint_dir),
        "benchmark_filename": ["train", "valid", "test"],
        "load_col": {
            "inter": ["user_id", "item_id", "rating", "timestamp"],
            "kg": ["head_id", "relation_id", "tail_id"],
            "link": ["item_id", "entity_id"],
        },
        "eval_args": {
            "split": {"RS": [0.8, 0.1, 0.1]},
            "order": "RO",
            "group_by": "user",
            "mode": {"valid": "full", "test": "full"},
        },
        "metrics": ["Recall", "NDCG", "Hit", "Precision", "Fidelity"],
        "topk": [10],
        "valid_metric": "NDCG@10",
        "epochs": args.epochs,
        "eval_step": 0,
        "stopping_step": 1,
        "train_batch_size": 128,
        "eval_batch_size": 32,
        "learning_rate": 2e-4,
        "weight_decay": 0.01,
        "warmup_steps": 0,
        "show_progress": True,
        "embedding_size": args.embedding_size,
        "num_heads": args.num_heads,
        "num_layers": args.num_layers,
        "use_kg_token_types": True,
        "base_model": "distilgpt2",
        "sequence_postprocessor": "Cumulative",
        "path_hop_length": 3,
        "context_length": 9,
        "MAX_PATHS_PER_USER": 1,
        "path_sample_args": {
            "strategy": "constrained-rw",
            "temporal_causality": False,
            "collaborative_path": True,
            "restrict_by_phase": False,
            "parallel_max_workers": 1,
            "MAX_RW_PATHS_PER_HOP": 1,
        },
        "path_generation_args": {
            "paths_per_user": 1,
            "num_beams": 1,
            "num_beam_groups": 1,
            "diversity_penalty": 0.0,
            "length_penalty": 0.0,
            "do_sample": False,
        },
    }

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
                "experiment_kind": "compact integration smoke",
                "model": args.model,
                "dataset": args.dataset,
                "epochs": args.epochs,
                "architecture": {
                    "embedding_size": args.embedding_size,
                    "num_heads": args.num_heads,
                    "num_layers": args.num_layers,
                },
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
