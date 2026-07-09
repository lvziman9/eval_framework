
# Goal 1: Research Positioning

## Goal Number

Goal 1

## Current Task

Extract the dissertation's research positioning from current README, docs, and reports, and frame the work as an evaluation framework dissertation rather than a new recommender-model dissertation.

## Thesis Positioning

The defensible dissertation framing is:

> A canonical evaluation framework for knowledge-graph recommenders with native recommendation paths, designed to compare recommendation accuracy and faithful path-based explainability under a shared dataset, export, and validation contract.

This should not be framed as inventing a new recommender model. The repository evidence repeatedly narrows the project toward evaluation: `README.md` states that the active experiment evaluates accuracy-explainability trade-offs only for KG recommenders with native recommendation paths, while non-path KG recommenders may be accuracy references only. `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` makes the same methodological boundary explicit: native path models can receive `NDCG / HR / Recall / Precision` plus `LIR / SEP / ETD`, while non-path models should not receive main explainability scores through post-hoc path recovery.

## Research Questions

1. RQ1: How can a canonical dataset and export contract make native-path KG recommender results comparable across heterogeneous model implementations?
   Evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/data/canonical/`; `reports/tables/canonical_export_validation/manifest.json`.
2. RQ2: Under a shared canonical evaluation protocol, how do native-path models differ in top-k recommendation accuracy across LastFM and ML-1M?
   Evidence: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/canonical_native_path_status_matrix.csv`.
3. RQ3: What do LIR, SEP, and ETD reveal about explanation quality that is not captured by HR@10 or NDCG@10 alone?
   Evidence: `docs/guides/PATH_METRICS_GUIDE.md`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`.
4. RQ4: What are the practical validation gates needed to distinguish faithful native-path explanations from post-hoc or invalid path artifacts?
   Evidence: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json`.
5. RQ5: Where do larger or less compatible datasets, especially Amazon-Book KGAT, expose the boundary conditions of a native-path evaluation framework?
   Evidence: `docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md`; `reports/tables/amazon_classic_port_readiness.json`; `reports/tables/canonical_native_path_status_matrix.md`.

## Dissertation Contributions

1. A canonical dataset layer that separates model-specific training views from shared canonical `uid/pid`, split, and label semantics.
   Evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/data/canonical/build_canonical_dataset.py`; `scripts/data/canonical/build_pgpr_view.py`; `scripts/data/canonical/build_ucpr_view.py`.
2. A native-path export contract requiring `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` for explainability scoring.
   Evidence: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/validation/validate_xrecsys_export.py`.
3. A validation-first evaluation protocol that enforces canonical test-user coverage, seen-item exclusion, path endpoint consistency, score ranges, and top-k/explanation agreement before results are reported.
   Evidence: `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_export_validation/manifest.json`.
4. A cross-model empirical comparison over six reportable native-path models on LastFM and ML-1M, with completed formal rows and figure bundles.
   Evidence: `reports/tables/canonical_native_path_status_matrix.md`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`.
5. A principled separation between faithful native-path explanations and post-hoc explanation recovery.
   Evidence: `README.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`.
6. A transparent boundary-case analysis for Amazon-Book KGAT, distinguishing reportable completed rows from blocked or N/A rows without inventing missing results.
   Evidence: `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`; `reports/tables/amazon_classic_port_readiness.json`; `reports/tables/canonical_native_path_status_matrix.md`.

## Key Evidence Paths

- `README.md`
- `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- `docs/guides/CANONICAL_DATASET_STANDARD.md`
- `docs/guides/PATH_METRICS_GUIDE.md`
- `docs/guides/DATA_PROVENANCE.md`
- `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`
- `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`
- `reports/tables/canonical_native_path_status_matrix.md`
- `reports/tables/canonical_export_validation/manifest.json`
- `reports/tables/amazon_classic_port_readiness.json`

## Next Goal

Goal 2: Dataset audit. Separate main experiment datasets from secondary, blocked, historical, or appendix datasets.
