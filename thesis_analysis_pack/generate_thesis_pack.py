#!/usr/bin/env python3
"""Generate thesis analysis pack files from existing repository artifacts.

This script is read-only with respect to experiment artifacts. It writes only
new analysis markdown files under thesis_analysis_pack/ and generated thesis
figures under reports/figures/thesis_final/.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "thesis_analysis_pack"
FIG_OUT = ROOT / "reports" / "figures" / "thesis_final"

STATUS_CSV = ROOT / "reports" / "tables" / "canonical_native_path_status_matrix.csv"
STATUS_MD = "reports/tables/canonical_native_path_status_matrix.md"
COMPLETION_AUDIT = "docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md"
HANDOFF = "docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md"
ARCH = "docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md"
CANONICAL_STD = "docs/guides/CANONICAL_DATASET_STANDARD.md"
PATH_METRICS = "docs/guides/PATH_METRICS_GUIDE.md"
DATA_PROVENANCE = "docs/guides/DATA_PROVENANCE.md"
MODEL_AUDIT = "docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md"
VALIDATION_MANIFEST = "reports/tables/canonical_export_validation/manifest.json"
AMAZON_READINESS = "reports/tables/amazon_classic_port_readiness.json"
ARTIFACT_MANIFEST = "reports/tables/canonical_native_path_artifact_manifest.json"

MODEL_ORDER = ["PGPR", "UCPR", "CAFE", "TPRec", "KGGLM", "PEARLM"]
DATASET_ORDER = ["LastFM", "ML-1M", "Amazon-Book KGAT"]
METRICS = ["LIR", "SEP", "ETD"]


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def read_status_rows() -> list[dict[str, str]]:
    with STATUS_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path | str) -> dict:
    with (ROOT / path if isinstance(path, str) else path).open() as f:
        return json.load(f)


def write(name: str, text: str) -> None:
    path = PACK / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def fmt(value: str | float | int | None, digits: int = 6) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, str):
        if not value or value == "N/A":
            return "N/A"
        try:
            value = float(value)
        except ValueError:
            return value
    if isinstance(value, float):
        if math.isnan(value):
            return "N/A"
        return f"{value:.{digits}f}"
    return str(value)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return "\n".join(lines)


def completed(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["stage"].startswith("Complete")]


def by_dataset(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["dataset"]].append(row)
    return grouped


def best_by_metric(rows: list[dict[str, str]], dataset: str, metric: str) -> dict[str, str] | None:
    candidates = [
        row for row in rows
        if row["dataset"] == dataset and row["stage"].startswith("Complete") and row[metric] != "N/A"
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row[metric]))


def tradeoff_path(dataset_slug: str, metric: str, rec_metric: str = "ndcg") -> Path:
    if dataset_slug == "lastfm":
        return ROOT / "reports" / "figures" / "tradeoff" / "canonical_lastfm_native_paths_v4_six_model" / f"tradeoff_lastfm_{metric}_{rec_metric}_models.csv"
    if dataset_slug == "ml1m":
        return ROOT / "reports" / "figures" / "tradeoff" / "canonical_ml1m_native_paths_v2" / f"tradeoff_ml1m_{metric}_{rec_metric}_models.csv"
    raise ValueError(dataset_slug)


def read_tradeoff(dataset_slug: str, metric: str, rec_metric: str = "ndcg") -> list[dict[str, str]]:
    path = tradeoff_path(dataset_slug, metric, rec_metric)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def alpha_endpoint_values(dataset_slug: str) -> dict[str, dict[str, tuple[str, str]]]:
    out: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    for metric in METRICS:
        rows = read_tradeoff(dataset_slug, metric, "ndcg")
        by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            by_model[row["model"]].append(row)
        for model, model_rows in by_model.items():
            model_rows = sorted(model_rows, key=lambda row: float(row["alpha"]))
            alpha0 = model_rows[0][metric]
            alpha1 = model_rows[-1][metric]
            out[model][metric] = (alpha0, alpha1)
    return out


def goal1() -> None:
    text = f"""
# Goal 1: Research Positioning

## Goal Number

Goal 1

## Current Task

Extract the dissertation's research positioning from current README, docs, and reports, and frame the work as an evaluation framework dissertation rather than a new recommender-model dissertation.

## Thesis Positioning

The defensible dissertation framing is:

> A canonical evaluation framework for knowledge-graph recommenders with native recommendation paths, designed to compare recommendation accuracy and faithful path-based explainability under a shared dataset, export, and validation contract.

This should not be framed as inventing a new recommender model. The repository evidence repeatedly narrows the project toward evaluation: `README.md` states that the active experiment evaluates accuracy-explainability trade-offs only for KG recommenders with native recommendation paths, while non-path KG recommenders may be accuracy references only. `{ARCH}` makes the same methodological boundary explicit: native path models can receive `NDCG / HR / Recall / Precision` plus `LIR / SEP / ETD`, while non-path models should not receive main explainability scores through post-hoc path recovery.

## Research Questions

1. RQ1: How can a canonical dataset and export contract make native-path KG recommender results comparable across heterogeneous model implementations?
   Evidence: `{CANONICAL_STD}`; `scripts/data/canonical/`; `reports/tables/canonical_export_validation/manifest.json`.
2. RQ2: Under a shared canonical evaluation protocol, how do native-path models differ in top-k recommendation accuracy across LastFM and ML-1M?
   Evidence: `{STATUS_MD}`; `reports/tables/canonical_native_path_status_matrix.csv`.
3. RQ3: What do LIR, SEP, and ETD reveal about explanation quality that is not captured by HR@10 or NDCG@10 alone?
   Evidence: `{PATH_METRICS}`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`.
4. RQ4: What are the practical validation gates needed to distinguish faithful native-path explanations from post-hoc or invalid path artifacts?
   Evidence: `{ARCH}`; `scripts/validation/validate_xrecsys_export.py`; `{VALIDATION_MANIFEST}`.
5. RQ5: Where do larger or less compatible datasets, especially Amazon-Book KGAT, expose the boundary conditions of a native-path evaluation framework?
   Evidence: `{HANDOFF}`; `{AMAZON_READINESS}`; `{STATUS_MD}`.

## Dissertation Contributions

1. A canonical dataset layer that separates model-specific training views from shared canonical `uid/pid`, split, and label semantics.
   Evidence: `{CANONICAL_STD}`; `scripts/data/canonical/build_canonical_dataset.py`; `scripts/data/canonical/build_pgpr_view.py`; `scripts/data/canonical/build_ucpr_view.py`.
2. A native-path export contract requiring `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` for explainability scoring.
   Evidence: `{ARCH}`; `{CANONICAL_STD}`; `scripts/validation/validate_xrecsys_export.py`.
3. A validation-first evaluation protocol that enforces canonical test-user coverage, seen-item exclusion, path endpoint consistency, score ranges, and top-k/explanation agreement before results are reported.
   Evidence: `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`; `{VALIDATION_MANIFEST}`.
4. A cross-model empirical comparison over six reportable native-path models on LastFM and ML-1M, with completed formal rows and figure bundles.
   Evidence: `{STATUS_MD}`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`.
5. A principled separation between faithful native-path explanations and post-hoc explanation recovery.
   Evidence: `README.md`; `{ARCH}`; `{MODEL_AUDIT}`.
6. A transparent boundary-case analysis for Amazon-Book KGAT, distinguishing reportable completed rows from blocked or N/A rows without inventing missing results.
   Evidence: `{COMPLETION_AUDIT}`; `{AMAZON_READINESS}`; `{STATUS_MD}`.

## Key Evidence Paths

- `README.md`
- `{ARCH}`
- `{CANONICAL_STD}`
- `{PATH_METRICS}`
- `{DATA_PROVENANCE}`
- `{MODEL_AUDIT}`
- `{COMPLETION_AUDIT}`
- `{STATUS_MD}`
- `{VALIDATION_MANIFEST}`
- `{AMAZON_READINESS}`

## Next Goal

