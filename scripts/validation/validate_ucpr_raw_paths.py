#!/usr/bin/env python3
"""Validate that a UCPR raw beam-path pickle covers the canonical test users."""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
from pathlib import Path
from typing import Optional


def load_expected_model_users(
    labels_path: Path,
    remap_path: Path,
    model_train_labels_path: Optional[Path],
) -> tuple[set[int], int]:
    with open(labels_path, "rb") as f:
        canonical_labels = pickle.load(f)
    canonical_to_model = {}
    with open(remap_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not {"canonical_uid", "ucpr_uid"}.issubset(reader.fieldnames or []):
            raise ValueError(f"Unexpected UCPR user remap columns: {reader.fieldnames}")
        for row in reader:
            canonical_to_model[int(row["canonical_uid"])] = int(row["ucpr_uid"])
    missing = sorted(set(canonical_labels) - set(canonical_to_model))
    if missing:
        raise ValueError(f"Canonical users absent from UCPR remap: {missing[:5]}")
    remapped_test_users = {canonical_to_model[int(uid)] for uid in canonical_labels}
    excluded_without_train_history = 0
    if model_train_labels_path is not None:
        with open(model_train_labels_path, "rb") as f:
            model_train_labels = pickle.load(f)
        train_users = {int(uid) for uid in model_train_labels}
        excluded_without_train_history = len(remapped_test_users - train_users)
        remapped_test_users &= train_users
    return remapped_test_users, excluded_without_train_history


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-paths", required=True)
    parser.add_argument("--test-labels", required=True)
    parser.add_argument("--user-remap", required=True)
    parser.add_argument(
        "--model-train-labels",
        help=(
            "Optional UCPR train_label.pkl. Native inference excludes test "
            "users without train history."
        ),
    )
    parser.add_argument("--expected-steps", type=int, default=3)
    parser.add_argument("--summary-json")
    args = parser.parse_args()

    with open(args.raw_paths, "rb") as f:
        data = pickle.load(f)
    if set(data) != {"paths", "probs"}:
        raise ValueError(f"Unexpected raw-path keys: {sorted(data)}")
    paths = data["paths"]
    probabilities = data["probs"]
    if len(paths) != len(probabilities) or not paths:
        raise ValueError(
            f"Path/probability size mismatch: paths={len(paths)}, probs={len(probabilities)}"
        )

    expected_users, excluded_without_train_history = load_expected_model_users(
        Path(args.test_labels),
        Path(args.user_remap),
        Path(args.model_train_labels) if args.model_train_labels else None,
    )
    observed_users = set()
    endpoint_products = 0
    probability_min = math.inf
    probability_max = -math.inf
    for index, (path, step_probabilities) in enumerate(zip(paths, probabilities)):
        if not path:
            raise ValueError(f"Empty path at index={index}")
        if path[0][1] != "user":
            raise ValueError(f"Non-user path origin at index={index}: {path[0]}")
        observed_users.add(int(path[0][2]))
        endpoint_products += path[-1][1] == "product"
        if len(step_probabilities) != args.expected_steps:
            raise ValueError(
                f"Unexpected probability steps at index={index}: "
                f"{len(step_probabilities)}"
            )
        for value in step_probabilities:
            value = float(value)
            if not math.isfinite(value):
                raise ValueError(f"Non-finite probability at index={index}: {value}")
            probability_min = min(probability_min, value)
            probability_max = max(probability_max, value)

    if observed_users != expected_users:
        raise ValueError(
            "Raw path users differ from canonical remapped test users: "
            f"missing={sorted(expected_users - observed_users)[:5]}, "
            f"extra={sorted(observed_users - expected_users)[:5]}"
        )

    summary = {
        "status": "PASS",
        "raw_paths": str(Path(args.raw_paths).resolve()),
        "paths": len(paths),
        "probability_rows": len(probabilities),
        "users": len(observed_users),
        "canonical_test_users_excluded_without_train_history": (
            excluded_without_train_history
        ),
        "expected_steps": args.expected_steps,
        "product_ending_paths": endpoint_products,
        "raw_step_value_range": [probability_min, probability_max],
        "note": (
            "Raw UCPR files may contain the historical +1 selection offset; "
            "canonical extraction validates corrected probabilities separately."
        ),
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.summary_json:
        output = Path(args.summary_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
