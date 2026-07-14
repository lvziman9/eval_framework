# Result Figure Decision Log

## 1. Strict Accuracy

**Decision:** Use one main strict NDCG@10 comparison figure and do not retain the mixed HR@10/NDCG@10 bar charts.

Figure 4.1 uses the 12 complete LastFM and ML-1M model rows in `reports/tables/canonical_native_path_status_matrix.csv`. Table 4.1 remains the source of HR@10, Precision@10, and Recall@10 detail. A separate HR@10 appendix figure is not generated because it would duplicate the table without supporting a distinct visual argument.

## 2. Explanation Endpoints

**Decision:** Retain the endpoint summary as Figure 4.2.

The figure adds a compact, cross-objective view of alpha=0 and alpha=1 movement that is not as quickly visible in Table 4.2. Panel scales remain metric-specific, and the caption explicitly identifies the endpoint data as alpha-sweep evidence rather than strict accuracy or user-study evidence.

## 3. Alpha-Sweep Figures

**Decision:** Use three consistently regenerated two-panel figures:

- Figure 4.3: LIR-oriented trade-off curves.
- Figure 4.4: SEP-oriented trade-off curves.
- Figure 4.5: ETD-oriented trade-off curves.

Each figure uses the canonical LastFM and ML-1M objective CSVs, the fixed six-model order, the same legend order, and `Sweep NDCG` on the vertical axis. The SEP caption retains the frozen repository-specific and non-user-perceived boundary.

## 4. Chapter 5 Figures

**Decision:** Keep Figure 5.1 and Figure 5.2 in the main text.

Figure 5.1 is limited to registered PGPR/UCPR ablation evidence and cannot be read as a six-model ablation. Figure 5.2 presents validation status, not model ranking.

**Decision:** Move the former Figure 5.3 Amazon decision flow to Appendix C as Figure C.1.

Table 5.3 and Figure 5.2 already carry the main boundary evidence. The flow remains useful as an appendix-level reportability diagram but would duplicate the Chapter 5 boundary discussion if retained in the main text.

## 5. Evidence Sources

| Figure set | Evidence source |
| --- | --- |
| Strict NDCG@10 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LIR sweep and endpoints | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv` |
| SEP sweep and endpoints | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv` |
| ETD sweep and endpoints | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv` |
| PGPR/UCPR ablation | `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv` |
| Validation matrix and Amazon boundary | `reports/tables/canonical_native_path_status_matrix.csv` and the registered boundary evidence cited by Table 5.3 |

No experiment, training run, or result recomputation was performed.
