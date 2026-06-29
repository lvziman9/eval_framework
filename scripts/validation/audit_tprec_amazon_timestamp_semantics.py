#!/usr/bin/env python3
"""Audit whether Amazon-book KGAT can support a formal temporal TPRec run."""

from __future__ import annotations

import argparse
import ast
import csv
import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion"
CANONICAL_ROOT = RUN / "amazon_book_kgat_v1"
HOPWISE_ROOT = RUN / "hopwise_data" / "canonical_amazon_book_kgat_v1"
OUT = (
    CANONICAL_ROOT
    / "model_views"
    / "tprec"
    / "tprec_timestamp_semantics_audit.json"
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def timestamp_counts(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    with gzip.open(path, "rt") as handle:
        reader = csv.reader(handle, delimiter="\t")
        first = next(reader, None)
        if first is None:
            return counts
        if first == ["uid", "pid", "rating", "timestamp"]:
            pass
        elif len(first) == 4:
            counts[first[3]] += 1
        else:
            raise ValueError(f"Unexpected canonical interaction row in {path}: {first}")
        for row in reader:
            if not row:
                continue
            if len(row) != 4:
                raise ValueError(f"Unexpected canonical interaction row in {path}: {row}")
            counts[row[3]] += 1
    return counts


def hopwise_timestamp_counts(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected = [
            "user_id:token",
            "item_id:token",
            "rating:float",
            "timestamp:float",
        ]
        if reader.fieldnames != expected:
            raise ValueError(f"Unexpected Hopwise interaction header in {path}: {reader.fieldnames}")
        for row in reader:
            counts[row["timestamp:float"]] += 1
    return counts


def kg_relations(path: Path) -> set[str]:
    values: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != ["head_id:token", "relation_id:token", "tail_id:token"]:
            raise ValueError(f"Unexpected Hopwise KG header in {path}: {reader.fieldnames}")
        for row in reader:
            values.add(row["relation_id:token"])
    return values


def literal_assignment(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise KeyError(f"{name} not found in {path}")


def constrained_relations(dataset: str) -> set[str]:
    if dataset != "canonical_amazon_book_kgat_v1":
        raise ValueError(f"unsupported TPRec timestamp audit dataset: {dataset}")
    constraints = literal_assignment(
        ROOT / "scripts" / "hopwise" / "tprec_runtime.py",
        "AMAZON_BOOK_KGAT_PATH_CONSTRAINTS",
    )
    relations: set[str] = set()
    for pattern in constraints:
        for node in pattern:
            for relation in node:
                if relation not in {None, "[UI-Relation]"}:
                    relations.add(str(relation))
    return relations


def counter_summary(counter: Counter[str]) -> dict[str, Any]:
    total = sum(counter.values())
    return {
        "total": total,
        "unique_values": len(counter),
        "top_values": counter.most_common(10),
        "sentinel_minus_one": counter.get("-1", 0),
        "sentinel_fraction": counter.get("-1", 0) / total if total else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", type=Path, default=CANONICAL_ROOT)
    parser.add_argument("--hopwise-root", type=Path, default=HOPWISE_ROOT)
    parser.add_argument("--summary-json", type=Path, default=OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = read_json(args.canonical_root / "metadata.json")
    manifest = read_json(args.hopwise_root / "hopwise_view_manifest.json")

    canonical_counts = {
        split: timestamp_counts(args.canonical_root / "interactions" / f"{split}.tsv.gz")
        for split in ("train", "valid", "test")
    }
    hopwise_counts = {
        split: hopwise_timestamp_counts(
            args.hopwise_root / f"canonical_amazon_book_kgat_v1.{split}.inter"
        )
        for split in ("train", "valid", "test")
    }
    all_timestamps = Counter()
    for counts in canonical_counts.values():
        all_timestamps.update(counts)

    available_relations = kg_relations(args.hopwise_root / "canonical_amazon_book_kgat_v1.kg")
    required_relations = constrained_relations("canonical_amazon_book_kgat_v1")
    missing_relations = sorted(required_relations - available_relations)

    all_timestamp_values = set(all_timestamps)
    only_sentinel_timestamp = all_timestamp_values == {"-1"}
    formal_temporal_reward_approved = not only_sentinel_timestamp
    status = "PASS" if formal_temporal_reward_approved and not missing_relations else "BLOCKED"

    summary = {
        "dataset": "canonical_amazon_book_kgat_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "formal_temporal_reward_approved": formal_temporal_reward_approved,
        "blocker": (
            "canonical Amazon-book KGAT interactions use sentinel timestamp -1; "
            "TPRec temporal rewards are therefore not semantically valid for formal reporting"
            if only_sentinel_timestamp
            else None
        ),
        "canonical_metadata_timestamp_policy": metadata.get("timestamp_policy"),
        "canonical_timestamp_summary": {
            split: counter_summary(counts)
            for split, counts in canonical_counts.items()
        },
        "hopwise_timestamp_summary": {
            split: counter_summary(counts)
            for split, counts in hopwise_counts.items()
        },
        "hopwise_view": {
            "manifest": str((args.hopwise_root / "hopwise_view_manifest.json").resolve()),
            "status": manifest.get("status"),
            "interactions_preserved": manifest.get("interactions_preserved"),
            "kg_preserved": manifest.get("kg_preserved"),
            "kept_link_rows": manifest.get("kept_link_rows"),
            "dropped_link_rows": manifest.get("dropped_link_rows"),
        },
        "path_constraints": {
            "required_relations": sorted(required_relations),
            "available_relation_count": len(available_relations),
            "missing_relations": missing_relations,
            "relations_present": not missing_relations,
        },
        "interpretation": (
            "Structural TPRec Amazon wiring can be smoke-tested, but a formal "
            "temporal TPRec baseline needs real interaction timestamps or an "
            "explicitly labeled non-temporal ablation protocol."
        ),
    }

    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
