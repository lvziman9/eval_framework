#!/usr/bin/env python3
"""Generate canonical native-path status matrices from current artifacts."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion"
OUT_DIR = ROOT / "reports" / "tables"
OUT_CSV = OUT_DIR / "canonical_native_path_status_matrix.csv"
OUT_MD = OUT_DIR / "canonical_native_path_status_matrix.md"
EXPORT_VALIDATION_DIR = OUT_DIR / "canonical_export_validation"
PGPR_AMAZON_FORMAL_STATUS = RUN / "pgpr_amazon_book_kgat_formal_pipeline_status.json"
UCPR_AMAZON_FORMAL_STATUS = RUN / "ucpr_amazon_book_kgat_formal_pipeline_status.json"


COMPLETE_ROWS = [
    ("LastFM", "PGPR", RUN / "pgpr_lastfm_accuracy.json"),
    ("LastFM", "UCPR", RUN / "ucpr_lastfm_accuracy.json"),
    ("LastFM", "CAFE", RUN / "cafe_lastfm_accuracy.json"),
    ("LastFM", "TPRec", RUN / "tprec_formal" / "canonical_lastfm_v1" / "accuracy.json"),
    ("LastFM", "KGGLM", RUN / "kgglm_formal" / "canonical_lastfm_v1" / "accuracy.json"),
    (
        "LastFM",
        "PEARLM",
        RUN / "pearlm_formal_bestval10" / "canonical_lastfm_v1" / "accuracy.json",
    ),
    ("ML-1M", "PGPR", RUN / "pgpr_ml1m_accuracy.json"),
    ("ML-1M", "UCPR", RUN / "ucpr_ml1m_accuracy.json"),
    ("ML-1M", "CAFE", RUN / "cafe_ml1m_accuracy.json"),
    ("ML-1M", "TPRec", RUN / "tprec_formal" / "canonical_ml1m_v1" / "accuracy.json"),
    ("ML-1M", "KGGLM", RUN / "kgglm_formal" / "canonical_ml1m_v1" / "accuracy.json"),
    (
        "ML-1M",
        "PEARLM",
        RUN / "pearlm_formal_bestval10" / "canonical_ml1m_v1" / "accuracy.json",
    ),
    (
        "Amazon-Book KGAT",
        "KGGLM",
        RUN / "kgglm_formal" / "canonical_amazon_book_kgat_v1" / "accuracy.json",
    ),
    (
        "Amazon-Book KGAT",
        "PEARLM",
        RUN / "pearlm_formal_bestval10" / "canonical_amazon_book_kgat_v1" / "accuracy.json",
    ),
    (
        "Amazon-Book KGAT",
        "PGPR",
        RUN / "pgpr_amazon_book_kgat_accuracy.json",
    ),
]

BLOCKED_ROWS = [
    {
        "dataset": "Amazon-Book KGAT",
        "model": "UCPR",
        "stage": "Blocked",
        "blocker_or_note": "UCPR_AMAZON_DYNAMIC_NOTE",
    },
    {
        "dataset": "Amazon-Book KGAT",
        "model": "CAFE",
        "stage": "Blocked",
        "blocker_or_note": (
            "Needs Amazon schema/data-builder port and compatible UCPR view/"
            "TransE checkpoint"
        ),
    },
    {
        "dataset": "Amazon-Book KGAT",
        "model": "TPRec",
        "stage": "Blocked",
        "blocker_or_note": (
            "Amazon TPRec structural path constraints/runtime entrypoints are wired; "
            "formal temporal TPRec remains blocked because canonical timestamps are sentinel -1"
        ),
    },
]

FIGURE_BUNDLES = {
    "LastFM": ROOT / "reports" / "figures" / "tradeoff" / "canonical_lastfm_native_paths_v4_six_model",
    "ML-1M": ROOT / "reports" / "figures" / "tradeoff" / "canonical_ml1m_native_paths_v2",
}

AMAZON_EXPORT_ROOTS = {
    "KGGLM": RUN / "kgglm_formal" / "canonical_amazon_book_kgat_v1",
    "PEARLM": RUN / "pearlm_formal_bestval10" / "canonical_amazon_book_kgat_v1",
}
PGPR_AMAZON_STREAMING_SUMMARY = RUN / "pgpr_amazon_book_kgat_streaming_export_formal.json"
PGPR_AMAZON_ACCURACY = RUN / "pgpr_amazon_book_kgat_accuracy.json"
PGPR_AMAZON_EXPORT_VALIDATION = RUN / "pgpr_amazon_book_kgat_export_validation.json"
PGPR_AMAZON_PATHS_DIR = (
    ROOT
    / "xrecsys"
    / "paths"
    / "amazon_book_kgat_v1"
    / "agent_topk=pgpr-amazon-formal-e50_a250_beam10-12-1"
)

FIELDNAMES = [
    "dataset",
    "model",
    "stage",
    "users",
    "hr_at_10",
    "ndcg_at_10",
    "precision_at_10",
    "recall_at_10",
    "export_validation",
    "export_evidence",
    "alpha_sweep_figures",
    "primary_evidence",
    "blocker_or_note",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def read_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def figure_status(dataset: str) -> str:
    if dataset == "Amazon-Book KGAT":
        return "N/A"
    directory = FIGURE_BUNDLES[dataset]
    png = len(list(directory.glob("*.png"))) if directory.exists() else 0
    csv_count = len(list(directory.glob("*.csv"))) if directory.exists() else 0
    return "Complete" if png == 12 and csv_count == 12 else f"Incomplete ({png} PNG + {csv_count} CSV)"


def export_summary_path(dataset: str, model: str) -> Path:
    dataset_label = {
        "LastFM": "lastfm",
        "ML-1M": "ml1m",
        "Amazon-Book KGAT": "amazon_book_kgat_v1",
    }[dataset]
    return EXPORT_VALIDATION_DIR / f"{dataset_label}_{model.lower()}.json"


def export_validation_status(dataset: str, model: str, expected_users: int) -> tuple[str, str]:
    path = export_summary_path(dataset, model)
    data = read_json(path)
    if data.get("status") != "PASS":
        raise ValueError(f"{path} is not PASS: {data.get('status')}")
    if int(data["topk_users"]) != expected_users:
        raise ValueError(
            f"{path} topk_users={data['topk_users']} does not match users={expected_users}"
        )
    if int(data["canonical_test_users"]) != expected_users:
        raise ValueError(
            f"{path} canonical_test_users={data['canonical_test_users']} "
            f"does not match users={expected_users}"
        )
    if not data.get("require_all_test_users"):
        raise ValueError(f"{path} was not run with require_all_test_users=true")
    return "PASS", rel(path)


def format_float(value: float | str) -> str:
    if isinstance(value, str):
        return value
    return f"{float(value):.6f}"


def format_int(value: int | str) -> str:
    if isinstance(value, str):
        return value
    return str(int(value))


def md_int(value: str) -> str:
    if value == "N/A":
        return value
    return f"{int(value):,}"


def md_evidence(value: str) -> str:
    if value == "N/A":
        return value
    if value.startswith("Needs ") or value.startswith("Historical ") or value.startswith("Runtime "):
        return value
    return f"`{value}`"


def pgpr_amazon_blocker_note() -> str:
    base = "Amazon PGPR data/preprocess/TransE/policy/export smokes are PASS"
    if not PGPR_AMAZON_FORMAL_STATUS.exists():
        return (
            f"{base}; formal policy run/full-user export/strict accuracy gates "
            "remain before an honest run"
        )
    data = read_json(PGPR_AMAZON_FORMAL_STATUS)
    status = data.get("status", "UNKNOWN")
    stage = data.get("stage", "unknown")
    export = data.get("export", {})
    beam = export.get("beam_topk", [])
    beam_text = "-".join(str(value) for value in beam) if beam else "unknown"
    return (
        f"{base}; formal-v1 pipeline status={status}, stage={stage}, "
        f"beam={beam_text}; strict full-user export/accuracy still pending"
    )


def ucpr_amazon_blocker_note() -> str:
    base = (
        "Amazon UCPR data view, adapter aliases, runtime schema patch, and "
        "preprocess/TransE-forward smokes are PASS"
    )
    if not UCPR_AMAZON_FORMAL_STATUS.exists():
        return f"{base}; formal training/export/accuracy are pending"
    data = read_json(UCPR_AMAZON_FORMAL_STATUS)
    status = data.get("status", "UNKNOWN")
    stage = data.get("stage", "unknown")
    policy = data.get("policy", {})
    policy_run = policy.get("run_name", "unknown")
    policy_batch = policy.get("batch_size", "unknown")
    export = data.get("export", {})
    beam = export.get("beam_topk", [])
    beam_text = "-".join(str(value) for value in beam) if beam else "unknown"
    inference = export.get("run_inference", "unknown")
    return (
        f"{base}; formal training pipeline status={status}, stage={stage}, "
        f"policy={policy_run}, policy_batch={policy_batch}, beam={beam_text}, "
        f"run_inference={inference}; strict full-user export/accuracy still pending"
    )


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for dataset, model, accuracy_path in COMPLETE_ROWS:
        data = read_json(accuracy_path)
        if data.get("status") != "PASS":
            raise ValueError(f"{accuracy_path} is not PASS: {data.get('status')}")
        metrics = data["metrics"]
        stage = "Complete" if dataset == "Amazon-Book KGAT" else "Complete + figures"
        note = ""
        if dataset == "Amazon-Book KGAT":
            note = "Amazon alpha-sweep N/A until approved timestamp/SEP/ETD denominator exists"
        users = int(data["users"])
        export_status, export_evidence = export_validation_status(dataset, model, users)
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "stage": stage,
                "users": format_int(users),
                "hr_at_10": format_float(metrics["hr"]),
                "ndcg_at_10": format_float(metrics["ndcg"]),
                "precision_at_10": format_float(metrics["precision"]),
                "recall_at_10": format_float(metrics["recall"]),
                "export_validation": export_status,
                "export_evidence": export_evidence,
                "alpha_sweep_figures": figure_status(dataset),
                "primary_evidence": rel(accuracy_path),
                "blocker_or_note": note,
            }
        )
    for blocked in BLOCKED_ROWS:
        row = {field: "N/A" for field in FIELDNAMES}
        row.update(blocked)
        if row["blocker_or_note"] == "PGPR_AMAZON_DYNAMIC_NOTE":
            row["blocker_or_note"] = pgpr_amazon_blocker_note()
        elif row["blocker_or_note"] == "UCPR_AMAZON_DYNAMIC_NOTE":
            row["blocker_or_note"] = ucpr_amazon_blocker_note()
        rows.append(row)
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bundle_rows() -> list[tuple[str, str, str, str]]:
    rows = []
    for name, directory in [
        ("LastFM six-model alpha-sweep bundle", FIGURE_BUNDLES["LastFM"]),
        ("ML-1M six-model alpha-sweep bundle", FIGURE_BUNDLES["ML-1M"]),
    ]:
        png = len(list(directory.glob("*.png"))) if directory.exists() else 0
        csv_count = len(list(directory.glob("*.csv"))) if directory.exists() else 0
        status = "Complete" if png == 12 and csv_count == 12 else "Incomplete"
        rows.append((name, status, f"{png} PNG + {csv_count} CSV", rel(directory)))
    for model, root in AMAZON_EXPORT_ROOTS.items():
        shard_count = len(list((root / "path_shards").glob("*.pkl")))
        rows.append(
            (
                f"Amazon {model} native-path export",
                "Complete" if (root / "pipeline.complete").exists() else "Incomplete",
                f"{shard_count:,} shards",
                rel(root),
            )
        )
    pgpr_summary = read_json(PGPR_AMAZON_STREAMING_SUMMARY)
    rows.append(
        (
            "Amazon PGPR native-path export",
            "Complete" if pgpr_summary.get("status") == "PASS" else "Incomplete",
            f"{int(pgpr_summary.get('raw_candidate_rows', 0)):,} rows",
            rel(PGPR_AMAZON_PATHS_DIR),
        )
    )
    return rows


def amazon_comparison_rows() -> list[dict[str, str]]:
    rows = []
    for model, root in AMAZON_EXPORT_ROOTS.items():
        adapter = read_json(root / "adapter.json")
        export_validation = read_json(root / "export_validation.json")
        accuracy = read_json(root / "accuracy.json")
        metrics = accuracy["metrics"]
        coverage = accuracy["recommendation_coverage"]
        rows.append(
            {
                "model": model,
                "users": f"{int(accuracy['users']):,}",
                "raw_paths": f"{int(adapter['raw_paths']):,}",
                "pred_path_rows": f"{int(export_validation['pred_path_rows']):,}",
                "explanations": f"{int(adapter['explanations']):,}",
                "hr": format_float(metrics["hr"]),
                "ndcg": format_float(metrics["ndcg"]),
                "slot_coverage": format_float(coverage["slot_coverage"]),
            }
        )
    pgpr_summary = read_json(PGPR_AMAZON_STREAMING_SUMMARY)
    pgpr_export_validation = read_json(PGPR_AMAZON_EXPORT_VALIDATION)
    pgpr_accuracy = read_json(PGPR_AMAZON_ACCURACY)
    pgpr_metrics = pgpr_accuracy["metrics"]
    pgpr_coverage = pgpr_accuracy["recommendation_coverage"]
    rows.append(
        {
            "model": "PGPR",
            "users": f"{int(pgpr_accuracy['users']):,}",
            "raw_paths": f"{int(pgpr_summary['raw_candidate_rows']):,}",
            "pred_path_rows": f"{int(pgpr_export_validation['pred_path_rows']):,}",
            "explanations": f"{int(pgpr_export_validation['explanations']):,}",
            "hr": format_float(pgpr_metrics["hr"]),
            "ndcg": format_float(pgpr_metrics["ndcg"]),
            "slot_coverage": format_float(pgpr_coverage["slot_coverage"]),
        }
    )
    return rows


def write_markdown(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Canonical Native-Path Status Matrix",
        "",
        f"Generated from current workspace artifacts on `{date.today().isoformat()}` Asia/Singapore.",
        "",
        f"Machine-readable companion: `{rel(OUT_CSV)}`.",
        "",
        "Export validation evidence: `reports/tables/canonical_export_validation/manifest.json`.",
        "The CSV includes per-row `export_evidence` JSON paths.",
        "",
        (
            "Amazon classic-model readiness evidence: "
            "`reports/tables/amazon_classic_port_readiness.json` and "
            "`reports/tables/amazon_classic_port_readiness.md`."
        ),
        "",
        "Artifact manifest: `reports/tables/canonical_native_path_artifact_manifest.json`.",
        "",
        "This table separates three states:",
        "",
        "- `Complete`: formal accuracy/export checks are present and passed.",
        "- `Complete + figures`: formal checks passed and canonical alpha-sweep figures/CSVs are available.",
        "- `Blocked`: not an honest runnable baseline on this dataset until schema/runtime support is added.",
        "",
        "Amazon-book alpha-sweep figures are intentionally marked `N/A`: the dataset has no approved canonical timestamp/SEP/ETD denominator yet.",
        "",
        "| Dataset | Model | Stage | Users | HR@10 | NDCG@10 | Export validation | Alpha-sweep figures | Primary evidence |",
        "|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        users = md_int(row["users"])
        evidence = (
            row["blocker_or_note"]
            if row["stage"] == "Blocked"
            else md_evidence(row["primary_evidence"])
        )
        lines.append(
            "| {dataset} | {model} | {stage} | {users} | {hr} | {ndcg} | {export} | {figures} | {evidence} |".format(
                dataset=row["dataset"],
                model=row["model"],
                stage=row["stage"],
                users=users,
                hr=row["hr_at_10"],
                ndcg=row["ndcg_at_10"],
                export=row["export_validation"],
                figures=row["alpha_sweep_figures"],
                evidence=evidence,
            )
        )

    lines.extend(
        [
            "",
            "## Figure and export bundles",
            "",
            "| Bundle | Status | Files | Evidence |",
            "|---|---:|---:|---|",
        ]
    )
    for bundle, status, files, evidence in bundle_rows():
        lines.append(f"| {bundle} | {status} | {files} | `{evidence}` |")

    lines.extend(
        [
            "",
            "## Amazon formal comparison",
            "",
            "| Model | Users | Raw paths | Pred-path rows | Explanations | HR@10 | NDCG@10 | Slot coverage |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in amazon_comparison_rows():
        lines.append(
            "| {model} | {users} | {raw_paths} | {pred_path_rows} | {explanations} | {hr} | {ndcg} | {slot_coverage} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Amazon classic-port acceptance criteria",
            "",
            "The remaining Amazon UCPR/CAFE/TPRec rows are blocked rather than failed.",
            "A future port should be treated as a schema/runtime task with the following",
            "acceptance gates before any formal comparison is reported.",
            "",
            "Shared gates:",
            "",
            "- define one approved Amazon product/entity/relation projection from",
            "  `canonical_amazon_book_kgat_v1`;",
            "- preserve canonical train/valid/test label semantics and prove remaps back to",
            "  canonical user/item ids;",
            "- produce a smoke export with native paths and `include-all-test-users`",
            "  behavior;",
            "- pass `validate_xrecsys_export.py --require-all-test-users`;",
            "- pass `evaluate_uid_topk.py` with strict full-user coverage, allowing only",
            "  naturally short recommendation lists;",
            "- document whether Amazon alpha-sweeps remain `N/A` or become reportable under",
            "  an approved timestamp/SEP/ETD denominator.",
            "",
            "Model-specific gates:",
            "",
            "| Model | Required porting work before launch |",
            "|---|---|",
            "| UCPR | Amazon data view, adapter book aliases, runtime schema patch, isolated preprocess smoke, and one-batch TransE forward/backward smoke now pass; next run TransE/policy training, native-path export, and strict full-user validation before formal reporting. |",
            "| CAFE | Build on the compatible Amazon UCPR view and UCPR TransE checkpoint; add executable Amazon CAFE schema/metapaths and verify non-empty native path execution. |",
            "| TPRec | Amazon relation-token path constraints, CLI choices, export aliases, and the pipeline case are wired; the default Amazon pipeline stops at the timestamp gate because all canonical timestamps are sentinel `-1`. Formal TPRec needs real timestamps or an explicitly labeled non-temporal ablation protocol. |",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines))


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_markdown(rows)
    print(f"Wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
