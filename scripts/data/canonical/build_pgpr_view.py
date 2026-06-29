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
import zipfile
from collections import defaultdict
from pathlib import Path


AMAZON_BOOK_KGAT = "amazon_book_kgat_v1"

# Default semantic item->entity relations for an Amazon-book PGPR data view.
# Technical Freebase type/name relations are intentionally excluded from the
# default native-path candidate schema.
AMAZON_BOOK_RELATION_IDS = [10, 13, 11, 5, 20, 15, 18, 19, 36]
AMAZON_BOOK_RELATION_NAMES = {
    5: "book_subject",
    10: "book_author",
    11: "book_original_language",
    13: "book_genre",
    15: "book_previous_in_series",
    18: "book_part_of_series",
    19: "book_character",
    20: "book_next_in_series",
    36: "book_interior_illustration",
}


RELATION_FILES = {
    "lastfm": [
        "alternative_version_of_s_rs.txt.gz",
        "belong_to_s_ca.txt.gz",
        "featured_by_s_a.txt.gz",
        "mixed_by_s_e.txt.gz",
        "orginal_version_of_s_rs.txt.gz",
        "produced_by_producer_s_pr.txt.gz",
        "related_to_s_rs.txt.gz",
        "sang_by_s_a.txt.gz",
    ],
    "ml1m": [
        "belong_to_m_ca.txt.gz",
        "cinematography_m_ci.txt.gz",
        "composed_by_m_c.txt.gz",
        "directed_by_m_d.txt.gz",
        "edited_by_m_ed.txt.gz",
        "produced_by_company_m_pc.txt.gz",
        "produced_by_producer_m_pr.txt.gz",
        "starring_m_a.txt.gz",
        "wrote_by_m_w.txt.gz",
    ],
    "amazon_book_kgat_v1": [
        "book_author_b_e.txt.gz",
        "book_genre_b_e.txt.gz",
        "book_original_language_b_e.txt.gz",
        "book_subject_b_e.txt.gz",
        "book_next_in_series_b_e.txt.gz",
        "book_previous_in_series_b_e.txt.gz",
        "book_part_of_series_b_e.txt.gz",
        "book_character_b_e.txt.gz",
        "book_interior_illustration_b_e.txt.gz",
    ],
}

PRODUCT_ENTITIES = {
    "lastfm": "song",
    "ml1m": "movie",
    "amazon_book_kgat_v1": "book",
}


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


def write_split(canonical_root, split, out_path, model_dataset):
    rows = 0
    users = set()
    products = set()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        for uid, pid, rating, ts in iter_canonical_interactions(canonical_root / "interactions" / f"{split}.tsv.gz"):
            if model_dataset == "ml1m":
                f.write(f"{uid} {pid} {rating} {ts}\n")
            else:
                f.write(f"{uid} {pid} {ts}\n")
            rows += 1
            users.add(uid)
            products.add(pid)
    return {"rows": rows, "users": len(users), "products": len(products)}


def write_plain_and_gzip_lines(path_no_gz, lines):
    lines = list(lines)
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
    if not src_dir.exists():
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    if names is None:
        paths = [p for p in src_dir.iterdir() if p.is_file()]
    else:
        paths = [src_dir / name for name in names]
    for src in paths:
        if src.exists():
            shutil.copy2(src, dst_dir / src.name)


def read_kgat_right_id_mapping(path):
    values = {}
    with open(path, errors="strict") as f:
        _header = f.readline()
        for line_number, line in enumerate(f, start=2):
            text = line.rstrip("\n")
            original_id, separator, remap_text = text.rpartition(" ")
            if not separator:
                raise ValueError(f"Malformed KGAT mapping row {path}:{line_number}: {text!r}")
            remap_id = int(remap_text)
            values[remap_id] = original_id
    if sorted(values) != list(range(len(values))):
        raise ValueError(f"Non-contiguous KGAT ids in {path}")
    return values


def read_kgat_item_mapping(path):
    values = {}
    with open(path) as f:
        _header = f.readline()
        for line_number, line in enumerate(f, start=2):
            columns = line.strip().split()
            if len(columns) != 3:
                raise ValueError(f"Malformed KGAT item row {path}:{line_number}: {line!r}")
            original_id, remap_text, freebase_id = columns
            values[int(remap_text)] = (original_id, freebase_id)
    if sorted(values) != list(range(len(values))):
        raise ValueError(f"Non-contiguous KGAT item ids in {path}")
    return values


