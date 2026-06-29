"""
PGPR Adapter
============
Converts PGPR's policy_paths_epoch<N>.pkl into the three CSV files
expected by xrecsys:

  pred_paths.csv           uid, pid, path_score, path_prob, path
  uid_topk.csv             uid, top10
  uid_pid_explanation.csv  uid, pid, path

Input pkl structure
-------------------
  {
    'paths': [                                              # one entry per sampled path
      [('self_loop','user',uid), ('rel','etype',eid), ..., ('rel','movie',pid)],
      ...
    ],
    'probs': [                                              # one entry per sampled path
      [step0_probability, step1_probability, ...],
      ...
    ]
  }

Path score = native PGPR TransE item relevance loaded from `transe_embed.pkl`,
then normalized globally to [0, 1]. Path probability is the product of the
policy's per-step action probabilities.

Usage
-----
  # run from eval_framework/ root
  python adapters/pgpr_adapter.py \\
      --pkl   xrecsys/models/PGPR/tmp/ml1m/train_agent/policy_paths_epoch50.pkl \\
      --dataset ml1m \\
      --xrecsys-dir xrecsys \\
      --topk 10
"""

import argparse
import csv
import pickle
import sys
import os
from functools import reduce
from operator import mul
from pathlib import Path

import numpy as np

# allow running as standalone script from any working directory
sys.path.insert(0, os.path.dirname(__file__))
from base_adapter import format_path, load_train_labels




