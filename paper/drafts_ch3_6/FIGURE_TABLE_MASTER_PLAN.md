# Figure and Table Master Plan

| Figure/Table | Chapter | Purpose | Existing file or new figure | Evidence path |
| ------------ | ------- | ------- | --------------------------- | ------------- |
| Figure 3.1 Overview of the implemented canonical native-path evaluation framework | 3 | Show the framework flow from canonical data to report layer. | New conceptual figure planned; not generated in this phase. | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`. |
| Figure 3.2 Alpha-sweep trade-off experiment design | 3 | Show how alpha changes ranking objective while strict accuracy remains separate. | New conceptual figure planned; not generated in this phase. | `thesis_analysis_pack/final_explanation_summary_table.md`; canonical trade-off CSV bundles. |
| Table 3.1 Canonical dataset and model-view design requirements | 3 | Summarise the canonical dataset contract. | New table in draft. | `docs/guides/CANONICAL_DATASET_STANDARD.md`. |
| Table 3.2 Native-path export contract | 3 | Define required export files and native-path boundaries. | New table in draft. | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `scripts/validation/validate_xrecsys_export.py`. |
| Table 3.3 Evaluation metrics | 3 | Separate accuracy metrics from explanation metrics. | New table in draft. | `docs/guides/PATH_METRICS_GUIDE.md`; `scripts/validation/evaluate_uid_topk.py`. |
| Table 3.4 Validation checks | 3 | Summarise validation gates. | New table in draft. | `thesis_analysis_pack/validation_status_table.md`; `reports/tables/canonical_export_validation/manifest.json`. |
| Table 3.5 Framework verification summary | 3 | Record PASS/BLOCKED/N/A verification status. | New table in draft. | `thesis_analysis_pack/validation_status_table.md`. |
| Table 3.6 Trade-off and ablation experiment design | 3 | State what later chapters may use. | New table in draft. | `thesis_analysis_pack/final_explanation_summary_table.md`; ablation tables. |
| Table 3.7 Representative alpha-sweep endpoint verification examples | 3 | Give endpoint examples without interpreting mechanisms. | New table in draft. | `thesis_analysis_pack/final_explanation_summary_table.md`. |
| Figure 4.1 LastFM accuracy comparison | 4 | Main strict accuracy visual. | Existing. | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`. |
| Figure 4.2 ML-1M accuracy comparison | 4 | Main strict accuracy visual. | Existing. | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`. |
| Figure 4.3 Explanation metric alpha endpoints | 4 | Endpoint comparison for LIR, SEP, ETD. | Existing. | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`. |
| Figure 4.4 LIR-NDCG trade-off | 4 | Main trade-off curve. | Existing. | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`. |
| Figure 5.1 PGPR/UCPR ablation trade-off figure | 5 | Ablation controllability evidence. | Existing. | `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg`; `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg`. |
| Figure 5.2 Experiment status matrix / boundary-case overview | 5 | Show complete versus blocked rows. | Existing. | `reports/figures/thesis_final/experiment_status_matrix.png`. |

