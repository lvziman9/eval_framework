# Thesis Writing Traceability Log

## 0. Purpose

This file records the provenance of all internal evidence, external citations, figures, tables, and claims used during the drafting of Chapter 3-6.

---

## 1. Phase Progress Log

| Phase | Status | Files generated | Evidence used | Citation work | Open issues |
|---|---|---|---|---|---|
| Phase 0 Global Plan and Boundary Audit | Completed | `PHASE_0_GLOBAL_PLAN.md`; `CHAPTER_BOUNDARY_MAP.md`; `FIGURE_TABLE_MASTER_PLAN.md`; `CITATION_NEEDS_INITIAL.md`; `THESIS_WRITING_TRACEABILITY_LOG.md` | Thesis handoff, Chapter 3 material pack, result summaries, validation table, guides, figure inventory. | Initial citation needs listed. | Later phases must continue claim mapping. |
| Phase 1 External Citation Audit | Completed with caveats | `EXTERNAL_CITATION_AUDIT.md`; `BIBTEX_SEED.bib` | External search results from arXiv-facing pages and available primary-source search snippets. | Seeds created for PGPR/KPRN, CAFE, TPRec, KGAT, KGIN, LightGCN, PEARLM, surveys. | UCPR, KGGLM, and XRecSys/LIR/SEP/ETD primary citations not verified. Venue/DOI metadata requires manual check. |
| Phase 2 Chapter 3 Draft | Completed draft pass and self-review pass | `chapter3_framework_implementation_and_verification_v2.md`; `chapter3_tables.md`; `chapter3_figure_specs.md`; `chapter3_evidence_used.md` | Canonical dataset guide, native-path architecture guide, path metric guide, validation table, accuracy table, explanation table. | External citations recorded as background seeds only. | Figure 3.1 and Figure 3.2 are planned, not generated. |

---

## 2. Internal Repository Evidence Register

| Evidence ID | Repo-relative path | Evidence type | Used in chapter / section | Claim supported | Notes |
|---|---|---|---|---|---|
| INT-001 | `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md` | methodology evidence | Ch.3-6 planning | Dissertation is an evaluation framework, not a new recommender model; LastFM/ML-1M complete; Amazon partial stress test. | Source-of-truth handoff. |
| INT-002 | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` | methodology evidence | Ch.3 | Chapter 3 pipeline: canonical layer, model views, export contract, validation gate, metrics, report layer. | Main Chapter 3 source. |
| INT-003 | `docs/guides/CANONICAL_DATASET_STANDARD.md` | methodology evidence | Ch.3.2 | Canonical datasets define shared users, products, splits, labels, KG provenance, and mapping requirements. | Primary canonical standard. |
| INT-004 | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` | methodology evidence | Ch.3.1, Ch.3.3 | Explainability scoring is limited to native-path models; non-path models are accuracy-only references. | Supports native/post-hoc separation. |
| INT-005 | `docs/guides/PATH_METRICS_GUIDE.md` | methodology evidence | Ch.3.3, Ch.3.4 | LIR, SEP, and ETD depend on native path structure and different path positions. | Internal metric evidence. |
| INT-006 | `thesis_analysis_pack/validation_status_table.md` | validation evidence | Ch.3.4, Ch.3.5 | LastFM/ML-1M six-model rows pass; Amazon has three pass and three blocked/N/A rows. | Validation summary. |
| INT-007 | `thesis_analysis_pack/final_accuracy_summary_table.md` | strict accuracy evidence | Ch.3.5 | Strict accuracy values exist for completed rows. | Must not be mixed with alpha-sweep metrics. |
| INT-008 | `thesis_analysis_pack/final_explanation_summary_table.md` | alpha-sweep evidence | Ch.3.5, Ch.3.6 | LIR/SEP/ETD alpha endpoints exist for LastFM and ML-1M; Amazon explanation metrics are N/A. | Endpoint evidence only. |
| INT-009 | `reports/tables/ablation/pgpr_ucpr_path_module/` | ablation evidence | Ch.3.6, planned Ch.5 | Ablation evidence exists for later controllability and mechanism analysis. | Chapter 3 mentions setup only. |
| INT-010 | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | figure evidence | Planned Ch.4 | LastFM strict accuracy figure exists. | Existing figure; not regenerated. |
| INT-011 | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | figure evidence | Planned Ch.4 | ML-1M strict accuracy figure exists. | Existing figure; not regenerated. |
| INT-012 | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | figure evidence | Planned Ch.4 | Explanation endpoint figure exists. | Existing figure; not regenerated. |
| INT-013 | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | figure evidence | Planned Ch.4 | LIR-NDCG trade-off figure exists. | Existing figure; not regenerated. |
| INT-014 | `reports/figures/thesis_final/experiment_status_matrix.png` | figure evidence | Planned Ch.5 | Complete and blocked experiment rows are visualised. | Existing figure; not regenerated. |
| INT-015 | `reports/tables/amazon_classic_port_readiness.json` | boundary-case evidence | Ch.3.5, planned Ch.5 | Amazon UCPR/CAFE/TPRec limitations are implementation/data-contract boundary cases. | Do not treat blocked rows as performance failures. |

