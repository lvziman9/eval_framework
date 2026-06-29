#!/usr/bin/env python3
"""Validate a PGPR preprocess smoke run against canonical labels."""

from __future__ import annotations

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_pickle(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def compare_labels(canonical_labels_dir: Path, pgpr_tmp_dir: Path, split: str) -> dict[str, Any]:
    canonical = load_pickle(canonical_labels_dir / f"{split}_label.pkl")
    generated = load_pickle(pgpr_tmp_dir / f"{split}_label.pkl")
    mismatched_users = [
        uid
        for uid in sorted(set(canonical) | set(generated))
        if canonical.get(uid) != generated.get(uid)
    ]
    return {
        "split": split,
        "canonical_users": len(canonical),
        "generated_users": len(generated),
        "canonical_interactions": sum(len(items) for items in canonical.values()),
        "generated_interactions": sum(len(items) for items in generated.values()),
        "exact_match": not mismatched_users,
        "mismatched_user_examples": mismatched_users[:10],
    }


def file_summary(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--canonical-labels-dir", required=True)
    parser.add_argument("--pgpr-tmp-dir", required=True)
    parser.add_argument("--summary-json", required=True)
    args = parser.parse_args()

    canonical_labels_dir = Path(args.canonical_labels_dir)
    pgpr_tmp_dir = Path(args.pgpr_tmp_dir)
    summary_path = Path(args.summary_json)

    split_checks = [
        compare_labels(canonical_labels_dir, pgpr_tmp_dir, split)
        for split in ("train", "test")
    ]
    core_files = {
        "dataset_pickle": file_summary(pgpr_tmp_dir / "dataset.pkl"),
        "kg_pickle": file_summary(pgpr_tmp_dir / "kg.pkl"),
        "train_label": file_summary(pgpr_tmp_dir / "train_label.pkl"),
        "test_label": file_summary(pgpr_tmp_dir / "test_label.pkl"),
    }
    status = "PASS"
    if not all(item["exact_match"] for item in split_checks):
        status = "FAIL"
    if not all(item["exists"] for item in core_files.values()):
        status = "FAIL"

    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "canonical_labels_dir": str(canonical_labels_dir),
        "pgpr_tmp_dir": str(pgpr_tmp_dir),
        "split_checks": split_checks,
        "core_files": core_files,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
