"""Convert CAFE native pred_paths.pkl into canonical xrecsys path CSVs."""

from __future__ import annotations

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
    "beauty": {
        "described_by": "described_as",
    },
    "beauty_legacy_v1": {
        "described_by": "described_as",
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
    "beauty": {},
    "beauty_legacy_v1": {},
}


def load_inverse_remap(path: Path, canonical_col: str, model_col: str) -> dict[int, int]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not {canonical_col, model_col}.issubset(reader.fieldnames or []):
            raise ValueError(f"Unexpected remap columns in {path}: {reader.fieldnames}")
        return {int(row[model_col]): int(row[canonical_col]) for row in reader}


def convert_path(path_tuples, uid_map, pid_map, dataset):
    converted = []
    for relation, entity_type, entity_id in path_tuples:
        if relation.startswith("rev_"):
            relation = relation[len("rev_") :]
        relation = RELATION_ALIASES[dataset].get(relation, relation)
        entity_type = ENTITY_ALIASES[dataset].get(entity_type, entity_type)
        if entity_type == "user":
            entity_id = uid_map.get(int(entity_id))
        elif entity_type in {"song", "movie", "product"}:
            entity_id = pid_map.get(int(entity_id))
        else:
            entity_id = int(entity_id)
        if entity_id is None:
            return None
        converted.append((relation, entity_type, entity_id))
    return converted


def convert(
    pred_pkl: str,
    dataset: str,
    xrecsys_dir: str,
    user_remap: str,
    product_remap: str,
    labels_dir: str,
    topk: int = 10,
    agent_topk_tag: str = "cafe-canonical",
) -> None:
    if dataset not in RELATION_ALIASES:
        raise ValueError(f"CAFE adapter does not support dataset={dataset!r}.")

    uid_map = load_inverse_remap(Path(user_remap), "canonical_uid", "cafe_uid")
    pid_map = load_inverse_remap(Path(product_remap), "canonical_pid", "cafe_product_idx")
    with open(pred_pkl, "rb") as f:
        pred_paths = pickle.load(f)

    xrecsys_dir = Path(xrecsys_dir)
    train_set = load_train_labels(xrecsys_dir, dataset, labels_dir=labels_dir)
    pred_rows = []
    uid_topk = {}
    uid_pid_best = {}
    skipped = {"user": 0, "product": 0, "path": 0}

    for cafe_uid, pid_dict in pred_paths.items():
        uid = uid_map.get(int(cafe_uid))
        if uid is None:
            skipped["user"] += 1
            continue
        ranked_items = []
        for cafe_pid, path_list in pid_dict.items():
            pid = pid_map.get(int(cafe_pid))
            if pid is None:
                skipped["product"] += 1
                continue
            if uid in train_set and pid in train_set[uid]:
                continue

            converted_paths = []
            for score, path_prob, path_tuples in path_list:
                if (
                    not path_tuples
                    or int(path_tuples[0][2]) != int(cafe_uid)
                    or int(path_tuples[-1][2]) != int(cafe_pid)
                ):
                    raise ValueError(
                        "CAFE path endpoints do not match their enclosing keys: "
                        f"uid={cafe_uid}, pid={cafe_pid}, path={path_tuples}"
                    )
                converted = convert_path(path_tuples, uid_map, pid_map, dataset)
                if converted is None:
                    skipped["path"] += 1
                    continue
                score = float(score)
                path_prob = float(path_prob)
                pred_rows.append((uid, pid, score, path_prob, format_path(converted)))
                converted_paths.append((score, path_prob, converted))
            if not converted_paths:
                continue

            # The runtime stores CAFE's summed path log-probability as score.
            best = max(converted_paths, key=lambda row: row[0])
            ranked_items.append((pid, best[0], best[1], best[2]))

        ranked_items.sort(key=lambda row: (row[1], row[2]), reverse=True)
        top_items = ranked_items[:topk]
        uid_topk[uid] = [pid for pid, _, _, _ in top_items]
        uid_pid_best[uid] = {
            pid: format_path(path_tuples) for pid, _, _, path_tuples in top_items
        }

    output_dir = xrecsys_dir / "paths" / dataset / f"agent_topk={agent_topk_tag}"
    if not pred_rows:
        raise ValueError("CAFE produced no unseen canonical candidate paths.")
    min_score = min(row[2] for row in pred_rows)
    max_score = max(row[2] for row in pred_rows)
    score_range = max_score - min_score if max_score != min_score else 1.0
    pred_rows = [
        (uid, pid, (score - min_score) / score_range, path_prob, path)
        for uid, pid, score, path_prob, path in pred_rows
    ]
    write_csvs(output_dir, pred_rows, uid_topk, uid_pid_best)
    print(f"Wrote CAFE outputs to {output_dir}")
    print(f"  raw score range         : [{min_score:.6f}, {max_score:.6f}]")
    print(f"  pred_paths.csv          : {len(pred_rows):,}")
    print(f"  uid_topk.csv            : {len(uid_topk):,}")
    print(f"  uid_pid_explanation.csv : {sum(len(v) for v in uid_pid_best.values()):,}")
    print(f"  skipped                 : {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-pkl", required=True)
    parser.add_argument("--dataset", required=True, choices=sorted(RELATION_ALIASES))
    parser.add_argument("--xrecsys-dir", default="xrecsys")
    parser.add_argument("--user-remap", required=True)
    parser.add_argument("--product-remap", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--agent-topk-tag", default="cafe-canonical")
    args = parser.parse_args()
    convert(
        pred_pkl=args.pred_pkl,
        dataset=args.dataset,
        xrecsys_dir=args.xrecsys_dir,
        user_remap=args.user_remap,
        product_remap=args.product_remap,
        labels_dir=args.labels_dir,
        topk=args.topk,
        agent_topk_tag=args.agent_topk_tag,
    )


if __name__ == "__main__":
    main()