Goal 2: Dataset audit. Separate main experiment datasets from secondary, blocked, historical, or appendix datasets.
"""
    write("goal_1_research_positioning.md", text)


def dataset_tables(status_rows: list[dict[str, str]]) -> tuple[str, str]:
    grouped = by_dataset(status_rows)
    table_rows = []
    for dataset in DATASET_ORDER:
        rows = grouped.get(dataset, [])
        complete_models = [row["model"] for row in rows if row["stage"].startswith("Complete")]
        blocked_models = [row["model"] for row in rows if row["stage"] == "Blocked"]
        metrics = "HR@10, NDCG@10, Precision@10, Recall@10"
        if dataset == "Amazon-Book KGAT":
            expl = "Accuracy complete for KGGLM/PEARLM/PGPR; LIR/SEP/ETD alpha sweeps N/A"
            role = "Secondary stress-test / boundary dataset"
            limitation = "No approved timestamp/SEP/ETD denominator; UCPR/CAFE/TPRec blocked"
        elif dataset in {"LastFM", "ML-1M"}:
            expl = "Accuracy plus LIR/SEP/ETD alpha-sweep evidence"
            role = "Main experiment dataset"
            limitation = "Use canonical status matrix and trade-off bundles; avoid older duplicate figure folders"
        else:
            expl = "N/A"
            role = "Appendix or historical"
            limitation = "Not current main-line result"
        validation = "PASS for complete rows" if complete_models else "N/A"
        if blocked_models:
            validation += f"; blocked rows: {', '.join(blocked_models)}"
        evidence = f"{STATUS_MD}; {COMPLETION_AUDIT}"
        table_rows.append([
            dataset,
            role,
            ", ".join(complete_models) if complete_models else "N/A",
            f"{metrics}; {expl}",
            validation,
            limitation,
            evidence,
        ])
    table_rows.append([
        "beauty_legacy_v1",
        "Historical/reference or appendix only",
        "Historical CAFE/PGPR references in docs; not a current main result row",
        "Not part of final status matrix",
        "N/A in current canonical native-path status matrix",
        "Compatibility protocol with empty validation split; should not be presented as large Amazon-Book KGAT result",
        f"{CANONICAL_STD}; {MODEL_AUDIT}",
    ])
    table = md_table(
        [
            "Dataset",
            "Role in dissertation",
            "Models available",
            "Metrics available",
            "Validation status",
            "Limitations",
            "Evidence file paths",
        ],
        table_rows,
    )
    audit = f"""
# Goal 2: Dataset and Experiment Scope Audit

## Goal Number

Goal 2

## Current Task

Identify datasets used by the project, separate main experiment datasets from secondary, partial, blocked, or historical datasets, and state how each should be used in the dissertation.

## Key Findings

1. LastFM and ML-1M are the main dissertation datasets. Both have six complete rows in `reports/tables/canonical_native_path_status_matrix.csv`: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
2. Amazon-Book KGAT is useful as a larger native-KG stress test, but it is not a fully symmetric six-model explanation experiment. KGGLM, PEARLM, and PGPR have complete formal accuracy/export rows; UCPR, CAFE, and TPRec remain blocked.
3. Amazon alpha-sweep figures and LIR/SEP/ETD trade-off claims are N/A under the current evidence because no approved timestamp/SEP/ETD denominator exists.
4. Beauty-related artifacts should be treated as historical/reference or appendix material, not as the main Amazon-Book KGAT experiment.
5. The dissertation should not hide blocked rows. Blocked rows are part of the framework evaluation: they show where native-path compatibility, timestamp semantics, or model-specific schema support are required before a fair comparison exists.

## Dataset Summary

{table}

## Suggested Dissertation Use

- Chapter 3: Use all three canonical datasets to explain framework scope, but emphasize canonical LastFM and ML-1M as the complete evaluation design.
- Chapter 4: Use LastFM and ML-1M as the primary empirical accuracy and explanation results. Use Amazon-Book KGAT as a secondary formal comparison for completed rows only.
- Chapter 5: Discuss Amazon-Book KGAT as a boundary case demonstrating validation-first evaluation and honest blocked/N/A handling.
- Appendix: Place historical Beauty or legacy material there if needed for provenance.

## Generated Files

- `thesis_analysis_pack/goal_2_dataset_audit.md`
- `thesis_analysis_pack/dataset_summary_table.md`

## Next Goal

Goal 3: Model and method audit.
"""
    return audit, "# Dataset Summary Table\n\n" + table


def goal2(status_rows: list[dict[str, str]]) -> None:
    audit, table = dataset_tables(status_rows)
    write("goal_2_dataset_audit.md", audit)
    write("dataset_summary_table.md", table)


def model_scope(status_rows: list[dict[str, str]]) -> tuple[str, str]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in status_rows:
        grouped[row["model"]].append(row)

    model_meta = {
        "PGPR": ("Yes", "Native RL/path reasoning baseline; main comparison model", f"{STATUS_MD}; {ARCH}"),
        "UCPR": ("Yes", "Native path baseline on LastFM/ML-1M; Amazon blocked", f"{STATUS_MD}; {AMAZON_READINESS}"),
        "CAFE": ("Yes", "Native path baseline on LastFM/ML-1M; Amazon blocked pending port", f"{STATUS_MD}; {AMAZON_READINESS}"),
        "TPRec": ("Yes where timestamps are valid", "Temporal native-path baseline on LastFM/ML-1M; Amazon blocked by sentinel timestamps", f"{MODEL_AUDIT}; {AMAZON_READINESS}"),
        "KGGLM": ("Yes", "Path-language-model native-path baseline; main comparison model", f"{MODEL_AUDIT}; {STATUS_MD}"),
        "PEARLM": ("Yes", "KG-constrained path-language-model baseline; main comparison model", f"{MODEL_AUDIT}; {STATUS_MD}"),
        "KGIN": ("No native recommendation path", "Accuracy-only reference / optional appendix, not LIR/SEP/ETD", f"README.md; {ARCH}; {MODEL_AUDIT}"),
        "KGAT": ("No native recommendation path in current protocol", "Accuracy-only reference / optional appendix", f"README.md; {ARCH}; {MODEL_AUDIT}"),
        "LightGCN": ("No native KG path", "Accuracy-only reference / optional appendix", f"README.md; {ARCH}; {MODEL_AUDIT}"),
        "TransE": ("No: embedding component", "Training/preprocessing component, not a recommender row", f"{HANDOFF}; {AMAZON_READINESS}"),
    }

    table_rows = []
    for model, (native, role, evidence) in model_meta.items():
        rows = grouped.get(model, [])
        datasets_completed = [row["dataset"] for row in rows if row["stage"].startswith("Complete")]
        accuracy = "Yes" if datasets_completed else "Deferred / N/A"
        expl = "Yes for completed LastFM/ML-1M rows" if model in MODEL_ORDER else "No"
        if model in {"KGGLM", "PEARLM", "PGPR"}:
            expl = "Yes for LastFM/ML-1M; Amazon LIR/SEP/ETD N/A"
        if model in {"UCPR", "CAFE", "TPRec"}:
            expl = "Yes for completed LastFM/ML-1M; blocked on Amazon"
        if model not in MODEL_ORDER:
            datasets_completed = []
        table_rows.append([
            model,
            native,
            ", ".join(datasets_completed) if datasets_completed else "N/A",
            accuracy,
            expl,
            role,
            evidence,
        ])

    table = md_table(
        [
            "Model",
            "Native path available?",
            "Datasets completed",
            "Accuracy metrics available?",
            "Explanation metrics available?",
            "Dissertation role",
            "Evidence file paths",
        ],
        table_rows,
    )
    audit = f"""
# Goal 3: Model and Method Audit

## Goal Number

Goal 3

## Current Task

Identify models represented in the repository, separate native-path models from non-native-path or accuracy-only references, and define each model's dissertation role.

## Key Findings

1. The main comparison set is six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
2. LastFM and ML-1M have complete rows for all six models, with accuracy metrics, export validation, and alpha-sweep figure bundles.
3. Amazon-Book KGAT has complete formal rows only for KGGLM, PEARLM, and PGPR. UCPR, CAFE, and TPRec must be written as blocked/N/A, not missing values to be filled.
4. KGIN, KGAT, LightGCN, MKR, CKE, and RippleNet are discussed in docs as strong non-path or accuracy-only candidates. They should not enter LIR/SEP/ETD comparison unless a faithful native path mechanism is available.
5. TransE appears in logs and validation as an embedding/preprocessing component, not as a final recommender row for dissertation comparison.

## Model Scope Table

{table}

## Dissertation Placement

- Main Chapter 4 comparison: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM on LastFM and ML-1M.
- Secondary boundary comparison: KGGLM, PEARLM, PGPR on Amazon-Book KGAT.
- Limitations or appendix: Amazon UCPR/CAFE/TPRec blocked rows; non-path accuracy-only models.
- Method chapter: model-specific views and adapters rather than model novelty.

## Generated Files

- `thesis_analysis_pack/goal_3_model_audit.md`
- `thesis_analysis_pack/model_scope_table.md`

## Next Goal

