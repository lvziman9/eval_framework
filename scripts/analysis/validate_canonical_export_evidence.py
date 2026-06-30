#!/usr/bin/env python3
"""Validate canonical native-path xRecSys exports for report evidence."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion"
OUT_DIR = ROOT / "reports" / "tables" / "canonical_export_validation"

sys.path.insert(0, str(ROOT))

from scripts.validation.validate_xrecsys_export import validate  # noqa: E402


EXPORTS = [
    {
        "dataset_label": "lastfm",
        "model": "PGPR",
        "dataset": "lastfm",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "lastfm"
        / "agent_topk=25-50-1-pgpr-canonical-native-score",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "lastfm",
        "model": "UCPR",
        "dataset": "lastfm",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "lastfm"
        / "agent_topk=25-50-1-ucpr-canonical-matched",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "lastfm",
        "model": "CAFE",
        "dataset": "lastfm",
        "paths_dir": ROOT / "xrecsys" / "paths" / "lastfm" / "agent_topk=cafe-canonical-lastfm",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "lastfm",
        "model": "TPRec",
        "dataset": "lastfm",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "lastfm"
        / "agent_topk=tprec-canonical-e50-25-50-1",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "lastfm",
        "model": "KGGLM",
        "dataset": "lastfm",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "lastfm"
        / "agent_topk=kgglm-canonical-p3-f2-h768-l6-b25",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "lastfm",
        "model": "PEARLM",
        "dataset": "lastfm",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "lastfm"
        / "agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25",
        "labels_dir": ROOT
        / "runs"
        / "debug_compare"
        / "2026-04-14_canonical_dataset"
        / "lastfm_v1"
        / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "PGPR",
        "dataset": "ml1m",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "ml1m"
        / "agent_topk=25-50-1-pgpr-canonical-ml1m",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "UCPR",
        "dataset": "ml1m",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "ml1m"
        / "agent_topk=25-50-1-ucpr-canonical-ml1m",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "CAFE",
        "dataset": "ml1m",
        "paths_dir": ROOT / "xrecsys" / "paths" / "ml1m" / "agent_topk=cafe-canonical-ml1m",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "TPRec",
        "dataset": "ml1m",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "ml1m"
        / "agent_topk=tprec-canonical-e50-25-50-1",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "KGGLM",
        "dataset": "ml1m",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "ml1m"
        / "agent_topk=kgglm-canonical-p3-f2-h768-l6-b25",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "ml1m",
        "model": "PEARLM",
        "dataset": "ml1m",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "ml1m"
        / "agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25",
        "labels_dir": RUN / "ml1m_v1" / "labels",
    },
    {
        "dataset_label": "amazon_book_kgat_v1",
        "model": "KGGLM",
        "dataset": "amazon_book_kgat_v1",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "amazon_book_kgat_v1"
        / "agent_topk=kgglm-canonical-p3-f2-h768-l6-b25",
        "labels_dir": RUN / "amazon_book_kgat_v1" / "labels",
    },
    {
        "dataset_label": "amazon_book_kgat_v1",
        "model": "PEARLM",
        "dataset": "amazon_book_kgat_v1",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "amazon_book_kgat_v1"
        / "agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25",
        "labels_dir": RUN / "amazon_book_kgat_v1" / "labels",
    },
    {
        "dataset_label": "amazon_book_kgat_v1",
        "model": "PGPR",
        "dataset": "amazon_book_kgat_v1",
        "paths_dir": ROOT
        / "xrecsys"
        / "paths"
        / "amazon_book_kgat_v1"
        / "agent_topk=pgpr-amazon-formal-e50_a250_beam10-12-1",
        "labels_dir": RUN / "amazon_book_kgat_v1" / "labels",
    },
]


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="DATASET:MODEL",
        help=(
            "Validate only a specific row, e.g. lastfm:PGPR or "
            "amazon_book_kgat_v1:PEARLM. Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available DATASET:MODEL keys and exit.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Build a manifest from existing summary JSONs without revalidating CSV files.",
    )
    return parser.parse_args()


def selected_exports(only: list[str]) -> list[dict]:
    if not only:
        return EXPORTS
    requested = set(only)
    available = {f"{spec['dataset_label']}:{spec['model']}": spec for spec in EXPORTS}
    missing = sorted(requested - set(available))
    if missing:
        raise ValueError(f"Unknown --only selection(s): {missing}; available={sorted(available)}")
    return [available[key] for key in only]


def summary_path(spec: dict) -> Path:
    return OUT_DIR / f"{spec['dataset_label']}_{spec['model'].lower()}.json"


def build_manifest(summaries: list[dict]) -> dict:
    return {
        "status": "PASS",
        "exports": len(summaries),
        "summaries": [
            {
                "dataset_label": item["dataset_label"],
                "model": item["model"],
                "topk_users": item["topk_users"],
                "canonical_test_users": item["canonical_test_users"],
                "pred_path_rows": item["pred_path_rows"],
                "explanations": item["explanations"],
                "summary_json": relative(
                    OUT_DIR / f"{item['dataset_label']}_{item['model'].lower()}.json"
                ),
            }
            for item in summaries
        ],
    }


def main() -> None:
    args = parse_args()
    available = [f"{spec['dataset_label']}:{spec['model']}" for spec in EXPORTS]
    if args.list:
        for key in available:
            print(key)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    specs = selected_exports(args.only)
    if args.manifest_only:
        for spec in specs:
            path = summary_path(spec)
            if not path.exists():
                raise FileNotFoundError(path)
            summaries.append(json.loads(path.read_text()))
        manifest_name = "manifest.json" if not args.only else "manifest_subset.json"
        (OUT_DIR / manifest_name).write_text(
            json.dumps(build_manifest(summaries), indent=2, sort_keys=True) + "\n"
        )
        print(f"Wrote {relative(OUT_DIR / manifest_name)}", flush=True)
        return

    for spec in specs:
        print(
            f"Validating {spec['dataset_label']} {spec['model']} from "
            f"{relative(spec['paths_dir'])}",
            flush=True,
        )
        summary = validate(
            paths_dir=spec["paths_dir"],
            labels_dir=spec["labels_dir"],
            dataset=spec["dataset"],
            topk=10,
            require_all_test_users=True,
        )
        summary.update(
            {
                "dataset_label": spec["dataset_label"],
                "model": spec["model"],
                "paths_dir": relative(spec["paths_dir"]),
                "labels_dir": relative(spec["labels_dir"]),
            }
        )
        output = summary_path(spec)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        summaries.append(summary)
        print(
            f"{spec['dataset_label']} {spec['model']}: "
            f"{summary['status']} topk_users={summary['topk_users']} "
            f"pred_path_rows={summary['pred_path_rows']}",
            flush=True,
        )

    manifest = build_manifest(summaries)
    manifest_name = "manifest.json" if not args.only else "manifest_subset.json"
    (OUT_DIR / manifest_name).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {relative(OUT_DIR / manifest_name)}", flush=True)


if __name__ == "__main__":
    main()
