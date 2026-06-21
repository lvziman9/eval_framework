#!/usr/bin/env python3
"""Regression checks for xrecsys top-k reranking invariants."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "xrecsys"))

from optimizations import _dedupe_and_fill_remaining, optimize_ETD


def candidate(pid, score, relation="shared_relation"):
    path = [
        ("self_loop", "user", "1"),
        ("watched", "movie", "0"),
        (relation, "actor", "0"),
        (relation, "movie", str(pid)),
    ]
    return [score, 0.5, path]


def main():
    candidates = [candidate(pid, 1.0 - pid / 100.0) for pid in range(20)]
    selected = candidates[:10]
    selected_pids = set(range(10))
    _dedupe_and_fill_remaining(candidates, selected, selected_pids, limit=10)
    assert len(selected) == 10
    assert len(selected_pids) == 10

    class PathData:
        pass

    path_data = PathData()
    path_data.pred_paths = {
        1: {pid: [candidate(pid, 1.0 - pid / 100.0)] for pid in range(20)}
    }
    path_data.uid_topk = {}
    path_data.uid_pid_explaination = {}
    optimize_ETD(path_data, alpha=0.5)
    assert len(path_data.uid_topk[1]) == 10, path_data.uid_topk[1]
    assert len(set(path_data.uid_topk[1])) == 10
    assert len(path_data.uid_pid_explaination[1]) == 10
    print("xrecsys ETD top-k invariant: PASS")


if __name__ == "__main__":
    main()
