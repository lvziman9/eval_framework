"""
UCPR Adapter
============
Converts UCPR's extracted `pred_paths.pkl` into the three CSV files
expected by xrecsys:

  pred_paths.csv           uid, pid, path_score, path_prob, path
  uid_topk.csv             uid, top10
  uid_pid_explanation.csv  uid, pid, path

This adapter is intentionally lightweight:
1. Reuse UCPR's already-extracted `pred_paths.pkl`
2. Map UCPR's compact uid/product indices back to canonical/xrecsys ids
3. Rename model-local product/entity/relation aliases to the canonical
   LastFM or ML-1M path schema
4. Preserve UCPR's ranking logic as closely as possible:
   - best path per (uid, pid) chosen by path probability
   - final item ranking chosen by (path_score, path_prob)

Backward compatibility
----------------------
For LastFM, the adapter keeps backward compatibility with the older local UCPR
conversion output:

  runs/debug_compare/2026-03-24_ucpr_lastfm_converter/output/
    user_remap.tsv
    product_remap.tsv

Usage
-----
  python adapters/ucpr_adapter.py \
      --pred-pkl /usr1/home/.../rep-path-reasoning-recsys/results/lfm1m/ucpr/pred_paths.pkl \
      --dataset lastfm \
      --xrecsys-dir xrecsys \
      --topk 10 \
      --agent-topk-tag 10-12-1-ucpr \
      --user-remap runs/.../model_views/ucpr/preprocessed/user_remap.tsv \
      --product-remap runs/.../model_views/ucpr/preprocessed/product_remap.tsv \
      --labels-dir runs/.../labels
"""

import argparse
import csv
import os
import pickle
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from base_adapter import format_path, load_train_labels, write_csvs


RELATION_ALIASES = {
    "lastfm": {
        "belong_to_genre": "belong_to",
        "featured_by_artist": "featured_by",
        "mixed_by_engineer": "mixed_by",
    },
    "ml1m": {
        "belong_to_category": "belong_to",
        "cinematography_by_cinematographer": "cinematography",
        "composed_by_composer": "composed_by",
        "directed_by_director": "directed_by",
        "edited_by_editor": "edited_by",
        "produced_by_prodcompany": "produced_by_company",
        "starred_by_actor": "starring",
        "wrote_by_writter": "wrote_by",
    },
}

ENTITY_ALIASES = {
    "lastfm": {
        "product": "song",
        "genre": "category",
    },
    "ml1m": {
        "product": "movie",
        "prodcompany": "production_company",
    },
}


