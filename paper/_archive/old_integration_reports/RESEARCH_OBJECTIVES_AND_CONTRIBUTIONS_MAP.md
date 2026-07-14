# Research Objectives and Contributions Map

## 1. Objective Coverage

| Objective | Introduced in Chapter 1 | Supported by chapters | Evidence source | Status | Required action |
| --- | --- | --- | --- | --- | --- |
| O1. Design a canonical evaluation framework for native-path KG recommender systems. | Section 1.3; Objective O1 | Chapter 3, especially Sections 3.1 and 3.4 | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` | supported | Preserve the evaluation-framework wording; do not recast it as a recommender model. |
| O2. Construct canonical datasets and model-specific views. | Section 1.3; Objective O2 | Section 3.2; boundary implications in Sections 5.4–5.5 | `docs/guides/CANONICAL_DATASET_STANDARD.md`; canonical mapping and validation records | supported | Retain the distinction between shared canonical truth and model-specific internal representations. |
| O3. Define a native-path export contract. | Section 1.3; Objective O3 | Section 3.3 | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; export-validation records | supported | Keep post-hoc paths outside the native-path evidence class. |
| O4. Validate recommendations and explanations before reporting. | Section 1.3; Objective O4 | Sections 3.4–3.5; Section 5.4 | `reports/tables/canonical_export_validation/manifest.json`; `thesis_analysis_pack/validation_status_table.md` | supported | Preserve PASS, BLOCKED, and N/A as evidence-eligibility states rather than performance labels. |
| O5. Evaluate strict recommendation accuracy. | Section 1.3; Objective O5 | Sections 3.4–3.5 and 4.2 | `reports/tables/canonical_native_path_status_matrix.csv`; `thesis_analysis_pack/final_accuracy_summary_table.md` | partially supported | Retain the `0/12` primary JSON caveat and describe rankings as draft-level descriptive comparisons. |
| O6. Evaluate explanation quality through LIR, SEP, and ETD. | Section 1.3; Objective O6 | Sections 3.4 and 4.3–4.6 | `docs/guides/PATH_METRICS_GUIDE.md`; canonical trade-off CSVs; `balloccu2022xrecsys` | supported | Cite XRecSys for conceptual origin and internal guide/code for exact implementation; do not infer user-perceived quality. |
| O7. Perform controlled accuracy–explainability trade-off analysis. | Section 1.3; Objective O7 | Sections 3.6 and 4.4–4.7 | Canonical LastFM and ML-1M alpha-sweep CSV bundles | supported | Keep sweep ranking values separate from strict accuracy and avoid a universal operating-point claim. |
| O8. Analyse ablation, mechanism dependence, and boundary cases. | Section 1.3; Objective O8 | Chapter 5 | `reports/tables/ablation/pgpr_ucpr_path_module/`; candidate audit; Amazon readiness and validation records | partially supported | Treat PGPR/UCPR controllability as tested; retain non-PGPR/UCPR mechanism explanations as descriptive and Amazon as partial. |

## 2. Contribution Coverage

| Contribution | Claimed in Chapter 1 | Demonstrated in chapters | Evidence source | Status | Required action |
| --- | --- | --- | --- | --- | --- |
| C1. Canonical native-path evaluation framework | Section 1.4; Contribution 1 | Chapter 3; synthesised in Chapter 6 | Canonical standard, framework architecture, and validation records | supported | Keep the contribution at framework level. |
| C2. Validation-first native-path export contract | Section 1.4; Contribution 2 | Sections 3.3–3.5 and 5.4 | Export specification and validation manifest | supported | Preserve endpoint, alignment, coverage, and path-fidelity conditions. |
| C3. Separation of strict accuracy and explanation metrics | Section 1.4; Contribution 3 | Sections 3.4, 4.1–4.6, 5.3, and 6.1 | Strict summaries, alpha-sweep CSVs, and traceability separation log | supported | Do not substitute sweep or ablation NDCG for strict NDCG@10. |
| C4. Controlled alpha-sweep trade-off analysis | Section 1.4; Contribution 4 | Chapter 4 | Canonical LastFM and ML-1M trade-off bundles | supported | State metric-, model-, and dataset-specific profiles; avoid universal dominance or coefficient claims. |
| C5. PGPR/UCPR ablation-based controllability evidence | Section 1.4; Contribution 5 | Section 5.1 | `reports/tables/ablation/pgpr_ucpr_path_module/` and paired figures | supported | Keep the claim bounded to frozen-item-set path/explanation control, exact alpha=0 preservation, and the declared retention rule. |
| C6. Mechanism- and dataset-level interpretation | Section 1.4; Contribution 6 | Sections 5.2–5.3 | Chapter 4 observations, PGPR/UCPR ablation, repository mechanism audits, verified model papers | partially supported | Use causal wording only for the registered control test; describe CAFE, TPRec, KGGLM, and PEARLM explanations as context or hypotheses. |
| C7. Amazon-Book KGAT boundary-case detection | Section 1.4; Contribution 7 | Sections 3.5, 5.4–5.5, and 6.1 | Validation table, status matrix, and Amazon readiness report | supported | Keep three PASS and three BLOCKED/N/A rows visible; do not construct a complete six-model Amazon comparison. |
| C8. Traceable dissertation evidence package | Section 1.4; Contribution 8 | Chapters 3–6, integration maps, and traceability log | `THESIS_WRITING_TRACEABILITY_LOG.md`; citation/provenance closure; figure/table evidence paths | partially supported | Recover or archive the 12 strict-accuracy JSON artifacts and freeze final hashes before upgrading this to submission-level archival completeness. |

No mapped objective or contribution is unsupported at draft level. O5, O8, C6, and C8 require bounded wording because their primary provenance, causal scope, or archival completeness is partial.