def read_kgat_relation_mapping(path):
    values = {}
    with open(path, errors="strict") as f:
        _header = f.readline()
        for line_number, line in enumerate(f, start=2):
            text = line.rstrip("\n")
            relation, separator, remap_text = text.rpartition(" ")
            if not separator:
                raise ValueError(f"Malformed KGAT relation row {path}:{line_number}: {text!r}")
            values[int(remap_text)] = relation
    return values


def write_amazon_entity_files(source_dir, entity_dir):
    users = read_kgat_right_id_mapping(source_dir / "user_list.txt")
    items = read_kgat_item_mapping(source_dir / "item_list.txt")
    entities = read_kgat_right_id_mapping(source_dir / "entity_list.txt")

    write_plain_and_gzip_lines(
        entity_dir / "user.txt",
        (users[idx] for idx in range(len(users))),
    )
    write_plain_and_gzip_lines(
        entity_dir / "book.txt",
        (items[idx][1] for idx in range(len(items))),
    )
    write_plain_and_gzip_lines(
        entity_dir / "entity.txt",
        (entities[idx] for idx in range(len(entities))),
    )
    return {
        "users": len(users),
        "products": len(items),
        "entities": len(entities),
        "max_user_id": len(users) - 1,
        "max_product_id": len(items) - 1,
        "max_entity_id": len(entities) - 1,
    }


