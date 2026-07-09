
# Goal 12: Chapter 3 Method Material Pack

## 3.1 Overview of the Canonical Evaluation Framework

The framework evaluates native-path KG recommenders by separating canonical dataset truth, model-specific training views, canonical exports, validation gates, and xrecsys metrics. Evidence: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`.

## 3.2 Canonical Dataset Layer

A canonical dataset defines model-independent user ids, product ids, train/valid/test interactions, labels, KG source assets, and output mapping requirements. Evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`.

Key writing point: the canonical layer standardizes the comparison contract, not every internal graph representation.

## 3.3 Model-Specific Views and ID Remapping

Models may use compact or reordered internal ids, but exported recommendations and paths must map back to canonical `uid/pid`. Evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/data/canonical/build_pgpr_view.py`; `scripts/data/canonical/build_ucpr_view.py`; `scripts/hopwise/build_canonical_hopwise_view.py`.

## 3.4 Native-Path Output Contract

Native-path models must export:

- `uid_topk.csv`
- `pred_paths.csv`
- `uid_pid_explanation.csv`

Non-path models only need `uid_topk.csv` and should not receive LIR/SEP/ETD scores. Evidence: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `scripts/validation/validate_xrecsys_export.py`.

## 3.5 Accuracy and Explanation Metrics

Accuracy metrics: HR@10, NDCG@10, Precision@10, Recall@10. Evidence: `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_native_path_status_matrix.csv`.

Explanation metrics:

- LIR: linked interaction recency
- SEP: serendipity of explanation path
- ETD: explanation type diversity

Evidence: `docs/guides/PATH_METRICS_GUIDE.md`; `xrecsys/metrics.py`.

## 3.6 Validation-First Evaluation

Before a result is reportable, validation checks canonical test-user coverage, duplicate top-k items, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate path consistency, and score ranges. Evidence: `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json`.

## 3.7 Reproducibility Design

The status matrix, export-validation manifest, Amazon readiness audit, and artifact manifest are generated reports. Evidence: `scripts/analysis/regenerate_canonical_native_path_reports.sh`; `reports/tables/canonical_native_path_artifact_manifest.json`.

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

- `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- `docs/guides/CANONICAL_DATASET_STANDARD.md`
- `docs/guides/PATH_METRICS_GUIDE.md`
- `docs/guides/DATA_PROVENANCE.md`
- `scripts/validation/validate_xrecsys_export.py`
- `scripts/validation/evaluate_uid_topk.py`
- `reports/tables/canonical_export_validation/manifest.json`
- `reports/tables/canonical_native_path_artifact_manifest.json`
