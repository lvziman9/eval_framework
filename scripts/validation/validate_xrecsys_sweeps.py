#!/usr/bin/env python3
"""Validate complete xrecsys baseline and moving-alpha result artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path


EXPECTED_ALPHAS = {round(index * 0.05, 2) for index in range(21)}
OPTIMIZATIONS = ("LIRopt", "SEPopt", "ETDopt")
EXPECTED_OVERALL_METRICS = {
    "ndcg",
    "hr",
    "recall",
    "precision",
    "LIR",
    "SEP",
    "ETD",
}


def alpha_counts(path: Path) -> Counter[float]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty xrecsys sweep output: {path}")
    counts: Counter[float] = Counter()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "alpha" not in reader.fieldnames:
            raise ValueError(f"Missing alpha column in xrecsys output: {path}")
        for row in reader:
            counts[round(float(row["alpha"]), 2)] += 1
    return counts


def validate_uniform_alpha_rows(path: Path) -> dict:
    counts = alpha_counts(path)
    found = set(counts)
    if found != EXPECTED_ALPHAS:
        raise ValueError(
            f"Incomplete alpha coverage in {path}: "
            f"missing={sorted(EXPECTED_ALPHAS - found)}, "
            f"extra={sorted(found - EXPECTED_ALPHAS)}"
        )
    row_counts = set(counts.values())
    if len(row_counts) != 1:
        raise ValueError(f"Non-uniform rows per alpha in {path}: {dict(counts)}")
    return {
        "path": str(path),
        "alphas": len(found),
        "rows_per_alpha": next(iter(row_counts)),
        "rows": sum(counts.values()),
    }


def validate_finite_overall_metrics(path: Path) -> dict:
    metrics_by_alpha = {
        alpha: set()
        for alpha in EXPECTED_ALPHAS
    }
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"alpha", "metric", "group", "data"}
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                f"Missing Overall-metric columns in xrecsys output: {path}"
            )
        for row in reader:
            if row["group"] != "Overall":
                continue
            alpha = round(float(row["alpha"]), 2)
            metric = row["metric"]
            if alpha not in metrics_by_alpha or metric not in EXPECTED_OVERALL_METRICS:
                continue
            value = float(row["data"])
            if not math.isfinite(value):
                raise ValueError(
                    f"Non-finite Overall {metric} at alpha={alpha:.2f} in {path}"
                )
            metrics_by_alpha[alpha].add(metric)

    incomplete = {
        alpha: sorted(EXPECTED_OVERALL_METRICS - metrics)
        for alpha, metrics in metrics_by_alpha.items()
        if metrics != EXPECTED_OVERALL_METRICS
    }
    if incomplete:
        raise ValueError(f"Missing Overall metrics in {path}: {incomplete}")
    return {
        "metrics": sorted(EXPECTED_OVERALL_METRICS),
        "alphas": len(metrics_by_alpha),
    }


def validate(results_dir: Path) -> dict:
    baseline = results_dir / "baseline_avg.csv"
    if not baseline.is_file() or baseline.stat().st_size == 0:
        raise ValueError(f"Missing or empty xrecsys baseline: {baseline}")
    baseline_overall = validate_finite_overall_metrics(baseline)

    outputs = {}
    for optimization in OPTIMIZATIONS:
        avg_path = results_dir / f"{optimization}_moving_alpha_avg.csv"
        outputs[optimization] = {
            "avg": {
                **validate_uniform_alpha_rows(avg_path),
                "finite_overall": validate_finite_overall_metrics(avg_path),
            },
            "distribution": validate_uniform_alpha_rows(
                results_dir / f"{optimization}_moving_alpha_distribution.csv"
            ),
        }
    return {
        "status": "PASS",
        "results_dir": str(results_dir),
        "expected_alphas": sorted(EXPECTED_ALPHAS),
        "baseline_avg": str(baseline),
        "baseline_finite_overall": baseline_overall,
        "optimizations": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path)
    args = parser.parse_args()
    summary = validate(args.results_dir)
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
