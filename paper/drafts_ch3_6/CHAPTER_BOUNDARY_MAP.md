# Chapter Boundary Map

| Chapter | Main question | Include | Exclude | Main evidence |
| ------- | ------------- | ------- | ------- | ------------- |
| Chapter 3 Framework Implementation and Verification | How was the canonical native-path evaluation framework implemented and checked before result interpretation? | Canonical dataset layer, model-specific views, native-path export contract, validation checks, metric definitions, verification summary, strict accuracy snapshot, alpha-sweep setup, ablation setup. | Deep interpretation of model mechanisms; cross-dataset conclusions; Amazon as full main experiment. | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/PATH_METRICS_GUIDE.md`; `thesis_analysis_pack/validation_status_table.md`. |
| Chapter 4 Accuracy-Explainability Trade-off Results | What do the completed strict accuracy and alpha-sweep results show on the main datasets? | LastFM and ML-1M six-model strict accuracy, explanation endpoints, LIR/SEP/ETD trade-off summaries, cross-dataset comparison. | Mechanism-level explanation, ablation details, limitations discussion, Amazon as full result set. | `thesis_analysis_pack/final_accuracy_summary_table.md`; `thesis_analysis_pack/final_explanation_summary_table.md`; `reports/figures/thesis_final/`; canonical trade-off CSV bundles. |
| Chapter 5 Ablation, Mechanism Analysis, and Boundary Cases | What do ablations and mechanism-level comparisons imply, and where are the framework boundaries? | PGPR/UCPR ablation, alpha=0 preservation, 95% NDCG retention if supported, native-path mechanism comparison, LIR/SEP/ETD non-interchangeability, Amazon boundary case, limitations. | Repeating every Chapter 4 table; new strict accuracy results; new experiments. | `thesis_analysis_pack/goal_10_insight_notes.md`; `thesis_analysis_pack/goal_11_chapter_5_material_pack.md`; `reports/tables/ablation/pgpr_ucpr_path_module/`; `thesis_analysis_pack/goal_13_limitations_and_risks.md`. |
| Chapter 6 Conclusion and Recommendations | What can be concluded from the verified evidence, and what should future work do next? | Framework contribution, validation-first contract, six-model LastFM/ML-1M comparison, trade-off findings, ablation and boundary-case summary, recommendations. | New results, new figures, unverified claims, full literature review. | Chapters 3-5 draft evidence maps; `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md`. |

## Required Separation Rules

Strict accuracy uses accuracy JSON summaries and final strict accuracy tables.

Alpha-sweep trade-off evidence uses trade-off CSVs and figures where metrics are reported as a function of alpha. These columns must not replace strict accuracy results.

Ablation evidence uses `reports/tables/ablation/pgpr_ucpr_path_module/` and related ablation figures. It should be interpreted as controllability and mechanism evidence, not as the main six-model result table.

Amazon-Book KGAT is a partial stress test. Complete rows may be used for limited validation and accuracy discussion, while blocked rows must not be ranked or treated as failed recommender performance.

