#!/usr/bin/env python3
"""Build a Hopwise-compatible view from a canonical RecBole-format view.

Hopwise currently requires every item listed in ``.link`` to occur in at least
one interaction file. Canonical datasets may legitimately retain linked catalog
items with no train/valid/test interactions. This view filters only those link
rows; interactions and KG triples are preserved byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def link_or_copy(source: Path, destination: Path) -> None:
    if destination.exists():
        destination.unlink()
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def interaction_items(path: Path) -> set[str]:
    items: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        item_idx = header.index("item_id:token")
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            items.add(fields[item_idx])
    return items


def main() -> None:
    args = parse_args()
    dataset = args.source_dir.name
    output_dir = args.output_root / dataset
    output_dir.mkdir(parents=True, exist_ok=True)

    active_items: set[str] = set()
    split_rows: dict[str, int] = {}
    for phase in ("train", "valid", "test"):
        source = args.source_dir / f"{dataset}.{phase}.inter"
        destination = output_dir / source.name
        link_or_copy(source, destination)
        phase_items = interaction_items(source)
        active_items.update(phase_items)
        with source.open(encoding="utf-8") as handle:
            split_rows[phase] = sum(1 for _ in handle) - 1

    kg_source = args.source_dir / f"{dataset}.kg"
    link_or_copy(kg_source, output_dir / kg_source.name)

    link_source = args.source_dir / f"{dataset}.link"
    link_destination = output_dir / link_source.name
    kept_links = 0
    dropped_link_count = 0
    dropped_link_examples: list[dict[str, str]] = []
    dropped_report = output_dir / "dropped_inactive_links.tsv"
    dropped_hasher = hashlib.sha256()
    with link_source.open(encoding="utf-8") as source_handle, link_destination.open(
        "w", encoding="utf-8"
    ) as destination_handle, dropped_report.open("w", encoding="utf-8") as dropped_handle:
        header = source_handle.readline()
        destination_handle.write(header)
        dropped_handle.write("item_id\tentity_id\treason\n")
        columns = header.rstrip("\n").split("\t")
        item_idx = columns.index("item_id:token")
        entity_idx = columns.index("entity_id:token")
        for line in source_handle:
            fields = line.rstrip("\n").split("\t")
            if fields[item_idx] in active_items:
                destination_handle.write(line)
                kept_links += 1
            else:
                reason = "item absent from canonical train/valid/test interactions"
                dropped_row = f"{fields[item_idx]}\t{fields[entity_idx]}\t{reason}\n"
                dropped_handle.write(dropped_row)
                dropped_hasher.update(dropped_row.encode("utf-8"))
                dropped_link_count += 1
                if len(dropped_link_examples) < 20:
                    dropped_link_examples.append(
                        {
                            "item_id": fields[item_idx],
                            "entity_id": fields[entity_idx],
                            "reason": reason,
                        }
                    )

    manifest = {
        "status": "PASS",
        "dataset": dataset,
        "source_dir": str(args.source_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "split_rows": split_rows,
        "active_interaction_items": len(active_items),
        "kept_link_rows": kept_links,
        "dropped_link_rows": dropped_link_count,
        "dropped_link_examples": dropped_link_examples,
        "dropped_link_report": str(dropped_report.resolve()),
        "dropped_link_report_sha256": dropped_hasher.hexdigest(),
        "interactions_preserved": True,
        "kg_preserved": True,
    }
    manifest_path = output_dir / "hopwise_view_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
