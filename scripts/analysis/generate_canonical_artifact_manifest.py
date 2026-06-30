#!/usr/bin/env python3
"""Generate a compact manifest for canonical native-path report artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables" / "canonical_native_path_artifact_manifest.json"
SMALL_HASH_LIMIT = 50 * 1024 * 1024


CORE_FILES = [
    ROOT / "reports" / "tables" / "canonical_native_path_status_matrix.csv",
    ROOT / "reports" / "tables" / "canonical_native_path_status_matrix.md",
    ROOT / "reports" / "tables" / "canonical_export_validation" / "manifest.json",
    ROOT / "reports" / "tables" / "amazon_classic_port_readiness.json",
    ROOT / "reports" / "tables" / "amazon_classic_port_readiness.md",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_view_metadata.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "preprocessed"
    / "ucpr_view_metadata.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "ucpr_runtime_preprocess_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "ucpr_transe_forward_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "ucpr_amazon_book_kgat_formal_pipeline_status.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "ucpr_amazon_book_kgat_preprocess_validation.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_runtime_preprocess_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_transe_forward_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_transe_training_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_env_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_training_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_inference_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_export_smoke_validation.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_streaming_export_smoke.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_streaming_export_smoke_validation.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pgpr_amazon_book_kgat_formal_pipeline_status.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pgpr_amazon_book_kgat_streaming_export_formal.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pgpr_amazon_book_kgat_export_validation.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pgpr_amazon_book_kgat_accuracy.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pgpr_amazon_book_kgat_preprocess_validation.json",
    ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "amazon_book_kgat_v1"
    / "model_views"
    / "tprec"
    / "tprec_timestamp_semantics_audit.json",
    ROOT / "docs" / "guides" / "CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md",
    ROOT / "docs" / "guides" / "CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md",
    ROOT / "docs" / "guides" / "NATIVE_PATH_IMPLEMENTATION_LOG_2026-06-20.md",
]

CORE_SCRIPTS = [
    ROOT / "scripts" / "analysis" / "regenerate_canonical_native_path_reports.sh",
    ROOT / "scripts" / "analysis" / "generate_native_path_figures.sh",
    ROOT / "scripts" / "analysis" / "generate_canonical_status_matrix.py",
    ROOT / "scripts" / "analysis" / "validate_canonical_export_evidence.py",
    ROOT / "scripts" / "analysis" / "audit_amazon_classic_port_readiness.py",
    ROOT / "scripts" / "analysis" / "generate_canonical_artifact_manifest.py",
    ROOT / "adapters" / "pgpr_adapter.py",
    ROOT / "adapters" / "ucpr_adapter.py",
    ROOT / "scripts" / "data" / "canonical" / "build_pgpr_view.py",
    ROOT / "scripts" / "data" / "canonical" / "build_ucpr_view.py",
    ROOT / "scripts" / "model_patches" / "patch_pgpr_runtime.py",
    ROOT / "scripts" / "model_patches" / "patch_pgpr_amazon_runtime.py",
    ROOT / "scripts" / "model_patches" / "patch_ucpr_amazon_runtime.py",
    ROOT / "scripts" / "validation" / "run_pgpr_amazon_preprocess_smoke.sh",
    ROOT / "scripts" / "validation" / "validate_pgpr_preprocess_smoke.py",
    ROOT / "scripts" / "validation" / "run_pgpr_transe_forward_smoke.py",
    ROOT / "scripts" / "validation" / "run_pgpr_amazon_transe_training_smoke.sh",
    ROOT / "scripts" / "validation" / "validate_pgpr_transe_training_smoke.py",
    ROOT / "scripts" / "validation" / "run_pgpr_policy_env_smoke.py",
    ROOT / "scripts" / "validation" / "run_pgpr_amazon_policy_training_smoke.sh",
    ROOT / "scripts" / "validation" / "validate_pgpr_policy_training_smoke.py",
    ROOT / "scripts" / "validation" / "run_pgpr_policy_inference_smoke.py",
    ROOT / "scripts" / "validation" / "export_pgpr_streaming.py",
    ROOT / "scripts" / "validation" / "run_pgpr_amazon_export_smoke.sh",
    ROOT / "scripts" / "validation" / "run_pgpr_amazon_formal_pipeline.sh",
    ROOT / "scripts" / "validation" / "launch_pgpr_amazon_formal_pipeline.sh",
    ROOT / "scripts" / "validation" / "run_ucpr_amazon_preprocess_smoke.sh",
    ROOT / "scripts" / "validation" / "validate_ucpr_preprocess_smoke.py",
    ROOT / "scripts" / "validation" / "run_ucpr_transe_forward_smoke.py",
    ROOT / "scripts" / "validation" / "export_ucpr_streaming.py",
    ROOT / "scripts" / "validation" / "run_ucpr_amazon_formal_pipeline.sh",
    ROOT / "scripts" / "validation" / "launch_ucpr_amazon_formal_pipeline.sh",
    ROOT / "scripts" / "validation" / "audit_tprec_amazon_timestamp_semantics.py",
    ROOT / "scripts" / "hopwise" / "run_canonical_tprec_pipeline.sh",
    ROOT / "scripts" / "hopwise" / "run_canonical_tprec.py",
    ROOT / "scripts" / "hopwise" / "export_tprec_paths.py",
    ROOT / "scripts" / "hopwise" / "tprec_runtime.py",
]

FIGURE_DIRS = [
    ROOT / "reports" / "figures" / "tradeoff" / "canonical_lastfm_native_paths_v4_six_model",
    ROOT / "reports" / "figures" / "tradeoff" / "canonical_ml1m_native_paths_v2",
]

EXPORT_EVIDENCE_DIR = ROOT / "reports" / "tables" / "canonical_export_validation"


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_entry(path: Path, *, hash_small: bool = True) -> dict[str, Any]:
    stat = path.stat()
    entry: dict[str, Any] = {
        "path": rel(path),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }
    if hash_small and stat.st_size <= SMALL_HASH_LIMIT:
        entry["sha256"] = sha256(path)
    elif hash_small:
        entry["sha256"] = None
        entry["sha256_note"] = f"skipped: file larger than {SMALL_HASH_LIMIT} bytes"
    return entry


def directory_entry(path: Path) -> dict[str, Any]:
    files = [item for item in path.iterdir() if item.is_file()]
    png = [item for item in files if item.suffix == ".png"]
    csv_files = [item for item in files if item.suffix == ".csv"]
    return {
        "path": rel(path),
        "exists": path.exists(),
        "files": len(files),
        "png": len(png),
        "csv": len(csv_files),
        "total_size_bytes": sum(item.stat().st_size for item in files),
    }


def load_status_counts() -> dict[str, int]:
    status_csv = ROOT / "reports" / "tables" / "canonical_native_path_status_matrix.csv"
    rows = list(csv.DictReader(status_csv.open()))
    return {
        "rows": len(rows),
        "complete_rows": sum(row["stage"].startswith("Complete") for row in rows),
        "blocked_rows": sum(row["stage"] == "Blocked" for row in rows),
    }


def load_export_manifest() -> dict[str, Any]:
    path = EXPORT_EVIDENCE_DIR / "manifest.json"
    data = json.loads(path.read_text())
    return {
        "status": data["status"],
        "exports": data["exports"],
    }


def load_readiness() -> dict[str, Any]:
    path = ROOT / "reports" / "tables" / "amazon_classic_port_readiness.json"
    data = json.loads(path.read_text())
    return {
        "status": data["status"],
        "ready_models": data["ready_models"],
        "blocked_models": data["blocked_models"],
    }


def main() -> None:
    missing = [path for path in [*CORE_FILES, *CORE_SCRIPTS] if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required manifest inputs: {[rel(path) for path in missing]}")
    for directory in FIGURE_DIRS:
        if not directory.exists():
            raise FileNotFoundError(directory)

    export_summaries = sorted(
        path
        for path in EXPORT_EVIDENCE_DIR.glob("*.json")
        if path.name not in {"manifest.json", "manifest_subset.json"}
    )
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status_matrix": load_status_counts(),
        "export_validation": load_export_manifest(),
        "amazon_classic_readiness": load_readiness(),
        "core_files": [file_entry(path) for path in CORE_FILES],
        "core_scripts": [file_entry(path) for path in CORE_SCRIPTS],
        "figure_bundles": [directory_entry(path) for path in FIGURE_DIRS],
        "export_validation_summaries": [file_entry(path) for path in export_summaries],
    }

    if report["status_matrix"] != {"rows": 18, "complete_rows": 15, "blocked_rows": 3}:
        raise ValueError(f"Unexpected status matrix counts: {report['status_matrix']}")
    if report["export_validation"] != {"status": "PASS", "exports": 15}:
        raise ValueError(f"Unexpected export validation summary: {report['export_validation']}")
    if len(report["export_validation_summaries"]) != 15:
        raise ValueError(
            "Unexpected export validation summary count: "
            f"{len(report['export_validation_summaries'])}"
        )
    if report["amazon_classic_readiness"]["status"] != "BLOCKED":
        raise ValueError(f"Unexpected Amazon readiness: {report['amazon_classic_readiness']}")
    for bundle in report["figure_bundles"]:
        if bundle["png"] != 12 or bundle["csv"] != 12:
            raise ValueError(f"Unexpected figure bundle counts: {bundle}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {rel(OUT)}")


if __name__ == "__main__":
    main()
