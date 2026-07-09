# Goal 10: Chapter 5 Insight Notes

## Validation is an experimental outcome, not just a preprocessing step

- Claim: The current framework reports 15 complete rows and 3 blocked Amazon rows, showing that validation determines what can be claimed.
- Supporting evidence: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/canonical_export_validation/manifest.json`; `reports/tables/amazon_classic_port_readiness.json`
- Suggested figure/table: `thesis_analysis_pack/validation_status_table.md`; `reports/figures/thesis_final/experiment_status_matrix.png`
- Dissertation interpretation: Place in 5.1 Validation of the Canonical Evaluation Pipeline.
- Caveat: Blocked does not mean failed accuracy; it means the model/dataset pair has not passed the required native-path support and validation gates.
- Evidence file paths: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/canonical_export_validation/manifest.json`; `reports/tables/amazon_classic_port_readiness.json`

## Best accuracy is dataset-dependent

- Claim: On LastFM, best HR@10 is UCPR (0.216416) while best NDCG@10 is TPRec (0.038981); on ML-1M, CAFE leads HR@10 (0.554305) and CAFE leads NDCG@10 (0.116655).
- Supporting evidence: `reports/tables/canonical_native_path_status_matrix.csv`
- Suggested figure/table: `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`
- Dissertation interpretation: Place in 5.2 Accuracy Comparison Across Native-Path Models.
- Caveat: Do not generalize one model's ranking across all datasets.
- Evidence file paths: `reports/tables/canonical_native_path_status_matrix.csv`

## Amazon-Book KGAT behaves as a stress test

- Claim: Among completed Amazon rows, PGPR has the highest HR@10 (0.054851); UCPR, CAFE, and TPRec remain blocked or N/A.
- Supporting evidence: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json`
- Suggested figure/table: `reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/experiment_status_matrix.png`
- Dissertation interpretation: Place in 5.5 Boundary Case and Limitations: Amazon-Book.
- Caveat: Amazon explanation alpha sweeps are not reportable under the current evidence.
- Evidence file paths: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json`

## Native-path fidelity changes the model comparison boundary

- Claim: The repository excludes post-hoc path recovery from main LIR/SEP/ETD scoring and uses non-path models only as accuracy references.
- Supporting evidence: `README.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`
- Suggested figure/table: `thesis_analysis_pack/model_scope_table.md`
- Dissertation interpretation: Place in 5.3 Explanation Quality Analysis.
- Caveat: This narrows the model universe but makes explanation scores more faithful.
- Evidence file paths: `README.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`

## LIR, SEP, and ETD capture different explanation dimensions

- Claim: The metric guide defines recency, bridge-entity serendipity, and path-type diversity separately, and the alpha-sweep CSVs report separate curves for each metric.
- Supporting evidence: `docs/guides/PATH_METRICS_GUIDE.md`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`
- Suggested figure/table: `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`
- Dissertation interpretation: Place in 5.3 Explanation Quality Analysis.
- Caveat: A high value on one explanation metric should not be described as overall explainability superiority.
- Evidence file paths: `docs/guides/PATH_METRICS_GUIDE.md`; `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`

## Accuracy and explanation quality are not reducible to one metric

- Claim: Alpha-sweep bundles show explanation metrics changing as alpha changes, while accuracy metrics must be interpreted separately.
- Supporting evidence: `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`; canonical trade-off CSVs
- Suggested figure/table: `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`
- Dissertation interpretation: Place in 5.4 Accuracy-Explainability Trade-off.
- Caveat: Strict accuracy JSON values and alpha-sweep CSV metric columns use different evidence roles.
- Evidence file paths: `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`; canonical trade-off CSVs

## Canonical IDs and model-specific views solve an unfair-comparison problem

- Claim: The canonical dataset standard allows models to remap internally while requiring all exported recommendations and paths to return to canonical uid/pid.
- Supporting evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/data/canonical/`; `scripts/validation/validate_xrecsys_export.py`
- Suggested figure/table: `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`
- Dissertation interpretation: Place in 5.1 Validation of the Canonical Evaluation Pipeline.
- Caveat: The framework standardizes the comparison contract, not every internal KG representation.
- Evidence file paths: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/data/canonical/`; `scripts/validation/validate_xrecsys_export.py`

## Short native-path recommendation lists are a valid framework condition

- Claim: The evaluator preserves short and empty lists, counts missing slots as non-hits, and reports slot coverage rather than filling with non-path recommendations.
- Supporting evidence: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/validation/evaluate_uid_topk.py`; per-row accuracy JSON files
- Suggested figure/table: `thesis_analysis_pack/final_accuracy_summary_table.md`
- Dissertation interpretation: Place in 5.1 Validation of the Canonical Evaluation Pipeline.
- Caveat: Short-list handling should be described as native-path candidate exhaustion, not as a post-hoc padding problem.
- Evidence file paths: `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/validation/evaluate_uid_topk.py`; per-row accuracy JSON files