---

## 3. External Citation Register

| Citation ID | Citation key | Claim supported | Paper title | Authors | Year | Venue / source | URL / DOI / arXiv | Used in chapter | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| EXT-001 | `wang2018pgpr` | KG path reasoning can produce recommendation paths used as explanations. | Explainable Reasoning over Knowledge Graphs for Recommendation | Xiang Wang et al. | 2018 | arXiv | https://arxiv.org/abs/1811.04540 | Ch.3 background; planned Ch.5 | Medium | Venue/DOI and exact PGPR naming require manual check. |
| EXT-002 | `xian2020cafe` | CAFE uses coarse-to-fine neural symbolic reasoning for explainable recommendation. | CAFE: Coarse-to-Fine Neural Symbolic Reasoning for Explainable Recommendation | Yikun Xian et al. | 2020 | arXiv | https://arxiv.org/abs/2010.15620 | Ch.3 model context | Medium | Venue/DOI require manual check. |
| EXT-003 | `zhao2021tprec` | TPRec is time-aware path reasoning for KG recommendation. | Time-aware Path Reasoning on Knowledge Graph for Recommendation | Yuyue Zhao et al. | 2021 | arXiv | https://arxiv.org/abs/2108.02634 | Ch.3 model context | Medium | Venue/DOI require manual check. |
| EXT-004 | `wang2019kgat` | KGAT models high-order KG connectivity through attention. | KGAT: Knowledge Graph Attention Network for Recommendation | Xiang Wang et al. | 2019 | arXiv | https://arxiv.org/abs/1905.07854 | Planned Ch.5 boundary context | Medium | Venue/DOI require manual check. |
| EXT-005 | `wang2021kgin` | KGIN models user intents and relational paths over a KG. | Learning Intents behind Interactions with Knowledge Graph for Recommendation | Xiang Wang et al. | 2021 | arXiv | https://arxiv.org/abs/2102.07057 | Background only | Medium | Venue/DOI require manual check. |
| EXT-006 | `he2020lightgcn` | LightGCN is a graph collaborative filtering reference model. | LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation | Xiangnan He et al. | 2020 | arXiv | https://arxiv.org/abs/2002.02126 | Background only | Medium | Venue/DOI require manual check. |
| EXT-007 | `balloccu2023pearlm` | PEARLM uses language modelling and KG-constrained decoding for faithful paths. | Faithful Path Language Modeling for Explainable Recommendation over Knowledge Graph | Giacomo Balloccu et al. | 2023 | arXiv | https://arxiv.org/abs/2310.16452 | Ch.3 model context | Medium | Venue/DOI require manual check. |
| EXT-008 | `zhang2018explainableSurvey` | Explainable recommendation includes model-intrinsic and post-hoc explanation settings. | Explainable Recommendation: A Survey and New Perspectives | Yongfeng Zhang; Xu Chen | 2018 | arXiv | https://arxiv.org/abs/1804.11192 | Background only | Medium | Use for general framing only. |
| EXT-009 | `chen2022measuringWhy` | Explanation evaluation requires explicit evaluation methods and perspectives. | Measuring "Why" in Recommender Systems | Xu Chen et al. | 2022 | arXiv | https://arxiv.org/abs/2202.06466 | Metric context | Medium | Use for evaluation framing only. |
| EXT-010 | `guo2020kgsurvey` | KG recommender systems use KGs for recommendation and explanation. | A Survey on Knowledge Graph-Based Recommender Systems | Qingyu Guo et al. | 2020 | arXiv | https://arxiv.org/abs/2003.00911 | Background only | Medium | Use for background only. |
| EXT-011 | `ucpr_manual_check` | UCPR origin and mechanism. | Not found with available search. Do not cite until manually verified. | requires manual check | requires manual check | requires manual check | requires manual check | Planned Ch.3/Ch.5 if verified | Low | Open citation gap. |
| EXT-012 | `kgglm_manual_check` | KGGLM origin and mechanism. | Not found with available search. Do not cite until manually verified. | requires manual check | requires manual check | requires manual check | requires manual check | Planned Ch.3/Ch.5 if verified | Low | Open citation gap. |
| EXT-013 | `xrecsys_metrics_manual_check` | XRecSys/LIR/SEP/ETD primary source. | Not found with available search. Do not cite until manually verified. | requires manual check | requires manual check | requires manual check | requires manual check | Ch.3 metric context | Low | Use repo implementation evidence meanwhile. |

