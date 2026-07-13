# Story Revision Changelog

## 1. Files Created

- `CONSISTENCY_REVIEW_CH3_6.md`
- `UNSUPPORTED_CLAIMS_CHECK.md`
- `STORYTELLING_DIAGNOSIS_CH3_6.md`
- `NARRATIVE_SPINE_CH3_6.md`
- `NARRATIVE_REVISION_PLAN_CH3_6.md`
- `chapter3_story_revised_v1.md`
- `chapter4_story_revised_v1.md`
- `chapter5_story_revised_v1.md`
- `chapter6_story_revised_v1.md`
- `STORY_REVISION_CHANGELOG.md`
- `REVISION_TODO.md`
- `UNIFIED_GOAL_CH3_6_STATUS.md`

## 2. Files Not Modified

The original Chapter 3–6 drafts were not modified:

- `chapter3_framework_implementation_and_verification_v2.md`
- `chapter4_accuracy_explainability_tradeoff_results_v1.md`
- `chapter5_ablation_mechanism_boundary_cases_v1.md`
- `chapter6_conclusion_and_recommendations_v1.md`

Their post-revision SHA-256 hashes match the recorded pre-revision baselines:

| Original draft | SHA-256 |
|---|---|
| `chapter3_framework_implementation_and_verification_v2.md` | `57320ff706eedccc56990ae2a83ea12fbc59e979398443bb9371f25fc83c524f` |
| `chapter4_accuracy_explainability_tradeoff_results_v1.md` | `d6f984a5b2495099778792574fad94294cf845f4484c0c4c1551838fc8e77d66` |
| `chapter5_ablation_mechanism_boundary_cases_v1.md` | `8301b35eeebf2612a2905842324aa1ef4de351f9580495f878239a28f02b7d2b` |
| `chapter6_conclusion_and_recommendations_v1.md` | `c20eb0640553f08ff7a62b4cc9a1e8030f91554baaac4e0ee25ec31b1e1748f3` |

## 3. Main Narrative Changes

| Chapter | Main change | What was preserved | Risk |
|---|---|---|---|
| Chapter 3 | Reframed implementation around the comparability problem and validation as an evidence gate. | Sections 3.1–3.6, framework scope, all artifacts, dataset coverage, values, paths, and native/post-hoc boundary | Low |
| Chapter 4 | Reorganised results around the absence of a universal winner and the existence of metric-specific trade-off profiles. | Sections 4.1–4.7, all values, table and figure numbers, strict/sweep separation, and Amazon exclusion | Low |
| Chapter 5 | Sharpened the distinction between tested ablation findings, descriptive mechanism context, and unsupported causality. | Sections 5.1–5.5, all ablation values, 95% rule, mechanism caveats, limitations, and Amazon boundary | Low |
| Chapter 6 | Reorganised the conclusion around comparability, multidimensional measurement, bounded interpretation, and auditability. | Sections 6.1–6.2, all contribution boundaries, recommendations, and unresolved caveats | Low |

## 4. Evidence Preservation Check

| Item | Status | Notes |
|---|---|---|
| Original drafts unchanged | PASS | SHA-256 hashes match the pre-revision baselines. |
| Original section structures preserved | PASS | Revised headings remain 3.1–3.6, 4.1–4.7, 5.1–5.5, and 6.1–6.2. |
| Experimental values preserved | PASS | No retained experimental value was altered; exhaustive values removed from prose remain in the registered tables, figures, and source artifacts. |
| Evidence paths preserved | PASS | No evidence path was renamed or reassigned. |
| Figure and table numbering preserved | PASS | Existing Chapter 3–5 identifiers remain unchanged; no new numbered artifact was created. |
| Strict accuracy and alpha-sweep evidence separated | PASS | Revised Chapters 3, 4, 5, and 6 retain explicit separation. |
| Ablation evidence kept separate | PASS | Revised Chapter 5 limits direct ablation claims to PGPR and UCPR under the registered protocol. |
| Amazon-Book boundary preserved | PASS | Revised Chapters 3, 5, and 6 describe Amazon only as a partial stress or boundary case. |
| Citation status preserved | PASS | No citation was added, verified, or upgraded. |
| Causal boundary preserved | PASS | Non-targeted mechanism interpretations remain descriptive, plausible, or hypothetical. |

## 5. Remaining Risks

- UCPR and KGGLM primary sources remain unverified.
- Primary sources for LIR, SEP, and ETD remain unverified.
- Venue and DOI metadata for the current citation seeds requires manual checking.
- The twelve primary strict-accuracy JSON paths require provenance verification.
- No registered statistical-significance artifact is available.
- No user-study artifact is available.
- Amazon-Book KGAT remains an incomplete six-model experiment with no approved explanation alpha sweeps.
- Optional Chapter 4 SEP and ETD figure placement requires an integration-stage decision.
- Chapter 1–2 integration, final bibliography work, appendix decisions, and NTU template formatting remain outside this revision.
