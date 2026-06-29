#!/usr/bin/env python3
"""Validate a PGPR policy training run checkpoint."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--expected-state-dim", type=int, required=True)
    parser.add_argument("--expected-act-dim", type=int, required=True)
    parser.add_argument(
        "--expected-hidden",
        type=int,
        nargs=2,
        default=[32, 16],
        metavar=("H1", "H2"),
        help="Expected ActorCritic hidden sizes. Defaults to the Amazon smoke size.",
    )
    parser.add_argument("--summary-json", required=True)
    args = parser.parse_args()

    import torch

    pgpr_tmp = (
        Path(args.runtime_root)
        / "models"
        / "PGPR"
        / "tmp"
        / args.dataset
    )
    run_dir = pgpr_tmp / args.run_name
    checkpoint = run_dir / f"policy_model_epoch_{args.epoch}.ckpt"
    train_log = run_dir / "train_log.txt"

    checkpoint_keys: list[str] = []
    checkpoint_shapes: dict[str, Any] = {}
    if checkpoint.exists():
        state = torch.load(checkpoint, map_location="cpu")
        checkpoint_keys = sorted(state)
        for key in checkpoint_keys:
            value = state[key]
            checkpoint_shapes[key] = list(value.shape) if hasattr(value, "shape") else None

    hidden_1, hidden_2 = args.expected_hidden
    expected_shapes = {
        "l1.weight": [hidden_1, args.expected_state_dim],
        "l2.weight": [hidden_2, hidden_1],
        "actor.weight": [args.expected_act_dim, hidden_2],
        "critic.weight": [1, hidden_2],
    }
    shape_checks = {
        key: checkpoint_shapes.get(key) == shape
        for key, shape in expected_shapes.items()
    }
    log_text = train_log.read_text() if train_log.exists() else ""
    status = "PASS"
    if not checkpoint.exists() or not all(shape_checks.values()):
        status = "FAIL"
    if f"policy_model_epoch_{args.epoch}.ckpt" not in log_text:
        status = "FAIL"

    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "runtime_root": str(Path(args.runtime_root).resolve()),
        "run_name": args.run_name,
        "epoch": args.epoch,
        "expected_state_dim": args.expected_state_dim,
        "expected_act_dim": args.expected_act_dim,
        "expected_hidden": args.expected_hidden,
        "checkpoint": {
            "path": str(checkpoint),
            "exists": checkpoint.exists(),
            "size_bytes": checkpoint.stat().st_size if checkpoint.exists() else None,
        },
        "train_log": {
            "path": str(train_log),
            "exists": train_log.exists(),
            "contains_save_marker": f"policy_model_epoch_{args.epoch}.ckpt" in log_text,
        },
        "checkpoint_keys": checkpoint_keys,
        "checkpoint_shapes": checkpoint_shapes,
        "shape_checks": shape_checks,
    }
    summary_path = Path(args.summary_json)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
