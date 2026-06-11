#!/usr/bin/env python3
"""Build a canonical dataset view from an xrecsys-style dataset.

The canonical layer is model-agnostic: it fixes one user/product id space,
one train/valid/test split, and one evaluation label source. Model-specific
converters may remap ids internally, but their outputs should map back here.
"""

import argparse
import csv
import gzip
import json
import pickle
import shutil
from collections import defaultdict
from pathlib import Path


DEFAULT_RATING = 1


def read_mapping(path, key_col, value_col):
    mapping = {}
    with open(path, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            mapping[int(row[key_col])] = int(row[value_col])
    return mapping, header


def read_valid_products(product_mapping_path, product_id_policy):
    # xrecsys product_mappings columns for lastfm/ml1m are conceptually:
    # canonical kgid in column 0 and raw dataset product id in column 1.
    valid = set()
    raw_to_kg = {}
    with open(product_mapping_path, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            kgid = int(row[0])
            rawid = int(row[1])
            valid.add(kgid)
            raw_to_kg[rawid] = kgid
    if product_id_policy not in {"xrecsys_kgid", "raw_to_xrecsys_kgid"}:
        raise ValueError(f"Unsupported product_id_policy: {product_id_policy}")
    return valid, raw_to_kg, header


def iter_interactions(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as f:
        reader = csv.reader(f, delimiter=" ")
        for row in reader:
            if not row:
                continue
            if len(row) < 3:
                raise ValueError(f"Expected at least 3 columns in {path}, got: {row}")
            yield int(row[0]), int(row[1]), int(row[2])


def canonicalize_split(split_path, user_raw_to_kg, valid_products, raw_product_to_kg, product_id_policy):
    rows = []
    stats = {
        "input_interactions": 0,
        "kept_interactions": 0,
        "skipped_user_interactions": 0,
        "skipped_product_interactions": 0,
    }
    for raw_uid, raw_pid, ts in iter_interactions(split_path):
        stats["input_interactions"] += 1
        uid = user_raw_to_kg.get(raw_uid)
        if uid is None:
            stats["skipped_user_interactions"] += 1
            continue
        if product_id_policy == "xrecsys_kgid":
            pid = raw_pid
            valid = pid in valid_products
        else:
            pid = raw_product_to_kg.get(raw_pid)
            valid = pid is not None
        if not valid:
            stats["skipped_product_interactions"] += 1
            continue
        rows.append((uid, pid, DEFAULT_RATING, ts))
        stats["kept_interactions"] += 1
    stats["users"] = len({r[0] for r in rows})
    stats["products"] = len({r[1] for r in rows})
    return rows, stats


def split_valid_from_train(train_rows, policy):
    if policy == "none":
        return train_rows, []
    if policy != "per_user_latest_one_from_train":
        raise ValueError(f"Unsupported valid policy: {policy}")

    by_user = defaultdict(list)
    for row in train_rows:
        by_user[row[0]].append(row)

    new_train = []
    valid = []
    for uid, rows in by_user.items():
        rows = sorted(rows, key=lambda x: x[3])
        if len(rows) >= 2:
            valid.append(rows[-1])
            new_train.extend(rows[:-1])
        else:
            new_train.extend(rows)
    return new_train, valid


def write_interactions(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for row in rows:
            writer.writerow(row)


def labels_from_rows(rows):
    labels = defaultdict(list)
    for uid, pid, _rating, _ts in rows:
        labels[uid].append(pid)
    return dict(labels)


def write_pickle(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def copy_if_exists(src, dst):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def summarize_rows(rows):
    return {
        "interactions": len(rows),
        "users": len({r[0] for r in rows}),
        "products": len({r[1] for r in rows}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Canonical dataset name, e.g. lastfm_v1")
    parser.add_argument("--source-dataset-dir", required=True, help="xrecsys source dataset dir")
    parser.add_argument("--out-dir", required=True, help="Canonical dataset output dir")
    parser.add_argument("--product-id-policy", default="xrecsys_kgid", choices=["xrecsys_kgid", "raw_to_xrecsys_kgid"])
    parser.add_argument("--valid-policy", default="per_user_latest_one_from_train", choices=["per_user_latest_one_from_train", "none"])
    parser.add_argument("--product-entity", default="product")
    parser.add_argument("--domain", default="unknown")
    args = parser.parse_args()

    source = Path(args.source_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    user_map, user_header = read_mapping(source / "mappings" / "user_mappings.txt", key_col=1, value_col=0)
    valid_products, raw_product_to_kg, product_header = read_valid_products(
        source / "mappings" / "product_mappings.txt", args.product_id_policy
    )

    raw_train, raw_train_stats = canonicalize_split(
        source / "train.txt.gz", user_map, valid_products, raw_product_to_kg, args.product_id_policy
    )
    test_rows, test_stats = canonicalize_split(
        source / "test.txt.gz", user_map, valid_products, raw_product_to_kg, args.product_id_policy
    )
    train_rows, valid_rows = split_valid_from_train(raw_train, args.valid_policy)

    write_interactions(out / "interactions" / "train.tsv.gz", train_rows)
    write_interactions(out / "interactions" / "valid.tsv.gz", valid_rows)
    write_interactions(out / "interactions" / "test.tsv.gz", test_rows)

    write_pickle(out / "labels" / "train_label.pkl", labels_from_rows(train_rows))
    write_pickle(out / "labels" / "valid_label.pkl", labels_from_rows(valid_rows))
    write_pickle(out / "labels" / "test_label.pkl", labels_from_rows(test_rows))

    copy_if_exists(source / "mappings" / "user_mappings.txt", out / "mappings" / "user_mapping.tsv")
    copy_if_exists(source / "mappings" / "product_mappings.txt", out / "mappings" / "product_mapping.tsv")

    metadata = {
        "name": args.name,
        "domain": args.domain,
        "source_dataset_dir": str(source),
        "interaction_format": "uid\tpid\trating\ttimestamp",
        "feedback_type": "implicit",
        "default_rating": DEFAULT_RATING,
        "user_id_policy": "raw_user_id_to_xrecsys_kgid_via_user_mappings_col1_to_col0",
        "product_id_policy": args.product_id_policy,
        "product_entity": args.product_entity,
        "valid_policy": args.valid_policy,
        "source_mapping_headers": {
            "user_mappings": user_header,
            "product_mappings": product_header,
        },
        "source_assets": {
            "entities_dir": str(source / "entities"),
            "relations_dir": str(source / "relations"),
            "kg_completion_dir": str(source / "kg-completion"),
        },
        "raw_train_stats_before_valid_split": raw_train_stats,
        "test_stats": test_stats,
        "canonical_split_stats": {
            "train": summarize_rows(train_rows),
            "valid": summarize_rows(valid_rows),
            "test": summarize_rows(test_rows),
        },
    }
    with open(out / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    with open(out / "README.md", "w") as f:
        f.write(f"# {args.name}\n\n")
        f.write("Canonical dataset generated by `scripts/data/canonical/build_canonical_dataset.py`.\n\n")
        f.write("See `metadata.json` for id policies, split policy, and source assets.\n")

    print(json.dumps(metadata["canonical_split_stats"], indent=2, sort_keys=True))
    print(f"Wrote canonical dataset to {out}")


if __name__ == "__main__":
    main()
