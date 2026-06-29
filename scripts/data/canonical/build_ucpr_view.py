#!/usr/bin/env python3
"""Build a UCPR model view from a canonical dataset.

The view uses compact user/product ids required by UCPR, while preserving
remap tables back to canonical ids.
"""

import argparse
import csv
import gzip
import json
import zipfile
from collections import defaultdict
from pathlib import Path


AMAZON_BOOK_KGAT = "amazon_book_kgat_v1"
AMAZON_BOOK_RELATION_IDS = [10, 13, 11, 5, 20, 15, 18, 19, 36]
AMAZON_BOOK_RELATION_NAMES = {
    5: "book_subject_entity",
    10: "book_author_entity",
    11: "book_original_language_entity",
    13: "book_genre_entity",
    15: "book_previous_in_series_entity",
    18: "book_part_of_series_entity",
    19: "book_character_entity",
    20: "book_next_in_series_entity",
    36: "book_interior_illustration_entity",
}


DATASET_CONFIG = {
    "lastfm": {
        "product_entity": "song",
        "entities": {
            "artist": "artist",
            "engineer": "engineer",
            "producer": "producer",
            "category": "genre",
        },
        "empty_entities": [],
        "relations": {
            "featured_by_s_a.txt": "featured_by_artist.txt.gz",
            "mixed_by_s_e.txt": "mixed_by_engineer.txt.gz",
            "produced_by_producer_s_pr.txt": "produced_by_producer.txt.gz",
            "belong_to_s_ca.txt": "belong_to_genre.txt.gz",
        },
        "empty_relations": [],
    },
    "ml1m": {
        "product_entity": "movie",
        "entities": {
            "actor": "actor",
            "director": "director",
            "production_company": "prodcompany",
            "editor": "editor",
            "writter": "writter",
            "cinematographer": "cinematographer",
            "composer": "composer",
            "category": "category",
            "producer": "producer",
        },
        "empty_entities": ["country", "wikipage"],
        "relations": {
            "cinematography_m_ci.txt": "cinematography_by_cinematographer.txt.gz",
            "produced_by_company_m_pc.txt": "produced_by_prodcompany.txt.gz",
            "composed_by_m_c.txt": "composed_by_composer.txt.gz",
            "belong_to_m_ca.txt": "belong_to_category.txt.gz",
            "starring_m_a.txt": "starred_by_actor.txt.gz",
            "edited_by_m_ed.txt": "edited_by_editor.txt.gz",
            "produced_by_producer_m_pr.txt": "produced_by_producer.txt.gz",
            "wrote_by_m_w.txt": "wrote_by_writter.txt.gz",
            "directed_by_m_d.txt": "directed_by_director.txt.gz",
        },
        "empty_relations": [
            "produced_in_country.txt.gz",
            "related_to_wikipage.txt.gz",
        ],
    },
    AMAZON_BOOK_KGAT: {
        "product_entity": "product",
        "source_format": "kgat_zip",
        "entities": {
            "entity": "entity",
        },
        "empty_entities": [],
        "relations": {},
        "empty_relations": [],
        "amazon_relation_ids": AMAZON_BOOK_RELATION_IDS,
    },
}


def read_entity_ids(path):
    ids = []
    with open(path, "r") as f:
        for line in f:
            value = line.strip()
            if value:
                ids.append(int(value))
    return ids


def read_kgat_right_id_mapping(path):
    values = {}
    with open(path, errors="strict") as f:
        _header = f.readline()
        for line_number, line in enumerate(f, start=2):
            text = line.rstrip("\n")
            original_id, separator, remap_text = text.rpartition(" ")
            if not separator:
                raise ValueError(f"Malformed KGAT mapping row {path}:{line_number}: {text!r}")
            values[int(remap_text)] = original_id
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