Goal 4: Final result file inventory.
"""
    return audit, "# Model Scope Table\n\n" + table


def goal3(status_rows: list[dict[str, str]]) -> None:
    audit, table = model_scope(status_rows)
    write("goal_3_model_audit.md", audit)
    write("model_scope_table.md", table)


def goal4(status_rows: list[dict[str, str]]) -> None:
    rows = []
    rows.append([
        "reports/tables/canonical_native_path_status_matrix.csv",
        "CSV",
        "All",
        "All",
        "Stage, users, HR@10, NDCG@10, Precision@10, Recall@10, validation, evidence paths",
        "Chapter 4 and 5",
        "Primary machine-readable final status table.",
    ])
    rows.append([
        VALIDATION_MANIFEST,
        "JSON",
        "All complete rows",
        "15 complete rows",
        "canonical users, top-k users, pred path rows, explanation rows, status",
        "Chapter 3, 4, and 5",
        "Validation-first evidence; use with per-row JSON summaries.",
    ])
    rows.append([
        AMAZON_READINESS,
        "JSON",
        "Amazon-Book KGAT",
        "PGPR, UCPR, CAFE, TPRec",
        "Readiness checks, blockers, required next steps",
        "Chapter 5 limitations",
        "Use to justify blocked rows; current status is BLOCKED overall with PGPR ready and UCPR/CAFE/TPRec blocked.",
    ])
    for row in status_rows:
        rows.append([
            row["primary_evidence"] if row["primary_evidence"] != "N/A" else "N/A",
            "JSON" if row["primary_evidence"].endswith(".json") else "N/A",
            row["dataset"],
            row["model"],
            "HR@10, NDCG@10, Precision@10, Recall@10" if row["stage"].startswith("Complete") else "N/A",
            "Chapter 4" if row["stage"].startswith("Complete") else "Chapter 5 limitations",
            row["blocker_or_note"] or f"Status: {row['stage']}; validation: {row['export_validation']}",
        ])
        if row["export_evidence"] != "N/A":
            rows.append([
                row["export_evidence"],
                "JSON",
                row["dataset"],
                row["model"],
                "Export validation: canonical users, top-k users, pred paths, explanations",
                "Chapter 3/4 validation",
                "Per-row validation evidence.",
            ])

    rows.extend([
        [
            "reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/",
            "PNG + CSV bundle",
            "LastFM",
            "Six native-path models",
            "LIR/SEP/ETD versus HR/NDCG/Precision/Recall alpha sweeps",
            "Chapter 4 and 5",
            "Canonical figure bundle; prefer over older duplicate LastFM folders.",
        ],
        [
            "reports/figures/tradeoff/canonical_ml1m_native_paths_v2/",
            "PNG + CSV bundle",
            "ML-1M",
            "Six native-path models",
            "LIR/SEP/ETD versus HR/NDCG/Precision/Recall alpha sweeps",
            "Chapter 4 and 5",
            "Canonical figure bundle; prefer over older duplicate ML-1M folders.",
        ],
        [
            "reports/tables/tradeoff_insights/ml1m_canonical_language_model_ndcg_tradeoff_summary.csv",
            "CSV",
            "ML-1M",
            "KGGLM, PEARLM",
            "Language-model trade-off endpoint summary",
            "Appendix or Chapter 5",
            "Useful for language-model-specific discussion; not a replacement for status matrix accuracy.",
        ],
    ])
    table = md_table(
        ["File path", "File type", "Dataset", "Model", "Metrics included", "Can be used in Chapter 4 or Chapter 5?", "Notes / caveats"],
        rows,
    )
    text = f"""
# Goal 4: Final Result File Inventory

## Goal Number

Goal 4

## Current Task

Locate final/canonical/native-path/accuracy/explanation/validation artifacts and explain how each should support the dissertation.

## Inventory

{table}

## Selection Guidance

1. Use `reports/tables/canonical_native_path_status_matrix.csv` as the main index for final rows and evidence paths.
2. Use per-row `accuracy.json` files for strict top-k accuracy values.
3. Use `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` and `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` for explanation trade-off figures and CSVs.
4. Use `reports/tables/canonical_export_validation/manifest.json` and per-row validation JSONs for validation claims.
5. Treat older duplicate figure folders as uncertain unless the dissertation specifically needs historical evolution.
6. Treat Amazon-Book KGAT explanation alpha sweeps as N/A until an approved timestamp/SEP/ETD denominator exists.

## Generated Files

- `thesis_analysis_pack/goal_4_result_file_inventory.md`

## Next Goal

Goal 5: Accuracy result summary.
"""
    write("goal_4_result_file_inventory.md", text)


def goal5(status_rows: list[dict[str, str]]) -> None:
    rows = []
    for row in status_rows:
        rows.append([
            row["dataset"],
            row["model"],
            fmt(row["hr_at_10"]),
            fmt(row["ndcg_at_10"]),
            fmt(row["precision_at_10"]),
            fmt(row["recall_at_10"]),
            row["stage"],
            row["primary_evidence"] if row["primary_evidence"] != "N/A" else row["blocker_or_note"],
        ])
    table = md_table(
        ["Dataset", "Model", "HR@10", "NDCG@10", "Precision@10", "Recall@10", "Status", "Evidence file path"],
        rows,
    )
    best_lines = []
    for dataset in DATASET_ORDER:
        best_hr = best_by_metric(status_rows, dataset, "hr_at_10")
        best_ndcg = best_by_metric(status_rows, dataset, "ndcg_at_10")
        if best_hr:
            best_lines.append(f"- {dataset}: best HR@10 is {best_hr['model']} ({fmt(best_hr['hr_at_10'])}); best NDCG@10 is {best_ndcg['model']} ({fmt(best_ndcg['ndcg_at_10'])}).")
    text = f"""
# Goal 5: Accuracy Result Summary

## Goal Number

Goal 5

## Current Task

Extract existing accuracy metrics for completed dataset-model rows, focusing on HR@10, NDCG@10, Precision@10, and Recall@10. Missing or blocked values remain N/A.

## Final Accuracy Summary

{table}

## Key Accuracy Findings

{chr(10).join(best_lines)}
- Amazon-Book KGAT has complete accuracy rows for KGGLM, PEARLM, and PGPR only; UCPR, CAFE, and TPRec are blocked and must remain N/A.
- Strict accuracy values are taken from the status matrix and the per-row `accuracy.json` evidence paths. They should not be replaced by alpha-sweep CSV metric columns.

## Generated Files

- `thesis_analysis_pack/goal_5_accuracy_summary.md`
- `thesis_analysis_pack/final_accuracy_summary_table.md`

## Next Goal

Goal 6: Explanation metric summary.
"""
    write("goal_5_accuracy_summary.md", text)
    write("final_accuracy_summary_table.md", "# Final Accuracy Summary Table\n\n" + table)


def goal6(status_rows: list[dict[str, str]]) -> None:
    endpoint = {
        "LastFM": alpha_endpoint_values("lastfm"),
        "ML-1M": alpha_endpoint_values("ml1m"),
    }
    rows = []
    for dataset in DATASET_ORDER:
        for model in MODEL_ORDER:
            matching = [r for r in status_rows if r["dataset"] == dataset and r["model"] == model]
            status = matching[0]["stage"] if matching else "N/A"
            if dataset in endpoint and model in endpoint[dataset] and status.startswith("Complete"):
                vals = endpoint[dataset][model]
                lir = f"{fmt(vals['LIR'][0], 4)} -> {fmt(vals['LIR'][1], 4)}"
                sep = f"{fmt(vals['SEP'][0], 4)} -> {fmt(vals['SEP'][1], 4)}"
                etd = f"{fmt(vals['ETD'][0], 4)} -> {fmt(vals['ETD'][1], 4)}"
                evidence = "; ".join([
                    rel(tradeoff_path("lastfm" if dataset == "LastFM" else "ml1m", metric, "ndcg"))
                    for metric in METRICS
                ])
                caveat = "Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values."
                native = "Yes"
            elif dataset == "Amazon-Book KGAT":
                lir = sep = etd = "N/A"
                evidence = STATUS_MD if status == "Blocked" else matching[0]["primary_evidence"]
                caveat = "Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy."
                native = "Yes if complete row; blocked otherwise"
            else:
                lir = sep = etd = "N/A"
                evidence = "N/A"
                caveat = "No current complete explanation evidence."
                native = "N/A"
            rows.append([dataset, model, lir, sep, etd, native, status, evidence, caveat])
    table = md_table(
        ["Dataset", "Model", "LIR", "SEP", "ETD", "Native path?", "Status", "Evidence file path", "Caveat"],
        rows,
    )
    text = f"""
# Goal 6: Explanation Metric Summary

## Goal Number

Goal 6

## Current Task

Summarize LIR, SEP, and ETD from existing result files, define each metric, and mark unavailable or invalid cases honestly.

## Metric Meanings

- LIR, Linked Interaction Recency: measures how recent the path's seed interaction is for the user. Higher values indicate recommendations anchored in more recent user behavior. Evidence: `{PATH_METRICS}`.
- SEP, Serendipity of Explanation Path: measures the low-degree or unusual nature of the bridge entity in the explanation path. Higher values indicate more serendipitous bridge entities. Evidence: `{PATH_METRICS}`.
- ETD, Explanation Type Diversity: measures the diversity of explanation path types across a user's top-k recommendations. Evidence: `{PATH_METRICS}`.

## Final Explanation Summary

{table}

## Key Findings

1. LastFM and ML-1M have complete LIR/SEP/ETD alpha-sweep evidence for all six native-path models.
2. Amazon-Book KGAT has completed native-path exports for KGGLM, PEARLM, and PGPR, but LIR/SEP/ETD alpha-sweep comparisons are N/A under the current evidence because timestamp and denominator semantics are not approved.
3. Blocked Amazon UCPR/CAFE/TPRec rows must not receive post-hoc or invented explanation scores.
4. The alpha-sweep CSVs are useful for accuracy-explainability trade-off analysis, but their `ndcg/hr/precision/recall` columns should not replace the strict accuracy summary from per-row `accuracy.json` files.

## Generated Files

- `thesis_analysis_pack/goal_6_explanation_metric_summary.md`
- `thesis_analysis_pack/final_explanation_summary_table.md`

## Next Goal

