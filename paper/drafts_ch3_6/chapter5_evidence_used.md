# Chapter 5 Evidence Used

## Evidence-Scope Rules

- Strict accuracy evidence, six-model alpha-sweep evidence, and PGPR/UCPR ablation evidence are separate evidence streams.
- Native-path explanations are used for LIR, SEP, and ETD; post-hoc path recovery is excluded from the main explanation comparison.
- Amazon-Book KGAT is a partial stress test and boundary case, not a complete main experiment.
- Internal repository evidence supports experimental claims. External sources provide provisional mechanism context only and do not replace repository provenance.

## Internal Evidence Register

| Evidence path | Evidence category | Chapter 5 use | Boundary or caveat |
| :--- | :--- | :--- | :--- |
| `reports/tables/ablation/pgpr_ucpr_path_module/alpha0_baseline_preservation.csv` | Ablation validation | Exact alpha=0 preservation for PGPR and UCPR on LastFM and ML-1M across LIR, SEP, and ETD. | Supports baseline preservation only; not a model-improvement claim. |
| `reports/tables/ablation/pgpr_ucpr_path_module/main_ablation_table_95pct_ndcg.csv` | Ablation results | Selected operating points under the 95% NDCG-retention rule and explanation gains. | NDCG belongs to the ablation protocol over a frozen original top-k item set. |
| `reports/tables/ablation/pgpr_ucpr_path_module/provenance_validation.csv` | Ablation provenance | Export, accuracy, alpha=0, and slot-coverage checks for the four dataset-model rows. | PGPR is main; UCPR is auxiliary. |
| `reports/tables/ablation/pgpr_ucpr_path_module/endpoint_comparison.csv` | Ablation endpoint evidence | Context for endpoint movement and objective-specific response. | Not the Chapter 4 six-model endpoint table. |
| `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg` | Ablation figure | Figure 5.1(a). | Existing asset; no regeneration. |
| `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg` | Ablation figure | Figure 5.1(b). | Existing asset; no regeneration. |
| `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md` | Prior chapter synthesis | Key findings used for mechanism and interaction synthesis. | Full Chapter 4 tables are not repeated. |
| `paper/drafts_ch3_6/chapter4_evidence_used.md` | Prior chapter provenance | Strict accuracy and six-model alpha-sweep source separation. | Chapter 4 evidence roles remain unchanged. |
| `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` | Methodology | Native-path versus post-hoc boundary and model-scope rule. | Earlier implementation details are contextual; current completed status comes from later validation evidence. |
| `docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md` | Mechanism and scope audit | Mechanism families, native-path gate, and language-model constrained-generation context. | Mechanism-family context does not prove causal explanations of curve shapes. |
| `docs/guides/PATH_METRICS_GUIDE.md` | Metric implementation | LIR timestamp dependency, SEP bridge-degree dependency, and ETD path-taxonomy dependency. | Primary external source for these metrics remains unverified. |
| `thesis_analysis_pack/validation_status_table.md` | Validation evidence | Fifteen PASS rows and three Amazon BLOCKED / N/A rows; exact Amazon export counts. | BLOCKED / N/A is not model-performance failure. |
| `reports/tables/amazon_classic_port_readiness.json` | Boundary-case evidence | Detailed UCPR, CAFE, and TPRec blockers and PGPR readiness. | Amazon explanation alpha sweeps remain N/A. |
| `reports/figures/thesis_final/experiment_status_matrix.png` | Boundary-case figure | Figure 5.2. | Existing asset; visualises status rather than performance ranking. |
| `thesis_analysis_pack/goal_10_insight_notes.md` | Synthesis notes | Validation, native-path fidelity, metric complementarity, and short-list interpretation. | Used only where supported by primary repository evidence. |
| `thesis_analysis_pack/goal_11_chapter_5_material_pack.md` | Writing plan | Chapter 5 evidence and boundary guidance. | Its earlier section suggestions were adapted to the user-mandated Chapter 5 structure. |
| `thesis_analysis_pack/goal_13_limitations_and_risks.md` | Limitation register | Coverage, Amazon, metric provenance, short-list, and archive limitations. | Limitations are reported as boundaries, not concealed failures. |

## External Citation Status

| Citation key or need | Intended use | Audit status | Chapter 5 treatment |
| :--- | :--- | :--- | :--- |
| `wang2018pgpr` | PGPR mechanism context | Medium | Not treated as final verified citation; venue/DOI require manual check. |
| `xian2020cafe` | CAFE mechanism context | Medium | Not treated as final verified citation; venue/DOI require manual check. |
| `zhao2021tprec` | TPRec mechanism context | Medium | Not treated as final verified citation; venue/DOI require manual check. |
| `balloccu2023pearlm` | PEARLM mechanism context | Medium | Not treated as final verified citation; venue/DOI require manual check. |
| `wang2019kgat` | Amazon dataset-name background context | Medium | Not required for experimental claims; venue/DOI require manual check. |
| `ucpr_manual_check` | UCPR mechanism | Low / unverified | No final citation used; mechanism origin requires manual check. |
| `kgglm_manual_check` | KGGLM mechanism | Low / unverified | No final citation used; mechanism origin requires manual check. |
| `xrecsys_metrics_manual_check` | LIR, SEP, and ETD origin | Low / unverified | Internal implementation evidence used; external origin requires manual check. |

## Missing or Uncertain Evidence

- No CAFE-, TPRec-, KGGLM-, or PEARLM-specific mechanism ablation is registered in the current evidence pack. Causal explanations of their curve shapes are unsupported.
- Candidate-path flexibility was not independently measured. Any interpretation linking smaller endpoint movement to restricted candidate flexibility requires manual check.
- No user-study artifact was identified. Chapter 5 makes no claim about perceived usefulness, clarity, or persuasiveness.
- No statistical-significance test artifact was identified in the registered evidence pack. Its final status requires manual check.
- UCPR, KGGLM, and LIR/SEP/ETD primary citations remain unverified. Other Chapter 5 citation seeds have medium confidence and require venue/DOI checks.
- Amazon explanation alpha sweeps are N/A because an approved timestamp, SEP, and ETD denominator protocol is not registered.

## Required Inputs Check

All files explicitly listed as required inputs for Goal 4 were present. No required input path was missing during this drafting pass.
