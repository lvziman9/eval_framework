# Chapter 4 Findings Revision Report

## 1. Current Problem

The integrated Chapter 4 reports the strict rankings, explanation endpoints, and paired alpha-sweep values accurately, but much of the discussion stops at model-by-model reporting. The original text identifies heterogeneity and occasionally notes different ranking costs, yet it does not consistently elevate those observations into reusable empirical findings. As a result, the reader must infer the main response types from individual endpoint paragraphs, and Chapter 5 carries more of the cross-model interpretation than its ablation and mechanism remit requires.

The main gap is not missing numerical evidence. It is the absence of an explicit result-level layer between the reported values and the mechanism discussion. Chapter 4 should state what patterns are visible in the validated curves while stopping before causal attribution.

## 2. Result-Level Findings Missing from Chapter 4

The following findings were present only implicitly or incompletely:

- strict accuracy has no universal winner and changes with dataset and metric;
- strict ranking position does not directly predict explanation-objective movement;
- LIR curves include costly, better-preserved, and restricted response profiles;
- SEP can move in the same direction across models while carrying different paired ranking costs;
- ETD produces a different ordering from LIR and SEP, including a dataset-dependent largest mover;
- flat or nearly flat curves are reportable outcomes rather than absent evidence;
- the same model can expose different response scales across LastFM and ML-1M;
- paired sweep NDCG remains distinct from the strict NDCG@10 evidence stream.

## 3. Content to Add to Chapter 4

Chapter 4 should add result-level interpretation after each evidence block. Section 4.1 should define the boundary between empirical findings and mechanism claims. Section 4.2 should connect dataset- and metric-dependent leadership to the absence of a universal strict winner. Section 4.3 should explain why endpoint movement, restricted movement, and the three explanation dimensions cannot be collapsed into one ranking. Sections 4.4-4.6 should classify the observed curve profiles and state their dataset dependence. Section 4.7 should consolidate the findings in one empirical-pattern table.

These additions may use cautious formulations such as “the observed profile suggests” and “at the result level, this indicates”. They must continue to label ranking values from the alpha sweeps as paired sweep metrics rather than strict accuracy.

## 4. Content to Keep in Chapter 5

Chapter 5 should retain all claims that require stronger evidential support than comparative curves provide:

- exact alpha=0 preservation and the 95% NDCG-retention rule from the PGPR/UCPR ablation;
- the distinction between direct ablation evidence and descriptive architectural context;
- mechanism-family discussion for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM;
- hypotheses concerning candidate generation, path selection, temporal requirements, or constrained decoding;
- Amazon-Book KGAT as a partial boundary case;
- limitations concerning coverage, user evaluation, statistical inference, metric implementation, citations, and native-path fidelity.

Chapter 5 should not repeat the complete empirical-pattern summary. Its role is to ask which Chapter 4 observations can be strengthened by ablation or mechanism-level evidence and where interpretation must stop.

## 5. Evidence Boundaries

The revision preserves the following boundaries:

1. Strict accuracy is supported at draft level by `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`; the twelve expected row-level primary JSON artifacts remain unavailable.
2. Alpha-sweep findings come from the registered LastFM and ML-1M trade-off CSV bundles and do not replace strict HR@10, NDCG@10, Precision@10, or Recall@10.
3. LIR, SEP, and ETD describe separate repository-implemented path properties and do not establish user-perceived explanation quality.
4. No statistical-significance artifact or user-study artifact is registered.
5. Comparative curves support result-level patterns, not causal model-mechanism conclusions.
6. Amazon-Book KGAT remains outside the complete six-model Chapter 4 comparison.
7. PEARLM final venue and publisher DOI remain subject to manual verification.

## 6. Batch 1 Revision Summary

The revised Chapter 4 retains every original experimental value and section boundary. It adds explicit findings for strict leadership, endpoint interpretation, LIR/SEP/ETD curve types, flat responses, paired ranking costs, and dataset dependence. A seven-row empirical-pattern summary closes Section 4.7. Mechanism-level interpretation, the PGPR/UCPR ablation, and the Amazon boundary remain in Chapter 5.