Goal 7: Validation and quality-control audit.
"""
    write("goal_6_explanation_metric_summary.md", text)
    write("final_explanation_summary_table.md", "# Final Explanation Summary Table\n\n" + table)


def goal7(status_rows: list[dict[str, str]]) -> None:
    manifest = read_json(VALIDATION_MANIFEST)
    validation_rows = []
    for summary in manifest["summaries"]:
        validation_rows.append([
            summary["dataset_label"],
            summary["model"],
            "PASS",
            str(summary["canonical_test_users"]),
            str(summary["topk_users"]),
            str(summary["pred_path_rows"]),
            str(summary["explanations"]),
            summary["summary_json"],
            "Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script.",
        ])
    for row in status_rows:
        if row["stage"] == "Blocked":
            validation_rows.append([
                row["dataset"],
                row["model"],
                "BLOCKED / N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                AMAZON_READINESS,
                row["blocker_or_note"],
            ])
    table = md_table(
        ["Dataset", "Model", "Validation status", "Canonical test users", "Top-k users", "Pred-path rows", "Explanation rows", "Evidence", "Notes"],
        validation_rows,
    )
    text = f"""
# Goal 7: Validation and Quality-Control Audit

## Goal Number

Goal 7

## Current Task

Find export, canonical, and path validation evidence; summarize passed, blocked, and N/A cases; and explain validation-first evaluation as a dissertation contribution.

## Validation Status Table

{table}

## Validation Gates Evidenced in Repository

- Canonical user coverage: `scripts/validation/validate_xrecsys_export.py` checks that `uid_topk.csv` covers the exact canonical test-user set when `require_all_test_users` is enabled.
- UID/PID endpoint consistency: the same validator parses each path and checks that it starts with the expected user and ends with the expected product type and pid.
- Seen-item leakage: both `validate_xrecsys_export.py` and `evaluate_uid_topk.py` reject training/validation items appearing in recommendations.
- Top-k/explanation consistency: `uid_topk.csv` and `uid_pid_explanation.csv` must contain the same recommended `(uid, pid)` pairs.
- Path score sanity: `pred_paths.csv` `path_score` and `path_prob` must be finite and within the expected range.
- Short-list policy: `evaluate_uid_topk.py` supports explicit short lists while preserving the denominator and counting missing slots as non-hits.

## Why This Matters

Native-path explainability is meaningful only when the path is faithful to the recommendation output and valid under canonical user/item ids. The validation gate is therefore not an implementation detail; it is part of the evaluation framework's research contribution. It prevents invalid path endpoints, missing users, seen-item leakage, and post-hoc explanation substitution from entering Chapter 4/5 claims.

## Generated Files

- `thesis_analysis_pack/goal_7_validation_audit.md`
- `thesis_analysis_pack/validation_status_table.md`

## Next Goal

Goal 8: Existing figure inventory.
"""
    write("goal_7_validation_audit.md", text)
    write("validation_status_table.md", "# Validation Status Table\n\n" + table)


def caption_for_figure(path: Path) -> tuple[str, str, str, str]:
    name = path.name
    dataset = "LastFM" if "lastfm" in name or "lastfm" in str(path) else "ML-1M" if "ml1m" in name or "ml1m" in str(path) else "Mixed/Other"
    chapter = "Chapter 5"
    use = "Use directly"
    reason = "Canonical promoted figure bundle" if "canonical_" in str(path) else "Useful but secondary or historical"
    if "ablation" in str(path):
        chapter = "Appendix"
        use = "Appendix / redraw if used"
        reason = "Ablation artifact outside the main canonical native-path status matrix"
    if "ml1m_tradeoff_insights" in str(path):
        chapter = "Appendix or Chapter 5"
        use = "Use selectively"
        reason = "Insight figure; useful for discussion but not the main status source"
    if "v3" in str(path) or "canonical_lastfm_native_paths/" in str(path) or "canonical_ml1m_native_paths/" in str(path):
        use = "Redraw or avoid unless historical"
        reason = "Older duplicate of canonical v4/v2 bundle"
    metric = "trade-off"
    for token in ["LIR", "SEP", "ETD"]:
        if token in name:
            metric = token
    rec_metric = "NDCG@10" if "ndcg" in name else "HR@10" if "_hr_" in name else "Precision@10" if "precision" in name else "Recall@10" if "recall" in name else "metric"
    caption = f"{dataset} {metric} versus {rec_metric} alpha-sweep comparison across native-path models."
    return dataset, chapter, caption, f"{use}|{reason}"


def goal8() -> None:
    figure_paths = sorted((ROOT / "reports" / "figures").glob("**/*"))
    png_svg = [p for p in figure_paths if p.suffix.lower() in {".png", ".svg"}]
    selected = []
    for p in png_svg:
        s = rel(p)
        if "canonical_lastfm_native_paths_v4_six_model" in s or "canonical_ml1m_native_paths_v2" in s or "ml1m_tradeoff_insights" in s or "ablation/pgpr_ucpr_path_module" in s:
            selected.append(p)
    rows = []
    cap_rows = []
    for p in selected:
        dataset, chapter, caption, use_reason = caption_for_figure(p)
        use, reason = use_reason.split("|", 1)
        rows.append([rel(p), dataset, "Alpha-sweep / trade-off" if "tradeoff" in rel(p) else "Ablation", chapter, caption, use, reason])
        cap_rows.append([rel(p), caption, chapter, reason])
    table = md_table(["Figure file path", "Dataset", "Model / metric", "Suggested chapter", "Suggested caption", "Use directly / redraw / appendix / not recommended", "Reason"], rows)
    cap_table = md_table(["Figure file path", "Thesis-ready caption", "Suggested chapter", "Caveat"], cap_rows)
    text = f"""
# Goal 8: Existing Figure Inventory

## Goal Number

Goal 8

## Current Task

Find dissertation-relevant figures, especially trade-off, accuracy, and status-matrix figures, and suggest where each should be used.

## Figure Inventory

{table}

## Key Guidance

1. Prefer `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` for LastFM because it is the latest six-model canonical bundle named in the completion audit.
2. Prefer `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` for ML-1M because it is the latest six-model canonical bundle named in the completion audit.
3. Use older canonical folders only if discussing historical evolution; otherwise mark them as duplicate/uncertain.
4. Use ablation figures in appendix unless the dissertation adds a dedicated ablation subsection.
5. Amazon-Book KGAT needs newly generated accuracy/status figures rather than explanation alpha-sweep figures.

## Generated Files

- `thesis_analysis_pack/goal_8_figure_inventory.md`
- `thesis_analysis_pack/figure_caption_suggestions.md`

## Next Goal