def convert(
    pkl_path: str,
    dataset: str,
    xrecsys_dir: str,
    topk: int = 10,
    agent_topk_tag: str = None,
    labels_dir: str = None,
    embedding_pkl: str = None,
) -> None:
    """
    Read policy_paths pkl and write the three xrecsys CSVs.

    Parameters
    ----------
    pkl_path      : path to policy_paths_epoch<N>.pkl
    dataset       : 'ml1m' or 'lastfm'
    xrecsys_dir   : root of the xrecsys repo clone
    topk          : number of top items to recommend per user (default 10)
    agent_topk_tag: folder suffix, e.g. '10-12-1'; inferred from topk if None
    """
    pkl_path    = Path(pkl_path)
    xrecsys_dir = Path(xrecsys_dir)

    print(f"Loading {pkl_path} ...")
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)

    paths = data['paths']
    probs = data['probs']
    print(f"  {len(paths):,} sampled paths")
    dataset_config = {
        "ml1m": ("movie", "watched"),
        "lastfm": ("song", "listened"),
        "beauty": ("product", "purchase"),
        "beauty_legacy_v1": ("product", "purchase"),
        "amazon_book_kgat_v1": ("book", "purchased"),
    }
    if dataset not in dataset_config:
        raise ValueError(
            f"Unsupported PGPR dataset={dataset!r}; "
            f"choose one of {sorted(dataset_config)}"
        )
    product_type, interaction = dataset_config[dataset]

    item_score = None
    if embedding_pkl:
        print(f"Loading native PGPR embeddings from {embedding_pkl} ...")
        with open(embedding_pkl, "rb") as f:
            embeddings = pickle.load(f)
        user_embeddings = embeddings["user"]
        product_embeddings = embeddings[product_type]
        interaction_embedding = embeddings[interaction][0]
        score_cache = {}

        def item_score(uid, pid):
            key = (int(uid), int(pid))
            if key[0] >= len(user_embeddings) or key[1] >= len(product_embeddings):
                raise IndexError(
                    f"PGPR embedding index out of range: uid={key[0]}, pid={key[1]}"
                )
            user_scores = score_cache.setdefault(key[0], {})
            if key[1] not in user_scores:
                user_scores[key[1]] = float(
                    np.dot(
                        user_embeddings[key[0]] + interaction_embedding,
                        product_embeddings[key[1]],
                    )
                )
            return user_scores[key[1]]
    else:
        print(
            "Warning: --embedding-pkl was not provided; falling back to policy "
            "path score. This is not the native PGPR item-ranking score."
        )

    sampled_prob_values = [
        float(value)
        for prob_list in probs[: min(10000, len(probs))]
        for value in prob_list
    ]
    legacy_prob_offset = (
        1.0
        if sampled_prob_values and max(sampled_prob_values) > 1.0 + 1e-6
        else 0.0
    )
    print(f"  detected legacy probability offset: {legacy_prob_offset:.1f}")

    print("Loading train labels ...")
    train_set = load_train_labels(xrecsys_dir, dataset, labels_dir=labels_dir)
    test_users = None
    if labels_dir:
        test_path = Path(labels_dir) / "test_label.pkl"
        with test_path.open("rb") as handle:
            test_users = {int(uid) for uid in pickle.load(handle)}

    def parse_candidate(path_tuples, prob_list):
        if not path_tuples or path_tuples[-1][1] != product_type:
            return None
        if path_tuples[0][1] != "user":
            raise ValueError(f"PGPR path does not start at a user: {path_tuples}")
        uid = int(path_tuples[0][2])
        pid = int(path_tuples[-1][2])
        if test_users is not None and uid not in test_users:
            raise ValueError(f"PGPR path uid={uid} is absent from canonical test labels")
        score = item_score(uid, pid) if item_score else sum(prob_list)
        action_probs = [
            max(0.0, float(value) - legacy_prob_offset) for value in prob_list
        ]
        path_prob = reduce(mul, action_probs, 1.0)
        return uid, pid, score, path_prob

    # First pass: find the global native-score range and retain at most the
    # ten baseline candidates per user. All candidate paths remain in the
    # loaded pickle and are streamed directly during the second pass.
    top_candidates = {}
    skipped_non_product = 0
    min_score = float("inf")
    max_score = float("-inf")
    valid_path_count = 0
    for path_tuples, prob_list in zip(paths, probs):
        candidate = parse_candidate(path_tuples, prob_list)
        if candidate is None:
            skipped_non_product += 1
            continue
        uid, pid, score, path_prob = candidate
        if pid in train_set.get(uid, set()):
            continue
        valid_path_count += 1
        min_score = min(min_score, score)
        max_score = max(max_score, score)

        user_top = top_candidates.setdefault(uid, {})
        current = user_top.get(pid)
        if current is not None:
            if path_prob > current[1]:
                user_top[pid] = (score, path_prob, path_tuples)
            continue
        if len(user_top) < topk:
            user_top[pid] = (score, path_prob, path_tuples)
            continue
        worst_pid, worst = min(
            user_top.items(), key=lambda row: (row[1][0], row[1][1])
        )
        if (score, path_prob) > (worst[0], worst[1]):
            del user_top[worst_pid]
            user_top[pid] = (score, path_prob, path_tuples)

    print(f"  skipped non-{product_type} endpoints: {skipped_non_product:,}")
    if valid_path_count == 0:
        raise ValueError("PGPR produced no unseen product-ending candidate paths.")
    score_range = max_score - min_score if max_score != min_score else 1.0
    print(f"  score range: [{min_score:.4f}, {max_score:.4f}]")

    if agent_topk_tag is None:
        agent_topk_tag = f"{topk}-{topk + 2}-1"
    output_dir = xrecsys_dir / 'paths' / dataset / f'agent_topk={agent_topk_tag}'
    print(f"Writing CSVs to {output_dir} ...")
    output_dir.mkdir(parents=True, exist_ok=True)

    pred_rows = 0
    with open(output_dir / "pred_paths.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["uid", "pid", "path_score", "path_prob", "path"])
        for path_tuples, prob_list in zip(paths, probs):
            candidate = parse_candidate(path_tuples, prob_list)
            if candidate is None:
                continue
            uid, pid, score, path_prob = candidate
            if pid in train_set.get(uid, set()):
                continue
            writer.writerow(
                [
                    uid,
                    pid,
                    (score - min_score) / score_range,
                    path_prob,
                    format_path(path_tuples),
                ]
            )
            pred_rows += 1

    output_users = sorted(test_users if test_users is not None else top_candidates)
    uid_topk = {uid: [] for uid in output_users}
    uid_pid_best = {uid: {} for uid in output_users}
    for uid, pid_candidates in top_candidates.items():
        top_items = sorted(
            (
                (pid, score, path_prob, path_tuples)
                for pid, (score, path_prob, path_tuples) in pid_candidates.items()
            ),
            key=lambda row: (row[1], row[2]),
            reverse=True,
        )
        uid_topk[uid] = [pid for pid, _, _, _ in top_items]
        uid_pid_best[uid] = {
            pid: format_path(path_tuples)
            for pid, _, _, path_tuples in top_items
        }

    with open(output_dir / "uid_topk.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["uid", "top10"])
        for uid, pids in uid_topk.items():
            writer.writerow([uid, " ".join(str(pid) for pid in pids)])

    with open(output_dir / "uid_pid_explanation.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["uid", "pid", "path"])
        for uid, pid_paths in uid_pid_best.items():
            for pid, path_str in pid_paths.items():
                writer.writerow([uid, pid, path_str])

    print("Done.")
    print(f"  pred_paths.csv          : {pred_rows:,} rows")
    print(f"  uid_topk.csv            : {len(uid_topk):,} users")
    print(f"  uid_pid_explanation.csv : {sum(len(v) for v in uid_pid_best.values()):,} uid-pid pairs")
    if embedding_pkl:
        print(
            "  cached native item scores: "
            f"{sum(len(user_scores) for user_scores in score_cache.values()):,}"
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PGPR policy_paths pkl to xrecsys CSVs')
    parser.add_argument('--pkl',            required=True,          help='Path to policy_paths_epoch<N>.pkl')
    parser.add_argument(
        '--dataset',
        required=True,
        help='ml1m, lastfm, beauty, beauty_legacy_v1, or amazon_book_kgat_v1',
    )
    parser.add_argument('--xrecsys-dir',    default='xrecsys',      help='Root of xrecsys repo clone')
    parser.add_argument('--topk',           type=int, default=10,   help='Top-K items per user')
    parser.add_argument('--agent-topk-tag', default=None,
                        help='Folder tag e.g. 10-12-1; inferred from --topk if omitted')
    parser.add_argument('--labels-dir', default=None,
                        help='Optional canonical labels directory containing train_label.pkl')
    parser.add_argument('--embedding-pkl', default=None,
                        help='PGPR transe_embed.pkl used for native item relevance scores')
    args = parser.parse_args()

    convert(
        pkl_path=args.pkl,
        dataset=args.dataset,
        xrecsys_dir=args.xrecsys_dir,
        topk=args.topk,
        agent_topk_tag=args.agent_topk_tag,
        labels_dir=args.labels_dir,
        embedding_pkl=args.embedding_pkl,
    )