def _load_ucpr_uid_to_xrecsys_uid(repo_root: Path, user_remap: Path = None) -> dict:
    """
    Load UCPR uid -> canonical/xrecsys user id.

    New canonical views write:
      canonical_uid -> ucpr_uid

    The older converter wrote:
      raw_lastfm_uid -> ucpr_uid, then needed xrecsys user_mappings.txt.
    """
    if user_remap is None:
        converter_dir = repo_root / "runs" / "debug_compare" / "2026-03-24_ucpr_lastfm_converter" / "output"
        user_remap = converter_dir / "user_remap.tsv"

    with open(user_remap, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = set(reader.fieldnames or [])
        if {"canonical_uid", "ucpr_uid"}.issubset(fieldnames):
            return {int(row["ucpr_uid"]): int(row["canonical_uid"]) for row in reader}

        if not {"raw_lastfm_uid", "ucpr_uid"}.issubset(fieldnames):
            raise ValueError(f"Unsupported user remap schema in {user_remap}: {reader.fieldnames}")

        raw_to_ucpr = {
            int(row["raw_lastfm_uid"]): int(row["ucpr_uid"])
            for row in reader
        }

    xrecsys_user_map = repo_root / "xrecsys" / "datasets" / "lastfm" / "mappings" / "user_mappings.txt"

    raw_to_xrecsys = {}
    with open(xrecsys_user_map) as f:
        next(f)  # header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            kgid = int(parts[0])
            raw_uid = int(parts[1])
            raw_to_xrecsys[raw_uid] = kgid

    ucpr_to_xrecsys = {}
    missing = 0
    for raw_uid, ucpr_uid in raw_to_ucpr.items():
        if raw_uid not in raw_to_xrecsys:
            missing += 1
            continue
        ucpr_to_xrecsys[ucpr_uid] = raw_to_xrecsys[raw_uid]

    if missing:
        print(f"Warning: {missing} raw user ids from UCPR remap not found in xrecsys user mappings")
    return ucpr_to_xrecsys


def _load_ucpr_pid_to_xrecsys_pid(repo_root: Path, product_remap: Path = None) -> dict:
    """
    Load UCPR product idx -> canonical/xrecsys product id.

    New canonical views write:
      canonical_pid -> ucpr_product_idx

    The older converter wrote:
      raw_xrecsys_pid -> ucpr_product_idx
    into:
      ucpr_product_idx -> xrecsys/canonical pid
    """
    if product_remap is None:
        converter_dir = repo_root / "runs" / "debug_compare" / "2026-03-24_ucpr_lastfm_converter" / "output"
        product_remap = converter_dir / "product_remap.tsv"

    ucpr_to_xrecsys = {}
    with open(product_remap, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = set(reader.fieldnames or [])
        if {"canonical_pid", "ucpr_product_idx"}.issubset(fieldnames):
            for row in reader:
                x_pid = int(row["canonical_pid"])
                ucpr_pid = int(row["ucpr_product_idx"])
                ucpr_to_xrecsys[ucpr_pid] = x_pid
            return ucpr_to_xrecsys

        if not {"raw_xrecsys_pid", "ucpr_product_idx"}.issubset(fieldnames):
            raise ValueError(f"Unsupported product remap schema in {product_remap}: {reader.fieldnames}")

        for row in reader:
            x_pid = int(row["raw_xrecsys_pid"])
            ucpr_pid = int(row["ucpr_product_idx"])
            ucpr_to_xrecsys[ucpr_pid] = x_pid
    return ucpr_to_xrecsys


def _convert_path_tuples(path_tuples, uid_map, pid_map, dataset):
    """
    Convert UCPR path tuples into xrecsys-compatible tuples.

    UCPR lastfm currently emits collaborative paths such as:
      ('self_loop','user',uid)
      ('listened','product',seed_pid)
      ('listened','user',bridge_uid)
      ('listened','product',target_pid)

    xrecsys lastfm expects `song` instead of `product` and `category`
    instead of UCPR's `genre`, but does accept collaborative
    `... listened user ... listened song ...` paths.
    """
    converted = []
    for rel, etype, eid in path_tuples:
        rel = RELATION_ALIASES[dataset].get(rel, rel)
        etype = ENTITY_ALIASES[dataset].get(etype, etype)

        if etype in {"song", "movie"}:
            eid = pid_map.get(int(eid))
        elif etype == "user":
            eid = uid_map.get(int(eid))
        else:
            eid = int(eid)
        if eid is None:
            return None
        converted.append((rel, etype, eid))
    return converted


def convert(
    pred_pkl: str,
    dataset: str,
    xrecsys_dir: str,
    topk: int = 10,
    agent_topk_tag: str = None,
    user_remap: str = None,
    product_remap: str = None,
    labels_dir: str = None,
) -> None:
    if dataset not in RELATION_ALIASES:
        raise ValueError(f"UCPR adapter does not support dataset={dataset!r}.")

    pred_pkl = Path(pred_pkl)
    xrecsys_dir = Path(xrecsys_dir)
    repo_root = xrecsys_dir.parent if xrecsys_dir.name == "xrecsys" else Path.cwd()

    print(f"Loading {pred_pkl} ...")
    with open(pred_pkl, "rb") as f:
        pred_paths = pickle.load(f)

    print(f"  {len(pred_paths):,} users with extracted paths")
    print("Loading remap tables ...")
    uid_map = _load_ucpr_uid_to_xrecsys_uid(repo_root, Path(user_remap) if user_remap else None)
    pid_map = _load_ucpr_pid_to_xrecsys_pid(repo_root, Path(product_remap) if product_remap else None)
    print(f"  uid remap entries       : {len(uid_map):,}")
    print(f"  product remap entries   : {len(pid_map):,}")
    train_set = load_train_labels(xrecsys_dir, dataset, labels_dir=labels_dir)

    pred_rows = []
    uid_topk = {}
    uid_pid_best = {}

    skipped_uid = 0
    skipped_pid = 0
    skipped_path = 0

    for ucpr_uid, pid_dict in pred_paths.items():
        x_uid = uid_map.get(int(ucpr_uid))
        if x_uid is None:
            skipped_uid += 1
            continue

        items_scores = []
        for ucpr_pid, path_list in pid_dict.items():
            x_pid = pid_map.get(int(ucpr_pid))
            if x_pid is None:
                skipped_pid += 1
                continue
            if x_uid in train_set and x_pid in train_set[x_uid]:
                continue

            converted_paths = []
            for score, path_prob, path_tuples in path_list:
                converted = _convert_path_tuples(path_tuples, uid_map, pid_map, dataset)
                if converted is None:
                    skipped_path += 1
                    continue
                path_str = format_path(converted)
                pred_rows.append((x_uid, x_pid, score, path_prob, path_str))
                converted_paths.append((score, path_prob, converted))

            if not converted_paths:
                continue

            # UCPR's evaluate_paths(): best path per item chosen by path_prob.
            best = max(converted_paths, key=lambda x: x[1])
            items_scores.append((x_pid, best[0], best[1], best[2]))

        # UCPR's final top-k: sorted by (path_score, path_prob), descending.
        items_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_items = items_scores[:topk]
        uid_topk[x_uid] = [pid for pid, _, _, _ in top_items]
        uid_pid_best[x_uid] = {pid: format_path(path_tuples) for pid, _, _, path_tuples in top_items}

    if agent_topk_tag is None:
        agent_topk_tag = f"{topk}-{topk + 2}-1-ucpr"
    output_dir = xrecsys_dir / "paths" / dataset / f"agent_topk={agent_topk_tag}"

    print(f"Writing CSVs to {output_dir} ...")
    write_csvs(output_dir, pred_rows, uid_topk, uid_pid_best)

    print("Done.")
    print(f"  pred_paths.csv          : {len(pred_rows):,} rows")
    print(f"  uid_topk.csv            : {len(uid_topk):,} users")
    print(f"  uid_pid_explanation.csv : {sum(len(v) for v in uid_pid_best.values()):,} uid-pid pairs")
    print(f"  skipped users           : {skipped_uid:,}")
    print(f"  skipped products        : {skipped_pid:,}")
    print(f"  skipped paths           : {skipped_path:,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert UCPR pred_paths.pkl to xrecsys CSVs")
    parser.add_argument("--pred-pkl", required=True, help="Path to UCPR pred_paths.pkl")
    parser.add_argument("--dataset", required=True, choices=sorted(RELATION_ALIASES))
    parser.add_argument("--xrecsys-dir", default="xrecsys", help="Root of xrecsys repo clone")
    parser.add_argument("--topk", type=int, default=10, help="Top-K items per user")
    parser.add_argument("--agent-topk-tag", default=None, help="Folder tag e.g. 10-12-1-ucpr")
    parser.add_argument("--user-remap", default=None, help="Optional canonical user_remap.tsv")
    parser.add_argument("--product-remap", default=None, help="Optional canonical product_remap.tsv")
    parser.add_argument("--labels-dir", default=None, help="Optional canonical labels dir containing train_label.pkl")
    args = parser.parse_args()

    convert(
        pred_pkl=args.pred_pkl,
        dataset=args.dataset,
        xrecsys_dir=args.xrecsys_dir,
        topk=args.topk,
        agent_topk_tag=args.agent_topk_tag,
        user_remap=args.user_remap,
        product_remap=args.product_remap,
        labels_dir=args.labels_dir,
    )
