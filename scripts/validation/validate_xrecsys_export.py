#!/usr/bin/env python3
"""Validate an adapter export before xrecsys evaluation."""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
from pathlib import Path


PRODUCT_TYPE = {
    "lastfm": "song",
    "ml1m": "movie",
    "beauty": "product",
    "beauty_legacy_v1": "product",
    "amazon_book_kgat_v1": "book",
}


def load_labels(labels_dir: Path, split: str) -> dict[int, set[int]]:
    with open(labels_dir / f"{split}_label.pkl", "rb") as f:
        labels = pickle.load(f)
    return {int(uid): {int(pid) for pid in pids} for uid, pids in labels.items()}


def parse_path(path_str: str, expected_uid: int, expected_pid: int, product_type: str):
    values = path_str.split()
    if len(values) < 9 or len(values) % 3 != 0:
        raise ValueError(
            "Expected a path with at least two hops and complete "
            f"(relation, entity, id) triples, got {len(values)} tokens: {path_str}"
        )
    path = [tuple(values[idx : idx + 3]) for idx in range(0, len(values), 3)]
    if path[0][1] != "user" or int(path[0][2]) != expected_uid:
        raise ValueError(f"Path user endpoint mismatch for uid={expected_uid}: {path_str}")
    if path[-1][1] != product_type or int(path[-1][2]) != expected_pid:
        raise ValueError(f"Path product endpoint mismatch for pid={expected_pid}: {path_str}")
    return path


def validate(
    paths_dir: Path,
    labels_dir: Path,
    dataset: str,
    topk: int,
    require_all_test_users: bool = False,
) -> dict:
    train = load_labels(labels_dir, "train")
    valid_path = labels_dir / "valid_label.pkl"
    if valid_path.exists():
        valid = load_labels(labels_dir, "valid")
        for uid, pids in valid.items():
            train.setdefault(uid, set()).update(pids)
    test = load_labels(labels_dir, "test")
    product_type = PRODUCT_TYPE[dataset]

    uid_topk = {}
    with open(paths_dir / "uid_topk.csv", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["uid", "top10"]:
            raise ValueError(f"Unexpected uid_topk.csv columns: {reader.fieldnames}")
        for row in reader:
            uid = int(row["uid"])
            pids = [int(value) for value in row["top10"].split() if value]
            if uid in uid_topk:
                raise ValueError(f"Duplicate uid={uid} in uid_topk.csv")
            if uid not in test:
                raise ValueError(f"uid={uid} is absent from canonical test labels")
            if len(pids) > topk or len(pids) != len(set(pids)):
                raise ValueError(f"Invalid top-k list for uid={uid}: {pids}")
            if any(pid in train.get(uid, set()) for pid in pids):
                raise ValueError(f"Seen training item leaked into top-k for uid={uid}")
            uid_topk[uid] = pids
    if require_all_test_users and set(uid_topk) != set(test):
        missing = sorted(set(test) - set(uid_topk))[:10]
        extra = sorted(set(uid_topk) - set(test))[:10]
        raise ValueError(
            "uid_topk.csv does not cover the exact canonical test-user set: "
            f"missing={missing}, extra={extra}"
        )

    explanations = {}
    explanation_pids_by_uid = {}
    with open(paths_dir / "uid_pid_explanation.csv", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["uid", "pid", "path"]:
            raise ValueError(
                f"Unexpected uid_pid_explanation.csv columns: {reader.fieldnames}"
            )
        for row in reader:
            uid, pid = int(row["uid"]), int(row["pid"])
            key = (uid, pid)
            if key in explanations:
                raise ValueError(f"Duplicate explanation for uid={uid}, pid={pid}")
            parse_path(row["path"], uid, pid, product_type)
            explanations[key] = row["path"]
            explanation_pids_by_uid.setdefault(uid, set()).add(pid)

    users_with_recommendations = {uid for uid, pids in uid_topk.items() if pids}
    if set(explanation_pids_by_uid) != users_with_recommendations:
        raise ValueError("uid_topk.csv and uid_pid_explanation.csv contain different users")
    for uid, pids in uid_topk.items():
        if set(pids) != explanation_pids_by_uid.get(uid, set()):
            raise ValueError(f"Top-k and explanation pids differ for uid={uid}")

    pending_explanations = set(explanations)
    pred_rows = 0
    candidate_users = set()
    min_score = math.inf
    max_score = -math.inf
    with open(paths_dir / "pred_paths.csv", newline="") as f:
        reader = csv.DictReader(f)
        expected = ["uid", "pid", "path_score", "path_prob", "path"]
        if reader.fieldnames != expected:
            raise ValueError(f"Unexpected pred_paths.csv columns: {reader.fieldnames}")
        for row in reader:
            uid, pid = int(row["uid"]), int(row["pid"])
            score = float(row["path_score"])
            path_prob = float(row["path_prob"])
            if uid not in test:
                raise ValueError(f"Candidate uid={uid} is absent from canonical test labels")
            if not math.isfinite(score) or score < -1e-9 or score > 1.0 + 1e-9:
                raise ValueError(f"Out-of-range path_score={score} for uid={uid}, pid={pid}")
            if (
                not math.isfinite(path_prob)
                or path_prob < -1e-9
                or path_prob > 1.0 + 1e-9
            ):
                raise ValueError(
                    f"Out-of-range path_prob={path_prob} for uid={uid}, pid={pid}"
                )
            if pid in train.get(uid, set()):
                raise ValueError(f"Seen training item leaked into candidates for uid={uid}, pid={pid}")
            parse_path(row["path"], uid, pid, product_type)
            key = (uid, pid)
            if key in pending_explanations and row["path"] == explanations[key]:
                pending_explanations.remove(key)
            candidate_users.add(uid)
            min_score = min(min_score, score)
            max_score = max(max_score, score)
            pred_rows += 1

    if pred_rows == 0:
        raise ValueError("pred_paths.csv contains no candidate paths")
    if pending_explanations:
        sample = sorted(pending_explanations)[:5]
        raise ValueError(f"Top-k explanations absent from pred_paths.csv: {sample}")

    return {
        "dataset": dataset,
        "paths_dir": str(paths_dir),
        "pred_path_rows": pred_rows,
        "candidate_users": len(candidate_users),
        "topk_users": len(uid_topk),
        "canonical_test_users": len(test),
        "require_all_test_users": require_all_test_users,
        "explanations": len(explanations),
        "score_range": [min_score, max_score],
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-dir", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--dataset", choices=sorted(PRODUCT_TYPE), required=True)
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--require-all-test-users", action="store_true")
    parser.add_argument("--summary-json")
    args = parser.parse_args()

    summary = validate(
        Path(args.paths_dir),
        Path(args.labels_dir),
        args.dataset,
        args.topk,
        args.require_all_test_users,
    )
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.summary_json:
        output = Path(args.summary_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
