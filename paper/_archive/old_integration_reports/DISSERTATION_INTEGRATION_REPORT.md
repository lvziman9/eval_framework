# Dissertation Integration Report

## 1. Source Readiness

| Source | Status | Used for | Notes |
| --- | --- | --- | --- |
| `research-writing-skill` | available and loaded | Argument alignment, English academic prose, claim restraint, and section integration | Thesis-specific evidence rules override generic writing guidance. |
| `scientific-toolkit-skill` | available and loaded | Citation/provenance checks and reproducibility-oriented source audit | No computation, retraining, or new experiment was run. |
| `office-academic-skill` | available and loaded for boundary control | Later Word/NTU packaging boundary | No DOCX, PDF, PPTX, or LaTeX artifact was generated. |
| Eight Chapter 2 literature outputs in `paper/literature/review_outputs/` | present | Chapter 2 v2, Chapter 1 background, citation and gap maps | The original Chapter 2 v1 remains unchanged. |
| `chapter3_story_revised_v1.md` | present | Chapter 3 integrated baseline | Original SHA256: `ff335a3e300d72d779974318a62123bbb0810983d00c4fca23221b852989f40a`. |
| `chapter4_story_revised_v1.md` | present | Chapter 4 integrated baseline | Original SHA256: `509c5430e0686166efbe348cae31dc047feb95d91bccd228151c5f28d85705e7`. |
| `chapter5_story_revised_v1.md` | present | Chapter 5 integrated baseline | Original SHA256: `d8ea973ddb2cbb4d468cda7bb0518d93646c10531ea49e7fca2d35f9eef545a9`. |
| `chapter6_story_revised_v1.md` | present | Chapter 6 integrated baseline | Original SHA256: `39643b4bc78111be869c26d6ab4242c7b4712a5f0a431519c097b93945ad11e9`. |
| Narrative spine, revision plan, changelog, and status | present | Cross-chapter argument and transition controls | The integration preserves Sections 3.1–3.6, 4.1–4.7, 5.1–5.5, and 6.1–6.2. |
| Citation and provenance closure package | present | Current citation statuses and strict-accuracy provenance | This package is newer and authoritative where older story-revised citation caveats conflict with it. |
| Verified BibTeX register | present | Chapter 1–6 model and metric citation keys | PGPR uses `xian2019pgpr`; `wang2018pgpr` is prohibited. |
| Chapter 2 BibTeX additions | present | Literature-review citation keys | Twenty-five non-duplicate additions are available. |
| `THESIS_WRITING_TRACEABILITY_LOG.md` | present | Evidence-role and claim-boundary control | Only an integration record may be appended. Existing evidence semantics must remain unchanged. |
| Chapter boundary and figure/table master plans | present | Section scope and numbering | Chapter boundaries match the requested Chapter 1–6 structure. |
| Nine specified `thesis_analysis_pack` inputs | present | Accuracy, explanation, validation, ablation, limitations, and figure context | All named source files in the Goal are accessible. |
| Core Figure 3.1–3.2, 4.1–4.4, and 5.1–5.2 assets | present | Figure integration plan | No regeneration is required. |
| Optional SEP/ETD figures for Figures 4.5–4.6 | present | Appendix candidates | Retained outside the four-figure Chapter 4 core. |

## 2. Missing or Partial Sources

| Missing / partial source | Impact | Required action |
| --- | --- | --- |
| Twelve expected LastFM/ML-1M row-level strict-accuracy JSON artifacts (`0/12` accessible) | Prevents primary-artifact closure and direct-inspection claims for strict values. | Recover and archive the original JSON files, or retain the explicit summary-level provenance limitation. |
| Statistical-significance artifact | Model and trade-off differences cannot be described as statistically significant. | Add only through a separately approved repeated-run/statistical-analysis task; keep current comparisons descriptive. |
| User-study artifact | LIR, SEP, and ETD cannot establish perceived usefulness, clarity, persuasion, or trust. | Retain human-facing outcomes as future work. |
| PEARLM final venue and publisher DOI | Final bibliography metadata remains partial. | Cite `balloccu2023pearlm` as arXiv and manually check final proceedings metadata before submission. |
| “Measuring Why” final venue and publisher DOI | A final publication claim would be unsupported. | The integrated draft omits the citation; decide later whether to retain the verified arXiv record or omit it. |
| Targeted mechanism ablations for CAFE, TPRec, KGGLM, and PEARLM | Observed curve shapes cannot be causally attributed to their architectural families. | Keep mechanism explanations descriptive and propose targeted tests as future work. |
| Approved Amazon timestamp, SEP, and ETD denominator protocol | Amazon explanation alpha sweeps remain unavailable. | Do not report Amazon explanation sweeps until the protocol and blocked ports are completed. |
| Submission-level immutable evidence and bibliography snapshot | The package is traceable at draft level but not frozen for submission. | Record final hashes, commands, versions, bibliography, and recovered primary artifacts in a later packaging goal. |

## 3. Integration Constraints

- The dissertation contribution is a canonical native-path evaluation and analysis framework, not a new recommender model.
- Chapter 1–6 use only the specified section structure; no additional numbered first-level sections are introduced.
- External publications support literature, model, and metric context only. Internal repository artifacts support experimental values and validation states.
- Strict accuracy, alpha-sweep, ablation, validation, and boundary-case evidence retain separate claim roles.
- Original Chapter 2 and Chapter 3–6 story-revised files are read-only baselines for this Goal.
- Integrated Chapter 3–6 copies receive only transition, terminology, citation-key, figure/table-reference, and current-caveat edits.
- Existing numerical values, table/figure identifiers, evidence paths, and Amazon statuses are not changed.
- Contradictions are recorded rather than silently absorbed. In particular, Chapter 5 story-revised text predates citation closure and incorrectly labels UCPR, CAFE, TPRec, KGGLM, and XRecSys/LIR/SEP/ETD sources as unverified. The integrated copy adopts the later verified register and preserves only unresolved citation caveats.
- No front matter, final reference list, NTU template styling, Word, PDF, PPTX, or LaTeX output is part of this Goal.

## 4. Caveats to Preserve

1. Strict-accuracy primary JSON artifacts: `0/12` accessible.
2. Current strict-accuracy provenance: `reports/tables/canonical_native_path_status_matrix.csv` plus the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`.
3. PEARLM final venue and publisher DOI require manual checking.
4. The “Measuring Why” final venue and publisher DOI require manual checking if the citation is used; it is omitted from the current integrated draft.
5. No statistical-significance artifact is registered.
6. No user-study artifact is registered.
7. Amazon-Book KGAT is a partial boundary case with three PASS and three BLOCKED/N/A rows; its explanation alpha sweeps are N/A.
8. LIR, SEP, and ETD have a verified external conceptual source, but their exact evaluated implementation is repository-specific.
9. Non-PGPR/UCPR mechanism explanations are descriptive rather than causal proof; even PGPR/UCPR causal wording must remain bounded to the registered ablation control.

The source package is sufficient for a complete internal Markdown integration. It is not sufficient for final evidence archiving, final bibliography freezing, NTU formatting, or an unqualified supervisor-submission claim.
