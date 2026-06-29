#!/usr/bin/env python3
"""Run a small PGPR beam inference smoke from a trained policy checkpoint."""

from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path


def to_jsonable(value):
    """Convert numpy/torch scalar containers into plain JSON values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        return to_jsonable(value.item())
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", default="amazon_book_kgat_v1")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--max-acts", type=int, default=250)
    parser.add_argument("--num-users", type=int, default=8)
    parser.add_argument(
        "--beam-batch-size",
        type=int,
        default=512,
        help="Number of users per beam-search batch.",
    )
    parser.add_argument(
        "--hidden",
        type=int,
        nargs=2,
        default=[32, 16],
        metavar=("H1", "H2"),
        help="ActorCritic hidden sizes used by the policy checkpoint.",
    )
    parser.add_argument("--topk", type=int, nargs=3, default=[5, 5, 1])
    parser.add_argument(
        "--paths-pkl",
        help="Optional PGPR policy_paths-style pickle to write for adapter/export smokes.",
    )
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    summary_path = Path(args.summary_json).resolve()
    pgpr_root = runtime_root / "models" / "PGPR"
    os.chdir(pgpr_root)
    sys.path.insert(0, str(pgpr_root))
    sys.path.insert(0, str(runtime_root))

    import torch

    from kg_env import BatchKGEnvironment
    from test_agent import batch_beam_search
    from train_agent import ActorCritic
    from utils import BOOK, load_labels

    policy_file = (
        pgpr_root
        / "tmp"
        / args.dataset
        / args.run_name
        / f"policy_model_epoch_{args.epoch}.ckpt"
    )
    if not policy_file.exists():
        raise FileNotFoundError(policy_file)

    env = BatchKGEnvironment(args.dataset, args.max_acts, max_path_len=3, state_history=1)
    model = ActorCritic(
        env.state_dim,
        env.act_dim,
        gamma=0.99,
        hidden_sizes=args.hidden,
    ).to(torch.device("cpu"))
    pretrained = torch.load(policy_file, map_location="cpu")
    model_state = model.state_dict()
    model_state.update(pretrained)
    model.load_state_dict(model_state)

    test_labels = load_labels(args.dataset, "test")
    user_ids = sorted(test_labels)
    if args.num_users > 0:
        user_ids = user_ids[: args.num_users]
    paths, probs = [], []
    for start in range(0, len(user_ids), args.beam_batch_size):
        batch_user_ids = user_ids[start : start + args.beam_batch_size]
        batch_paths, batch_probs = batch_beam_search(
            env,
            model,
            batch_user_ids,
            torch.device("cpu"),
            topk=args.topk,
        )
        paths.extend(batch_paths)
        probs.extend(batch_probs)
    book_ending_paths = [path for path in paths if path[-1][1] == BOOK]
    finite_prob_rows = [
        all(math.isfinite(float(probability)) for probability in row)
        for row in probs
    ]
    status = "PASS"
    if not paths or len(probs) != len(paths) or not all(finite_prob_rows):
        status = "FAIL"
    if not book_ending_paths:
        status = "FAIL"
    paths_pkl = Path(args.paths_pkl).resolve() if args.paths_pkl else None
    if paths_pkl is not None:
        paths_pkl.parent.mkdir(parents=True, exist_ok=True)
        with paths_pkl.open("wb") as handle:
            pickle.dump({"paths": paths, "probs": probs}, handle)

    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "runtime_root": str(runtime_root),
        "policy_file": str(policy_file),
        "run_name": args.run_name,
        "epoch": args.epoch,
        "max_acts": args.max_acts,
        "hidden": args.hidden,
        "topk": args.topk,
        "beam_batch_size": args.beam_batch_size,
        "num_users": len(user_ids),
        "user_ids": user_ids,
        "state_dim": env.state_dim,
        "act_dim": env.act_dim,
        "path_count": len(paths),
        "paths_pkl": str(paths_pkl) if paths_pkl is not None else None,
        "probability_rows": len(probs),
        "book_ending_path_count": len(book_ending_paths),
        "finite_probability_rows": sum(finite_prob_rows),
        "path_examples": paths[:10],
        "probability_examples": probs[:10],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    jsonable_summary = to_jsonable(summary)
    summary_path.write_text(json.dumps(jsonable_summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(jsonable_summary, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
