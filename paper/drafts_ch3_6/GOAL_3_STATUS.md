# Goal 3 Status

## Outcome

Goal 3, "Generate Chapter 4 - Accuracy-Explainability Trade-off Results," is complete at first-draft level.

## Files Created or Updated

- `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`
- `paper/drafts_ch3_6/chapter4_tables.md`
- `paper/drafts_ch3_6/chapter4_figure_plan.md`
- `paper/drafts_ch3_6/chapter4_evidence_used.md`
- `paper/drafts_ch3_6/GOAL_3_STATUS.md`
- `paper/drafts_ch3_6/THESIS_WRITING_TRACEABILITY_LOG.md`

## Scope Completed

- Sections 4.1-4.7 were drafted using the required structure.
- Strict accuracy results were reported for LastFM and ML-1M across PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
- LIR, SEP, and ETD alpha=0 to alpha=1 endpoints were reported from the canonical NDCG sweep summaries.
- LIR-, SEP-, and ETD-oriented trade-off results were reported at result level.
- Cross-dataset differences were summarised without asserting a universal winner.
- Tables 4.1-4.3 and the Figure 4.1-4.4 core plan were completed.
- Existing figures were reused; no new figures or libraries were required.

## Constraint Audit

| Check | Result |
| --- | --- |
| Chapter 4 contains main empirical results only. | Pass |
| Mechanism-level and ablation analysis remain in Chapter 5. | Pass |
| Strict accuracy and alpha-sweep evidence are separated. | Pass |
| Amazon-Book KGAT is not presented as a complete main experiment. | Pass |
| Every reported number is traceable to a listed evidence path. | Pass |
| Every core figure has an existing source and data provenance. | Pass |
| Native-path and post-hoc explanations are not conflated. | Pass |
| Unsupported claims are recorded. | Pass |
| The traceability log is updated. | Pass |

## Open Evidence Issues

- The primary external publication for the XRecSys LIR/SEP/ETD definitions requires manual verification.
- The twelve primary strict-accuracy JSON paths recorded by the summary table are not present in the current worktree. Their values match the accessible canonical status matrix, but the primary JSON provenance requires manual checking.
- Amazon-Book KGAT does not provide a complete six-model explanation alpha-sweep result set and remains excluded from the main Chapter 4 analysis.
- Causal explanations for model-specific trade-off curves are not established by the Chapter 4 evidence and are deferred to Chapter 5.

## Pause Point

Chapter 5 has not been drafted. The recommended next goal is Goal 4: Generate Chapter 5 - Ablation, Mechanism Analysis, and Boundary Cases.
