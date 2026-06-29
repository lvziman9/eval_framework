#!/usr/bin/env python3
"""Validate a small PGPR TransE training smoke run."""

from __future__ import annotations

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_RELATIONS = [
    "purchased",
    "book_author",
    "book_genre",
    "book_original_language",
    "book_subject",
    "book_next_in_series",
    "book_previous_in_series",
    "book_part_of_series",
    "book_character",
    "book_interior_illustration",
]


def load_pickle(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--expected-embed-size", type=int, required=True)
    parser.add_argument("--summary-json", required=True)
    args = parser.parse_args()

    pgpr_tmp = (
        Path(args.runtime_root)
        / "models"
        / "PGPR"
        / "tmp"
        / args.dataset
    )
    run_dir = pgpr_tmp / args.run_name
    checkpoint = run_dir / f"transe_model_sd_epoch_{args.epoch}.ckpt"
    train_log = run_dir / "train_log.txt"
    embed_path = pgpr_tmp / "transe_embed.pkl"

    embeds = load_pickle(embed_path) if embed_path.exists() else {}
    required_keys = ["user", "book", "entity", *EXPECTED_RELATIONS]
    missing_keys = [key for key in required_keys if key not in embeds]
    shape_summary: dict[str, Any] = {}
    if not missing_keys:
        for key in ["user", "book", "entity"]:
            shape_summary[key] = list(embeds[key].shape)
        for key in EXPECTED_RELATIONS:
            relation_vec, relation_bias = embeds[key]
            shape_summary[key] = {
                "relation": list(relation_vec.shape),
                "bias": list(relation_bias.shape),
            }

    embed_size_ok = True
    if not missing_keys:
        embed_size_ok = all(
            shape_summary[key][1] == args.expected_embed_size
            for key in ["user", "book", "entity"]
        )
        embed_size_ok = embed_size_ok and all(
            shape_summary[key]["relation"] == [args.expected_embed_size]
            for key in EXPECTED_RELATIONS
        )

    log_text = train_log.read_text() if train_log.exists() else ""
    status = "PASS"
    if not checkpoint.exists() or not embed_path.exists() or missing_keys or not embed_size_ok:
        status = "FAIL"
    if "Epoch: 01" not in log_text:
        status = "FAIL"

    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "runtime_root": str(Path(args.runtime_root).resolve()),
        "run_name": args.run_name,
        "epoch": args.epoch,
        "expected_embed_size": args.expected_embed_size,
        "checkpoint": {
            "path": str(checkpoint),
            "exists": checkpoint.exists(),
            "size_bytes": checkpoint.stat().st_size if checkpoint.exists() else None,
        },
        "embedding_pickle": {
            "path": str(embed_path),
            "exists": embed_path.exists(),
            "size_bytes": embed_path.stat().st_size if embed_path.exists() else None,
        },
        "train_log": {
            "path": str(train_log),
            "exists": train_log.exists(),
            "contains_epoch_01": "Epoch: 01" in log_text,
        },
        "missing_embedding_keys": missing_keys,
        "embedding_shapes": shape_summary,
        "embed_size_ok": embed_size_ok,
    }
    summary_path = Path(args.summary_json)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
