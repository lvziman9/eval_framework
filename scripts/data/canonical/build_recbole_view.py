#!/usr/bin/env python3
"""Build a pre-split RecBole view from a canonical dataset.

The view preserves canonical user/item ids as RecBole tokens and projects the
xrecsys item-centric KG into RecBole ``.link`` and ``.kg`` files. It can be
used by both KG-aware accuracy references (KGIN/KGAT) and interaction-only
references (LightGCN).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import pickle
import zipfile
from pathlib import Path


DATASET_CONFIG = {
    "lastfm": {
        "product_entity": "song",
        "relations": {
            "alternative_version_of_s_rs.txt.gz": (
                "alternative_version_of",
                "related_song",
            ),
            "belong_to_s_ca.txt.gz": ("belong_to", "category"),
            "featured_by_s_a.txt.gz": ("featured_by", "artist"),
            "mixed_by_s_e.txt.gz": ("mixed_by", "engineer"),
            "orginal_version_of_s_rs.txt.gz": (
                "original_version_of",
                "related_song",
            ),
            "produced_by_producer_s_pr.txt.gz": ("produced_by", "producer"),
            "related_to_s_rs.txt.gz": ("related_to", "related_song"),
            "sang_by_s_a.txt.gz": ("sang_by", "artist"),
        },
    },
    "ml1m": {
        "product_entity": "movie",
        "relations": {
            "belong_to_m_ca.txt.gz": ("belong_to", "category"),
            "cinematography_m_ci.txt.gz": (
                "cinematography_by",
                "cinematographer",
            ),
            "composed_by_m_c.txt.gz": ("composed_by", "composer"),
            "directed_by_m_d.txt.gz": ("directed_by", "director"),
            "edited_by_m_ed.txt.gz": ("edited_by", "editor"),
            "produced_by_company_m_pc.txt.gz": (
                "produced_by_company",
                "production_company",
            ),
            "produced_by_producer_m_pr.txt.gz": (
                "produced_by_producer",
                "producer",
            ),
            "starring_m_a.txt.gz": ("starring", "actor"),
            "wrote_by_m_w.txt.gz": ("wrote_by", "writter"),
        },
    },
    "amazon-book": {
        "product_entity": "entity",
        "source_format": "kgat_zip",
        "kg_archive": "kg_final.txt.zip",
    },
}


def iter_interactions(path: Path):
    with gzip.open(path, "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        first = next(reader, None)
        if first is None:
            return
        if first != ["uid", "pid", "rating", "timestamp"]:
            if len(first) != 4:
                raise ValueError(f"Unexpected canonical interaction row in {path}: {first}")
            yield tuple(map(int, first))
        for row in reader:
            if row:
                yield tuple(map(int, row))


def load_mapping_ids(path: Path) -> list[int]:
    with open(path, newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header:
            raise ValueError(f"Empty mapping file: {path}")
        return [int(row[0]) for row in reader if row]


def load_labels(path: Path) -> dict[int, list[int]]:
    with open(path, "rb") as f:
        return {int(uid): [int(pid) for pid in pids] for uid, pids in pickle.load(f).items()}


def entity_token(entity_type: str, entity_id: int) -> str:
    return f"{entity_type}:{entity_id}"


def write_split(canonical_root: Path, split: str, out_path: Path) -> dict:
    rows = list(iter_interactions(canonical_root / "interactions" / f"{split}.tsv.gz"))
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "user_id:token",
                "item_id:token",
                "rating:float",
                "timestamp:float",
            ]
        )
        writer.writerows(rows)
    return {
        "interactions": len(rows),
        "users": len({row[0] for row in rows}),
        "items": len({row[1] for row in rows}),
    }


def write_id_files(out: Path, dataset_token: str, users: list[int], products: list[int]):
    with open(out / f"{dataset_token}.user", "w") as f:
        f.write("user_id:token\n")
        for uid in users:
            f.write(f"{uid}\n")
    with open(out / f"{dataset_token}.item", "w") as f:
        f.write("item_id:token\n")
        for pid in products:
            f.write(f"{pid}\n")


def write_link_file(
    out: Path,
    dataset_token: str,
    product_entity: str,
    products: list[int],
):
    with open(out / f"{dataset_token}.link", "w") as f:
        f.write("item_id:token\tentity_id:token\n")
        for pid in products:
            f.write(f"{pid}\t{entity_token(product_entity, pid)}\n")


def write_kg_file(
    out: Path,
    dataset_token: str,
    source: Path,
    config: dict,
    canonical_products: set[int],
) -> tuple[dict, set[int]]:
    if config.get("source_format") == "kgat_zip":
        return write_kgat_kg_file(
            out,
            dataset_token,
            source / config["kg_archive"],
            canonical_products,
        )

    edge_counts = {}
    total = 0
    linked_products = set()
    with open(out / f"{dataset_token}.kg", "w") as fout:
        fout.write("head_id:token\trelation_id:token\ttail_id:token\n")
        for filename, (relation, target_type) in config["relations"].items():
            relation_path = source / "relations" / filename
            count = 0
            if not relation_path.exists():
                edge_counts[relation] = 0
                continue
            with gzip.open(relation_path, "rt") as fin:
                for product_id, line in enumerate(fin):
                    if product_id not in canonical_products:
                        continue
                    for raw_tail in line.split():
                        tail_id = int(raw_tail)
                        fout.write(
                            f"{entity_token(config['product_entity'], product_id)}\t"
                            f"{relation}\t{entity_token(target_type, tail_id)}\n"
                        )
                        count += 1
                        linked_products.add(product_id)
            edge_counts[relation] = count
            total += count
    return {
        "total_edges": total,
        "relation_edges": edge_counts,
        "linked_products": len(linked_products),
    }, linked_products


def write_kgat_kg_file(
    out: Path,
    dataset_token: str,
    archive_path: Path,
    canonical_products: set[int],
) -> tuple[dict, set[int]]:
    relation_edges: dict[str, int] = {}
    total = 0
    linked_products = set()
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.namelist()
        if members != ["kg_final.txt"]:
            raise ValueError(f"Unexpected KGAT archive members: {members}")
        with archive.open(members[0]) as fin, open(
            out / f"{dataset_token}.kg", "w"
        ) as fout:
            fout.write("head_id:token\trelation_id:token\ttail_id:token\n")
            for line_number, line in enumerate(fin, start=1):
                columns = line.split()
                if len(columns) != 3:
                    raise ValueError(
                        f"Malformed KGAT triple at line {line_number}: {line!r}"
                    )
                head, relation, tail = map(int, columns)
                relation_token = f"relation:{relation}"
                fout.write(
                    f"{entity_token('entity', head)}\t{relation_token}\t"
                    f"{entity_token('entity', tail)}\n"
                )
                relation_edges[relation_token] = (
                    relation_edges.get(relation_token, 0) + 1
                )
                total += 1
                if head in canonical_products:
                    linked_products.add(head)
                if tail in canonical_products:
                    linked_products.add(tail)
    return {
        "total_edges": total,
        "relation_edges": relation_edges,
        "linked_products": len(linked_products),
    }, linked_products


def validate_round_trip(canonical_root: Path, out: Path, dataset_token: str) -> dict:
    report = {}
    for split in ["train", "valid", "test"]:
        rebuilt: dict[int, list[int]] = {}
        with open(out / f"{dataset_token}.{split}.inter", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                rebuilt.setdefault(int(row["user_id:token"]), []).append(
                    int(row["item_id:token"])
                )
        canonical = load_labels(canonical_root / "labels" / f"{split}_label.pkl")
        report[split] = {
            "exact": rebuilt == canonical,
            "users": len(rebuilt),
            "interactions": sum(len(items) for items in rebuilt.values()),
        }
        if rebuilt != canonical:
            raise ValueError(f"RecBole {split} split does not round-trip to canonical labels")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument(
        "--source-dataset-dir",
        "--source-xrecsys-dataset-dir",
        dest="source_dataset_dir",
        required=True,
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset-token", required=True)
    parser.add_argument("--model-dataset", choices=sorted(DATASET_CONFIG), required=True)
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    source = Path(args.source_dataset_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = DATASET_CONFIG[args.model_dataset]

    users = load_mapping_ids(canonical_root / "mappings" / "user_mapping.tsv")
    products = load_mapping_ids(canonical_root / "mappings" / "product_mapping.tsv")

    split_stats = {
        split: write_split(
            canonical_root,
            split,
            out / f"{args.dataset_token}.{split}.inter",
        )
        for split in ["train", "valid", "test"]
    }
    write_id_files(out, args.dataset_token, users, products)
    kg_stats, linked_products = write_kg_file(
        out,
        args.dataset_token,
        source,
        config,
        set(products),
    )
    write_link_file(
        out,
        args.dataset_token,
        config["product_entity"],
        sorted(linked_products),
    )
    validation = validate_round_trip(canonical_root, out, args.dataset_token)

    metadata = {
        "dataset_token": args.dataset_token,
        "model_dataset": args.model_dataset,
        "canonical_root": str(canonical_root),
        "source_dataset_dir": str(source),
        "out_dir": str(out),
        "users": len(users),
        "products": len(products),
        "split_stats": split_stats,
        "kg_stats": kg_stats,
        "validation": validation,
        "id_policy": "canonical uid/pid values are preserved as RecBole tokens",
    }
    with open(out / "recbole_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