Goal 9: Generate thesis-ready figures from existing results.
"""
    write("goal_8_figure_inventory.md", text)
    write("figure_caption_suggestions.md", "# Figure Caption Suggestions\n\n" + cap_table)


def load_metric_series(path: Path) -> dict[str, list[tuple[float, float, float]]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    rec_col = [c for c in rows[0] if c not in {"model", "alpha"}][0]
    exp_col = [c for c in rows[0] if c not in {"model", "alpha", rec_col}][0]
    series: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for row in rows:
        series[row["model"]].append((float(row["alpha"]), float(row[rec_col]), float(row[exp_col])))
    return series


def generate_figures(status_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont

    created: list[dict[str, str]] = []
    colors = {
        "PGPR": (47, 107, 154),
        "UCPR": (217, 95, 2),
        "CAFE": (27, 158, 119),
        "TPRec": (117, 112, 179),
        "KGGLM": (231, 41, 138),
        "PEARLM": (102, 166, 30),
    }

    def font(size: int, bold: bool = False):
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        for candidate in candidates:
            p = Path(candidate)
            if p.exists():
                return ImageFont.truetype(str(p), size)
        return ImageFont.load_default()

    FONT_TITLE = font(28, True)
    FONT_SUBTITLE = font(20, True)
    FONT = font(17)
    FONT_SMALL = font(14)
    FONT_TINY = font(12)

    def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
        if hasattr(draw, "textbbox"):
            box = draw.textbbox((0, 0), text, font=fnt)
            return box[2] - box[0], box[3] - box[1]
        return draw.textsize(text, font=fnt)

    def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt, fill=(30, 30, 30)) -> None:
        w, h = text_size(draw, text, fnt)
        draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=fnt, fill=fill)

    def new_canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        image = Image.new("RGB", (width, height), "white")
        return image, ImageDraw.Draw(image)

    def draw_axes(
        draw: ImageDraw.ImageDraw,
        left: int,
        top: int,
        right: int,
        bottom: int,
        y_max: float,
        y_label: str = "Metric value",
    ) -> None:
        axis = (40, 40, 40)
        grid = (220, 224, 228)
        draw.line((left, top, left, bottom), fill=axis, width=2)
        draw.line((left, bottom, right, bottom), fill=axis, width=2)
        for i in range(6):
            value = y_max * i / 5
            y = bottom - (bottom - top) * i / 5
            draw.line((left, y, right, y), fill=grid, width=1)
            draw.text((left - 72, y - 8), f"{value:.3f}", font=FONT_TINY, fill=(60, 60, 60))
        draw.text((left - 90, top - 30), y_label, font=FONT_SMALL, fill=(60, 60, 60))

    def fig_accuracy(dataset: str, filename: str) -> None:
        rows = [r for r in status_rows if r["dataset"] == dataset and r["stage"].startswith("Complete")]
        labels = [r["model"] for r in rows]
        hr = [float(r["hr_at_10"]) for r in rows]
        ndcg = [float(r["ndcg_at_10"]) for r in rows]
        width, height = 1200, 760
        left, top, right, bottom = 110, 105, 1140, 610
        image, draw = new_canvas(width, height)
        draw.text((left, 35), f"{dataset} accuracy comparison", font=FONT_TITLE, fill=(30, 30, 30))
        draw_axes(draw, left, top, right, bottom, max(hr + ndcg) * 1.18)
        group_w = (right - left) / max(1, len(labels))
        bar_w = group_w * 0.28
        y_max = max(hr + ndcg) * 1.18
        for i, label in enumerate(labels):
            cx = left + group_w * (i + 0.5)
            for j, (value, color, metric_label) in enumerate([
                (hr[i], (68, 119, 170), "HR@10"),
                (ndcg[i], (204, 102, 119), "NDCG@10"),
            ]):
                x0 = cx + (j - 1) * bar_w
                x1 = x0 + bar_w
                y0 = bottom - (value / y_max) * (bottom - top)
                draw.rectangle((x0, y0, x1, bottom), fill=color)
                centered(draw, ((x0 + x1) / 2, y0 - 12), f"{value:.3f}", FONT_TINY)
            centered(draw, (cx, bottom + 28), label, FONT_SMALL)
        legend_x = right - 230
        for k, (metric_label, color) in enumerate([("HR@10", (68, 119, 170)), ("NDCG@10", (204, 102, 119))]):
            y = top - 42 + k * 24
            draw.rectangle((legend_x, y, legend_x + 20, y + 14), fill=color)
            draw.text((legend_x + 28, y - 2), metric_label, font=FONT_SMALL, fill=(40, 40, 40))
        out = FIG_OUT / filename
        image.save(out)
        created.append({
            "path": rel(out),
            "source": "reports/tables/canonical_native_path_status_matrix.csv",
            "chapter": "Chapter 4",
            "caption": f"{dataset} HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol.",
            "caveat": "Accuracy values come from strict per-row accuracy evidence indexed by the status matrix.",
        })

    fig_accuracy("LastFM", "lastfm_accuracy_hr_ndcg.png")
    fig_accuracy("ML-1M", "ml1m_accuracy_hr_ndcg.png")
    fig_accuracy("Amazon-Book KGAT", "amazon_book_accuracy_hr_ndcg.png")

    width, height = 1500, 900
    image, draw = new_canvas(width, height)
    draw.text((60, 25), "Explanation metric endpoints from NDCG alpha sweeps", font=FONT_TITLE, fill=(30, 30, 30))
    panel_w, panel_h = 440, 335
    start_x, start_y = 70, 105
    for row_idx, dataset_slug in enumerate(["lastfm", "ml1m"]):
        dataset_name = "LastFM" if dataset_slug == "lastfm" else "ML-1M"
        endpoints = alpha_endpoint_values(dataset_slug)
        for col_idx, metric in enumerate(METRICS):
            px = start_x + col_idx * (panel_w + 30)
            py = start_y + row_idx * (panel_h + 70)
            left, top, right, bottom = px + 55, py + 45, px + panel_w - 10, py + panel_h - 55
            labels = [m for m in MODEL_ORDER if m in endpoints]
            alpha0 = [float(endpoints[m][metric][0]) for m in labels]
            alpha1 = [float(endpoints[m][metric][1]) for m in labels]
            y_max = max(alpha0 + alpha1) * 1.12 if max(alpha0 + alpha1) > 0 else 1
            draw.text((px, py), f"{dataset_name} {metric}", font=FONT_SUBTITLE, fill=(30, 30, 30))
            draw_axes(draw, left, top, right, bottom, y_max, "")
            gap = (right - left) / max(1, len(labels) - 1)
            for i, label in enumerate(labels):
                x = left + gap * i if len(labels) > 1 else (left + right) / 2
                y0 = bottom - (alpha0[i] / y_max) * (bottom - top)
                y1 = bottom - (alpha1[i] / y_max) * (bottom - top)
                draw.line((x, y0, x, y1), fill=(150, 150, 150), width=2)
                draw.ellipse((x - 5, y0 - 5, x + 5, y0 + 5), fill=(51, 34, 136))
                draw.ellipse((x - 5, y1 - 5, x + 5, y1 + 5), fill=(170, 68, 153))
                centered(draw, (x, bottom + 20), label, FONT_TINY)
    draw.ellipse((1180, 58, 1192, 70), fill=(51, 34, 136))
    draw.text((1200, 54), "alpha=0", font=FONT_SMALL, fill=(40, 40, 40))
    draw.ellipse((1280, 58, 1292, 70), fill=(170, 68, 153))
    draw.text((1300, 54), "alpha=1", font=FONT_SMALL, fill=(40, 40, 40))
    out = FIG_OUT / "explanation_metric_alpha_endpoints.png"
    image.save(out)
    created.append({
        "path": rel(out),
        "source": "reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/*_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/*_ndcg_models.csv",
        "chapter": "Chapter 5",
        "caption": "Endpoint comparison of LIR, SEP, and ETD at alpha=0 and alpha=1 for LastFM and ML-1M native-path models.",
        "caveat": "Endpoint values come from alpha-sweep CSVs and should be interpreted as trade-off evidence, not strict standalone accuracy.",
    })

    width, height = 1500, 780
    image, draw = new_canvas(width, height)
    draw.text((60, 25), "LIR and NDCG trade-off curves", font=FONT_TITLE, fill=(30, 30, 30))
    for panel, (dataset_slug, dataset_name) in enumerate([("lastfm", "LastFM"), ("ml1m", "ML-1M")]):
        px = 70 + panel * 720
        py = 100
        left, top, right, bottom = px + 80, py + 45, px + 650, py + 430
        series = load_metric_series(tradeoff_path(dataset_slug, "LIR", "ndcg"))
        all_points = [point for points in series.values() for point in points]
        min_x = min(p[2] for p in all_points)
        max_x = max(p[2] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)
        if max_x == min_x:
            max_x = min_x + 1
        if max_y == min_y:
            max_y = min_y + 1
        draw.text((px, py), f"{dataset_name}: LIR vs NDCG sweep metric", font=FONT_SUBTITLE, fill=(30, 30, 30))
        draw.line((left, top, left, bottom), fill=(40, 40, 40), width=2)
        draw.line((left, bottom, right, bottom), fill=(40, 40, 40), width=2)
        for i in range(5):
            y = bottom - (bottom - top) * i / 4
            value = min_y + (max_y - min_y) * i / 4
            draw.line((left, y, right, y), fill=(220, 224, 228), width=1)
            draw.text((left - 70, y - 8), f"{value:.3f}", font=FONT_TINY, fill=(60, 60, 60))
        for i in range(5):
            x = left + (right - left) * i / 4
            value = min_x + (max_x - min_x) * i / 4
            x_fmt = f"{value:.3f}" if max_x < 0.1 else f"{value:.2f}"
            draw.text((x - 20, bottom + 18), x_fmt, font=FONT_TINY, fill=(60, 60, 60))
        draw.text((left, bottom + 45), "LIR", font=FONT_SMALL, fill=(60, 60, 60))
        draw.text((left - 75, top - 28), "NDCG", font=FONT_SMALL, fill=(60, 60, 60))
        for model in MODEL_ORDER:
            if model not in series:
                continue
            points = sorted(series[model], key=lambda t: t[0])
            coords = []
            for _, rec, exp in points:
                x = left + (exp - min_x) / (max_x - min_x) * (right - left)
                y = bottom - (rec - min_y) / (max_y - min_y) * (bottom - top)
                coords.append((x, y))
            color = colors.get(model, (80, 80, 80))
            if len(coords) > 1:
                draw.line(coords, fill=color, width=2)
            for x, y in coords[::4]:
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
            lx = px + 470
            ly = py + 470 + MODEL_ORDER.index(model) * 20
            draw.rectangle((lx, ly, lx + 16, ly + 10), fill=color)
            draw.text((lx + 22, ly - 4), model, font=FONT_TINY, fill=(40, 40, 40))
    out = FIG_OUT / "lir_ndcg_tradeoff_lastfm_ml1m.png"
    image.save(out)
    created.append({
        "path": rel(out),
        "source": f"{rel(tradeoff_path('lastfm', 'LIR', 'ndcg'))}; {rel(tradeoff_path('ml1m', 'LIR', 'ndcg'))}",
        "chapter": "Chapter 5",
        "caption": "Accuracy-explainability trade-off curves showing LIR against the NDCG sweep metric on LastFM and ML-1M.",
        "caveat": "Use as trade-off evidence; strict accuracy is reported separately from per-row accuracy JSON files.",
    })

    grid = []
    for dataset in DATASET_ORDER:
        row = []
        for model in MODEL_ORDER:
            match = [r for r in status_rows if r["dataset"] == dataset and r["model"] == model]
            if not match:
                row.append(0)
            elif match[0]["stage"].startswith("Complete"):
                row.append(2)
            elif match[0]["stage"] == "Blocked":
                row.append(1)
            else:
                row.append(0)
        grid.append(row)
    width, height = 1200, 520
    image, draw = new_canvas(width, height)
    draw.text((60, 35), "Canonical native-path experiment status matrix", font=FONT_TITLE, fill=(30, 30, 30))
    left, top = 230, 130
    cell_w, cell_h = 145, 82
    status_colors = {
        0: (238, 238, 238),
        1: (221, 204, 119),
        2: (17, 119, 51),
    }
    for j, model in enumerate(MODEL_ORDER):
        centered(draw, (left + j * cell_w + cell_w / 2, top - 28), model, FONT_SMALL)
    for i, dataset in enumerate(DATASET_ORDER):
        draw.text((40, top + i * cell_h + 28), dataset, font=FONT_SMALL, fill=(40, 40, 40))
        for j, model in enumerate(MODEL_ORDER):
            value = grid[i][j]
            label = "Complete" if value == 2 else "Blocked" if value == 1 else "N/A"
            x0 = left + j * cell_w
            y0 = top + i * cell_h
            draw.rectangle((x0, y0, x0 + cell_w - 4, y0 + cell_h - 4), fill=status_colors[value], outline=(255, 255, 255), width=2)
            centered(draw, (x0 + cell_w / 2 - 2, y0 + cell_h / 2 - 2), label, FONT_TINY, fill=(255, 255, 255) if value == 2 else (30, 30, 30))
    legend_y = top + len(DATASET_ORDER) * cell_h + 35
    for k, (label, value) in enumerate([("Complete", 2), ("Blocked", 1), ("N/A", 0)]):
        x = left + k * 170
        draw.rectangle((x, legend_y, x + 22, legend_y + 16), fill=status_colors[value])
        draw.text((x + 32, legend_y - 2), label, font=FONT_SMALL, fill=(40, 40, 40))
    out = FIG_OUT / "experiment_status_matrix.png"
    image.save(out)
    created.append({
        "path": rel(out),
        "source": "reports/tables/canonical_native_path_status_matrix.csv",
        "chapter": "Chapter 4 or Chapter 5",
        "caption": "Status matrix for canonical native-path experiments, separating complete rows from blocked Amazon-Book KGAT rows.",
        "caveat": "Blocked means not honestly reportable under the current validation and model-support gates.",
    })
    return created


def goal9(status_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    created = generate_figures(status_rows)
    table = md_table(
        ["Generated figure", "Data source", "Recommended chapter", "Caption", "Caveat"],
        [[c["path"], c["source"], c["chapter"], c["caption"], c["caveat"]] for c in created],
    )
    text = f"""