def write_label_entity_file(values, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        f.write("id\n")
        for value in values:
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


def write_empty_entity_file(out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        f.write("id\n")


def write_empty_relation_file(out_path, product_count):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        for _ in range(product_count + 1):
            f.write("\n")


def write_amazon_relation_file(out_path, tails_by_product, product_count):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        for pid in range(product_count):
            f.write("\t".join(str(tail) for tail in sorted(tails_by_product[pid])) + "\n")


def write_amazon_ucpr_entities(source, out):
    items = read_kgat_item_mapping(source / "item_list.txt")
    entities = read_kgat_right_id_mapping(source / "entity_list.txt")
    write_label_entity_file(
        (items[idx][1] for idx in range(len(items))),
        out / "product.txt.gz",
    )
    write_label_entity_file(
        (entities[idx] for idx in range(len(entities))),
        out / "entity.txt.gz",
    )
    return {
        "products": len(items),
        "entities": len(entities),
    }


def write_amazon_ucpr_relations(source, out, selected_relation_ids):
    items = read_kgat_item_mapping(source / "item_list.txt")
    relation_names = read_kgat_relation_mapping(source / "relation_list.txt")
    product_count = len(items)
    selected_relation_ids = list(selected_relation_ids)
    missing_names = [
        relation_id
        for relation_id in selected_relation_ids
        if relation_id not in AMAZON_BOOK_RELATION_NAMES
    ]
    if missing_names:
        raise ValueError(
            "Missing stable UCPR relation filenames for Amazon relation ids: "
            f"{missing_names}"
        )
    buckets = {
        relation_id: [set() for _ in range(product_count)]
        for relation_id in selected_relation_ids
    }
    with zipfile.ZipFile(source / "kg_final.txt.zip") as archive:
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

    stats = {}
    for relation_id in selected_relation_ids:
        relation_name = AMAZON_BOOK_RELATION_NAMES[relation_id]
        filename = f"{relation_name}.txt.gz"
        write_amazon_relation_file(out / filename, buckets[relation_id], product_count)
        covered_products = sum(bool(tails) for tails in buckets[relation_id])
        edge_count = sum(len(tails) for tails in buckets[relation_id])
        tail_entities = len({tail for tails in buckets[relation_id] for tail in tails})
        stats[relation_name] = {
            "relation_id": relation_id,
            "freebase_relation": relation_names[relation_id],
            "file": filename,
            "covered_products": covered_products,
            "edges": edge_count,
            "tail_entities": tail_entities,
        }
    return stats


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


def load_labels(path):
    import pickle

    with open(path, "rb") as f:
        return {int(uid): [int(pid) for pid in pids] for uid, pids in pickle.load(f).items()}


def validate_remapped_labels(canonical_root, out, user_remap, product_remap):
    inverse_user = {model_uid: canonical_uid for canonical_uid, model_uid in user_remap.items()}
    inverse_product = {
        model_pid: canonical_pid for canonical_pid, model_pid in product_remap.items()
    }
    report = {}
    for split in ["train", "valid", "test"]:
        rebuilt = defaultdict(list)
        with gzip.open(out / f"{split}.txt.gz", "rt") as f:
            for row in csv.reader(f, delimiter="\t"):
                if not row:
                    continue
                uid, pid = int(row[0]), int(row[1])
                rebuilt[inverse_user[uid]].append(inverse_product[pid])
        canonical = load_labels(canonical_root / "labels" / f"{split}_label.pkl")
        mismatched = [
            uid
            for uid in sorted(set(canonical) | set(rebuilt))
            if canonical.get(uid) != rebuilt.get(uid)
        ]
        report[split] = {
            "canonical_users": len(canonical),
            "rebuilt_users": len(rebuilt),
            "canonical_interactions": sum(len(items) for items in canonical.values()),
            "rebuilt_interactions": sum(len(items) for items in rebuilt.values()),
            "exact_match": not mismatched,
            "mismatched_user_examples": mismatched[:10],
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument("--source-xrecsys-dataset-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset", default="lastfm_v1")
    parser.add_argument("--model-dataset", choices=sorted(DATASET_CONFIG), default="lastfm")
    parser.add_argument(
        "--amazon-relation-id",
        type=int,
        nargs="*",
        default=AMAZON_BOOK_RELATION_IDS,
        help=(
            "Amazon KGAT relation ids to expose in the generic UCPR "
            "product/entity view. Defaults to semantic book relations only."
        ),
    )
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    source = Path(args.source_xrecsys_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = DATASET_CONFIG[args.model_dataset]

    canonical_users = read_canonical_users(canonical_root)
    if config.get("source_format") == "kgat_zip":
        product_ids = sorted(read_kgat_item_mapping(source / "item_list.txt"))
    else:
        product_ids = read_entity_ids(source / "entities" / f"{config['product_entity']}.txt")

    user_remap = {uid: idx for idx, uid in enumerate(canonical_users)}
    product_remap = {pid: idx for idx, pid in enumerate(product_ids)}

    write_entity_file(canonical_users, out / "user.txt.gz", compact=True)
    if config.get("source_format") == "kgat_zip":
        entity_stats = write_amazon_ucpr_entities(source, out)
        relation_stats = write_amazon_ucpr_relations(
            source,
            out,
            args.amazon_relation_id,
        )
    else:
        write_entity_file(product_ids, out / "product.txt.gz", compact=True)
        entity_stats = {"products": len(product_ids)}
        for src_name, dst_name in config["entities"].items():
            copy_entity_file(source / "entities" / f"{src_name}.txt", out / f"{dst_name}.txt.gz")
        for entity_name in config["empty_entities"]:
            write_empty_entity_file(out / f"{entity_name}.txt.gz")

        for src_name, dst_name in config["relations"].items():
            copy_relation_file(source / "relations" / src_name, out / dst_name)
        for relation_name in config["empty_relations"]:
            write_empty_relation_file(out / relation_name, len(product_ids))
        relation_stats = {
            "copied_relations": config["relations"],
            "empty_relations": config["empty_relations"],
        }

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
    label_validation = validate_remapped_labels(canonical_root, out, user_remap, product_remap)

    metadata = {
        "dataset": args.dataset,
        "model_dataset": args.model_dataset,
        "canonical_root": str(canonical_root),
        "source_xrecsys_dataset_dir": str(source),
        "out_dir": str(out),
        "user_count": len(user_remap),
        "product_count": len(product_remap),
        "split_stats": split_stats,
        "label_validation": label_validation,
        "id_policy": {
            "users": "compact remap from canonical uid",
            "products": (
                "compact remap from canonical pid using source "
                f"{config['product_entity']} entity order"
            ),
            "output_must_map_back_to": "canonical uid/pid",
        },
        "schema_projection": {
            "product_entity": config["product_entity"],
            "copied_entities": config["entities"],
            "empty_entities": config["empty_entities"],
            "entity_stats": entity_stats,
            "relations": relation_stats,
            "source_format": config.get("source_format", "xrecsys"),
        },
        "runtime_note": (
            "For amazon_book_kgat_v1 this is a canonical UCPR data-view "
            "artifact. The Amazon runtime schema/preprocess gate is handled "
            "by patch_ucpr_amazon_runtime.py and validated separately. Formal "
            "UCPR Amazon training/export/accuracy still remain pending."
        ) if args.model_dataset == AMAZON_BOOK_KGAT else "",
    }
    with open(out.parent / "ucpr_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
