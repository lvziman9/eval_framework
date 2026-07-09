# Chapter 3 Framework Design and Verification

Evidence pack for Chapter 3 only. Keep final result interpretation for Chapter 5.

## 3.1 Framework Overview

| Required item | Evidence matrix |
| --- | --- |
| framework layers | Layer 1: source datasets and KG provenance. Layer 2: canonical dataset layer with uid/pid, train/valid/test splits, labels, mappings. Layer 3: model-specific views and remaps. Layer 4: native model training/inference outside this writing pack. Layer 5: canonical export contract. Layer 6: validation gate. Layer 7: strict accuracy and explanation/trade-off metrics. Layer 8: report layer. |
| repo paths corresponding to each layer | Source/provenance: `docs/guides/DATA_PROVENANCE.md`; `data_sources/kgat_amazon_book/`. Canonical data: `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/`; `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/`. Model views: `scripts/data/canonical/`; `scripts/hopwise/build_canonical_hopwise_view.py`; dataset `model_views/` folders. Exports: `xrecsys/paths/`. Validation: `scripts/validation/validate_xrecsys_export.py`; `reports/tables/canonical_export_validation/manifest.json`. Reports: `reports/tables/`; `reports/figures/thesis_final/`; `reports/figures/tradeoff/`. |
| suggested Figure 3.1 nodes and arrows | Nodes: Source dataset/KG -> Canonical dataset -> Model-specific views -> Native model inference -> Canonical export files -> Validation gate -> Metric computation -> Report tables/figures. Arrows: provenance and split construction; id remapping; native path generation; export to canonical uid/pid; validation pass/block; metrics separated into strict accuracy and alpha-sweep explanation/trade-off. |
| existing figure if available | No existing framework overview figure was found. Existing related figure is `reports/figures/thesis_final/experiment_status_matrix.png`, useful later for validation/result status, not as Figure 3.1. Figure 3.1 should be newly drawn from `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`. |
| caveats | Chapter 3 should describe design and verification protocol, not make model ranking claims. Do not describe Amazon as complete. Do not merge strict accuracy and alpha-sweep values. |

## 3.2 Canonical Dataset and Model View Design

