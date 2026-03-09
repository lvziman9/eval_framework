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
      [step0_logprob, step1_logprob, ...],
      ...
    ]
  }

Path score = sum of per-step log-probs, then normalized globally to [0, 1]
(same convention as extract_predicted_paths.py in xrecsys).

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
import pickle
import sys
import os
from collections import defaultdict
from pathlib import Path

# allow running as standalone script from any working directory
sys.path.insert(0, os.path.dirname(__file__))
from base_adapter import format_path, load_train_labels, write_csvs




def convert(
    pkl_path: str,
    dataset: str,
    xrecsys_dir: str,
    topk: int = 10,
    agent_topk_tag: str = None,
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

    # ------------------------------------------------------------------
    # Group paths by (uid, pid)
    # uid = first tuple's id:  ('self_loop', 'user', uid)
    # pid = last  tuple's id:  ('relation',  'item', pid)
    # path score = sum of per-step log-probs
    # ------------------------------------------------------------------
    uid_pid_paths = defaultdict(lambda: defaultdict(list))
    for path_tuples, prob_list in zip(paths, probs):
        uid   = path_tuples[0][2]
        pid   = path_tuples[-1][2]
        score = sum(prob_list)
        uid_pid_paths[uid][pid].append((score, prob_list[-1], path_tuples))

    # ------------------------------------------------------------------
    # Load train labels for filtering already-seen items
    # ------------------------------------------------------------------
    print("Loading train labels ...")
    train_set = load_train_labels(xrecsys_dir, dataset)

    # ------------------------------------------------------------------
    # Global score normalisation (excluding train items)
    # ------------------------------------------------------------------
    score_list = [
        score
        for uid, pid_dict in uid_pid_paths.items()
        for pid, path_list in pid_dict.items()
        if not (uid in train_set and pid in train_set[uid])
        for (score, _, _) in path_list
    ]
    min_score   = min(score_list)
    max_score   = max(score_list)
    score_range = max_score - min_score if max_score != min_score else 1.0
    print(f"  score range: [{min_score:.4f}, {max_score:.4f}]")

    # ------------------------------------------------------------------
    # Build the three output structures
    # ------------------------------------------------------------------
    pred_rows    = []   # (uid, pid, norm_score, path_prob, path_str)
    uid_topk     = {}   # uid -> [pid, ...]  descending score order
    uid_pid_best = {}   # uid -> {pid -> path_str}  (top-k items only)

    for uid, pid_dict in uid_pid_paths.items():
        items_scores = []
        for pid, path_list in pid_dict.items():
            if uid in train_set and pid in train_set[uid]:
                continue
            # all sampled paths for this uid-pid pair -> pred_paths.csv
            for (score, last_prob, path_tuples) in path_list:
                norm_score = (score - min_score) / score_range
                pred_rows.append((uid, pid, norm_score, last_prob, format_path(path_tuples)))
            # best path per item -> used for top-k ranking & explanation CSV
            best = max(path_list, key=lambda x: x[0])
            items_scores.append((pid, best[0], best[2]))

        items_scores.sort(key=lambda x: x[1], reverse=True)
        top_items = items_scores[:topk]
        uid_topk[uid]     = [pid for pid, _, _           in top_items]
        uid_pid_best[uid] = {pid: format_path(path_tuples) for pid, _, path_tuples in top_items}

    # ------------------------------------------------------------------
    # Write CSVs
    # ------------------------------------------------------------------
    if agent_topk_tag is None:
        agent_topk_tag = f"{topk}-{topk + 2}-1"
    output_dir = xrecsys_dir / 'paths' / dataset / f'agent_topk={agent_topk_tag}'

    print(f"Writing CSVs to {output_dir} ...")
    write_csvs(output_dir, pred_rows, uid_topk, uid_pid_best)

    print("Done.")
    print(f"  pred_paths.csv          : {len(pred_rows):,} rows")
    print(f"  uid_topk.csv            : {len(uid_topk):,} users")
    print(f"  uid_pid_explanation.csv : {sum(len(v) for v in uid_pid_best.values()):,} uid-pid pairs")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PGPR policy_paths pkl to xrecsys CSVs')
    parser.add_argument('--pkl',            required=True,          help='Path to policy_paths_epoch<N>.pkl')
    parser.add_argument('--dataset',        required=True,          help='ml1m or lastfm')
    parser.add_argument('--xrecsys-dir',    default='xrecsys',      help='Root of xrecsys repo clone')
    parser.add_argument('--topk',           type=int, default=10,   help='Top-K items per user')
    parser.add_argument('--agent-topk-tag', default=None,
                        help='Folder tag e.g. 10-12-1; inferred from --topk if omitted')
    args = parser.parse_args()

    convert(
        pkl_path=args.pkl,
        dataset=args.dataset,
        xrecsys_dir=args.xrecsys_dir,
        topk=args.topk,
        agent_topk_tag=args.agent_topk_tag,
    )
