# Batch 1 Revision Status

## 1. Overall Status

**Batch 1 generated but requires configuration verification**

The targeted revision is complete at Markdown draft level. Chapter 4 now combines empirical reporting with bounded result-level findings, Chapter 3.6 records the accessible experiment-configuration provenance and its limits, and Chapter 5 preserves ablation and mechanism interpretation as a separate evidential layer. The batch is ready for internal review of argument and evidence boundaries, but it is not ready for configuration freeze or final formatting.

## 2. Files Created

- `CHAPTER3_FRAMEWORK_IMPLEMENTATION_BATCH1_CONFIG_V2.md`
- `CHAPTER4_TRADEOFF_RESULTS_BATCH1_FINDINGS_V2.md`
- `CHAPTER5_ANALYSIS_BOUNDARY_LIMITATIONS_BATCH1_V2.md`
- `FULL_DISSERTATION_DRAFT_BATCH1_V2.md`
- `CH4_FINDINGS_REVISION_REPORT.md`
- `CHAPTER4_EMPIRICAL_PATTERN_SUMMARY_TABLE.md`
- `EXPERIMENT_CONFIGURATION_PROVENANCE.md`
- `BATCH1_REVISION_STATUS.md`

## 3. Chapter 4 Findings Improvements

Chapter 4 retains the original structure and all reported experimental values. Section 4.1 now distinguishes result-level interpretation from Chapter 5 mechanism analysis and excludes statistical, user-perception, causal, and universal-superiority claims. Section 4.2 states the dataset- and metric-dependent strict leadership pattern and separates it from sweep ranking metrics. Sections 4.3-4.6 identify non-interchangeable endpoints, costly, better-preserved, and restricted curve profiles, different SEP costs, distinct ETD behaviour, and dataset dependence. Section 4.7 closes with a seven-row empirical-pattern summary whose standalone copy is also provided.

## 4. Chapter 3 Configuration Improvements

Section 3.6 now records the canonical top-k, strict metrics, 21-point alpha grid, objective-specific sweeps, validation gate, ablation separation, and model-native configuration boundary. The accompanying provenance audit distinguishes script-declared settings from implementation-log records and missing run artifacts. It explicitly states that heterogeneous models do not share one internal hyperparameter space and that inaccessible parameters are not reconstructed or inferred.

## 5. Chapter 5 Adjustments

Only Section 5.3 was revised. It now starts from the Chapter 4 empirical findings and grades the evidence available for interpretation. The PGPR/UCPR ablation remains the stronger evidence for bounded controllability. CAFE, TPRec, KGGLM, and PEARLM mechanism statements remain descriptive. Sections 5.4 and 5.5, including the Amazon boundary and all limitations, are unchanged.

## 6. Evidence and Caveats Preserved

- The twelve expected LastFM/ML-1M strict-accuracy primary JSON artifacts remain `0/12` accessible.
- Current strict provenance remains the canonical status matrix plus the exactly matching final accuracy summary.
- Strict accuracy, main alpha sweeps, PGPR/UCPR ablation, validation, and Amazon boundary evidence remain separate.
- No statistical-significance artifact or user-study artifact is available.
- Amazon-Book KGAT remains a partial boundary case with no approved explanation sweeps.
- LIR, SEP, and ETD retain external conceptual provenance but repository-specific exact implementation.
- Non-PGPR/UCPR mechanism interpretations remain descriptive rather than causal.
- PEARLM final venue and publisher DOI require manual verification.

## 7. Remaining Risks

The historical `runs/debug_compare/` tree and generated checkpoint files are absent from the current worktree. Exact checkpoint paths, hashes, seeds, and several PGPR/UCPR/CAFE model-native optimiser settings therefore require manual verification or recovery from the archived execution environment. The detailed configuration table should not be treated as a frozen reproducibility appendix until those sources are archived.

The existing standalone Chapter 3-5 tables and figure captions have not been refreshed in this batch. Their evidence wording, final numbering, placement, and caption-level distinction between strict accuracy, sweep evidence, ablation, and boundary status remain pending. No final bibliography, NTU formatting, Word, PDF, or LaTeX output was generated.

## 8. Recommended Batch 2

Proceed to **Table / figure / evidence wording refresh**. Batch 2 should update the standalone table provenance language, insert or number the Chapter 4 empirical-pattern table, align captions with the revised evidence boundaries, and verify every selected figure/table source path. It should not begin the supervisor package or final NTU formatting.
