#!/usr/bin/env python3
"""Evaluate uid_topk.csv against canonical labels."""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
from pathlib import Path


def load_labels(labels_dir: Path, split: str) -> dict[int, set[int]]:
    with open(labels_dir / f"{split}_label.pkl", "rb") as f:
        return {
            int(uid): {int(pid) for pid in pids}
            for uid, pids in pickle.load(f).items()
        }


def ndcg(hit_list: list[int], ideal_hits: int) -> float:
    if not hit_list or not any(hit_list):
        return 0.0
    dcg = sum(
        value / math.log2(rank + 2)
        for rank, value in enumerate(hit_list)
    )
    idcg = sum(1 / math.log2(rank + 2) for rank in range(ideal_hits))
    return dcg / idcg


def evaluate(
    uid_topk_path: Path,
    labels_dir: Path,
    topk: int,
    allow_short: bool = False,
    allow_user_subset: bool = False,
) -> dict:
    excluded = load_labels(labels_dir, "train")
    valid_path = labels_dir / "valid_label.pkl"
    if valid_path.exists():
        for uid, pids in load_labels(labels_dir, "valid").items():
            excluded.setdefault(uid, set()).update(pids)
    test = load_labels(labels_dir, "test")

    predictions = {}
    with open(uid_topk_path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["uid", "top10"]:
            raise ValueError(f"Unexpected uid_topk columns: {reader.fieldnames}")
        for row in reader:
            uid = int(row["uid"])
            pids = [int(pid) for pid in row["top10"].split() if pid]
            if len(pids) != len(set(pids)):
                raise ValueError(f"uid={uid} contains duplicate items")
            if len(pids) > topk:
                raise ValueError(f"uid={uid} has {len(pids)} items, expected at most {topk}")
            if not allow_short and len(pids) != topk:
                raise ValueError(f"uid={uid} does not have {topk} unique items")
            if any(pid in excluded.get(uid, set()) for pid in pids):
                raise ValueError(f"Seen item leaked into recommendations for uid={uid}")
            predictions[uid] = pids

    missing_users = sorted(set(test) - set(predictions))
    extra_users = sorted(set(predictions) - set(test))
    if extra_users or (missing_users and not allow_user_subset):
        raise ValueError(
            f"Prediction/test users differ: missing={missing_users[:5]}, "
            f"extra={extra_users[:5]}"
        )
    evaluated_users = sorted(set(test) & set(predictions))
    if not evaluated_users:
        raise ValueError("No predicted users overlap with the canonical test split")

    values = {"ndcg": [], "hr": [], "recall": [], "precision": []}
    for uid in evaluated_users:
        relevant = test[uid]
        pids = predictions[uid]
        hits = [int(pid in relevant) for pid in pids]
        hit_count = sum(hits)
        values["ndcg"].append(ndcg(hits, min(topk, len(relevant))))
        values["hr"].append(float(hit_count > 0))
        values["recall"].append(hit_count / len(relevant))
        values["precision"].append(hit_count / topk)

    recommendation_counts = [len(predictions[uid]) for uid in evaluated_users]
    short_users = sum(count < topk for count in recommendation_counts)

    return {
        "status": "PASS",
        "uid_topk": str(uid_topk_path),
        "users": len(evaluated_users),
        "canonical_test_users": len(test),
        "missing_test_users": len(missing_users),
        "extra_prediction_users": len(extra_users),
        "topk": topk,
        "allow_short": allow_short,
        "allow_user_subset": allow_user_subset,
        "user_coverage": len(evaluated_users) / len(test),
        "recommendation_coverage": {
            "exact_k_users": len(evaluated_users) - short_users,
            "short_users": short_users,
            "empty_users": sum(count == 0 for count in recommendation_counts),
            "min_items": min(recommendation_counts),
            "max_items": max(recommendation_counts),
            "mean_items": sum(recommendation_counts) / len(recommendation_counts),
            "slot_coverage": sum(recommendation_counts) / (len(evaluated_users) * topk),
        },
        "metrics": {
            name: sum(metric_values) / len(metric_values)
            for name, metric_values in values.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid-topk", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--allow-short", action="store_true")
    parser.add_argument(
        "--allow-user-subset",
        action="store_true",
        help="Evaluate only predicted users that belong to the test split. "
        "Default keeps the formal protocol strict and requires all test users.",
    )
    parser.add_argument("--summary-json")
    args = parser.parse_args()
    summary = evaluate(
        Path(args.uid_topk),
        Path(args.labels_dir),
        args.topk,
        args.allow_short,
        args.allow_user_subset,
    )
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.summary_json:
        output = Path(args.summary_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
