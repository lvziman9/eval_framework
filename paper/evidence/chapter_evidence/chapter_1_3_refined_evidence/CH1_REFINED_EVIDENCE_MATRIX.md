# Chapter 1 Introduction

Evidence pack for the tentative dissertation title:

`A Canonical Framework for Accuracy-Explainability Trade-off Analysis in Native-Path Knowledge Graph Recommenders`

Scope rules:

- This is an evidence matrix, not formal dissertation prose.
- Do not use README TODOs as completed evidence.
- Experimental conclusions must come from generated evidence artifacts, not docs alone.
- Strict accuracy evidence and alpha-sweep trade-off evidence must remain separate.
- Native-path explanation evidence and post-hoc explanation evidence must remain separate.
- Amazon-Book KGAT is a partial stress test / boundary case, not a complete explanation experiment.

## 1.1 Background

| Required item | Evidence matrix |
| --- | --- |
| core writing claim | The dissertation can be framed as a canonical evaluation framework for KG recommenders that emit native recommendation paths, comparing strict top-k accuracy and path-based explainability under shared dataset, export, validation, and reporting contracts. |
| repo evidence paths | `thesis_analysis_pack/goal_1_research_positioning.md`; `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/canonical_export_validation/manifest.json`. |
| external paper evidence needed, if any | Needed for literature/background claims about KG recommendation and path explanation, but not for repository experimental claims. Suggested external sources: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM, KGAT Amazon-book/KB4Rec, and papers defining or motivating path-based explainability/trade-off analysis. Local audit references: `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`. |
| metric/model/dataset evidence | Models: `thesis_analysis_pack/model_scope_table.md`. Datasets: `thesis_analysis_pack/dataset_summary_table.md`. Metrics: `thesis_analysis_pack/final_accuracy_summary_table.md`; `thesis_analysis_pack/final_explanation_summary_table.md`; `docs/guides/PATH_METRICS_GUIDE.md`; `scripts/validation/evaluate_uid_topk.py`; `xrecsys/metrics.py`. |
| caveats | Do not claim a new recommender model. Do not claim universal KG recommender explainability. Do not score non-native-path models with LIR/SEP/ETD. Amazon-Book KGAT has complete strict accuracy/export rows only for KGGLM, PEARLM, and PGPR; explanation alpha sweeps are N/A. |

## 1.2 Motivation

| Required item | Evidence matrix |
| --- | --- |
| accuracy-only evaluation insufficiency evidence | Accuracy table reports HR@10, NDCG@10, Precision@10, Recall@10, but explanation summary shows separate LIR/SEP/ETD alpha-sweep evidence. Use `thesis_analysis_pack/final_accuracy_summary_table.md` with `thesis_analysis_pack/final_explanation_summary_table.md` to motivate that accuracy and explanation properties are not the same evidence type. |
| post-hoc explanation unsuitable for main evaluation evidence | Native-path boundary is stated in `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` and `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`. Historical post-hoc VRKG material is archived under `archive/historical_code/posthoc_vrkg/` and `archive/historical_docs/posthoc_vrkg/`; use it only as background/negative motivation, not main experimental evidence. |
| canonical comparison necessity evidence | `docs/guides/CANONICAL_DATASET_STANDARD.md` states the canonical layer separates model-specific training views from shared uid/pid, split, label, and output semantics. Completed validation evidence is in `reports/tables/canonical_export_validation/manifest.json`; status evidence is in `reports/tables/canonical_native_path_status_matrix.csv`. |
| trade-off / alpha-sweep / ablation existence evidence | Canonical alpha-sweep bundles: `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`. Thesis-ready trade-off figure: `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`. PGPR/UCPR path-module ablation evidence: `reports/tables/ablation/pgpr_ucpr_path_module/main_ablation_table_95pct_ndcg.csv`; `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv`; `reports/figures/ablation/pgpr_ucpr_path_module/`. |
| caveats | The alpha-sweep CSVs are trade-off evidence and must not replace strict accuracy JSON values. Some ablation artifacts are appendix/supporting material, not the primary canonical status matrix. Amazon alpha-sweeps are N/A under current evidence. |

## 1.3 Objectives and Specifications

| Required item | Evidence matrix |
| --- | --- |
| objective wording evidence | Use wording from `thesis_analysis_pack/goal_1_research_positioning.md`: build/evaluate a canonical native-path KG recommender evaluation framework rather than propose a new recommender model. |
| datasets evidence | `thesis_analysis_pack/dataset_summary_table.md`; `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json`. |
| models evidence | Six main native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM. Evidence: `thesis_analysis_pack/model_scope_table.md`; `reports/tables/canonical_native_path_status_matrix.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`. |
| metrics evidence | Strict accuracy: HR@10, NDCG@10, Precision@10, Recall@10 from per-row `accuracy.json` files indexed by `reports/tables/canonical_native_path_status_matrix.csv` and summarized in `thesis_analysis_pack/final_accuracy_summary_table.md`. Explanation/trade-off: LIR, SEP, ETD from alpha-sweep CSVs summarized in `thesis_analysis_pack/final_explanation_summary_table.md`. |
| validation requirement evidence | `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_export_validation/manifest.json`; `thesis_analysis_pack/validation_status_table.md`. |
| output contract evidence | Required native-path files: `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv`. Evidence: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; formal export examples under `xrecsys/paths/{lastfm,ml1m,amazon_book_kgat_v1}/agent_topk=*/`. |
| trade-off experiment evidence | Alpha range `0.0000` to `1.0000` in 0.05 steps appears in canonical trade-off CSVs, for example `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv` and `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv`. |

