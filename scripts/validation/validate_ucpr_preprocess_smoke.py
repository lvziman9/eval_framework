#!/usr/bin/env python3
"""Validate an isolated UCPR runtime preprocess smoke.

The check proves that a patched runtime can load the generated canonical UCPR
view, build UCPR's dataset/KG/label pickles, and round-trip model ids back to
canonical labels without changing train/valid/test semantics.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path


AMAZON_DATASET = "amazon_book_kgat_v1"
AMAZON_RELATIONS = [
    "book_author_entity",
    "book_genre_entity",
    "book_original_language_entity",
    "book_subject_entity",
    "book_next_in_series_entity",
    "book_previous_in_series_entity",
    "book_part_of_series_entity",
    "book_character_entity",
    "book_interior_illustration_entity",
]
AMAZON_PATTERN_IDS = {0, 5, 10, 11, 13, 15, 18, 19, 20, 36}


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def load_labels(path: Path) -> dict[int, list[int]]:
    raw = load_pickle(path)
    return {int(uid): [int(pid) for pid in pids] for uid, pids in raw.items()}


def load_remap(path: Path, source_column: str, target_column: str) -> dict[int, int]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = set(reader.fieldnames or [])
        expected = {source_column, target_column}
        if not expected.issubset(fields):
            raise ValueError(f"{path} columns={reader.fieldnames}, expected {sorted(expected)}")
        return {int(row[target_column]): int(row[source_column]) for row in reader}


def validate_labels(
    runtime_tmp: Path,
    canonical_labels: Path,
    user_remap: dict[int, int],
    product_remap: dict[int, int],
) -> dict[str, dict[str, object]]:
    report = {}
    for split in ["train", "valid", "test"]:
        model_labels = load_labels(runtime_tmp / f"{split}_label.pkl")
        rebuilt = {
            user_remap[int(uid)]: [product_remap[int(pid)] for pid in pids]
            for uid, pids in model_labels.items()
        }
        canonical = load_labels(canonical_labels / f"{split}_label.pkl")
        mismatched = [
            uid
            for uid in sorted(set(canonical) | set(rebuilt))
            if canonical.get(uid) != rebuilt.get(uid)
        ]
        report[split] = {
            "canonical_users": len(canonical),
            "generated_users": len(model_labels),
            "canonical_interactions": sum(len(items) for items in canonical.values()),
            "generated_interactions": sum(len(items) for items in model_labels.values()),
            "exact_match": not mismatched,
            "mismatched_user_examples": mismatched[:10],
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--canonical-root", required=True)
    parser.add_argument("--view-root", required=True)
    parser.add_argument("--dataset", default=AMAZON_DATASET)
    parser.add_argument("--summary-json", required=True)
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    canonical_root = Path(args.canonical_root).resolve()
    view_root = Path(args.view_root).resolve()
    dataset = args.dataset
    runtime_tmp = (
        runtime_root
        / "data"
        / dataset
        / "preprocessed"
        / "ucpr"
        / "tmp"
    )

    sys.path.insert(0, str(runtime_root))
    from models.UCPR import utils as ucpr_utils  # type: ignore

    user_remap = load_remap(view_root / "user_remap.tsv", "canonical_uid", "ucpr_uid")
    product_remap = load_remap(
        view_root / "product_remap.tsv",
        "canonical_pid",
        "ucpr_product_idx",
    )

    core_files = {
        "dataset_pickle": runtime_tmp / "dataset.pkl",
        "kg_pickle": runtime_tmp / "kg.pkl",
        "train_label": runtime_tmp / "train_label.pkl",
        "valid_label": runtime_tmp / "valid_label.pkl",
        "test_label": runtime_tmp / "test_label.pkl",
    }
    core_file_report = {
        name: {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
        for name, path in core_files.items()
    }

    dataset_obj = load_pickle(core_files["dataset_pickle"])
    kg_obj = load_pickle(core_files["kg_pickle"])
    label_checks = validate_labels(
        runtime_tmp,
        canonical_root / "labels",
        user_remap,
        product_remap,
    )

    schema_checks = {
        "dataset_constant": getattr(ucpr_utils, "AMAZON_BOOK_KGAT", None) == dataset,
        "interaction": ucpr_utils.INTERACTION.get(dataset) == "purchased",
        "main_product_interaction": ucpr_utils.MAIN_PRODUCT_INTERACTION.get(dataset)
        == ("product", "purchased"),
        "kg_relation_has_dataset": dataset in ucpr_utils.KG_RELATION,
        "path_pattern_ids": set(ucpr_utils.PATH_PATTERN.get(dataset, {})) == AMAZON_PATTERN_IDS,
        "product_relations": set(
            ucpr_utils.KG_RELATION.get(dataset, {}).get("product", {})
        )
        == set(["purchased"] + AMAZON_RELATIONS),
        "entity_reverse_relations": set(
            ucpr_utils.KG_RELATION.get(dataset, {}).get("entity", {})
        )
        == set(AMAZON_RELATIONS),
    }
    dataset_checks = {
        "dataset_name": getattr(dataset_obj, "dataset_name", None) == dataset,
        "entity_names": sorted(getattr(dataset_obj, "entity_names", [])),
        "other_relation_names": sorted(getattr(dataset_obj, "other_relation_names", [])),
        "relation2entity_all_entity": all(
            getattr(dataset_obj, "relation2entity", {}).get(relation) == "entity"
            for relation in AMAZON_RELATIONS
        ),
        "review_rows": int(getattr(dataset_obj.review, "size", 0)),
    }
    kg_purchase_edges = sum(
        len(edges.get("purchased", []))
        for edges in getattr(kg_obj, "G", {}).get("user", {}).values()
    )
    kg_relation_edges = {
        relation: sum(
            len(edges.get(relation, []))
            for edges in getattr(kg_obj, "G", {}).get("product", {}).values()
        )
        for relation in AMAZON_RELATIONS
    }
    kg_checks = {
        "dataset_name": getattr(kg_obj, "dataset_name", None) == dataset,
        "user_purchase_edges": kg_purchase_edges,
        "relation_edges": kg_relation_edges,
        "all_relation_edges_nonempty": all(value > 0 for value in kg_relation_edges.values()),
    }

    passed = (
        all(item["exists"] for item in core_file_report.values())
        and all(result["exact_match"] for result in label_checks.values())
        and all(schema_checks.values())
        and dataset_checks["dataset_name"]
        and set(dataset_checks["entity_names"]) == {"entity", "product", "user"}
        and set(dataset_checks["other_relation_names"]) == set(AMAZON_RELATIONS)
        and dataset_checks["relation2entity_all_entity"]
        and kg_checks["dataset_name"]
        and kg_checks["user_purchase_edges"]
        == label_checks["train"]["canonical_interactions"]
        and kg_checks["all_relation_edges_nonempty"]
    )

    report = {
        "status": "PASS" if passed else "FAIL",
        "dataset": dataset,
        "runtime_root": str(runtime_root),
        "runtime_tmp": str(runtime_tmp),
        "canonical_root": str(canonical_root),
        "view_root": str(view_root),
        "core_files": core_file_report,
        "label_checks": label_checks,
        "schema_checks": schema_checks,
        "dataset_checks": dataset_checks,
        "kg_checks": kg_checks,
    }
    out = Path(args.summary_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
