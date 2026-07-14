# Figure Placement Decision: SEP Trend

## 1. Decision

**Placement:** Main text, Chapter 4.5.

SEP-NDCG trade-off curve should remain in the main Chapter 4 evidence stream because it provides a visually clear example of implemented objective movement under the alpha-sweep design.

This decision applies to the registered LastFM and ML-1M SEP-NDCG curve assets. It changes placement and evidential emphasis only; it does not change either figure, its values, the alpha grid, or the underlying experimental artifacts.

## 2. Evidence Role

The SEP-oriented sweep provides one of the clearest empirical trade-off profiles in the alpha-sweep results. The curve shows that several models move substantially along the implemented SEP objective while paired sweep NDCG changes at different rates. It is therefore useful for analysing framework controllability under an explanation-side objective.

The figure remains alpha-sweep evidence. It is not strict accuracy, user-study evidence, a statistical-significance result, or proof of a causal model mechanism.

## 3. Frozen Caption

**Figure 4.5.** SEP-oriented trade-off curves under the implemented repository-specific SEP objective. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. The SEP axis reflects movement along the implemented SEP score, not independently validated user-perceived serendipity. The figure is used to analyse trade-off movement along the implemented SEP objective.

## 4. Source Assets

| Dataset | Source asset | Evidence stream | Placement | Status |
| --- | --- | --- | --- | --- |
| LastFM | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.png` | Alpha-sweep SEP-NDCG | Chapter 4.5 main text | Existing asset; no regeneration |
| ML-1M | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.png` | Alpha-sweep SEP-NDCG | Chapter 4.5 main text | Existing asset; no regeneration |

## 5. Interpretation Boundary

SEP is treated as a repository-specific bridge-entity score following the XRecSys-style explanation-metric setting. The figure records movement along the implemented SEP objective. It does not show that higher SEP always corresponds to lower bridge-entity degree, and it does not establish greater user-perceived serendipity, surprise, novelty, usefulness, or explanation quality.

## 6. Deferred Work

Image insertion, final numbering, layout, rendering, Word formatting, and NTU formatting remain outside this Mini Batch.
