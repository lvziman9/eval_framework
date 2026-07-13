# Consistency Review for Chapter 3–6

## 1. Chapter Boundary Review

| Check | Status | Evidence | Required action |
|---|---|---|---|
| Chapter 3 is limited to framework implementation and verification. | PASS | `chapter3_framework_implementation_and_verification_v2.md`; `CHAPTER_BOUNDARY_MAP.md` | Preserve the current boundary in all revisions. |
| Chapter 4 reports accuracy and explainability trade-off results without introducing ablation claims. | PASS | `chapter4_accuracy_explainability_tradeoff_results_v1.md`; `chapter4_evidence_used.md` | Preserve the separation between strict accuracy and alpha-sweep evidence. |
| Chapter 5 contains ablation, mechanism analysis, and boundary cases. | PASS | `chapter5_ablation_mechanism_boundary_cases_v1.md`; `chapter5_evidence_used.md` | Keep causal wording restricted to the registered PGPR and UCPR ablation evidence. |
| Chapter 6 contains conclusions and recommendations only. | PASS | `chapter6_conclusion_and_recommendations_v1.md`; `chapter6_evidence_used.md` | Do not add new empirical claims or results to the conclusion. |
| Chapter 1–2 integration remains outside the current package. | PASS | `GOAL_5_STATUS.md`; `THESIS_WRITING_TRACEABILITY_LOG.md` | Defer integration until the next dissertation-wide review stage. |

## 2. Evidence Separation Review

| Evidence type | Correct use | Misuse found? | Location | Required action |
|---|---|---|---|---|
| Validation evidence | Establishes which dataset-model combinations are usable and which are blocked. | No | Chapters 3 and 5; `chapter3_evidence_used.md`; `chapter5_evidence_used.md` | Retain validation as an evidence gate, not as a performance result. |
| Strict accuracy evidence | Supports the twelve LastFM and ML-1M model-dataset accuracy comparisons. | No | Chapter 4, Section 4.2; `thesis_analysis_pack/final_accuracy_summary_table.md`; `reports/tables/canonical_native_path_status_matrix.csv` | Preserve the distinction from alpha-sweep endpoints and complete primary-JSON provenance checks before final submission. |
| Six-model alpha-sweep evidence | Supports the observed LIR, SEP, and ETD response profiles. | No | Chapter 4, Sections 4.3–4.6; `thesis_analysis_pack/final_explanation_summary_table.md`; registered bundles under `reports/figures/tradeoff/` | Do not describe alpha-sweep endpoint accuracy as strict accuracy. |
| PGPR and UCPR ablation evidence | Supports exact alpha-zero preservation and selected trade-off statements for the registered ablation scope. | No | Chapter 5, Section 5.1; `chapter5_tables.md` | Keep model-improvement and universal-causality language excluded. |
| Amazon-Book validation evidence | Supports a partial boundary case with three passing and three blocked models. | No | Chapter 5, Section 5.4; Chapter 6, Sections 6.1–6.2 | Continue to describe Amazon-Book only as a partial stress or boundary case. |
| Native explanation exports | Support model-faithful explanation collection where available. | No | Chapter 3, Section 3.3; Chapter 5, Section 5.2 | Keep native explanation evidence separate from any post-hoc explanation concept. |
| Mechanism interpretation | Supports descriptive or plausible interpretation except where a registered ablation directly tests the mechanism. | No | Chapter 5, Sections 5.1–5.3 | Maintain explicit non-causal wording for CAFE, TPRec, KGGLM, and PEARLM. |

## 3. Figure and Table Consistency Review

| Item | Expected location | Current status | Evidence path | Required action |
|---|---|---|---|---|
| Figure 3.1 framework overview | Chapter 3, Section 3.1 | PASS | `figures/figure_3_1_framework_overview.png`; `chapter3_figure_specs.md` | Preserve the registered number and path. |
| Figure 3.2 alpha-sweep design | Chapter 3, Section 3.4 | PASS | `figures/figure_3_2_alpha_sweep_design.png`; `chapter3_figure_specs.md` | Preserve the registered number and path. |
| Figures 4.1–4.4 | Chapter 4, Sections 4.2–4.4 | PASS | `chapter4_figure_plan.md`; assets under `reports/figures/thesis_final/` and registered trade-off CSVs under `reports/figures/tradeoff/` | Preserve placement and captions in the revised chapter. |
| Optional Figures 4.5–4.6 | Chapter 4 appendix or optional diagnostic placement | REQUIRES MANUAL CHECK | `chapter4_figure_plan.md` | Decide final inclusion and placement during dissertation integration. |
| Figures 5.1–5.2 | Chapter 5, Sections 5.1 and 5.4 | PASS | `chapter5_figure_plan.md`; assets under `reports/figures/ablation/pgpr_ucpr_path_module/` and `reports/figures/thesis_final/` | Preserve the registered numbers and evidence boundaries. |
| Tables 3.1–3.7 | Chapter 3 | PASS | `chapter3_tables.md` | Preserve table content and numbering. |
| Tables 4.1–4.3 | Chapter 4 | PASS | `chapter4_tables.md` | Preserve all reported values and keep strict and sweep evidence separate. |
| Tables 5.1–5.4 | Chapter 5 | PASS | `chapter5_tables.md` | Preserve all values and caveats. |
| Earlier caption-placement suggestions | Earlier working notes place some trade-off figures in Chapter 5. | MINOR ISSUE | `thesis_analysis_pack/figure_caption_suggestions.md`; `thesis_analysis_pack/generated_figure_captions.md` | Treat the current chapter figure plans and master plan as authoritative; do not renumber assets. |

## 4. Citation and Traceability Review

| Item | Status | Evidence | Required action |
|---|---|---|---|
| Chapter 3–6 claim-to-evidence mapping | PASS | `THESIS_WRITING_TRACEABILITY_LOG.md` | Extend the log to register the story-revised drafts without changing existing claim status. |
| Primary citations for PGPR, CAFE, TPRec, and PEARLM | MINOR ISSUE | `EXTERNAL_CITATION_AUDIT.md`; `BIBTEX_SEED.bib` | Verify venue and DOI metadata before final submission. |
| Primary citations for UCPR and KGGLM | REQUIRES MANUAL CHECK | `CITATION_NEEDS_INITIAL.md`; `EXTERNAL_CITATION_AUDIT.md` | Locate and verify the primary sources before final submission. |
| Primary sources for LIR, SEP, and ETD | REQUIRES MANUAL CHECK | `CITATION_NEEDS_INITIAL.md`; `EXTERNAL_CITATION_AUDIT.md` | Add verified metric-origin sources during bibliography completion. |
| Strict-accuracy primary JSON provenance | REQUIRES MANUAL CHECK | `thesis_analysis_pack/final_accuracy_summary_table.md`; `reports/tables/canonical_native_path_status_matrix.csv`; `GOAL_5_STATUS.md` | Verify the twelve primary JSON artifacts or retain the provenance caveat. |
| Statistical-significance support | REQUIRES MANUAL CHECK | `THESIS_WRITING_TRACEABILITY_LOG.md`; `GOAL_5_STATUS.md` | Avoid significance wording unless a statistical artifact is added. |
| User-study support | REQUIRES MANUAL CHECK | `THESIS_WRITING_TRACEABILITY_LOG.md`; `GOAL_5_STATUS.md` | Avoid claims about perceived usefulness or human judgment. |
| Amazon-Book boundary traceability | PASS | `chapter5_evidence_used.md`; `chapter6_evidence_used.md`; `THESIS_WRITING_TRACEABILITY_LOG.md` | Preserve the partial-boundary wording. |