# Generated Figure Captions

## Goal 9: Thesis-Ready Figures

All figures below were generated from existing CSV/JSON/MD result files. No training, model export, checkpoint writing, or evaluation pipeline mutation was performed.

{table}

## Metrics

- HR@10: whether at least one relevant test item appears in the top-10 recommendation list.
- NDCG@10: rank-sensitive recommendation quality against canonical test labels.
- LIR: recency of the path's linked historical interaction.
- SEP: serendipity/low-degree quality of the bridge entity.
- ETD: diversity of explanation path types in top-k recommendations.

## Caveat

Generated accuracy figures use strict status-matrix accuracy values. Generated explanation/trade-off figures use alpha-sweep CSVs and should be interpreted as trade-off evidence rather than replacements for strict accuracy JSON values.
"""
    write("generated_figure_captions.md", text)
    return created


def goal10(status_rows: list[dict[str, str]], created_figures: list[dict[str, str]]) -> None:
    best_lastfm_hr = best_by_metric(status_rows, "LastFM", "hr_at_10")
    best_lastfm_ndcg = best_by_metric(status_rows, "LastFM", "ndcg_at_10")
    best_ml1m_hr = best_by_metric(status_rows, "ML-1M", "hr_at_10")
    best_ml1m_ndcg = best_by_metric(status_rows, "ML-1M", "ndcg_at_10")
    best_amz_hr = best_by_metric(status_rows, "Amazon-Book KGAT", "hr_at_10")
    insights = [
        (
            "Validation is an experimental outcome, not just a preprocessing step",
            "The current framework reports 15 complete rows and 3 blocked Amazon rows, showing that validation determines what can be claimed.",
            f"`{STATUS_MD}`; `{VALIDATION_MANIFEST}`; `{AMAZON_READINESS}`",
            "`thesis_analysis_pack/validation_status_table.md`; `reports/figures/thesis_final/experiment_status_matrix.png`",
            "5.1 Validation of the Canonical Evaluation Pipeline",
            "Blocked does not mean failed accuracy; it means the model/dataset pair has not passed the required native-path support and validation gates.",
        ),
        (
            "Best accuracy is dataset-dependent",
            f"On LastFM, best HR@10 is {best_lastfm_hr['model']} ({fmt(best_lastfm_hr['hr_at_10'])}) while best NDCG@10 is {best_lastfm_ndcg['model']} ({fmt(best_lastfm_ndcg['ndcg_at_10'])}); on ML-1M, {best_ml1m_hr['model']} leads HR@10 ({fmt(best_ml1m_hr['hr_at_10'])}) and {best_ml1m_ndcg['model']} leads NDCG@10 ({fmt(best_ml1m_ndcg['ndcg_at_10'])}).",
            "`reports/tables/canonical_native_path_status_matrix.csv`",
            "`reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`",
            "5.2 Accuracy Comparison Across Native-Path Models",
            "Do not generalize one model's ranking across all datasets.",
        ),
        (
            "Amazon-Book KGAT behaves as a stress test",
            f"Among completed Amazon rows, {best_amz_hr['model']} has the highest HR@10 ({fmt(best_amz_hr['hr_at_10'])}); UCPR, CAFE, and TPRec remain blocked or N/A.",
            f"`{STATUS_MD}`; `{AMAZON_READINESS}`",
            "`reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/experiment_status_matrix.png`",
            "5.5 Boundary Case and Limitations: Amazon-Book",
            "Amazon explanation alpha sweeps are not reportable under the current evidence.",
        ),
        (
            "Native-path fidelity changes the model comparison boundary",
            "The repository excludes post-hoc path recovery from main LIR/SEP/ETD scoring and uses non-path models only as accuracy references.",
            f"`README.md`; `{ARCH}`; `{MODEL_AUDIT}`",
            "`thesis_analysis_pack/model_scope_table.md`",
            "5.3 Explanation Quality Analysis",
            "This narrows the model universe but makes explanation scores more faithful.",
        ),
        (
            "LIR, SEP, and ETD capture different explanation dimensions",
            "The metric guide defines recency, bridge-entity serendipity, and path-type diversity separately, and the alpha-sweep CSVs report separate curves for each metric.",
            f"`{PATH_METRICS}`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`",
            "`reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`",
            "5.3 Explanation Quality Analysis",
            "A high value on one explanation metric should not be described as overall explainability superiority.",
        ),
        (
            "Accuracy and explanation quality are not reducible to one metric",
            "Alpha-sweep bundles show explanation metrics changing as alpha changes, while accuracy metrics must be interpreted separately.",
            "`reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`; canonical trade-off CSVs",
            "`reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`",
            "5.4 Accuracy-Explainability Trade-off",
            "Strict accuracy JSON values and alpha-sweep CSV metric columns use different evidence roles.",
        ),
        (
            "Canonical IDs and model-specific views solve an unfair-comparison problem",
            "The canonical dataset standard allows models to remap internally while requiring all exported recommendations and paths to return to canonical uid/pid.",
            f"`{CANONICAL_STD}`; `scripts/data/canonical/`; `scripts/validation/validate_xrecsys_export.py`",
            "`thesis_analysis_pack/goal_12_chapter_3_material_pack.md`",
            "5.1 Validation of the Canonical Evaluation Pipeline",
            "The framework standardizes the comparison contract, not every internal KG representation.",
        ),
        (
            "Short native-path recommendation lists are a valid framework condition",
            "The evaluator preserves short and empty lists, counts missing slots as non-hits, and reports slot coverage rather than filling with non-path recommendations.",
            f"`{CANONICAL_STD}`; `scripts/validation/evaluate_uid_topk.py`; per-row accuracy JSON files",
            "`thesis_analysis_pack/final_accuracy_summary_table.md`",
            "5.1 Validation of the Canonical Evaluation Pipeline",
            "Short-list handling should be described as native-path candidate exhaustion, not as a post-hoc padding problem.",
        ),
    ]
    blocks = []
    for title, claim, evidence, fig, subsection, caveat in insights:
        blocks.append(f"""## {title}

- Claim: {claim}
- Supporting evidence: {evidence}
- Suggested figure/table: {fig}
- Dissertation interpretation: Place in {subsection}.
- Caveat: {caveat}
- Evidence file paths: {evidence}
""")
    text = "# Goal 10: Chapter 5 Insight Notes\n\n" + "\n".join(blocks)
    write("goal_10_insight_notes.md", text)


def goal11() -> None:
    text = f"""
