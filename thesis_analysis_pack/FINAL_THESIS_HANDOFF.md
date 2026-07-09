
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

Evidence: `thesis_analysis_pack/dataset_summary_table.md`; `reports/tables/canonical_native_path_status_matrix.md`.

## 6. Models

Main native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.

Accuracy-only or appendix context: KGIN, KGAT, LightGCN, MKR, CKE, RippleNet, unless a faithful native-path output contract is available.

Evidence: `thesis_analysis_pack/model_scope_table.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`.

## 7. Metrics

Accuracy: HR@10, NDCG@10, Precision@10, Recall@10.

Explainability: LIR, SEP, ETD.

Evidence: `docs/guides/PATH_METRICS_GUIDE.md`; `scripts/validation/evaluate_uid_topk.py`.

## 8. Framework Design Summary

Chapter 3 should follow `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`: canonical dataset layer, model-specific views, native-path output contract, validation gate, xrecsys metrics, and report layer.

## 9. Key Results

- Current final status matrix has 15 complete rows and 3 blocked rows.
- LastFM and ML-1M are complete six-model comparisons.
- Amazon-Book KGAT has complete KGGLM, PEARLM, and PGPR rows, with UCPR/CAFE/TPRec blocked.
- Final accuracy table: `thesis_analysis_pack/final_accuracy_summary_table.md`.
- Final explanation table: `thesis_analysis_pack/final_explanation_summary_table.md`.

## 10. Key Insights

Use `thesis_analysis_pack/goal_10_insight_notes.md`.

## 11. Figures to Use

- `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`: LastFM HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol.
- `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`: ML-1M HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol.
- `reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png`: Amazon-Book KGAT HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol.
- `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`: Endpoint comparison of LIR, SEP, and ETD at alpha=0 and alpha=1 for LastFM and ML-1M native-path models.
- `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`: Accuracy-explainability trade-off curves showing LIR against the NDCG sweep metric on LastFM and ML-1M.
- `reports/figures/thesis_final/experiment_status_matrix.png`: Status matrix for canonical native-path experiments, separating complete rows from blocked Amazon-Book KGAT rows.

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
- `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- `docs/guides/CANONICAL_DATASET_STANDARD.md`
- `docs/guides/PATH_METRICS_GUIDE.md`
- `docs/guides/DATA_PROVENANCE.md`
- `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`
- `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`
- `docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md`
- `reports/tables/canonical_native_path_status_matrix.md`
- `reports/tables/canonical_native_path_status_matrix.csv`
- `reports/tables/canonical_export_validation/manifest.json`
- `reports/tables/amazon_classic_port_readiness.json`
- `reports/tables/canonical_native_path_artifact_manifest.json`
- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`
