
# Goal 11: Chapter 5 Material Pack

## 5.1 Validation of the Canonical Evaluation Pipeline

Core claim: The framework's first contribution is not simply producing scores, but deciding which model/dataset outputs are valid enough to score.

Use:
- Table: `thesis_analysis_pack/validation_status_table.md`
- Figure: `reports/figures/thesis_final/experiment_status_matrix.png`
- Evidence: `reports/tables/canonical_export_validation/manifest.json`; `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`

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
- Evidence: `docs/guides/PATH_METRICS_GUIDE.md`; canonical LastFM and ML-1M trade-off CSV bundles.

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
- Evidence: `reports/tables/amazon_classic_port_readiness.json`; `docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md`; `reports/tables/canonical_native_path_status_matrix.md`

Caveat: Present Amazon as a boundary/stress test, not as a complete six-model explanation experiment.