# Goal 11: Chapter 5 Material Pack

## 5.1 Validation of the Canonical Evaluation Pipeline

Core claim: The framework's first contribution is not simply producing scores, but deciding which model/dataset outputs are valid enough to score.

Use:
- Table: `thesis_analysis_pack/validation_status_table.md`
- Figure: `reports/figures/thesis_final/experiment_status_matrix.png`
- Evidence: `{VALIDATION_MANIFEST}`; `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`

Caveat: Blocked rows should be interpreted as validation outcomes, not failed recommender performance.

## 5.2 Accuracy Comparison Across Native-Path Models

Core claim: LastFM and ML-1M provide the main complete six-model accuracy comparison, while Amazon-Book KGAT provides a partial stress-test comparison.

Use:
- Table: `thesis_analysis_pack/final_accuracy_summary_table.md`
- Figures: `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png`
- Evidence: `reports/tables/canonical_native_path_status_matrix.csv`

Caveat: Do not rank blocked Amazon rows.

## 5.3 Explanation Quality Analysis

Core claim: LIR, SEP, and ETD measure different properties of faithful native paths and should be discussed as complementary dimensions.

Use:
- Table: `thesis_analysis_pack/final_explanation_summary_table.md`
- Figure: `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`
- Evidence: `{PATH_METRICS}`; canonical LastFM and ML-1M trade-off CSV bundles.

Caveat: Amazon explanation metrics are N/A under current evidence.

## 5.4 Accuracy-Explainability Trade-off

Core claim: The framework supports alpha-sweep analysis showing how explanation objectives can alter ranking metrics and path properties.

Use:
- Figure: `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`
- Existing figures: `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`
- Evidence: alpha-sweep CSVs in those folders.

Caveat: The alpha-sweep metric columns are trade-off evidence, not replacements for strict accuracy JSON values.

## 5.5 Boundary Case and Limitations: Amazon-Book

Core claim: Amazon-Book KGAT demonstrates the limits of native-path evaluation when model support, timestamps, and explanation denominators are not uniformly available.

Use:
- Table: `thesis_analysis_pack/dataset_summary_table.md`
- Figure: `reports/figures/thesis_final/experiment_status_matrix.png`
- Evidence: `{AMAZON_READINESS}`; `{HANDOFF}`; `{STATUS_MD}`

Caveat: Present Amazon as a boundary/stress test, not as a complete six-model explanation experiment.
"""
    write("goal_11_chapter_5_material_pack.md", text)


def goal12() -> None:
    text = f"""
# Goal 12: Chapter 3 Method Material Pack

## 3.1 Overview of the Canonical Evaluation Framework

The framework evaluates native-path KG recommenders by separating canonical dataset truth, model-specific training views, canonical exports, validation gates, and xrecsys metrics. Evidence: `{ARCH}`; `{CANONICAL_STD}`.

## 3.2 Canonical Dataset Layer

A canonical dataset defines model-independent user ids, product ids, train/valid/test interactions, labels, KG source assets, and output mapping requirements. Evidence: `{CANONICAL_STD}`.

Key writing point: the canonical layer standardizes the comparison contract, not every internal graph representation.

## 3.3 Model-Specific Views and ID Remapping

Models may use compact or reordered internal ids, but exported recommendations and paths must map back to canonical `uid/pid`. Evidence: `{CANONICAL_STD}`; `scripts/data/canonical/build_pgpr_view.py`; `scripts/data/canonical/build_ucpr_view.py`; `scripts/hopwise/build_canonical_hopwise_view.py`.

## 3.4 Native-Path Output Contract

Native-path models must export:

- `uid_topk.csv`
- `pred_paths.csv`
- `uid_pid_explanation.csv`

Non-path models only need `uid_topk.csv` and should not receive LIR/SEP/ETD scores. Evidence: `{ARCH}`; `scripts/validation/validate_xrecsys_export.py`.

## 3.5 Accuracy and Explanation Metrics

Accuracy metrics: HR@10, NDCG@10, Precision@10, Recall@10. Evidence: `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_native_path_status_matrix.csv`.

Explanation metrics:

- LIR: linked interaction recency
- SEP: serendipity of explanation path
- ETD: explanation type diversity

Evidence: `{PATH_METRICS}`; `xrecsys/metrics.py`.

## 3.6 Validation-First Evaluation

Before a result is reportable, validation checks canonical test-user coverage, duplicate top-k items, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate path consistency, and score ranges. Evidence: `scripts/validation/validate_xrecsys_export.py`; `{VALIDATION_MANIFEST}`.

## 3.7 Reproducibility Design

The status matrix, export-validation manifest, Amazon readiness audit, and artifact manifest are generated reports. Evidence: `scripts/analysis/regenerate_canonical_native_path_reports.sh`; `{ARTIFACT_MANIFEST}`.

## Framework Diagram Text Description

Suggested diagram flow:

1. Raw/preprocessed dataset and KG sources.
2. Canonical dataset layer with shared `uid`, `pid`, splits, labels, and KG provenance.
3. Model-specific views for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
4. Native model training/inference outside the thesis analysis pack.
5. Canonical export contract: `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv`.
6. Validation gate: user coverage, id consistency, path endpoint consistency, leakage checks, top-k/explanation consistency.
7. Evaluation metrics: HR@10, NDCG@10, Precision@10, Recall@10, LIR, SEP, ETD.
8. Report layer: status matrix, accuracy table, explanation table, trade-off figures, limitations.

## Evidence Paths

- `{ARCH}`
- `{CANONICAL_STD}`
- `{PATH_METRICS}`
- `{DATA_PROVENANCE}`
- `scripts/validation/validate_xrecsys_export.py`
- `scripts/validation/evaluate_uid_topk.py`
- `{VALIDATION_MANIFEST}`
- `{ARTIFACT_MANIFEST}`
"""
    write("goal_12_chapter_3_material_pack.md", text)


def goal13() -> None:
    limitations = [
        [
            "Amazon-Book KGAT is partial, not a complete six-model explanation experiment",
            "Only KGGLM, PEARLM, and PGPR have complete formal rows; UCPR/CAFE/TPRec are blocked.",
            "Frame Amazon as a boundary/stress test for the framework.",
            f"{STATUS_MD}; {AMAZON_READINESS}",
            "Port UCPR/CAFE safely and resolve TPRec timestamp protocol before formal reporting.",
        ],
        [
            "Amazon explanation alpha sweeps are N/A",
            "Current docs state no approved timestamp/SEP/ETD denominator exists.",
            "Do not report LIR/SEP/ETD alpha-sweep values for Amazon.",
            f"{COMPLETION_AUDIT}; {HANDOFF}",
            "Define an approved timestamp and path-type denominator protocol.",
        ],
        [
            "Non-path models are excluded from explanation scoring",
            "Post-hoc paths would not faithfully represent the model decision process.",
            "Use non-path models only as accuracy references or appendix context.",
            f"`README.md`; {ARCH}; {MODEL_AUDIT}",
            "Add only models with auditable native recommendation paths.",
        ],
        [
            "Strict accuracy and alpha-sweep metric columns have different evidence roles",
            "Status-matrix accuracy values come from per-row accuracy JSON; alpha-sweep CSVs support trade-off analysis.",
            "Keep final accuracy tables separate from explanation trade-off figures.",
            "`reports/tables/canonical_native_path_status_matrix.csv`; canonical trade-off CSV bundles",
            "Document metric provenance in captions and table notes.",
        ],
        [
            "Short or empty recommendation lists can occur under native-path candidate exhaustion",
            "The framework counts missing slots as non-hits rather than padding with non-path recommendations.",
            "Describe this as faithful native-path evaluation behavior.",
            f"{CANONICAL_STD}; `scripts/validation/evaluate_uid_topk.py`",
            "Report slot coverage and short-user counts alongside accuracy where relevant.",
        ],
        [
            "Historical/archive materials are not current source of truth",
            "Older handoffs and duplicate figure folders can conflict with current reports.",
            "Use completion audit, status matrix, validation manifest, and artifact manifest as primary evidence.",
            f"{COMPLETION_AUDIT}; {STATUS_MD}; {ARTIFACT_MANIFEST}",
            "Keep archive material in appendix only when needed for provenance.",
        ],
    ]
    table = md_table(["Limitation", "Why it matters", "How dissertation should phrase it", "Evidence file path", "Suggested future work"], limitations)
    text = f"""
# Goal 13: Limitations and Risks

## Current Task

List limitations that must be stated honestly in the dissertation and phrase them as framework boundaries or future work rather than hidden failures.

{table}
"""
    write("goal_13_limitations_and_risks.md", text)


def final_handoff(status_rows: list[dict[str, str]], created_figures: list[dict[str, str]]) -> None:
    rows = completed(status_rows)
    complete_count = len(rows)
    blocked_count = len([r for r in status_rows if r["stage"] == "Blocked"])
    fig_list = "\n".join(f"- `{c['path']}`: {c['caption']}" for c in created_figures)
    text = f"""
# Final Thesis Handoff

## 1. Dissertation Title Recommendation

