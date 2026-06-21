#!/usr/bin/env python3
"""Build a CAFE view from a canonical dataset and a compatible UCPR view.

CAFE and UCPR use the same compact entity/relation schema in the
rep-path-reasoning framework. Reusing the UCPR entity order lets CAFE consume
the already-trained TransE state dict while preserving canonical uid/pid
round trips.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import pickle
import shutil
from collections import defaultdict
from pathlib import Path


DATASET_CONFIG = {
    "lastfm": {
        "entities": [
            ("user", "user.txt.gz"),
            ("product", "product.txt.gz"),
            ("artist", "artist.txt.gz"),
            ("engineer", "engineer.txt.gz"),
            ("genre", "genre.txt.gz"),
            ("producer", "producer.txt.gz"),
        ],
        "relations": [
            ("listened", None, "user", "product"),
            ("belong_to_genre", "belong_to_genre.txt.gz", "product", "genre"),
            ("featured_by_artist", "featured_by_artist.txt.gz", "product", "artist"),
            ("mixed_by_engineer", "mixed_by_engineer.txt.gz", "product", "engineer"),
            ("produced_by_producer", "produced_by_producer.txt.gz", "product", "producer"),
        ],
        "interaction": "listened",
        "disabled_rules": [],
    },
    "ml1m": {
        "entities": [
            ("user", "user.txt.gz"),
            ("product", "product.txt.gz"),
            ("actor", "actor.txt.gz"),
            ("director", "director.txt.gz"),
            ("prodcompany", "prodcompany.txt.gz"),
            ("editor", "editor.txt.gz"),
            ("writter", "writter.txt.gz"),
            ("cinematographer", "cinematographer.txt.gz"),
            ("composer", "composer.txt.gz"),
            ("country", "country.txt.gz"),
            ("category", "category.txt.gz"),
            ("producer", "producer.txt.gz"),
            ("wikipage", "wikipage.txt.gz"),
        ],
        "relations": [
            ("watched", None, "user", "product"),
            ("belong_to_category", "belong_to_category.txt.gz", "product", "category"),
            ("produced_by_producer", "produced_by_producer.txt.gz", "product", "producer"),
            ("directed_by_director", "directed_by_director.txt.gz", "product", "director"),
            ("produced_by_prodcompany", "produced_by_prodcompany.txt.gz", "product", "prodcompany"),
            ("starred_by_actor", "starred_by_actor.txt.gz", "product", "actor"),
            ("edited_by_editor", "edited_by_editor.txt.gz", "product", "editor"),
            ("wrote_by_writter", "wrote_by_writter.txt.gz", "product", "writter"),
            (
                "cinematography_by_cinematographer",
                "cinematography_by_cinematographer.txt.gz",
                "product",
                "cinematographer",
            ),
            ("composed_by_composer", "composed_by_composer.txt.gz", "product", "composer"),
            ("produced_in_country", "produced_in_country.txt.gz", "product", "country"),
            ("related_to_wikipage", "related_to_wikipage.txt.gz", "product", "wikipage"),
        ],
        "interaction": "watched",
        "disabled_rules": [
            "composed_by_composer",
            "produced_in_country",
            "related_to_wikipage",
        ],
    },
}


def read_compact_entity_ids(path: Path) -> list[int]:
    with gzip.open(path, "rt") as f:
        header = next(f, "").strip()
        if header != "id":
            raise ValueError(f"Expected entity header 'id' in {path}, got {header!r}")
        ids = [int(line.strip()) for line in f if line.strip()]
    if ids != list(range(len(ids))):
        raise ValueError(f"CAFE requires contiguous local ids in {path}")
    return ids


def read_remap(path: Path, canonical_col: str, model_col: str) -> tuple[dict[int, int], dict[int, int]]:
    canonical_to_model = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not {canonical_col, model_col}.issubset(reader.fieldnames or []):
            raise ValueError(f"Unexpected remap columns in {path}: {reader.fieldnames}")
        for row in reader:
            canonical_to_model[int(row[canonical_col])] = int(row[model_col])
    model_to_canonical = {model_id: canonical_id for canonical_id, model_id in canonical_to_model.items()}
    return canonical_to_model, model_to_canonical


def load_labels(path: Path) -> dict[int, list[int]]:
    with open(path, "rb") as f:
        return pickle.load(f)


def write_labels(
    path: Path,
    labels: dict[int, list[int]],
    user_remap: dict[int, int],
    product_remap: dict[int, int],
) -> dict:
    written = {}
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for canonical_uid in sorted(labels):
            if canonical_uid not in user_remap:
                raise KeyError(f"Missing user remap for canonical uid={canonical_uid}")
            model_uid = user_remap[canonical_uid]
            model_pids = []
            for canonical_pid in labels[canonical_uid]:
                if canonical_pid not in product_remap:
                    raise KeyError(f"Missing product remap for canonical pid={canonical_pid}")
                model_pids.append(product_remap[canonical_pid])
            writer.writerow([model_uid, *model_pids])
            written[model_uid] = model_pids
    return written


def iter_relation_rows(path: Path):
    with gzip.open(path, "rt") as f:
        for product_id, line in enumerate(f):
            values = line.strip().split()
            yield product_id, [int(value) for value in values]


def write_remap(path: Path, header: list[str], rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def validate_embedding_checkpoint(path: Path, entity_ids: dict, relations: list) -> dict:
    import torch

    state = torch.load(path, map_location="cpu")
    embedding_dim = None
    entity_shapes = {}
    relation_shapes = {}
    for entity_type, ids in entity_ids.items():
        key = f"{entity_type}.weight"
        if key not in state:
            raise KeyError(f"Missing {key} in {path}")
        shape = tuple(state[key].shape)
        expected_rows = len(ids) + 2
        if shape[0] != expected_rows:
            raise ValueError(
                f"{key} rows={shape[0]}, expected {expected_rows} "
                "(real entities + UCPR vocab padding + embedding padding)"
            )
        embedding_dim = embedding_dim or shape[1]
        if shape[1] != embedding_dim:
            raise ValueError(f"Inconsistent embedding dimension for {key}: {shape}")
        entity_shapes[key] = shape

    for relation_name, _filename, _head_type, tail_type in relations:
        relation_key = relation_name
        bias_key = f"{relation_name}_bias.weight"
        if relation_key not in state or bias_key not in state:
            raise KeyError(f"Missing {relation_key} or {bias_key} in {path}")
        relation_shape = tuple(state[relation_key].shape)
        bias_shape = tuple(state[bias_key].shape)
        if relation_shape != (1, embedding_dim):
            raise ValueError(f"Unexpected shape for {relation_key}: {relation_shape}")
        expected_bias_rows = len(entity_ids[tail_type]) + 2
        if bias_shape != (expected_bias_rows, 1):
            raise ValueError(
                f"Unexpected shape for {bias_key}: {bias_shape}; "
                f"expected {(expected_bias_rows, 1)}"
            )
        relation_shapes[relation_key] = relation_shape
        relation_shapes[bias_key] = bias_shape

    return {
        "embedding_dim": embedding_dim,
        "entity_shapes": {key: list(shape) for key, shape in entity_shapes.items()},
        "relation_shapes": {key: list(shape) for key, shape in relation_shapes.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument("--ucpr-view-dir", required=True, help="Directory containing compact UCPR *.txt.gz files")
    parser.add_argument("--user-remap", required=True)
    parser.add_argument("--product-remap", required=True)
    parser.add_argument("--embedding-ckpt", required=True, help="Compatible UCPR TransE state dict")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset", default="lastfm_v1")
    parser.add_argument("--model-dataset", choices=sorted(DATASET_CONFIG), default="lastfm")
    args = parser.parse_args()

    canonical_root = Path(args.canonical_root)
    ucpr_view = Path(args.ucpr_view_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = DATASET_CONFIG[args.model_dataset]

    canonical_to_user, user_to_canonical = read_remap(
        Path(args.user_remap), "canonical_uid", "ucpr_uid"
    )
    canonical_to_product, product_to_canonical = read_remap(
        Path(args.product_remap), "canonical_pid", "ucpr_product_idx"
    )

    entity_ids = {}
    global_ids = {}
    entity_rows = []
    next_global_id = 0
    for entity_type, filename in config["entities"]:
        ids = read_compact_entity_ids(ucpr_view / filename)
        entity_ids[entity_type] = ids
        global_ids[entity_type] = {}
        for local_id in ids:
            global_ids[entity_type][local_id] = next_global_id
            if entity_type == "user":
                value = f"canonical_uid_{user_to_canonical[local_id]}"
            elif entity_type == "product":
                value = f"canonical_pid_{product_to_canonical[local_id]}"
            else:
                value = f"{entity_type}_{local_id}"
            entity_rows.append((next_global_id, f"{entity_type}_{local_id}", value))
            next_global_id += 1

    with gzip.open(out / "kg_entities.txt.gz", "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["global_id", "local_id", "value"])
        writer.writerows(entity_rows)

    relation_names = [row[0] for row in config["relations"]]
    relation_to_id = {name: idx for idx, name in enumerate(relation_names)}
    reverse_offset = len(relation_names)
    reverse_relation_to_id = {
        name: reverse_offset + relation_to_id[name] for name in relation_names
    }
    with gzip.open(out / "kg_relations.txt.gz", "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for name in relation_names:
            writer.writerow([relation_to_id[name], name])
        for name in relation_names:
            writer.writerow([reverse_relation_to_id[name], f"rev_{name}"])

    with gzip.open(out / "kg_rules.txt.gz", "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for name in relation_names:
            if name in config["disabled_rules"]:
                continue
            forward = relation_to_id[name]
            reverse = reverse_relation_to_id[name]
            if name == config["interaction"]:
                writer.writerow([forward, reverse, forward])
            else:
                writer.writerow([relation_to_id[config["interaction"]], forward, reverse])

    canonical_labels = {
        split: load_labels(canonical_root / "labels" / f"{split}_label.pkl")
        for split in ["train", "valid", "test"]
    }
    compact_labels = {
        split: write_labels(
            out / f"{split}.txt.gz",
            canonical_labels[split],
            canonical_to_user,
            canonical_to_product,
        )
        for split in ["train", "valid", "test"]
    }

    triple_count = 0
    relation_edge_counts = defaultdict(int)
    with gzip.open(out / "kg_triples.txt.gz", "wt", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["entity_head", "relation", "entity_tail"])

        interaction_name = config["interaction"]
        interaction_id = relation_to_id[interaction_name]
        rev_interaction_id = reverse_relation_to_id[interaction_name]
        for uid, pids in compact_labels["train"].items():
            user_gid = global_ids["user"][uid]
            for pid in pids:
                product_gid = global_ids["product"][pid]
                writer.writerow([user_gid, interaction_id, product_gid])
                writer.writerow([product_gid, rev_interaction_id, user_gid])
                triple_count += 2
                relation_edge_counts[interaction_name] += 1

        for relation_name, filename, head_type, tail_type in config["relations"][1:]:
            forward_id = relation_to_id[relation_name]
            reverse_id = reverse_relation_to_id[relation_name]
            expected_products = len(entity_ids[head_type])
            rows_seen = 0
            for head_local_id, tail_local_ids in iter_relation_rows(ucpr_view / filename):
                rows_seen += 1
                # The framework relation files contain one trailing blank row
                # after the final compact product id.
                if head_local_id == expected_products and not tail_local_ids:
                    continue
                if head_local_id not in global_ids[head_type]:
                    raise KeyError(f"Unknown {head_type} id {head_local_id} in {filename}")
                head_gid = global_ids[head_type][head_local_id]
                for tail_local_id in tail_local_ids:
                    if tail_local_id not in global_ids[tail_type]:
                        raise KeyError(
                            f"Unknown {tail_type} id {tail_local_id} in {filename}"
                        )
                    tail_gid = global_ids[tail_type][tail_local_id]
                    writer.writerow([head_gid, forward_id, tail_gid])
                    writer.writerow([tail_gid, reverse_id, head_gid])
                    triple_count += 2
                    relation_edge_counts[relation_name] += 1
            if rows_seen not in {expected_products, expected_products + 1}:
                raise ValueError(
                    f"{filename} has {rows_seen} product rows; expected {expected_products}"
                )

    embedding_src = Path(args.embedding_ckpt)
    if not embedding_src.exists():
        raise FileNotFoundError(embedding_src)
    embedding_validation = validate_embedding_checkpoint(
        embedding_src, entity_ids, config["relations"]
    )
    shutil.copy2(embedding_src, out / "kg_embedding.ckpt")

    write_remap(
        out / "mappings" / "user_remap.tsv",
        ["canonical_uid", "cafe_uid"],
        sorted(canonical_to_user.items(), key=lambda row: row[1]),
    )
    write_remap(
        out / "mappings" / "product_remap.tsv",
        ["canonical_pid", "cafe_product_idx"],
        sorted(canonical_to_product.items(), key=lambda row: row[1]),
    )

    validation = {}
    for split in ["train", "valid", "test"]:
        rebuilt = {
            user_to_canonical[uid]: [product_to_canonical[pid] for pid in pids]
            for uid, pids in compact_labels[split].items()
        }
        validation[split] = {
            "canonical_users": len(canonical_labels[split]),
            "cafe_users": len(compact_labels[split]),
            "exact_match": rebuilt == canonical_labels[split],
        }

    metadata = {
        "dataset": args.dataset,
        "model_dataset": args.model_dataset,
        "canonical_root": str(canonical_root),
        "ucpr_view_dir": str(ucpr_view),
        "out_dir": str(out),
        "embedding_source": str(embedding_src),
        "embedding_validation": embedding_validation,
        "entity_counts": {name: len(ids) for name, ids in entity_ids.items()},
        "relation_ids": relation_to_id,
        "reverse_relation_ids": reverse_relation_to_id,
        "disabled_rules": config["disabled_rules"],
        "forward_edge_counts": dict(relation_edge_counts),
        "triple_count_including_reverse": triple_count,
        "label_validation": validation,
        "id_policy": {
            "users": "reuse UCPR compact uid; map back through user_remap.tsv",
            "products": "reuse UCPR compact product id; map back through product_remap.tsv",
            "external_entities": "reuse UCPR/xrecsys local entity ids",
        },
    }
    with open(out / "cafe_view_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
