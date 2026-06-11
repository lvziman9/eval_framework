#!/usr/bin/env python3
"""Build a PGPR-compatible view from a canonical dataset without editing PGPR code.

PGPR expects interaction item ids to be raw product ids and maps them through
`product_mappings.txt` column 1 -> column 0. This view uses identity-style
mappings so canonical ids can pass through PGPR's original loader unchanged.
"""

import argparse
import csv
import gzip
import json
import pickle
import shutil
from collections import defaultdict
from pathlib import Path


LASTFM_RELATIONS = [
    "alternative_version_of_s_rs.txt.gz",
    "belong_to_s_ca.txt.gz",
    "featured_by_s_a.txt.gz",
    "mixed_by_s_e.txt.gz",
    "orginal_version_of_s_rs.txt.gz",
    "produced_by_producer_s_pr.txt.gz",
    "related_to_s_rs.txt.gz",
    "sang_by_s_a.txt.gz",
]


def iter_canonical_interactions(path):
    with gzip.open(path, "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if len(row) != 4:
                raise ValueError(f"Expected 4 columns in {path}, got {row}")
            yield int(row[0]), int(row[1]), int(row[2]), int(row[3])


def load_labels(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def write_split(canonical_root, split, out_path):
    rows = 0
    users = set()
    products = set()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        for uid, pid, _rating, ts in iter_canonical_interactions(canonical_root / "interactions" / f"{split}.tsv.gz"):
            # LastFM PGPR expects three space-separated columns: raw_uid raw_pid timestamp.
            # The identity mappings in this view map these canonical values back to themselves.
            f.write(f"{uid} {pid} {ts}\n")
            rows += 1
            users.add(uid)
            products.add(pid)
    return {"rows": rows, "users": len(users), "products": len(products)}


def write_plain_and_gzip_lines(path_no_gz, lines):
    path_no_gz.parent.mkdir(parents=True, exist_ok=True)
    with open(path_no_gz, "w") as f:
        for line in lines:
            f.write(f"{line}\n")
    with gzip.open(str(path_no_gz) + ".gz", "wt") as f:
        for line in lines:
            f.write(f"{line}\n")


def read_gzip_lines(path):
    with gzip.open(path, "rt") as f:
        return [line.rstrip("\n") for line in f]


def pad_entity_file_for_identity_ids(entity_dir, entity_name, max_id):
    """Ensure PGPR embedding tables are large enough for sparse canonical ids.

    PGPR builds entity embedding sizes from the number of lines in each entity
    file. The canonical LastFM user ids are xrecsys kg ids and are sparse, so an
    identity user mapping can otherwise produce uid values larger than the user
    embedding table.
    """
    path_no_gz = entity_dir / f"{entity_name}.txt"
    path_gz = entity_dir / f"{entity_name}.txt.gz"
    if path_gz.exists():
        lines = read_gzip_lines(path_gz)
    elif path_no_gz.exists():
        with open(path_no_gz, "r") as f:
            lines = [line.rstrip("\n") for line in f]
    else:
        raise FileNotFoundError(f"Missing entity file for {entity_name}: {path_gz}")

    original_count = len(lines)
    while len(lines) <= max_id:
        lines.append(f"__canonical_pad_{entity_name}_{len(lines)}")
    write_plain_and_gzip_lines(path_no_gz, lines)
    return {
        "entity": entity_name,
        "original_count": original_count,
        "padded_count": len(lines),
        "max_required_id": max_id,
        "padded": len(lines) != original_count,
    }


def copy_tree_files(src_dir, dst_dir, names=None):
    dst_dir.mkdir(parents=True, exist_ok=True)
    if names is None:
        paths = [p for p in src_dir.iterdir() if p.is_file()]
    else:
        paths = [src_dir / name for name in names]
    for src in paths:
        if src.exists():
            shutil.copy2(src, dst_dir / src.name)


def write_identity_mappings(canonical_root, out_mappings_dir, source_mappings_dir):
    train = load_labels(canonical_root / "labels" / "train_label.pkl")
    valid = load_labels(canonical_root / "labels" / "valid_label.pkl")
    test = load_labels(canonical_root / "labels" / "test_label.pkl")
    users = sorted(set(train) | set(valid) | set(test))
    products = sorted({pid for labels in [train, valid, test] for items in labels.values() for pid in items})

    out_mappings_dir.mkdir(parents=True, exist_ok=True)
    with open(out_mappings_dir / "user_mappings.txt", "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["kgid", "canonical_uid"])
        for uid in users:
            writer.writerow([uid, uid])

    # Preserve optional metadata columns where possible, but force col0 == col1 == canonical pid.
    source_product = source_mappings_dir / "product_mappings.txt"
    metadata_by_kgid = {}
    if source_product.exists():
        with open(source_product, "r", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader, None)
            for row in reader:
                if row:
                    metadata_by_kgid[int(row[0])] = row
    with open(out_mappings_dir / "product_mappings.txt", "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["kgid", "canonical_pid", "source_col2", "name", "source_col4"])
        for pid in products:
            old = metadata_by_kgid.get(pid)
            if old and len(old) >= 5:
                writer.writerow([pid, pid, old[2], old[3], old[4]])
            else:
                writer.writerow([pid, pid, "", "", ""])
    return {
        "users": len(users),
        "products": len(products),
        "max_user_id": max(users),
        "max_product_id": max(products),
    }


def validate_identity_labels(canonical_root, view_root):
    user_map = {}
    with open(view_root / "mappings" / "user_mappings.txt", "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            user_map[int(row[1])] = int(row[0])
    product_map = {}
    with open(view_root / "mappings" / "product_mappings.txt", "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            product_map[int(row[1])] = int(row[0])

    report = {}
    for split in ["train", "test"]:
        rebuilt = defaultdict(list)
        with gzip.open(view_root / f"{split}.txt.gz", "rt") as f:
            for line in f:
                uid_raw, pid_raw, _ts = map(int, line.strip().split(" "))
                rebuilt[user_map[uid_raw]].append(product_map[pid_raw])
        canonical = load_labels(canonical_root / "labels" / f"{split}_label.pkl")
        report[split] = {
            "rebuilt_users": len(rebuilt),
            "canonical_users": len(canonical),
            "exact_match": dict(rebuilt) == canonical,
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument("--source-xrecsys-dataset-dir", required=True)
    parser.add_argument("--out-dir", required=True, help="Output PGPR view dir; basename should be lastfm for unmodified PGPR loaders")
    parser.add_argument("--dataset", default="lastfm_v1")
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    source = Path(args.source_xrecsys_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    split_stats = {
        "train": write_split(canonical_root, "train", out / "train.txt.gz"),
        "valid": write_split(canonical_root, "valid", out / "valid.txt.gz"),
        "test": write_split(canonical_root, "test", out / "test.txt.gz"),
    }

    copy_tree_files(source / "entities", out / "entities")
    copy_tree_files(source / "relations", out / "relations", names=LASTFM_RELATIONS)
    copy_tree_files(source / "kg-completion", out / "kg-completion")
    copy_tree_files(source / "mappings", out / "mappings")
    mapping_stats = write_identity_mappings(canonical_root, out / "mappings", source / "mappings")
    entity_padding = {
        "user": pad_entity_file_for_identity_ids(out / "entities", "user", mapping_stats["max_user_id"]),
    }

    validation = validate_identity_labels(canonical_root, out)
    metadata = {
        "dataset": args.dataset,
        "canonical_root": str(canonical_root),
        "source_xrecsys_dataset_dir": str(source),
        "out_dir": str(out),
        "id_policy": {
            "users": "identity mapping: canonical_uid as PGPR raw uid and kg uid",
            "products": "identity mapping: canonical_pid as PGPR raw pid and kg pid",
            "output_must_map_back_to": "canonical uid/pid",
        },
        "split_stats": split_stats,
        "mapping_stats": mapping_stats,
        "entity_padding": entity_padding,
        "identity_label_validation": validation,
    }
    with open(out.parent / "pgpr_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
