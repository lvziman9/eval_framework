#!/usr/bin/env python3
"""Run PGPR beam inference and export xrecsys CSVs without a giant paths pickle.

The legacy PGPR inference path accumulates every sampled path in Python memory
and then serializes one large ``policy_paths`` pickle.  That is fine for ML-1M
and LastFM, but Amazon-book KGAT has ~70k test users; beam=10-12-1 can create
millions of path objects.  This exporter keeps the native PGPR beam search and
ranking semantics, but streams candidate rows through a temporary CSV and keeps
only per-user top-k state in memory.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pickle
import sys
from datetime import datetime, timezone
from functools import reduce
from operator import mul
from pathlib import Path
from typing import Dict, List, Set, Tuple


def format_path(path_tuples) -> str:
    return " ".join(str(part) for triple in path_tuples for part in triple)


def load_label_sets(labels_dir: Path, split: str) -> Dict[int, Set[int]]:
    with (labels_dir / f"{split}_label.pkl").open("rb") as handle:
        raw = pickle.load(handle)
    return {int(uid): {int(pid) for pid in pids} for uid, pids in raw.items()}


def to_jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        return to_jsonable(value.item())
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return str(value)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(payload), indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", default="amazon_book_kgat_v1")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--embedding-pkl", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--paths-dir", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--max-acts", type=int, default=250)
    parser.add_argument("--beam-batch-size", type=int, default=128)
    parser.add_argument("--hidden", type=int, nargs=2, default=[512, 256])
    parser.add_argument("--topk", type=int, nargs=3, default=[10, 12, 1])
    parser.add_argument("--recommendation-topk", type=int, default=10)
    parser.add_argument(
        "--num-users",
        type=int,
        default=0,
        help="Optional smoke limit; 0 exports every canonical test user.",
    )
    parser.add_argument(
        "--keep-raw-temp",
        action="store_true",
        help="Keep pred_paths.raw.tmp.csv for debugging after final CSV generation.",
    )
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    pgpr_root = runtime_root / "models" / "PGPR"
    labels_dir = Path(args.labels_dir).resolve()
    paths_dir = Path(args.paths_dir).resolve()
    summary_path = Path(args.summary_json).resolve()
    embedding_path = Path(args.embedding_pkl).resolve()
    paths_dir.mkdir(parents=True, exist_ok=True)

    os.chdir(pgpr_root)
    sys.path.insert(0, str(pgpr_root))
    sys.path.insert(0, str(runtime_root))

    import torch

    from kg_env import BatchKGEnvironment
    from test_agent import batch_beam_search
    from train_agent import ActorCritic
    from utils import get_interaction_relation, get_product_entity

    product_type = get_product_entity(args.dataset)
    interaction = get_interaction_relation(args.dataset)

    policy_file = (
        pgpr_root
        / "tmp"
        / args.dataset
        / args.run_name
        / f"policy_model_epoch_{args.epoch}.ckpt"
    )
    if not policy_file.exists():
        raise FileNotFoundError(policy_file)
    if not embedding_path.exists():
        raise FileNotFoundError(embedding_path)

    train = load_label_sets(labels_dir, "train")
    valid_path = labels_dir / "valid_label.pkl"
    if valid_path.exists():
        for uid, pids in load_label_sets(labels_dir, "valid").items():
            train.setdefault(uid, set()).update(pids)
    test = load_label_sets(labels_dir, "test")
    user_ids = sorted(test)
    if args.num_users > 0:
        user_ids = user_ids[: args.num_users]

    with embedding_path.open("rb") as handle:
        embeddings = pickle.load(handle)
    user_embeddings = embeddings["user"]
    product_embeddings = embeddings[product_type]
    interaction_embedding = embeddings[interaction][0]
    score_cache = {}  # type: Dict[int, Dict[int, float]]

    def item_score(uid: int, pid: int) -> float:
        if uid >= len(user_embeddings) or pid >= len(product_embeddings):
            raise IndexError(f"PGPR embedding index out of range: uid={uid}, pid={pid}")
        user_scores = score_cache.setdefault(uid, {})
        if pid not in user_scores:
            user_scores[pid] = float(
                (user_embeddings[uid] + interaction_embedding).dot(product_embeddings[pid])
            )
        return user_scores[pid]

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
    model.eval()

    raw_tmp = paths_dir / "pred_paths.raw.tmp.csv"
    pred_tmp = paths_dir / "pred_paths.csv.tmp"
    uid_tmp = paths_dir / "uid_topk.csv.tmp"
    explanation_tmp = paths_dir / "uid_pid_explanation.csv.tmp"

    top_candidates = {}  # type: Dict[int, Dict[int, Tuple[float, float, str]]]
    min_score = math.inf
    max_score = -math.inf
    raw_rows = 0
    valid_path_count = 0
    skipped_non_product = 0
    skipped_seen = 0
    finite_probability_rows = 0
    processed_users = 0

    start_payload = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "stage": "beam_stream",
        "runtime_root": str(runtime_root),
        "policy_file": str(policy_file),
        "embedding_pkl": str(embedding_path),
        "paths_dir": str(paths_dir),
        "labels_dir": str(labels_dir),
        "topk": args.topk,
        "recommendation_topk": args.recommendation_topk,
        "beam_batch_size": args.beam_batch_size,
        "test_users": len(user_ids),
        "canonical_test_users": len(test),
        "num_users_limit": args.num_users,
        "state_dim": env.state_dim,
        "act_dim": env.act_dim,
    }
    write_json(summary_path, start_payload)

    with raw_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "raw_score", "path_prob", "path"])
        for start in range(0, len(user_ids), args.beam_batch_size):
            batch_user_ids = user_ids[start : start + args.beam_batch_size]
            paths, probs = batch_beam_search(
                env,
                model,
                batch_user_ids,
                torch.device("cpu"),
                topk=args.topk,
            )
            processed_users += len(batch_user_ids)
            for path_tuples, prob_list in zip(paths, probs):
                if not path_tuples or path_tuples[-1][1] != product_type:
                    skipped_non_product += 1
                    continue
                uid = int(path_tuples[0][2])
                pid = int(path_tuples[-1][2])
                if uid not in test:
                    raise ValueError(f"PGPR path uid={uid} is absent from canonical test labels")
                if pid in train.get(uid, set()):
                    skipped_seen += 1
                    continue
                action_probs = [float(value) for value in prob_list]
                if not all(math.isfinite(value) for value in action_probs):
                    raise ValueError(f"Non-finite PGPR path probability for uid={uid}, pid={pid}")
                path_prob = reduce(mul, action_probs, 1.0)
                if math.isfinite(path_prob):
                    finite_probability_rows += 1
                else:
                    raise ValueError(f"Non-finite PGPR path probability product for uid={uid}, pid={pid}")
                score = item_score(uid, pid)
                path_str = format_path(path_tuples)
                writer.writerow([uid, pid, score, path_prob, path_str])
                raw_rows += 1
                valid_path_count += 1
                min_score = min(min_score, score)
                max_score = max(max_score, score)

                user_top = top_candidates.setdefault(uid, {})
                current = user_top.get(pid)
                if current is not None:
                    if path_prob > current[1]:
                        user_top[pid] = (score, path_prob, path_str)
                    continue
                if len(user_top) < args.recommendation_topk:
                    user_top[pid] = (score, path_prob, path_str)
                    continue
                worst_pid, worst = min(
                    user_top.items(), key=lambda row: (row[1][0], row[1][1])
                )
                if (score, path_prob) > (worst[0], worst[1]):
                    del user_top[worst_pid]
                    user_top[pid] = (score, path_prob, path_str)

            if processed_users % max(args.beam_batch_size * 10, 1) == 0:
                print(
                    "processed_users={} raw_rows={} candidate_users={}".format(
                        processed_users, raw_rows, len(top_candidates)
                    ),
                    flush=True,
                )

    if valid_path_count == 0:
        raise ValueError("PGPR produced no unseen product-ending candidate paths.")
    score_range = max_score - min_score if max_score != min_score else 1.0

    with raw_tmp.open(newline="") as source, pred_tmp.open("w", newline="") as target:
        reader = csv.DictReader(source)
        writer = csv.writer(target)
        writer.writerow(["uid", "pid", "path_score", "path_prob", "path"])
        for row in reader:
            score = float(row["raw_score"])
            writer.writerow(
                [
                    row["uid"],
                    row["pid"],
                    (score - min_score) / score_range,
                    row["path_prob"],
                    row["path"],
                ]
            )

    uid_topk = {uid: [] for uid in user_ids}  # type: Dict[int, List[int]]
    uid_pid_best = {uid: {} for uid in user_ids}  # type: Dict[int, Dict[int, str]]
    for uid, pid_candidates in top_candidates.items():
        top_items = sorted(
            (
                (pid, score, path_prob, path_str)
                for pid, (score, path_prob, path_str) in pid_candidates.items()
            ),
            key=lambda row: (row[1], row[2]),
            reverse=True,
        )
        uid_topk[uid] = [pid for pid, _, _, _ in top_items]
        uid_pid_best[uid] = {pid: path_str for pid, _, _, path_str in top_items}

    with uid_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "top10"])
        for uid in user_ids:
            writer.writerow([uid, " ".join(str(pid) for pid in uid_topk[uid])])

    with explanation_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "path"])
        for uid in user_ids:
            for pid, path_str in uid_pid_best[uid].items():
                writer.writerow([uid, pid, path_str])

    pred_tmp.replace(paths_dir / "pred_paths.csv")
    uid_tmp.replace(paths_dir / "uid_topk.csv")
    explanation_tmp.replace(paths_dir / "uid_pid_explanation.csv")
    if not args.keep_raw_temp:
        if raw_tmp.exists():
            raw_tmp.unlink()

    recommendation_counts = [len(uid_topk[uid]) for uid in user_ids]
    summary = {
        **start_payload,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "stage": "complete",
        "processed_users": processed_users,
        "raw_candidate_rows": raw_rows,
        "valid_path_count": valid_path_count,
        "candidate_users": len(top_candidates),
        "topk_users": len(uid_topk),
        "empty_users": sum(1 for count in recommendation_counts if count == 0),
        "short_users": sum(
            1 for count in recommendation_counts if count < args.recommendation_topk
        ),
        "min_recommendations": min(recommendation_counts),
        "max_recommendations": max(recommendation_counts),
        "mean_recommendations": sum(recommendation_counts) / len(recommendation_counts),
        "slot_coverage": sum(recommendation_counts)
        / (len(recommendation_counts) * args.recommendation_topk),
        "finite_probability_rows": finite_probability_rows,
        "skipped_non_product_endpoints": skipped_non_product,
        "skipped_seen_items": skipped_seen,
        "score_range": [min_score, max_score],
        "cached_native_item_scores": sum(len(values) for values in score_cache.values()),
        "outputs": {
            "pred_paths": str(paths_dir / "pred_paths.csv"),
            "uid_topk": str(paths_dir / "uid_topk.csv"),
            "uid_pid_explanation": str(paths_dir / "uid_pid_explanation.csv"),
        },
    }
    write_json(summary_path, summary)
    print(json.dumps(to_jsonable(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