Canonical Native-Path Evaluation for Knowledge-Graph Recommender Systems: Accuracy, Explainability, and Validation under a Shared Export Contract

## 2. One-Paragraph Thesis Positioning

This dissertation presents an evaluation framework for knowledge-graph recommender systems whose explanations are native to the recommendation process. Instead of proposing a new recommender model, it standardizes canonical datasets, model-specific views, native-path exports, validation gates, and accuracy/explanation metrics so heterogeneous path-based recommenders can be compared fairly. The framework reports complete LastFM and ML-1M six-model comparisons, a partial Amazon-Book KGAT stress test, and an explicit account of blocked/N/A cases where faithful native-path evaluation is not yet valid.

## 3. Research Questions

Use the five RQs in `thesis_analysis_pack/goal_1_research_positioning.md`.

## 4. Contributions

Use the six contributions in `thesis_analysis_pack/goal_1_research_positioning.md`: canonical dataset layer, native-path export contract, validation-first protocol, six-model empirical comparison, faithful native/post-hoc separation, and Amazon boundary-case analysis.

## 5. Datasets

- LastFM: main complete dataset, six models complete.
- ML-1M: main complete dataset, six models complete.
- Amazon-Book KGAT: secondary stress-test dataset; KGGLM, PEARLM, and PGPR complete; UCPR, CAFE, and TPRec blocked; explanation alpha sweeps N/A.
- Beauty legacy: historical/reference or appendix only.

Evidence: `thesis_analysis_pack/dataset_summary_table.md`; `{STATUS_MD}`.

## 6. Models

Main native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.

Accuracy-only or appendix context: KGIN, KGAT, LightGCN, MKR, CKE, RippleNet, unless a faithful native-path output contract is available.

Evidence: `thesis_analysis_pack/model_scope_table.md`; `{MODEL_AUDIT}`.

## 7. Metrics

Accuracy: HR@10, NDCG@10, Precision@10, Recall@10.

Explainability: LIR, SEP, ETD.

Evidence: `{PATH_METRICS}`; `scripts/validation/evaluate_uid_topk.py`.

## 8. Framework Design Summary

Chapter 3 should follow `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`: canonical dataset layer, model-specific views, native-path output contract, validation gate, xrecsys metrics, and report layer.

## 9. Key Results

- Current final status matrix has {complete_count} complete rows and {blocked_count} blocked rows.
- LastFM and ML-1M are complete six-model comparisons.
- Amazon-Book KGAT has complete KGGLM, PEARLM, and PGPR rows, with UCPR/CAFE/TPRec blocked.
- Final accuracy table: `thesis_analysis_pack/final_accuracy_summary_table.md`.
- Final explanation table: `thesis_analysis_pack/final_explanation_summary_table.md`.

## 10. Key Insights

Use `thesis_analysis_pack/goal_10_insight_notes.md`.

## 11. Figures to Use

{fig_list}

Existing canonical figure bundles:

- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`

## 12. Tables to Use

- `thesis_analysis_pack/dataset_summary_table.md`
- `thesis_analysis_pack/model_scope_table.md`
- `thesis_analysis_pack/final_accuracy_summary_table.md`
- `thesis_analysis_pack/final_explanation_summary_table.md`
- `thesis_analysis_pack/validation_status_table.md`

## 13. Limitations

Use `thesis_analysis_pack/goal_13_limitations_and_risks.md`. The most important limitations are Amazon partial status, Amazon explanation N/A, exclusion of post-hoc non-path models from explanation scoring, and separation between strict accuracy and alpha-sweep trade-off evidence.

## 14. Appendix Material

Useful appendix material includes existing figure inventories, ablation figures, historical archive notes, and Amazon readiness audit details.

## 15. Critical Evidence Paths

- `README.md`
- `{ARCH}`
- `{CANONICAL_STD}`
- `{PATH_METRICS}`
- `{DATA_PROVENANCE}`
- `{MODEL_AUDIT}`
- `{COMPLETION_AUDIT}`
- `{HANDOFF}`
- `{STATUS_MD}`
- `reports/tables/canonical_native_path_status_matrix.csv`
- `{VALIDATION_MANIFEST}`
- `{AMAZON_READINESS}`
- `{ARTIFACT_MANIFEST}`
- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`
"""
    write("FINAL_THESIS_HANDOFF.md", text)


def update_progress(created_figures: list[dict[str, str]]) -> None:
    progress_rows = [
        ["0", "Completed", "`thesis_analysis_pack/goal_0_repo_map.md`", "Repo map identifies docs/results/figures/validation/scripts and current source-of-truth files.", "Use current reports over README TODOs."],
        ["1", "Completed", "`thesis_analysis_pack/goal_1_research_positioning.md`", "Positioned dissertation as native-path KG recommender evaluation framework, not new model proposal.", "RQs should be adapted to final NTU chapter wording."],
        ["2", "Completed", "`thesis_analysis_pack/goal_2_dataset_audit.md`; `thesis_analysis_pack/dataset_summary_table.md`", "LastFM/ML-1M are main complete datasets; Amazon-Book KGAT is partial stress test.", "Beauty legacy only if appendix/provenance is needed."],
        ["3", "Completed", "`thesis_analysis_pack/goal_3_model_audit.md`; `thesis_analysis_pack/model_scope_table.md`", "Six native-path models are main comparison; non-path models are accuracy-only or appendix.", "Do not add LIR/SEP/ETD to non-path models."],
        ["4", "Completed", "`thesis_analysis_pack/goal_4_result_file_inventory.md`", "Status matrix, accuracy JSONs, validation JSONs, and canonical trade-off bundles are final evidence sources.", "Older duplicate figure folders remain uncertain/historical."],
        ["5", "Completed", "`thesis_analysis_pack/goal_5_accuracy_summary.md`; `thesis_analysis_pack/final_accuracy_summary_table.md`", "Strict accuracy values extracted for completed rows; blocked rows remain N/A.", "Keep alpha-sweep metric columns separate."],
        ["6", "Completed", "`thesis_analysis_pack/goal_6_explanation_metric_summary.md`; `thesis_analysis_pack/final_explanation_summary_table.md`", "LIR/SEP/ETD summarized from canonical LastFM/ML-1M alpha-sweep CSVs; Amazon explanation N/A.", "Endpoint values are alpha=0 -> alpha=1, not strict accuracy metrics."],
        ["7", "Completed", "`thesis_analysis_pack/goal_7_validation_audit.md`; `thesis_analysis_pack/validation_status_table.md`", "15 export validations pass; Amazon UCPR/CAFE/TPRec blocked/N/A.", "Per-row JSONs are concise; script gives full gate semantics."],
        ["8", "Completed", "`thesis_analysis_pack/goal_8_figure_inventory.md`; `thesis_analysis_pack/figure_caption_suggestions.md`", "Canonical LastFM v4 and ML-1M v2 bundles are preferred figure sources.", "Use older figures only selectively."],
        ["9", "Completed", "`reports/figures/thesis_final/`; `thesis_analysis_pack/generated_figure_captions.md`", f"Generated {len(created_figures)} thesis-ready figures from existing CSV/JSON evidence.", "No Amazon explanation figure generated because alpha sweeps are N/A."],
        ["10", "Completed", "`thesis_analysis_pack/goal_10_insight_notes.md`", "Eight Chapter 5 insights prepared with evidence paths and caveats.", "Convert to prose during thesis drafting."],
        ["11", "Completed", "`thesis_analysis_pack/goal_11_chapter_5_material_pack.md`", "Chapter 5 organized by research questions and evidence, not model-by-model diary.", "Tighten subsection numbering to match NTU template later."],
        ["12", "Completed", "`thesis_analysis_pack/goal_12_chapter_3_material_pack.md`", "Chapter 3 framework design material prepared with diagram text description.", "Actual diagram can be drawn later from this description."],
        ["13", "Completed", "`thesis_analysis_pack/goal_13_limitations_and_risks.md`", "Limitations phrased as framework boundaries and future work.", "Keep limitations visible in final dissertation."],
        ["14", "Completed", "`thesis_analysis_pack/FINAL_THESIS_HANDOFF.md`", "Final thesis handoff package summarizes title, positioning, RQs, contributions, datasets, models, metrics, results, figures, tables, limitations, and evidence paths.", "Ready for Chapter 1-6 drafting."],
    ]
    table = md_table(["Goal", "Status", "Output files", "Key findings", "Open questions"], progress_rows)
    write("PROGRESS.md", "# Thesis Analysis Pack Progress\n\n" + table)


def main() -> None:
    PACK.mkdir(exist_ok=True)
    rows = read_status_rows()
    goal1()
    goal2(rows)
    goal3(rows)
    goal4(rows)
    goal5(rows)
    goal6(rows)
    goal7(rows)
    goal8()
    created_figures = goal9(rows)
    goal10(rows, created_figures)
    goal11()
    goal12()
    goal13()
    final_handoff(rows, created_figures)
    update_progress(created_figures)
    print(json.dumps({
        "status": "PASS",
        "pack_dir": rel(PACK),
        "figures_dir": rel(FIG_OUT),
        "figures_created": [c["path"] for c in created_figures],
    }, indent=2))


if __name__ == "__main__":
    main()
