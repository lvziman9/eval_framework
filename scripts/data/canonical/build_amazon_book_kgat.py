#!/usr/bin/env python3
"""Build a canonical dataset from the KGAT Amazon-book release."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import pickle
import zipfile
from collections import defaultdict
from pathlib import Path


def read_right_id_mapping(path: Path) -> tuple[list[str], dict[int, str]]:
    """Read a mapping whose textual id may contain spaces.

    KGAT's Amazon-book ``entity_list.txt`` contains a small number of literal
    Freebase values with spaces, so parsing must split only at the final space.
    """

    values = {}
    with open(path, errors="strict") as f:
        header = f.readline().strip().split()
        for line_number, line in enumerate(f, start=2):
            text = line.rstrip("\n")
            original_id, separator, remap_text = text.rpartition(" ")
            if not separator:
                raise ValueError(f"Malformed mapping row {path}:{line_number}: {text!r}")
            remap_id = int(remap_text)
            if remap_id in values:
                raise ValueError(f"Duplicate remap id={remap_id} in {path}")
            values[remap_id] = original_id
    if sorted(values) != list(range(len(values))):
        raise ValueError(f"Non-contiguous remap ids in {path}")
    return header, values


def read_item_mapping(path: Path) -> tuple[list[str], dict[int, tuple[str, str]]]:
    values = {}
    with open(path) as f:
        header = f.readline().strip().split()
        for line_number, line in enumerate(f, start=2):
            columns = line.strip().split()
            if len(columns) != 3:
                raise ValueError(f"Malformed item row {path}:{line_number}: {line!r}")
            original_id, remap_text, freebase_id = columns
            remap_id = int(remap_text)
            if remap_id in values:
                raise ValueError(f"Duplicate item remap id={remap_id}")
            values[remap_id] = (original_id, freebase_id)
    if sorted(values) != list(range(len(values))):
        raise ValueError("Amazon-book item ids are not contiguous")
    return header, values


def read_interactions(path: Path) -> tuple[dict[int, list[int]], dict]:
    labels = {}
    pair_count = 0
    empty_users = 0
    with open(path) as f:
        for line_number, line in enumerate(f, start=1):
            columns = line.split()
            if not columns:
                raise ValueError(f"Blank interaction row {path}:{line_number}")
            uid = int(columns[0])
            pids = [int(value) for value in columns[1:]]
            if uid in labels:
                raise ValueError(f"Duplicate uid={uid} in {path}")
            if len(pids) != len(set(pids)):
                raise ValueError(f"Duplicate products for uid={uid} in {path}")
            labels[uid] = pids
            pair_count += len(pids)
            empty_users += not pids
    return labels, {
        "user_rows": len(labels),
        "interactions": pair_count,
        "empty_user_rows": empty_users,
        "min_items_per_row": min(map(len, labels.values())),
        "max_items_per_row": max(map(len, labels.values())),
    }


def deterministic_validation_pid(uid: int, pids: list[int], seed: str) -> int:
    return max(
        pids,
        key=lambda pid: hashlib.sha256(f"{seed}:{uid}:{pid}".encode()).digest(),
    )


def split_source_train(
    source_train: dict[int, list[int]], seed: str
) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    train = {}
    valid = {}
    for uid, pids in source_train.items():
        if len(pids) < 2:
            raise ValueError(f"uid={uid} has fewer than two source-train items")
        held_out = deterministic_validation_pid(uid, pids, seed)
        train[uid] = [pid for pid in pids if pid != held_out]
        valid[uid] = [held_out]
    return train, valid


def labels_to_pairs(labels: dict[int, list[int]]) -> set[tuple[int, int]]:
    return {(uid, pid) for uid, pids in labels.items() for pid in pids}


def write_interactions(path: Path, labels: dict[int, list[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for uid in sorted(labels):
            for pid in labels[uid]:
                writer.writerow([uid, pid, 1, -1])


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


def audit_kg(path: Path, entity_count: int, relation_count: int) -> dict:
    entities = set()
    relations = set()
    triples = set()
    duplicate_count = 0
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        if members != ["kg_final.txt"]:
            raise ValueError(f"Unexpected KG zip members: {members}")
        with archive.open(members[0]) as f:
            for line_number, line in enumerate(f, start=1):
                columns = line.split()
                if len(columns) != 3:
                    raise ValueError(f"Malformed KG triple at line {line_number}")
                head, relation, tail = map(int, columns)
                if not (0 <= head < entity_count and 0 <= tail < entity_count):
                    raise ValueError(f"Out-of-range KG entity at line {line_number}")
                if not 0 <= relation < relation_count:
                    raise ValueError(f"Out-of-range KG relation at line {line_number}")
                triple = (head, relation, tail)
                duplicate_count += triple in triples
                triples.add(triple)
                entities.update((head, tail))
                relations.add(relation)
    return {
        "triples": len(triples),
        "duplicate_triples": duplicate_count,
        "referenced_entities": len(entities),
        "referenced_relations": len(relations),
        "entity_id_range": [min(entities), max(entities)],
        "relation_id_range": [min(relations), max(relations)],
    }


def split_stats(labels: dict[int, list[int]]) -> dict:
    return {
        "users": len(labels),
        "users_with_interactions": sum(bool(pids) for pids in labels.values()),
        "interactions": sum(map(len, labels.values())),
        "products": len({pid for pids in labels.values() for pid in pids}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--name", default="amazon_book_kgat_v1")
    parser.add_argument("--validation-seed", default="amazon-book-kgat-v1")
    args = parser.parse_args()

    source = Path(args.source_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    user_header, users = read_right_id_mapping(source / "user_list.txt")
    item_header, items = read_item_mapping(source / "item_list.txt")
    entity_header, entities = read_right_id_mapping(source / "entity_list.txt")
    relation_header, relations = read_right_id_mapping(source / "relation_list.txt")

    if len(users) != 70679 or len(items) != 24915:
        raise ValueError(
            f"Unexpected source dimensions: users={len(users)}, items={len(items)}"
        )
    for pid, (_original_id, freebase_id) in items.items():
        if entities.get(pid) != freebase_id:
            raise ValueError(
                f"Item/entity mapping mismatch for pid={pid}: "
                f"item={freebase_id!r}, entity={entities.get(pid)!r}"
            )

    source_train, source_train_stats = read_interactions(source / "train.txt")
    source_test_all, source_test_stats = read_interactions(source / "test.txt")
    expected_users = set(range(len(users)))
    if set(source_train) != expected_users or set(source_test_all) != expected_users:
        raise ValueError("Source train/test user rows do not cover the user mapping")

    train, valid = split_source_train(source_train, args.validation_seed)
    test = {uid: pids for uid, pids in source_test_all.items() if pids}

    train_pairs = labels_to_pairs(train)
    valid_pairs = labels_to_pairs(valid)
    test_pairs = labels_to_pairs(test)
    if train_pairs & valid_pairs or train_pairs & test_pairs or valid_pairs & test_pairs:
        raise ValueError("Canonical Amazon-book splits overlap")
    source_train_pairs = labels_to_pairs(source_train)
    if train_pairs | valid_pairs != source_train_pairs:
        raise ValueError("Canonical train+valid does not reconstruct source train")
    if test_pairs != labels_to_pairs(source_test_all):
        raise ValueError("Canonical test does not reconstruct non-empty source test")

    valid_products = set(range(len(items)))
    for split, pairs in {
        "train": train_pairs,
        "valid": valid_pairs,
        "test": test_pairs,
    }.items():
        unknown = sorted({pid for _uid, pid in pairs} - valid_products)
        if unknown:
            raise ValueError(f"Unknown products in {split}: {unknown[:5]}")

    kg_stats = audit_kg(
        source / "kg_final.txt.zip", len(entities), len(relations)
    )
    if kg_stats["triples"] != 2557746 or kg_stats["duplicate_triples"]:
        raise ValueError(f"Unexpected KG audit: {kg_stats}")

    for split, labels in (("train", train), ("valid", valid), ("test", test)):
        write_interactions(out / "interactions" / f"{split}.tsv.gz", labels)
        write_pickle(out / "labels" / f"{split}_label.pkl", labels)

    write_mapping(
        out / "mappings" / "user_mapping.tsv",
        ["canonical_uid", "source_original_uid"],
        ((uid, users[uid]) for uid in range(len(users))),
    )
    write_mapping(
        out / "mappings" / "product_mapping.tsv",
        ["canonical_pid", "source_original_item_id", "freebase_id"],
        (
            (pid, items[pid][0], items[pid][1])
            for pid in range(len(items))
        ),
    )
    write_mapping(
        out / "mappings" / "entity_mapping.tsv",
        ["canonical_entity_id", "freebase_id_or_literal"],
        ((eid, entities[eid]) for eid in range(len(entities))),
    )
    write_mapping(
        out / "mappings" / "relation_mapping.tsv",
        ["canonical_relation_id", "freebase_relation"],
        ((rid, relations[rid]) for rid in range(len(relations))),
    )

    metadata = {
        "name": args.name,
        "domain": "amazon_books",
        "source": {
            "directory": str(source.resolve()),
            "repository": (
                "https://github.com/xiangwang1223/"
                "knowledge_graph_attention_network"
            ),
            "commit": "c03737be46ac26a0b5431efe149828e982ffbbfb",
            "benchmark": "KGAT Amazon-book",
            "kg_provenance": (
                "Benchmark-provided Freebase KG following the KGAT/KB4Rec "
                "item-to-entity mapping; not authored by Amazon or this project."
            ),
        },
        "interaction_format": "uid\tpid\trating\ttimestamp",
        "feedback_type": "implicit",
        "default_rating": 1,
        "timestamp_policy": -1,
        "user_id_policy": "preserve KGAT remap user id",
        "product_id_policy": "preserve KGAT remap item/entity id",
        "validation_policy": "one deterministic SHA-256-selected source-train item per user",
        "validation_seed": args.validation_seed,
        "source_mapping_headers": {
            "user": user_header,
            "item": item_header,
            "entity": entity_header,
            "relation": relation_header,
        },
        "source_release_stats": {
            "users": len(users),
            "items": len(items),
            "source_train": source_train_stats,
            "source_test": source_test_stats,
            "source_unique_interactions": len(source_train_pairs | test_pairs),
            "total_entity_ids_including_item_entities": len(entities),
            "non_item_kg_entities": len(entities) - len(items),
            "relations": len(relations),
            "kg": kg_stats,
        },
        "published_table_stats_for_comparison": {
            "users": 70679,
            "items": 24915,
            "interactions": 847733,
            "non_item_kg_entities": 88572,
            "relations": 39,
            "kg_triples": 2557746,
            "note": (
                "The fixed official repository release contains 846,434 "
                "unique interaction pairs; canonical counts use actual files."
            ),
        },
        "canonical_split_stats": {
            "train": split_stats(train),
            "valid": split_stats(valid),
            "test": split_stats(test),
        },
        "test_source_empty_user_rows_omitted_from_evaluation_labels": (
            source_test_stats["empty_user_rows"]
        ),
        "kg_policy": (
            "Preserve source KG only; no interaction-derived or metadata-derived "
            "triples are added by the canonical builder."
        ),
    }
    with open(out / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    with open(out / "README.md", "w") as f:
        f.write(f"# {args.name}\n\n")
        f.write(
            "Canonical import of the KGAT Amazon-book benchmark. The source "
            "Freebase KG is preserved by reference; see `metadata.json` for "
            "the fixed commit, actual release counts, split policy, and "
            "provenance distinction.\n"
        )

    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