---

## 4. Claim-to-Evidence Map

### Chapter 3 Claim Map

| Section | Claim | Evidence ID / Citation ID | Evidence type | Status |
|---|---|---|---|---|
| 3.1 | The dissertation contributes an evaluation framework, not a new recommender model. | INT-001; INT-002 | methodology evidence | Supported |
| 3.1 | The framework separates canonical dataset truth, model views, exports, validation, and reporting. | INT-002; INT-003; INT-004 | methodology evidence | Supported |
| 3.2 | Canonical datasets define shared identifiers, splits, labels, KG provenance, and mapping requirements. | INT-003 | methodology evidence | Supported |
| 3.2 | LastFM and ML-1M are complete six-model datasets; Amazon-Book KGAT is partial. | INT-001; INT-006 | validation evidence | Supported |
| 3.3 | Native-path rows require `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv`. | INT-004; INT-005 | methodology evidence | Supported |
| 3.3 | Non-path models should not receive LIR/SEP/ETD scores without native paths. | INT-004 | methodology evidence | Supported |
| 3.4 | Strict accuracy metrics and explanation metrics come from different evidence streams. | INT-005; INT-007; INT-008 | methodology / strict accuracy / alpha-sweep evidence | Supported |
| 3.5 | LastFM and ML-1M have six PASS rows. | INT-006 | validation evidence | Supported |
| 3.5 | Amazon-Book KGAT has three PASS rows and three blocked/N/A rows. | INT-006; INT-015 | boundary-case evidence | Supported |
| 3.5 | Alpha-sweep endpoints verify trade-off pipeline operation but are not strict accuracy values. | INT-008 | alpha-sweep evidence | Supported |
| 3.6 | Ablation evidence is separate from the main six-model result set. | INT-009 | ablation evidence | Supported |

### Chapter 4 Claim Map

| Section | Claim | Evidence ID / Citation ID | Evidence type | Status |
|---|---|---|---|---|
| 4.1-4.7 | Chapter 4 not drafted in this pass. | N/A | N/A | Pending |

### Chapter 5 Claim Map

| Section | Claim | Evidence ID / Citation ID | Evidence type | Status |
|---|---|---|---|---|
| 5.1-5.5 | Chapter 5 not drafted in this pass. | N/A | N/A | Pending |

### Chapter 6 Claim Map

| Section | Claim | Evidence ID / Citation ID | Evidence type | Status |
|---|---|---|---|---|
| 6.1-6.2 | Chapter 6 not drafted in this pass. | N/A | N/A | Pending |

---

## 5. Figure and Table Provenance

| Figure/Table | Chapter | Source file / generated from | Evidence type | Notes |
|---|---|---|---|---|
| Figure 3.1 | 3 | Planned conceptual figure from INT-002, INT-003, INT-004 | methodology evidence | Not generated in this phase. |
| Figure 3.2 | 3 | Planned conceptual figure from INT-007 and alpha-sweep CSV bundles | alpha-sweep evidence | Not generated in this phase. |
| Tables 3.1-3.7 | 3 | `chapter3_tables.md` generated from INT-002 to INT-009 | methodology / validation / strict accuracy / alpha-sweep / ablation evidence | Draft tables generated. |
| Figure 4.1 | 4 | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | figure evidence | Existing figure; planned. |
| Figure 4.2 | 4 | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | figure evidence | Existing figure; planned. |
| Figure 4.3 | 4 | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | figure evidence | Existing figure; planned. |
| Figure 4.4 | 4 | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | figure evidence | Existing figure; planned. |
| Figure 5.1 | 5 | `reports/figures/ablation/pgpr_ucpr_path_module/` | ablation evidence | Existing figures; planned. |
| Figure 5.2 | 5 | `reports/figures/thesis_final/experiment_status_matrix.png` | boundary-case evidence | Existing figure; planned. |

