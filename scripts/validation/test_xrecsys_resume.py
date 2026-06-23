#!/usr/bin/env python3
"""Regression checks for resumable xrecsys alpha outputs."""

from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "xrecsys"))

import main as xrecsys_main


def write_rows(path: Path, rows: list[tuple]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["alpha", "metric", "group", "data", "opt"])
        writer.writerows(rows)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        avg = root / "SEPopt_moving_alpha_avg.csv"
        distribution = root / "SEPopt_moving_alpha_distribution.csv"
        write_rows(
            avg,
            [
                (0.0, "ndcg", "Overall", 0.1, "SEPopt"),
                (0.0, "hr", "Overall", 0.2, "SEPopt"),
                (0.05, "ndcg", "Overall", 0.1, "SEPopt"),
                (0.05, "hr", "Overall", 0.2, "SEPopt"),
                (0.1, "ndcg", "Overall", 0.1, "SEPopt"),
            ],
        )
        write_rows(
            distribution,
            [
                (0.0, "ndcg", "Male", 0.1, "SEPopt"),
                (0.0, "ndcg", "Female", 0.2, "SEPopt"),
                (0.05, "ndcg", "Male", 0.1, "SEPopt"),
                (0.05, "ndcg", "Female", 0.2, "SEPopt"),
                (0.1, "ndcg", "Male", 0.1, "SEPopt"),
            ],
        )

        completed = xrecsys_main._completed_alpha_outputs(
            str(avg), str(distribution)
        )
        assert completed == {0.0, 0.05}, completed
        xrecsys_main._retain_complete_alphas(str(avg), completed)
        xrecsys_main._retain_complete_alphas(str(distribution), completed)
        assert set(xrecsys_main._alpha_row_counts(str(avg))) == completed
        assert (
            set(xrecsys_main._alpha_row_counts(str(distribution))) == completed
        )
    print("xrecsys moving-alpha resume invariant: PASS")


if __name__ == "__main__":
    main()
