# SEP Wording Freeze and Trend Preservation Status

## 1. Overall Status

**Status:** Complete at the isolated Markdown revision level.

The Mini Batch freezes conservative SEP semantics, preserves and strengthens the Chapter 4.5 SEP trend analysis, and registers the SEP-NDCG curves as main-text Chapter 4 evidence. No experiment, metric, value, source figure, citation, or Batch 1C file was modified.

## 2. Files Created

Required outputs:

1. `SEP_WORDING_AND_TREND_PRESERVATION_REPORT.md`
2. `CHAPTER3_FRAMEWORK_IMPLEMENTATION_SEP_TREND_V5.md`
3. `CHAPTER4_TRADEOFF_RESULTS_SEP_TREND_V5.md`
4. `CHAPTER5_ANALYSIS_BOUNDARY_LIMITATIONS_SEP_TREND_V5.md`
5. `FULL_DISSERTATION_DRAFT_SEP_TREND_V5.md`
6. `FORMULA_INVENTORY_AND_EVIDENCE_MAP_SEP_TREND.md`
7. `REVISED_TABLES_AND_CAPTIONS_SEP_TREND.md`
8. `FIGURE_PLACEMENT_DECISION_SEP_TREND.md`
9. `BATCH_SEP_WORDING_TREND_STATUS.md`

Additional isolated correction:

10. `SINGLE_EXAMPLE_TRACE_SEP_TREND.md`

The additional file is necessary to apply the required top-k placeholder correction without overwriting the Batch 1C source trace.

## 3. Frozen SEP Wording

The revised outputs use the following semantic position:

- SEP is a repository-specific bridge-entity score.
- SEP follows the XRecSys-style explanation-metric setting but is interpreted here through the implemented repository metric pipeline.
- SEP is used as an operational explanation-side metric rather than as direct evidence of user-perceived serendipity.
- The dissertation does not independently validate SEP semantic direction against user perception or external serendipity judgments.

## 4. Chapter 3 Status

The SEP formula remains abstract:

\[
\mathrm{SEP}(p_{u,i})
=
\sigma_d(b(p_{u,i})),
\quad
\sigma_d(\cdot) \in [0,1].
\]

The main body defines \(\sigma_d\) operationally and no longer discusses generator sorting or historical `sep_matrix.pkl` provenance. Those issues remain in reports and limitations rather than the Chapter 3 method definition.

## 5. Chapter 4 Trend Status

The dedicated Section 4.5 and every registered LastFM and ML-1M value are retained. The revision strengthens the result-level interpretation that several models move substantially along the implemented SEP objective while paired sweep NDCG changes at different rates.

The SEP-oriented sweep is identified as one of the clearest visual trade-off profiles in the alpha-sweep results and as useful for analysing framework controllability under an explanation-side objective. No new ratio, metric, result, significance statement, or mechanism claim is added.

## 6. SEP Figure Placement

**Decision:** Figure 4.5 is main-text Chapter 4.5 evidence.

SEP-NDCG trade-off curve should remain in the main Chapter 4 evidence stream because it provides a visually clear example of implemented objective movement under the alpha-sweep design.

The paired NDCG remains alpha-sweep evidence and is not strict NDCG@10. The SEP axis records movement along the implemented score and is not user-study evidence or proof of user-perceived serendipity.

## 7. Chapter 5 Status

Chapter 5 states that SEP is adopted as an implemented explanation-side metric rather than independently validated as a user-perceived serendipity construct. It also preserves that LIR / SEP / ETD exact implementation is repository-specific and retains the unavailable historical-cache caveat. No causal mechanism is inferred from SEP movement.

## 8. Formula, Table, and Caption Status

The formula inventory retains all 26 Batch 1C entries. The SEP row now records:

- purpose: repository-specific bridge-entity score following the XRecSys-style metric setting;
- confidence: implemented metric available; semantic direction conservatively bounded;
- caveat: historical cached SEP matrix unavailable and no direct user-perceived serendipity claim.

Figure 4.5 is marked as a main-text alpha-sweep trade-off figure, and its existing source paths are unchanged. Related table notes and captions use the implemented repository-specific bridge-entity-score wording.

## 9. Single-Example Trace Fix

The isolated trace copy uses `j*` for top-k position instead of `i*`. User and item placeholders remain abstract, and no real identifier is introduced.

## 10. Preserved Boundaries

- No experiment was run.
- No new result or metric was generated.
- No experimental value was changed.
- No SEP matrix was revalidated.
- No historical cache was searched.
- No historical matrix provenance was claimed.
- No user-perceived serendipity, novelty, usefulness, surprise, or explanation-quality improvement was claimed.
- Strict accuracy, alpha-sweep, ablation, and boundary evidence remain separate.
- Batch 1C outputs remain unchanged.
- No Word, PDF, LaTeX, PNG, SVG, or rendered figure was generated.

## 11. Remaining Caveat

The historical cached SEP matrix is not available in the current evidence package. The wording is frozen conservatively around the implemented objective, but historical artifact provenance and external user-perception semantics are not closed.

## 12. Full Draft Status

`FULL_DISSERTATION_DRAFT_SEP_TREND_V5.md` contains Chapter 1-6 in order. Chapter 1, Chapter 2, and Chapter 6 use the unchanged integrated source files. Chapter 3-5 use the isolated SEP-trend versions. References and Appendix remain placeholders.

## 13. Recommended Next Batch

**Markdown cleanup and supervisor-review preparation.**

Figure rendering, supervisor packaging, final Word/PDF generation, and NTU formatting remain deferred and require separate authorisation.