| Required item | Evidence matrix |
| --- | --- |
| canonical uid/pid evidence | `docs/guides/CANONICAL_DATASET_STANDARD.md` defines canonical user/product ids and requires exported recommendations and paths to map back to canonical ids. Dataset metadata files define dataset-specific policies: LastFM `product_id_policy=xrecsys_kgid`; ML-1M `product_id_policy=raw_to_xrecsys_kgid`; Amazon `product_id_policy=preserve KGAT remap item/entity id`. |
| train/valid/test split evidence | LastFM metadata: `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/metadata.json` with train/valid/test stats. ML-1M metadata: `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/metadata.json`. Amazon metadata: `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json`. |
| labels evidence | Canonical labels exist as `labels/train_label.pkl`, `labels/valid_label.pkl`, `labels/test_label.pkl` under each canonical dataset directory. Evaluation scripts load these labels: `scripts/validation/evaluate_uid_topk.py`; `scripts/validation/validate_xrecsys_export.py`. |
| KG source provenance evidence | General provenance: `docs/guides/DATA_PROVENANCE.md`. LastFM/ML-1M source directories: `xrecsys/datasets/lastfm/`; `xrecsys/datasets/ml1m/`. Amazon KGAT source: `data_sources/kgat_amazon_book/`; `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json` records fixed KGAT commit, Freebase KG provenance, source release counts, and no metadata-derived triples. |
| model-specific view evidence | PGPR/UCPR/CAFE views appear under canonical dataset `model_views/` folders. Hopwise/native path model views are built through `scripts/hopwise/build_canonical_hopwise_view.py` and related pipeline scripts. Amazon PGPR/UCPR/TPrec view evidence appears under `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/`. |
| remap evidence | UCPR and CAFE view folders include `user_remap.tsv` and `product_remap.tsv` where internal ids differ. PGPR view metadata records identity mapping back to canonical uid/pid. Evidence: `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/ucpr/preprocessed/user_remap.tsv`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/model_views/ucpr/preprocessed/product_remap.tsv`; `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/pgpr/pgpr_view_metadata.json`; `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/model_views/pgpr/pgpr_view_metadata.json`. |
| LastFM / ML-1M / Amazon role evidence | `thesis_analysis_pack/dataset_summary_table.md`: LastFM and ML-1M are main complete datasets; Amazon-Book KGAT is a secondary stress-test/boundary dataset; Beauty legacy is historical/reference only. |

Suggested Table 3.1 content:

| Dataset | Role | Canonical product entity | Split/label evidence | Model-view evidence | Caveat |
| --- | --- | --- | --- | --- | --- |
| LastFM | Main complete dataset | song | `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/metadata.json`; `labels/*.pkl` | `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/` | Use canonical v1, not historical duplicate folders. |
| ML-1M | Main complete dataset | movie | `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/metadata.json`; `labels/*.pkl` | `runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/model_views/` | Six-model formal rows complete. |
| Amazon-Book KGAT | Partial stress test / boundary case | book | `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/metadata.json`; `labels/*.pkl` | `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/` | Explanation alpha sweeps N/A; UCPR/CAFE/TPRec blocked. |

## 3.3 Native-Path Export Contract

| Required item | Evidence matrix |
| --- | --- |
| `uid_topk.csv` evidence | Required columns are `uid,top10`, validated in `scripts/validation/validate_xrecsys_export.py` and `scripts/validation/evaluate_uid_topk.py`. Formal example path: `xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score/uid_topk.csv`. |
| `pred_paths.csv` evidence | Required columns are `uid,pid,path_score,path_prob,path`, validated in `scripts/validation/validate_xrecsys_export.py`. Formal example path: `xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score/pred_paths.csv`. |
| `uid_pid_explanation.csv` evidence | Required columns are `uid,pid,path`, validated in `scripts/validation/validate_xrecsys_export.py`. Formal example path: `xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score/uid_pid_explanation.csv`. |
| schema examples if available | `uid_topk.csv`: `uid,top10`. `pred_paths.csv`: `uid,pid,path_score,path_prob,path`. `uid_pid_explanation.csv`: `uid,pid,path`. Example native path shape from formal PGPR LastFM export: `self_loop user 2 listened song 19949 listened user 298 listened song 6711`. |
| validation script evidence | `scripts/validation/validate_xrecsys_export.py` checks exact field names, duplicate users/items, canonical test-user membership, seen-item leakage, path user/product endpoints, top-k/explanation consistency, candidate path existence, and finite score ranges. |
| completed model-dataset output evidence | `reports/tables/canonical_export_validation/manifest.json` records `exports=15`, `status=PASS`. Completed rows: LastFM six models, ML-1M six models, Amazon-Book KGAT KGGLM/PEARLM/PGPR. Per-row JSONs are under `reports/tables/canonical_export_validation/`. |
| non-native path exclusion evidence | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`; `thesis_analysis_pack/model_scope_table.md`. Non-native models such as KGIN, KGAT, LightGCN are accuracy-only/appendix references unless a faithful native path contract exists. |

Suggested Table 3.2 content:

| Export file | Required columns | Purpose | Validation checks | Evidence path |
| --- | --- | --- | --- | --- |
| `uid_topk.csv` | `uid`, `top10` | Ordered recommendation list for strict top-k accuracy | canonical test-user coverage, no duplicates, no seen items, max length K | `scripts/validation/evaluate_uid_topk.py`; `scripts/validation/validate_xrecsys_export.py` |
| `pred_paths.csv` | `uid`, `pid`, `path_score`, `path_prob`, `path` | Candidate native paths used to support top-k explanations | endpoint consistency, score range, candidate path non-empty, no seen item leakage | `scripts/validation/validate_xrecsys_export.py` |
| `uid_pid_explanation.csv` | `uid`, `pid`, `path` | One selected explanation path per recommended pair | top-k/explanation pair consistency and path endpoint validity | `scripts/validation/validate_xrecsys_export.py` |

## 3.4 Evaluation Metrics

| Required item | Evidence matrix |
| --- | --- |
| HR@10 evidence | Implemented in `scripts/validation/evaluate_uid_topk.py` as whether at least one relevant test item is hit; summarized in `thesis_analysis_pack/final_accuracy_summary_table.md`; per-row evidence paths listed in `reports/tables/canonical_native_path_status_matrix.csv`. |
| NDCG@10 evidence | Implemented in `scripts/validation/evaluate_uid_topk.py` with ideal hits `min(K, number_of_relevant_items)`; also present in `xrecsys/metrics.py`. Strict values are in per-row `accuracy.json` files and `thesis_analysis_pack/final_accuracy_summary_table.md`. |
| Precision@10 evidence | Implemented in `scripts/validation/evaluate_uid_topk.py`; precision divides by `topk`, including short-list handling. Strict values are in `thesis_analysis_pack/final_accuracy_summary_table.md`. |
| Recall@10 evidence | Implemented in `scripts/validation/evaluate_uid_topk.py` as hit count divided by the number of relevant test items; summarized in `thesis_analysis_pack/final_accuracy_summary_table.md`. |
| short-list / empty-list handling evidence | `docs/guides/CANONICAL_DATASET_STANDARD.md` defines short native-path lists as allowed only for candidate exhaustion. `scripts/validation/evaluate_uid_topk.py` reports exact-K users, short users, empty users, min/max/mean items, and slot coverage. |
| LIR definition and implementation evidence | Definition in `docs/guides/PATH_METRICS_GUIDE.md`: recency of the path's linked historical interaction. Implementation: `xrecsys/metrics.py` functions `LIR_single`, `topk_LIR`, `avg_LIR`. Trade-off evidence: `*_LIR_*_models.csv` in canonical LastFM/ML-1M bundles. |
| SEP definition and implementation evidence | Definition in `docs/guides/PATH_METRICS_GUIDE.md`: serendipity/low-degree bridge entity in the explanation path. Implementation: `xrecsys/metrics.py` functions `SEP_single`, `topks_SEP`, `avg_SEP`. Trade-off evidence: `*_SEP_*_models.csv` in canonical bundles. |
| ETD definition and implementation evidence | Definition in `docs/guides/PATH_METRICS_GUIDE.md`: diversity of explanation path types in top-k recommendations. Implementation: `xrecsys/metrics.py` functions `topk_ETD`, `avg_ETD`; denominator in `xrecsys/myutils.py` `TOTAL_PATH_TYPES`. Trade-off evidence: `*_ETD_*_models.csv` in canonical bundles. |
| strict accuracy vs alpha-sweep distinction evidence | Strict accuracy values come from per-row `accuracy.json` files and final accuracy table. Alpha-sweep CSVs contain `model,alpha,<accuracy metric>,<explanation metric>` and are trade-off evidence. The distinction is explicitly noted in `thesis_analysis_pack/final_explanation_summary_table.md` and `thesis_analysis_pack/generated_figure_captions.md`. |

Suggested Table 3.3 content:

| Metric | Family | Computed from | Primary implementation/evidence | Use in dissertation |
| --- | --- | --- | --- | --- |
| HR@10 | Strict accuracy | `uid_topk.csv` vs canonical `test_label.pkl` | `scripts/validation/evaluate_uid_topk.py`; per-row `accuracy.json` | Chapter 5 accuracy results |
| NDCG@10 | Strict accuracy | ranked top-k hits vs canonical labels | `scripts/validation/evaluate_uid_topk.py`; per-row `accuracy.json` | Chapter 5 accuracy results and alpha-sweep x-axis |
| Precision@10 | Strict accuracy | top-k hits / K | `scripts/validation/evaluate_uid_topk.py` | Chapter 5 accuracy results |
| Recall@10 | Strict accuracy | top-k hits / relevant test items | `scripts/validation/evaluate_uid_topk.py` | Chapter 5 accuracy results |
| LIR | Explanation/trade-off | native explanation path plus train timestamps | `docs/guides/PATH_METRICS_GUIDE.md`; `xrecsys/metrics.py`; alpha CSVs | Chapter 5 explanation/trade-off |
| SEP | Explanation/trade-off | bridge entity degree / SEP matrix | `docs/guides/PATH_METRICS_GUIDE.md`; `xrecsys/metrics.py`; alpha CSVs | Chapter 5 explanation/trade-off |
| ETD | Explanation/trade-off | path type diversity over top-k paths | `docs/guides/PATH_METRICS_GUIDE.md`; `xrecsys/metrics.py`; alpha CSVs | Chapter 5 explanation/trade-off |

## 3.5 Validation and Verification Protocol

| Required item | Evidence matrix |
| --- | --- |
| validation checks | Exact canonical test-user coverage when required; `uid_topk.csv` schema; duplicate users/items; canonical test-user membership; seen-item leakage from train/valid; path start/end endpoint consistency; top-k/explanation agreement; explanation path appears in candidate paths; finite score range; non-empty candidate paths. |
| validation script path | `scripts/validation/validate_xrecsys_export.py`; strict accuracy checker `scripts/validation/evaluate_uid_topk.py`; evidence aggregation `scripts/analysis/validate_canonical_export_evidence.py`. |
| validation manifest path | `reports/tables/canonical_export_validation/manifest.json`; per-row summaries under `reports/tables/canonical_export_validation/*.json`. |
| PASS/BLOCKED/N/A status evidence | PASS: `reports/tables/canonical_export_validation/manifest.json` has `exports=15`, `status=PASS`. BLOCKED/N/A: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json`; `thesis_analysis_pack/validation_status_table.md`. |
| framework feasibility evidence | 15 formal rows pass export validation: LastFM six models, ML-1M six models, Amazon-Book KGAT KGGLM/PEARLM/PGPR. Evidence: `thesis_analysis_pack/validation_status_table.md`. |
| Amazon boundary case evidence | Amazon formal comparison has KGGLM, PEARLM, PGPR complete with strict export/accuracy PASS, while UCPR/CAFE/TPRec are blocked. Amazon alpha-sweeps are N/A because there is no approved timestamp/SEP/ETD denominator. Evidence: `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json`. |

Suggested Table 3.4 content:

| Gate | What it prevents | Script/artifact | Result evidence |
| --- | --- | --- | --- |
| Canonical user coverage | Dropping hard users or comparing different test sets | `validate_xrecsys_export.py --require-all-test-users`; `evaluate_uid_topk.py` | `reports/tables/canonical_export_validation/manifest.json` |
| Seen-item exclusion | Recommending train/valid items as test predictions | `validate_xrecsys_export.py`; `evaluate_uid_topk.py` | per-row validation JSONs |
| Path endpoint consistency | Invalid or post-hoc paths not tied to the recommended item | `validate_xrecsys_export.py` | per-row validation JSONs |
| Top-k/explanation consistency | Explanations for different items than the recommendation list | `validate_xrecsys_export.py` | per-row validation JSONs |
| Score sanity | Non-finite or out-of-range path scores/probabilities | `validate_xrecsys_export.py` | per-row validation JSONs |
| Blocked-row reporting | Inventing missing model/dataset results | status matrix + Amazon readiness audit | `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json` |

## 3.6 Trade-off and Ablation Experiment Design

| Required item | Evidence matrix |
| --- | --- |
| alpha-sweep purpose evidence | Alpha sweeps evaluate how optimizing or reweighting explanation objectives changes recommendation metrics and path properties over a fixed native-path output space. Evidence: canonical trade-off CSV/PNG bundles; `thesis_analysis_pack/final_explanation_summary_table.md`; `thesis_analysis_pack/goal_10_insight_notes.md`. |
| alpha range and CSV columns | Canonical trade-off CSVs use alpha values from `0.0000` to `1.0000` in 0.05 steps. Example columns: `model,alpha,ndcg,LIR`; `model,alpha,hr,SEP`; `model,alpha,recall,ETD`. Evidence: files under `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` and `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`. |
| LIR sweep evidence | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv`; corresponding HR/Precision/Recall CSVs and PNGs. |
| SEP sweep evidence | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv`; corresponding HR/Precision/Recall CSVs and PNGs. |
| ETD sweep evidence | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv`; corresponding HR/Precision/Recall CSVs and PNGs. |
| HR/NDCG/Precision/Recall trade-off outputs | Each canonical bundle contains 12 CSV + 12 PNG files per main dataset: 3 explanation metrics x 4 accuracy metrics. Evidence: `reports/tables/canonical_native_path_status_matrix.md`; `thesis_analysis_pack/figure_caption_suggestions.md`. |
| ablation figures / CSVs | PGPR/UCPR path module ablation: `reports/tables/ablation/pgpr_ucpr_path_module/main_ablation_table_95pct_ndcg.csv`; `endpoint_comparison.csv`; `alpha0_baseline_preservation.csv`; `tradeoff_curves_long.csv`; figures `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg`; `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg`. |
| PGPR/UCPR path module ablation if available | Available. `alpha0_baseline_preservation.csv` records `status=PASS` for baseline preservation at alpha=0. `main_ablation_table_95pct_ndcg.csv` selects explanation-gain points with NDCG retention >= 95%. Use as supporting/appendix evidence unless Chapter 3 needs to define the ablation design. |
| mechanism family evidence for PGPR/UCPR/CAFE/TPRec/KGGLM/PEARLM | PGPR/UCPR/CAFE: native path baselines in `thesis_analysis_pack/model_scope_table.md`. TPRec: temporal native-path model, blocked on Amazon due to sentinel timestamps. KGGLM/PEARLM: path-language-model baselines with KG-constrained/generated paths. Evidence: `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`; `reports/tables/canonical_native_path_status_matrix.md`. |
| suggested Figure 3.2 | New diagram: Validated native-path export -> original top-k ranking at alpha=0 -> alpha grid 0.00 to 1.00 -> optimize LIR/SEP/ETD separately -> compute HR/NDCG/Precision/Recall plus LIR/SEP/ETD -> output trade-off curves and endpoint summaries. |
| caveats about what belongs in Chapter 3 vs Chapter 5 | Chapter 3 should define the alpha-sweep and ablation protocol and cite available CSV/figure evidence. Chapter 5 should interpret curves, compare models, and discuss trade-offs. Do not place final model ranking or Amazon limitation interpretation in Chapter 3 except as protocol boundaries. |

Suggested Table 3.5 content:

| Experiment design element | Dataset scope | Models | Output files | Evidence role | Caveat |
| --- | --- | --- | --- | --- | --- |
| Canonical alpha-sweep | LastFM, ML-1M | Six native-path models | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` | Main trade-off design evidence | Not strict accuracy evidence. |
| Thesis final trade-off figure | LastFM, ML-1M | Six native-path models | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | Chapter 5 visual summary | Derived from alpha-sweep CSVs. |
| Explanation endpoints | LastFM, ML-1M | Six native-path models | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png`; `thesis_analysis_pack/final_explanation_summary_table.md` | Endpoint comparison evidence | Values are alpha=0 to alpha=1, not strict accuracy. |
| PGPR/UCPR path-module ablation | LastFM, ML-1M | PGPR, UCPR | `reports/tables/ablation/pgpr_ucpr_path_module/`; `reports/figures/ablation/pgpr_ucpr_path_module/` | Supporting mechanism evidence | Prefer appendix unless needed to explain design. |
| Amazon boundary | Amazon-Book KGAT | KGGLM, PEARLM, PGPR complete; UCPR/CAFE/TPRec blocked | `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/amazon_classic_port_readiness.json` | Boundary/validation evidence | No Amazon explanation alpha-sweep claim. |
