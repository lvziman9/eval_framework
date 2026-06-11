#!/usr/bin/env python3
"""Build a UCPR model view from a canonical dataset.

The view uses compact user/product ids required by UCPR, while preserving
remap tables back to canonical ids.
"""

import argparse
import csv
import gzip
import json
from pathlib import Path


ENTITY_MAP_LASTFM = {
    "artist": "artist",
    "engineer": "engineer",
    "producer": "producer",
    "category": "genre",
}

RELATION_MAP_LASTFM = {
    "featured_by_s_a.txt": "featured_by_artist.txt.gz",
    "mixed_by_s_e.txt": "mixed_by_engineer.txt.gz",
    "produced_by_producer_s_pr.txt": "produced_by_producer.txt.gz",
    "belong_to_s_ca.txt": "belong_to_genre.txt.gz",
}


def read_entity_ids(path):
    ids = []
    with open(path, "r") as f:
        for line in f:
            value = line.strip()
            if value:
                ids.append(int(value))
    return ids


def read_canonical_users(canonical_root):
    users = set()
    for split in ["train", "valid", "test"]:
        with gzip.open(canonical_root / "interactions" / f"{split}.tsv.gz", "rt") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row:
                    users.add(int(row[0]))
    return sorted(users)


def write_entity_file(ids, out_path, compact=True):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        f.write("id\n")
        if compact:
            for idx in range(len(ids)):
                f.write(f"{idx}\n")
        else:
            for value in ids:
                f.write(f"{value}\n")


def copy_entity_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "r") as fin, gzip.open(dst, "wt") as fout:
        fout.write("id\n")
        for line in fin:
            value = line.strip()
            if value:
                fout.write(f"{value}\n")


def copy_relation_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "r") as fin, gzip.open(dst, "wt") as fout:
        for line in fin:
            parts = line.strip().split()
            fout.write("\t".join(parts) + "\n" if parts else "\n")


def iter_canonical_interactions(path):
    with gzip.open(path, "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if len(row) != 4:
                raise ValueError(f"Expected 4 columns in {path}, got {row}")
            yield int(row[0]), int(row[1]), int(row[2]), int(row[3])


def write_ucpr_interactions(canonical_path, out_path, user_remap, product_remap):
    count = 0
    skipped_user = 0
    skipped_product = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as fout:
        for uid, pid, rating, ts in iter_canonical_interactions(canonical_path):
            if uid not in user_remap:
                skipped_user += 1
                continue
            if pid not in product_remap:
                skipped_product += 1
                continue
            fout.write(f"{user_remap[uid]}\t{product_remap[pid]}\t{rating}\t{ts}\n")
            count += 1
    return {"rows": count, "skipped_user": skipped_user, "skipped_product": skipped_product}


def write_remap(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument("--source-xrecsys-dataset-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset", default="lastfm_v1")
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    source = Path(args.source_xrecsys_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    canonical_users = read_canonical_users(canonical_root)
    product_ids = read_entity_ids(source / "entities" / "song.txt")

    user_remap = {uid: idx for idx, uid in enumerate(canonical_users)}
    product_remap = {pid: idx for idx, pid in enumerate(product_ids)}

    write_entity_file(canonical_users, out / "user.txt.gz", compact=True)
    write_entity_file(product_ids, out / "product.txt.gz", compact=True)
    for src_name, dst_name in ENTITY_MAP_LASTFM.items():
        copy_entity_file(source / "entities" / f"{src_name}.txt", out / f"{dst_name}.txt.gz")

    for src_name, dst_name in RELATION_MAP_LASTFM.items():
        copy_relation_file(source / "relations" / src_name, out / dst_name)

    split_stats = {}
    for split in ["train", "valid", "test"]:
        split_stats[split] = write_ucpr_interactions(
            canonical_root / "interactions" / f"{split}.tsv.gz",
            out / f"{split}.txt.gz",
            user_remap,
            product_remap,
        )

    write_remap(out.parent / "user_remap.tsv", ["canonical_uid", "ucpr_uid"], sorted(user_remap.items(), key=lambda x: x[1]))
    write_remap(out.parent / "product_remap.tsv", ["canonical_pid", "ucpr_product_idx"], sorted(product_remap.items(), key=lambda x: x[1]))

    metadata = {
        "dataset": args.dataset,
        "canonical_root": str(canonical_root),
        "source_xrecsys_dataset_dir": str(source),
        "out_dir": str(out),
        "user_count": len(user_remap),
        "product_count": len(product_remap),
        "split_stats": split_stats,
        "id_policy": {
            "users": "compact remap from canonical uid",
            "products": "compact remap from canonical pid using source song entity order",
            "output_must_map_back_to": "canonical uid/pid",
        },
    }
    with open(out.parent / "ucpr_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
