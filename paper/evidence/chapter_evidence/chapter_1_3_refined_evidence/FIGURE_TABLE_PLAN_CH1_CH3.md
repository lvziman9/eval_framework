# Figure and Table Plan for Chapter 1 and Chapter 3

## Chapter 1

Chapter 1 usually does not need figures. At most, include one compact specification table if the introduction needs to make the dissertation scope unambiguous.

| Candidate | Recommendation | Evidence/source path | New or existing |
| --- | --- | --- | --- |
| Specification table | Optional. Use a small table covering target models, datasets, metrics, validation, and boundary cases. | `paper/chapter_1_3_refined_evidence/CH1_REFINED_EVIDENCE_MATRIX.md`; `thesis_analysis_pack/dataset_summary_table.md`; `thesis_analysis_pack/model_scope_table.md`; `reports/tables/canonical_native_path_status_matrix.md`. | New table in thesis text. |
| Figure | Not recommended for Chapter 1 unless supervisor requests a high-level overview. | If needed, reuse the Figure 3.1 framework concept, but keep the full version in Chapter 3. | New only if requested. |

## Chapter 3

| Figure/Table | Recommended use | Data or evidence source paths | New or existing |
| --- | --- | --- | --- |
| Figure 3.1 Framework overview | Show the full framework flow: source data/KG -> canonical dataset -> model-specific views -> native inference -> export contract -> validation -> metrics -> reports. | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `reports/tables/canonical_export_validation/manifest.json`. | New figure needed. |
| Figure 3.2 Alpha-sweep experiment design | Show alpha grid, explanation objective selection, accuracy/explanation metric recomputation, and output trade-off curves. | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`; `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv`. | New design figure preferred; existing trade-off figures are Chapter 5 result figures. |
| Table 3.1 Canonical dataset and model-view requirements | Summarize dataset role, product entity, split/label evidence, model-view evidence, and caveats. | `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json`; `thesis_analysis_pack/dataset_summary_table.md`. | New table in thesis text. |
| Table 3.2 Native-path export contract | Define `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv`, schemas, purpose, and validation checks. | `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`; `xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score/`; `reports/tables/canonical_export_validation/manifest.json`. | New table in thesis text. |
| Table 3.3 Evaluation metrics | Separate strict accuracy metrics from explanation/trade-off metrics. | `scripts/validation/evaluate_uid_topk.py`; `xrecsys/metrics.py`; `xrecsys/myutils.py`; `docs/guides/PATH_METRICS_GUIDE.md`; `thesis_analysis_pack/final_accuracy_summary_table.md`; `thesis_analysis_pack/final_explanation_summary_table.md`. | New table in thesis text. |
| Table 3.4 Validation checks | List validation gates and what invalid evidence they prevent. | `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json`; `thesis_analysis_pack/validation_status_table.md`; `reports/tables/amazon_classic_port_readiness.json`. | New table in thesis text. |
| Table 3.5 Trade-off and ablation experiment design | Summarize alpha-sweep datasets, model scope, metrics, output CSV/figures, and ablation support. | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`; `reports/tables/ablation/pgpr_ucpr_path_module/`; `reports/figures/ablation/pgpr_ucpr_path_module/`; `thesis_analysis_pack/generated_figure_captions.md`. | New table in thesis text. |

## Existing Figures To Avoid In Chapter 3

| Existing figure | Use later instead | Reason |
| --- | --- | --- |
| `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | Chapter 5 | Result figure, not framework design. |
| `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | Chapter 5 | Result figure, not framework design. |
| `reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png` | Chapter 5 boundary/result section | Amazon is partial stress test. |
| `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Chapter 5 | Endpoint result, not methodology design. |
| `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | Chapter 5 | Trade-off result figure. |
| `reports/figures/thesis_final/experiment_status_matrix.png` | Chapter 5 or Chapter 4/5 bridge | Validation/result status figure, not the framework overview. |