### Recommended Specification Table

| Specification dimension | Dissertation wording anchor | Evidence path | Evidence type |
| --- | --- | --- | --- |
| Evaluation target | Native-path KG recommenders whose explanations are emitted by the recommendation process | `thesis_analysis_pack/model_scope_table.md` | Methodology + scope |
| Main datasets | LastFM and ML-1M complete six-model comparisons | `reports/tables/canonical_native_path_status_matrix.md` | Experimental |
| Boundary dataset | Amazon-Book KGAT partial stress test | `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json` | Experimental boundary |
| Strict accuracy metrics | HR@10, NDCG@10, Precision@10, Recall@10 | `thesis_analysis_pack/final_accuracy_summary_table.md`; per-row `accuracy.json` files | Experimental |
| Explanation/trade-off metrics | LIR, SEP, ETD from native paths | `thesis_analysis_pack/final_explanation_summary_table.md`; canonical trade-off CSV bundles | Experimental trade-off |
| Export contract | `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv` | `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json` | Mechanism + validation |
| Validation gate | Full test-user coverage, endpoint consistency, seen-item exclusion, top-k/explanation agreement, score sanity | `scripts/validation/validate_xrecsys_export.py`; `thesis_analysis_pack/validation_status_table.md` | Methodology + experimental validation |

## 1.4 Major contribution of the Dissertation

| Contribution | contribution wording | supporting artifact | evidence path | type | evidence role |
| --- | --- | --- | --- | --- | --- |
| C1 | Canonical dataset layer separating shared uid/pid, splits, labels, and KG provenance from model-specific internal views. | Canonical metadata, labels, mappings, model-view directories. | `docs/guides/CANONICAL_DATASET_STANDARD.md`; `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json`. | framework | methodology evidence |
| C2 | Native-path export contract for comparable path-based recommendation outputs. | `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv`; export validator. | `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json`; `xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score/`. | mechanism | methodology + validation evidence |
| C3 | Validation-first protocol that decides which model/dataset rows are reportable. | Validation manifest and per-row validation JSONs. | `reports/tables/canonical_export_validation/manifest.json`; `thesis_analysis_pack/validation_status_table.md`; `reports/tables/amazon_classic_port_readiness.json`. | mechanism | experimental validation evidence |
| C4 | Six-model empirical comparison on the two complete main datasets. | Status matrix, strict accuracy table, final figures. | `reports/tables/canonical_native_path_status_matrix.csv`; `thesis_analysis_pack/final_accuracy_summary_table.md`; `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png`; `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png`. | experiment | experimental evidence |
| C5 | Accuracy-explainability trade-off analysis using native path metrics. | Alpha-sweep CSV/PNG bundles and explanation summary. | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`; `thesis_analysis_pack/final_explanation_summary_table.md`; `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png`. | experiment | experimental trade-off evidence |
| C6 | Explicit boundary-case handling for incomplete or incompatible native-path rows. | Amazon readiness audit and status matrix blocked rows. | `reports/tables/amazon_classic_port_readiness.json`; `reports/tables/canonical_native_path_status_matrix.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md`. | boundary | experimental boundary + limitation evidence |

## 1.5 Organisation of the Dissertation

| Chapter | Content suggestion | Corresponding evidence |
| --- | --- | --- |
| Chapter 2 | Literature review: KG recommender systems, path-based recommendation, native vs post-hoc explanations, accuracy and explainability metrics, and trade-off evaluation. | Use external papers for literature claims. Local scoping aid: `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`. |
| Chapter 3 | Framework design and verification: canonical dataset layer, model-specific views, native-path export contract, metrics, validation gate, and alpha-sweep design. | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_export_validation/manifest.json`. |
| Chapter 4 | Implementation / experiment setup: datasets, models, formal run scope, output artifacts, figure/table generation, and reproducibility commands. | `thesis_analysis_pack/dataset_summary_table.md`; `thesis_analysis_pack/model_scope_table.md`; `reports/tables/canonical_native_path_artifact_manifest.json`; `scripts/analysis/regenerate_canonical_native_path_reports.sh`. |
| Chapter 5 | Results and analysis: validation outcomes, strict accuracy comparisons, explanation endpoint results, trade-off analysis, Amazon boundary case. | `thesis_analysis_pack/goal_11_chapter_5_material_pack.md`; `thesis_analysis_pack/final_accuracy_summary_table.md`; `thesis_analysis_pack/final_explanation_summary_table.md`; `reports/figures/thesis_final/`; canonical trade-off bundles. |
| Chapter 6 | Conclusion, limitations, and future work: what the framework proves, what remains blocked, and what future ports or datasets require. | `thesis_analysis_pack/goal_13_limitations_and_risks.md`; `reports/tables/amazon_classic_port_readiness.json`; `reports/tables/canonical_native_path_status_matrix.md`. |
