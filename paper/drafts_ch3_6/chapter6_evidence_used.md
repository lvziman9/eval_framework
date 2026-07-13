# Chapter 6 Evidence Used

## Evidence-Scope Rules

- Chapter 6 summarises claims already established in Chapters 3-5 and introduces no new experimental result.
- Strict accuracy, six-model alpha-sweep evidence, and PGPR/UCPR ablation evidence retain their separate roles.
- Amazon-Book KGAT is summarised only as a partial stress test and boundary case.
- Native-path and post-hoc explanations remain distinct; extending the framework to post-hoc baselines is a recommendation, not a completed result.
- No new external citation is used in Chapter 6.

## Conclusion Evidence Map

| Chapter 6 conclusion | Prior supported source | Evidence role | Boundary retained |
| :--- | :--- | :--- | :--- |
| The dissertation contributes a canonical native-path evaluation and analysis framework rather than a new recommender model. | `paper/drafts_ch3_6/chapter3_framework_implementation_and_verification_v2.md`; `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md` | Framework scope | No new-model or state-of-the-art claim. |
| The framework combines canonical datasets, model-specific views, native-path exports, validation, accuracy metrics, explanation metrics, and trade-off analysis. | `paper/drafts_ch3_6/chapter3_framework_implementation_and_verification_v2.md`; `paper/drafts_ch3_6/chapter3_evidence_used.md` | Methodology and validation | Chapter 6 does not add implementation stages. |
| LastFM and ML-1M provide complete six-model native-path comparisons. | `paper/drafts_ch3_6/chapter3_framework_implementation_and_verification_v2.md`; `thesis_analysis_pack/validation_status_table.md` | Validation scope | Amazon is excluded from this complete main scope. |
| Strict accuracy leadership and explanation-metric movement do not produce one universal model ordering. | `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`; `paper/drafts_ch3_6/chapter4_evidence_used.md` | Strict accuracy and alpha-sweep synthesis | No Chapter 4 table or new numeric result is repeated. |
| LIR, SEP, and ETD are distinct and non-interchangeable explanation dimensions. | `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`; `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md` | Metric interpretation | No generic explanation-superiority score is claimed. |
| The PGPR/UCPR ablation supports explanation-objective controllability under the registered preservation protocol. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `paper/drafts_ch3_6/chapter5_evidence_used.md` | Ablation synthesis | Controllability is not presented as recommender improvement or a main six-model result. |
| Trade-off behaviour is model-, dataset-, and metric-dependent. | `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`; `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md` | Alpha-sweep and mechanism synthesis | No new causal mechanism claim. |
| Amazon-Book KGAT demonstrates validation-first boundary detection. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `thesis_analysis_pack/validation_status_table.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md` | Boundary-case synthesis | Partial stress test only; blocked rows are not ranked and explanation sweeps remain N/A. |

## Recommendation-to-Limitation Map

| Recommendation | Limitation or boundary addressed | Supporting source | Current status |
| :--- | :--- | :--- | :--- |
| Complete UCPR, CAFE, and TPRec Amazon ports under the existing validation contract. | Three Amazon rows remain BLOCKED / N/A. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md` | Future work; no completion claim. |
| Extend canonical evaluation to additional datasets. | Complete six-model coverage is limited to LastFM and ML-1M. | `paper/drafts_ch3_6/chapter5_tables.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md` | Future work; no new dataset result. |
| Add a registered statistical analysis protocol. | No statistical-significance artifact was identified. | `paper/drafts_ch3_6/chapter5_evidence_used.md`; `paper/drafts_ch3_6/GOAL_4_STATUS.md` | Future work; current significance status requires manual check. |
| Add a user study or human evaluation. | Computational path metrics do not establish perceived usefulness. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `paper/drafts_ch3_6/chapter5_tables.md` | Future work; no current user-study evidence. |
| Develop path-grounded natural-language explanations. | Current evaluation concerns structured native paths rather than natural-language usefulness. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; native-path contract in Chapter 3 | Future work; no effectiveness claim. |
| Evaluate post-hoc explanation baselines in a separate group. | Post-hoc explanations are excluded from faithful native-path scoring. | `paper/drafts_ch3_6/chapter3_framework_implementation_and_verification_v2.md`; `paper/drafts_ch3_6/chapter5_tables.md` | Future work; native/post-hoc separation must remain explicit. |
| Test the robustness of LIR, SEP, and ETD. | LIR depends on timestamps, SEP on degree assumptions, and ETD on path taxonomy. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `paper/drafts_ch3_6/chapter5_tables.md` | Future work; primary metric citations require manual check. |
| Improve reporting and treatment of short or empty native-path lists. | Candidate exhaustion affects strict accuracy and slot coverage. | `paper/drafts_ch3_6/chapter5_ablation_mechanism_boundary_cases_v1.md`; `paper/drafts_ch3_6/chapter5_tables.md` | Future work; no post-hoc padding proposed as a completed method. |
| Verify UCPR, KGGLM, and metric primary sources and complete citation metadata. | Primary sources and venue/DOI metadata remain provisional. | `paper/drafts_ch3_6/EXTERNAL_CITATION_AUDIT.md`; `paper/drafts_ch3_6/GOAL_4_STATUS.md` | Requires manual check before final submission. |
| Consolidate the final reproducibility package. | Evidence is distributed across scripts, configurations, manifests, figures, and traceability records; historical files are not source of truth. | `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md`; `thesis_analysis_pack/goal_13_limitations_and_risks.md` | Future packaging work; no rerun performed in Goal 5. |

## Missing or Uncertain Evidence

- Primary sources for UCPR, KGGLM, and LIR/SEP/ETD remain unverified.
- Venue and DOI metadata for the existing medium-confidence citation seeds require manual check.
- No registered statistical-significance artifact or user-study artifact was identified.
- Natural-language explanation usefulness has not been evaluated; it is recommended future work only.
- Post-hoc explanation baselines have not been added to the reported experiment matrix; they are recommended as a separate future evaluation group.
- Amazon explanation alpha sweeps remain N/A under the current evidence.

## Required Inputs Check

All files explicitly listed as required inputs for Goal 5 were present and read. No required input path was missing during this drafting pass.

## Chapter 6 Artifact Decision

No Chapter 6 figure or table is required. The chapter provides a concise synthesis and recommendation set without repeating the result tables from Chapters 4 and 5.