---

## 6. Unsupported or Uncertain Claims

| Claim | Intended chapter | Problem | Required action | Status |
|---|---|---|---|---|
| Exact venue/DOI metadata for arXiv citation seeds. | Ch.3-6 | Search verified arXiv pages but not publisher metadata. | Manually check against ACM/IEEE/Springer/AAAI/WWW/KDD/SIGIR records. | Open |
| UCPR model citation. | Ch.3/Ch.5 | Not found with available search. | Add only after primary source is verified. | Open |
| KGGLM model citation. | Ch.3/Ch.5 | Not found with available search. | Add only after primary source is verified. | Open |
| XRecSys/LIR/SEP/ETD primary publication. | Ch.3 | Not found with available search. | Use internal implementation docs unless verified. | Open |
| Any claim that Amazon-Book KGAT is a complete main trade-off experiment. | Ch.4/Ch.5 | Contradicted by current evidence. | Do not write this claim. | Blocked / excluded |

---

## 7. Strict Accuracy vs Alpha-Sweep Separation Log

| Item | Source file | Evidence category | Can be used for | Must not be used for |
|---|---|---|---|---|
| Strict accuracy summary | `thesis_analysis_pack/final_accuracy_summary_table.md` | strict accuracy evidence | HR@10, NDCG@10, Precision@10, Recall@10 strict results. | Explanation endpoint claims or alpha-sweep trade-off curves. |
| Accuracy JSON files | Paths listed in `thesis_analysis_pack/final_accuracy_summary_table.md` | strict accuracy evidence | Exact completed-row accuracy values. | LIR/SEP/ETD endpoint claims. |
| Explanation summary table | `thesis_analysis_pack/final_explanation_summary_table.md` | alpha-sweep evidence | LIR/SEP/ETD alpha=0 -> alpha=1 endpoint summaries. | Strict accuracy replacement. |
| Trade-off CSV bundles | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` | alpha-sweep evidence | Trade-off curves and endpoint analysis. | Baseline strict accuracy reporting. |
| PGPR/UCPR ablation tables | `reports/tables/ablation/pgpr_ucpr_path_module/` | ablation evidence | Chapter 5 controllability and mechanism analysis. | Main six-model result table. |

---

## 8. Amazon-Book KGAT Boundary Log

| Claim | Evidence path | Status | How to phrase in thesis |
|---|---|---|---|
| Amazon-Book KGAT has complete rows for KGGLM, PEARLM, and PGPR. | `thesis_analysis_pack/validation_status_table.md`; `thesis_analysis_pack/final_accuracy_summary_table.md` | Supported | "Amazon-Book KGAT provides a partial stress test with three complete rows." |
| Amazon-Book KGAT UCPR is blocked. | `reports/tables/amazon_classic_port_readiness.json`; `thesis_analysis_pack/validation_status_table.md` | Supported | "UCPR remains blocked for strict full-user export/accuracy under the current formal pipeline evidence." |
| Amazon-Book KGAT CAFE is blocked. | `reports/tables/amazon_classic_port_readiness.json`; `thesis_analysis_pack/validation_status_table.md` | Supported | "CAFE requires additional Amazon schema/data-builder support before it can be treated as a complete row." |
| Amazon-Book KGAT TPRec is blocked. | `reports/tables/amazon_classic_port_readiness.json`; `thesis_analysis_pack/validation_status_table.md` | Supported | "TPRec remains blocked because the temporal path requirement is not satisfied by the current sentinel timestamp setting." |
| Amazon-Book KGAT explanation alpha sweeps are available. | `thesis_analysis_pack/final_explanation_summary_table.md` | Unsupported | Do not claim; phrase as "Amazon explanation alpha sweeps are N/A under current evidence." |

---

## 9. Final Audit Notes

- Fully supported chapters: Chapter 3 draft package is supported at draft level.
- Chapters needing manual citation check: Chapter 3 citation formatting; future Chapters 4-6 if they use model background citations.
- Figures needing drawing: Figure 3.1 and Figure 3.2 are planned conceptual figures, not generated.
- Tables needing manual formatting: Tables 3.1-3.7 may need NTU template formatting later.
- Claims to remove if evidence cannot be verified: UCPR external citation claims, KGGLM external citation claims, XRecSys primary-publication claims, and any Amazon complete-trade-off claim.