def write_amazon_identity_mappings(out_mappings_dir, source_dir):
    users = read_kgat_right_id_mapping(source_dir / "user_list.txt")
    items = read_kgat_item_mapping(source_dir / "item_list.txt")

    out_mappings_dir.mkdir(parents=True, exist_ok=True)
    with open(out_mappings_dir / "user_mappings.txt", "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["kgid", "canonical_uid", "source_original_uid"])
        for uid in range(len(users)):
            writer.writerow([uid, uid, users[uid]])

    with open(out_mappings_dir / "product_mappings.txt", "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["kgid", "canonical_pid", "source_original_item_id", "freebase_id"])
        for pid in range(len(items)):
            source_item_id, freebase_id = items[pid]
            writer.writerow([pid, pid, source_item_id, freebase_id])
    return {
        "users": len(users),
        "products": len(items),
        "max_user_id": len(users) - 1,
        "max_product_id": len(items) - 1,
    }


def write_amazon_relation_files(source_dir, out_relations_dir, selected_relation_ids):
    items = read_kgat_item_mapping(source_dir / "item_list.txt")
    relation_names = read_kgat_relation_mapping(source_dir / "relation_list.txt")
    product_count = len(items)
    selected_relation_ids = list(selected_relation_ids)
    missing_names = [
        relation_id
        for relation_id in selected_relation_ids
        if relation_id not in AMAZON_BOOK_RELATION_NAMES
    ]
    if missing_names:
        raise ValueError(
            "Missing stable PGPR relation filenames for Amazon relation ids: "
            f"{missing_names}"
        )

    buckets = {
        relation_id: [set() for _ in range(product_count)]
        for relation_id in selected_relation_ids
    }
    with zipfile.ZipFile(source_dir / "kg_final.txt.zip") as archive:
        members = archive.namelist()
        if members != ["kg_final.txt"]:
            raise ValueError(f"Unexpected KGAT KG zip members: {members}")
        with archive.open("kg_final.txt") as f:
            for line_number, raw in enumerate(f, start=1):
                columns = raw.split()
                if len(columns) != 3:
                    raise ValueError(f"Malformed KGAT triple at line {line_number}")
                head, relation, tail = map(int, columns)
                if relation in buckets and 0 <= head < product_count:
                    buckets[relation][head].add(tail)

    out_relations_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    for relation_id in selected_relation_ids:
        relation_name = AMAZON_BOOK_RELATION_NAMES[relation_id]
        filename = f"{relation_name}_b_e.txt"
        lines = [
            " ".join(str(value) for value in sorted(tails))
            for tails in buckets[relation_id]
        ]
        write_plain_and_gzip_lines(out_relations_dir / filename, lines)
        covered_products = sum(bool(tails) for tails in buckets[relation_id])
        edge_count = sum(len(tails) for tails in buckets[relation_id])
        tail_entities = len({tail for tails in buckets[relation_id] for tail in tails})
        stats[relation_name] = {
            "relation_id": relation_id,
            "freebase_relation": relation_names[relation_id],
            "file": f"relations/{filename}.gz",
            "covered_products": covered_products,
            "edges": edge_count,
            "tail_entities": tail_entities,
        }
    return stats


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
    for split in ["train", "valid", "test"]:
        rebuilt = defaultdict(list)
        with gzip.open(view_root / f"{split}.txt.gz", "rt") as f:
            for line in f:
                parts = line.strip().split(" ")
                uid_raw, pid_raw = int(parts[0]), int(parts[1])
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
    parser.add_argument("--model-dataset", choices=sorted(RELATION_FILES), default="lastfm")
    parser.add_argument(
        "--amazon-relation-id",
        type=int,
        nargs="*",
        default=AMAZON_BOOK_RELATION_IDS,
        help=(
            "Amazon KGAT relation ids to expose in the generic PGPR book/entity "
            "view. Defaults to semantic book relations only."
        ),
    )
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    source = Path(args.source_xrecsys_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    split_stats = {
        "train": write_split(canonical_root, "train", out / "train.txt.gz", args.model_dataset),
        "valid": write_split(canonical_root, "valid", out / "valid.txt.gz", args.model_dataset),
        "test": write_split(canonical_root, "test", out / "test.txt.gz", args.model_dataset),
    }

    if args.model_dataset == AMAZON_BOOK_KGAT:
        entity_stats = write_amazon_entity_files(source, out / "entities")
        mapping_stats = write_amazon_identity_mappings(out / "mappings", source)
        relation_stats = write_amazon_relation_files(
            source,
            out / "relations",
            args.amazon_relation_id,
        )
        copy_tree_files(source, out / "kg-completion", names=["kg_final.txt.zip"])
        entity_padding = {
            "user": {
                "entity": "user",
                "original_count": entity_stats["users"],
                "padded_count": entity_stats["users"],
                "max_required_id": mapping_stats["max_user_id"],
                "padded": False,
            },
            "book": {
                "entity": "book",
                "original_count": entity_stats["products"],
                "padded_count": entity_stats["products"],
                "max_required_id": mapping_stats["max_product_id"],
                "padded": False,
            },
            "entity": {
                "entity": "entity",
                "original_count": entity_stats["entities"],
                "padded_count": entity_stats["entities"],
                "max_required_id": entity_stats["max_entity_id"],
                "padded": False,
            },
        }
    else:
        copy_tree_files(source / "entities", out / "entities")
        copy_tree_files(source / "relations", out / "relations", names=RELATION_FILES[args.model_dataset])
        copy_tree_files(source / "kg-completion", out / "kg-completion")
        copy_tree_files(source / "mappings", out / "mappings")
        mapping_stats = write_identity_mappings(canonical_root, out / "mappings", source / "mappings")
        relation_stats = {
            "copied_relation_files": RELATION_FILES[args.model_dataset],
        }
        entity_padding = {
            "user": pad_entity_file_for_identity_ids(out / "entities", "user", mapping_stats["max_user_id"]),
            PRODUCT_ENTITIES[args.model_dataset]: pad_entity_file_for_identity_ids(
                out / "entities",
                PRODUCT_ENTITIES[args.model_dataset],
                mapping_stats["max_product_id"],
            ),
        }

    validation = validate_identity_labels(canonical_root, out)
    metadata = {
        "dataset": args.dataset,
        "model_dataset": args.model_dataset,
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
        "relation_projection": relation_stats,
        "identity_label_validation": validation,
        "runtime_note": (
            "For amazon_book_kgat_v1 this is a data-view smoke artifact only; "
            "PGPR runtime constants/path patterns still need an Amazon patch "
            "before training or formal reporting."
        ) if args.model_dataset == AMAZON_BOOK_KGAT else "",
    }
    with open(out.parent / "pgpr_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
