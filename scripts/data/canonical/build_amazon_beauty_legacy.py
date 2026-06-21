#!/usr/bin/env python3
"""Build a legacy-compatible canonical Amazon Beauty dataset.

The historical PGPR and CAFE Beauty assets use the same compact user/product
id space and the same train/test pair sets. This builder verifies that claim,
restores rating/timestamp fields from the raw Amazon review file, and emits a
canonical dataset without changing the historical split.

The validation split is intentionally empty. Moving interactions out of the
historical training split would also require rebuilding CAFE's interaction and
review-text KG edges; doing only the label split would leak validation data
through the graph.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import pickle
from collections import defaultdict
from pathlib import Path


def read_vocab(path: Path) -> list[str]:
    with gzip.open(path, "rt") as f:
        return [line.rstrip("\n") for line in f]


def read_pgpr_pairs(path: Path) -> list[tuple[int, int]]:
    pairs = []
    with gzip.open(path, "rt") as f:
        for line in f:
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 2:
                raise ValueError(f"Malformed PGPR row in {path}: {line!r}")
            pairs.append((int(columns[0]), int(columns[1])))
    if len(pairs) != len(set(pairs)):
        raise ValueError(f"Duplicate user-product pairs in {path}")
    return pairs


def read_cafe_labels(path: Path) -> dict[int, list[int]]:
    labels = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            columns = [int(value) for value in line.rstrip("\n").split("\t") if value]
            if not columns:
                continue
            uid, pids = columns[0], columns[1:]
            if uid in labels:
                raise ValueError(f"Duplicate uid={uid} in {path}")
            if len(pids) != len(set(pids)):
                raise ValueError(f"Duplicate products for uid={uid} in {path}")
            labels[uid] = pids
    return labels


def pairs_to_labels(pairs: list[tuple[int, int]]) -> dict[int, list[int]]:
    labels = defaultdict(list)
    for uid, pid in pairs:
        labels[uid].append(pid)
    return dict(labels)


def compare_label_sets(
    pgpr_labels: dict[int, list[int]],
    cafe_labels: dict[int, list[int]],
    split: str,
) -> dict:
    if set(pgpr_labels) != set(cafe_labels):
        raise ValueError(f"PGPR/CAFE {split} user sets differ")
    mismatched = [
        uid
        for uid in pgpr_labels
        if set(pgpr_labels[uid]) != set(cafe_labels[uid])
    ]
    if mismatched:
        raise ValueError(
            f"PGPR/CAFE {split} product sets differ for users {mismatched[:5]}"
        )
    return {
        "users": len(pgpr_labels),
        "interactions": sum(len(pids) for pids in pgpr_labels.values()),
        "per_user_pair_sets_equal": True,
        "per_user_list_order_equal": all(
            pgpr_labels[uid] == cafe_labels[uid] for uid in pgpr_labels
        ),
    }


def load_raw_reviews(
    path: Path,
    user_to_id: dict[str, int],
    product_to_id: dict[str, int],
) -> tuple[dict[tuple[int, int], tuple[int, int]], dict]:
    reviews = {}
    raw_rows = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            raw_rows += 1
            review = json.loads(line)
            raw_uid = review["reviewerID"]
            raw_pid = review["asin"]
            if raw_uid not in user_to_id or raw_pid not in product_to_id:
                raise ValueError(
                    f"Raw review id absent from PGPR vocab: user={raw_uid}, asin={raw_pid}"
                )
            pair = (user_to_id[raw_uid], product_to_id[raw_pid])
            if pair in reviews:
                raise ValueError(f"Duplicate raw review pair: {pair}")
            reviews[pair] = (
                int(float(review.get("overall", 1))),
                int(review.get("unixReviewTime", -1)),
            )
    return reviews, {
        "raw_review_rows": raw_rows,
        "mapped_unique_pairs": len(reviews),
        "duplicate_pairs": 0,
    }


def write_interactions(
    path: Path,
    pairs: list[tuple[int, int]],
    reviews: dict[tuple[int, int], tuple[int, int]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for uid, pid in pairs:
            rating, timestamp = reviews[(uid, pid)]
            writer.writerow([uid, pid, rating, timestamp])


def write_pickle(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(value, f)


def write_mapping(path: Path, header: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pgpr-data-dir", required=True)
    parser.add_argument("--cafe-data-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--name", default="beauty_legacy_v1")
    args = parser.parse_args()

    pgpr = Path(args.pgpr_data_dir)
    cafe = Path(args.cafe_data_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    users = read_vocab(pgpr / "users.txt.gz")
    products = read_vocab(pgpr / "product.txt.gz")
    if len(users) != len(set(users)) or len(products) != len(set(products)):
        raise ValueError("PGPR user/product vocab contains duplicate raw ids")

    pgpr_pairs = {
        split: read_pgpr_pairs(pgpr / f"{split}.txt.gz")
        for split in ("train", "test")
    }
    pgpr_labels = {
        split: pairs_to_labels(pairs) for split, pairs in pgpr_pairs.items()
    }
    cafe_labels = {
        split: read_cafe_labels(cafe / f"{split}_labels.txt.gz")
        for split in ("train", "test")
    }
    source_agreement = {
        split: compare_label_sets(pgpr_labels[split], cafe_labels[split], split)
        for split in ("train", "test")
    }

    train_pairs = set(pgpr_pairs["train"])
    test_pairs = set(pgpr_pairs["test"])
    overlap = train_pairs & test_pairs
    if overlap:
        raise ValueError(f"Historical train/test overlap: {sorted(overlap)[:5]}")

    reviews, review_stats = load_raw_reviews(
        cafe / "reviews_Beauty_5.json.gz",
        {raw_id: idx for idx, raw_id in enumerate(users)},
        {raw_id: idx for idx, raw_id in enumerate(products)},
    )
    split_pairs = train_pairs | test_pairs
    if split_pairs != set(reviews):
        missing = sorted(split_pairs - set(reviews))[:5]
        unused = sorted(set(reviews) - split_pairs)[:5]
        raise ValueError(
            f"Raw reviews and historical split differ: missing={missing}, unused={unused}"
        )

    write_interactions(
        out / "interactions" / "train.tsv.gz", pgpr_pairs["train"], reviews
    )
    write_interactions(out / "interactions" / "valid.tsv.gz", [], reviews)
    write_interactions(
        out / "interactions" / "test.tsv.gz", pgpr_pairs["test"], reviews
    )
    write_pickle(out / "labels" / "train_label.pkl", pgpr_labels["train"])
    write_pickle(out / "labels" / "valid_label.pkl", {})
    write_pickle(out / "labels" / "test_label.pkl", pgpr_labels["test"])

    write_mapping(
        out / "mappings" / "user_mapping.tsv",
        ["canonical_uid", "raw_reviewer_id"],
        enumerate(users),
    )
    write_mapping(
        out / "mappings" / "product_mapping.tsv",
        ["canonical_pid", "raw_asin"],
        enumerate(products),
    )
    write_mapping(
        out / "model_views" / "cafe" / "mappings" / "user_remap.tsv",
        ["canonical_uid", "cafe_uid"],
        ((uid, uid) for uid in range(len(users))),
    )
    write_mapping(
        out / "model_views" / "cafe" / "mappings" / "product_remap.tsv",
        ["canonical_pid", "cafe_product_idx"],
        ((pid, pid) for pid in range(len(products))),
    )
    write_mapping(
        out / "model_views" / "pgpr" / "mappings" / "user_remap.tsv",
        ["canonical_uid", "pgpr_uid"],
        ((uid, uid) for uid in range(len(users))),
    )
    write_mapping(
        out / "model_views" / "pgpr" / "mappings" / "product_remap.tsv",
        ["canonical_pid", "pgpr_product_idx"],
        ((pid, pid) for pid in range(len(products))),
    )

    metadata = {
        "name": args.name,
        "domain": "amazon_beauty",
        "feedback_type": "explicit_rating",
        "interaction_format": "uid\tpid\trating\ttimestamp",
        "product_entity": "product",
        "interaction_relation": "purchase",
        "user_id_policy": "historical PGPR/CAFE compact user index",
        "product_id_policy": "historical PGPR/CAFE compact product index",
        "valid_policy": "empty_legacy_compatibility",
        "valid_policy_reason": (
            "Preserve the historical PGPR/CAFE training graph exactly. "
            "A non-empty validation split requires rebuilding CAFE review-text "
            "and purchase KG edges."
        ),
        "source_assets": {
            "pgpr_data_dir": str(pgpr),
            "cafe_data_dir": str(cafe),
            "raw_reviews": str(cafe / "reviews_Beauty_5.json.gz"),
            "cafe_kg_entities": str(cafe / "kg_entities.txt.gz"),
            "cafe_kg_relations": str(cafe / "kg_relations.txt.gz"),
            "cafe_kg_triples": str(cafe / "kg_triples.txt.gz"),
        },
        "source_agreement": source_agreement,
        "raw_review_validation": review_stats,
        "model_view_policy": (
            "PGPR and CAFE use identity remaps because their historical Beauty "
            "assets already share the canonical compact id space."
        ),
        "canonical_split_stats": {
            "train": {
                "interactions": len(pgpr_pairs["train"]),
                "users": len(pgpr_labels["train"]),
                "products": len({pid for _uid, pid in pgpr_pairs["train"]}),
            },
            "valid": {"interactions": 0, "users": 0, "products": 0},
            "test": {
                "interactions": len(pgpr_pairs["test"]),
                "users": len(pgpr_labels["test"]),
                "products": len({pid for _uid, pid in pgpr_pairs["test"]}),
            },
        },
        "train_test_overlap_pairs": 0,
        "users": len(users),
        "products": len(products),
    }
    with open(out / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    with open(out / "README.md", "w") as f:
        f.write(f"# {args.name}\n\n")
        f.write(
            "Canonical Amazon Beauty dataset preserving the historical PGPR/CAFE "
            "train/test protocol. The validation split is intentionally empty; "
            "see `metadata.json` for the graph-leakage rationale and provenance.\n"
        )

    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
