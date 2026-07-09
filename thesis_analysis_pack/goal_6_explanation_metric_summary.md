
# Goal 6: Explanation Metric Summary

## Goal Number

Goal 6

## Current Task

Summarize LIR, SEP, and ETD from existing result files, define each metric, and mark unavailable or invalid cases honestly.

## Metric Meanings

- LIR, Linked Interaction Recency: measures how recent the path's seed interaction is for the user. Higher values indicate recommendations anchored in more recent user behavior. Evidence: `docs/guides/PATH_METRICS_GUIDE.md`.
- SEP, Serendipity of Explanation Path: measures the low-degree or unusual nature of the bridge entity in the explanation path. Higher values indicate more serendipitous bridge entities. Evidence: `docs/guides/PATH_METRICS_GUIDE.md`.
- ETD, Explanation Type Diversity: measures the diversity of explanation path types across a user's top-k recommendations. Evidence: `docs/guides/PATH_METRICS_GUIDE.md`.

## Final Explanation Summary

| Dataset | Model | LIR | SEP | ETD | Native path? | Status | Evidence file path | Caveat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | 0.0062 -> 0.0219 | 0.5688 -> 0.9877 | 0.1396 -> 0.3552 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| LastFM | UCPR | 0.0050 -> 0.0118 | 0.5170 -> 0.9336 | 0.1196 -> 0.1856 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| LastFM | CAFE | 0.0012 -> 0.0042 | 0.7308 -> 0.9890 | 0.2314 -> 0.3728 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| LastFM | TPRec | 0.0056 -> 0.0111 | 0.5499 -> 0.9132 | 0.1766 -> 0.3983 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| LastFM | KGGLM | 0.0007 -> 0.0009 | 0.6963 -> 0.7187 | 0.1265 -> 0.1294 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| LastFM | PEARLM | 0.0011 -> 0.0014 | 0.5267 -> 0.6106 | 0.1111 -> 0.1117 | Yes | Complete + figures | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | PGPR | 0.4655 -> 0.9627 | 0.4798 -> 0.9833 | 0.1611 -> 0.5191 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | UCPR | 0.4568 -> 0.7342 | 0.4935 -> 0.7406 | 0.2088 -> 0.2555 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | CAFE | 0.3949 -> 0.6986 | 0.4619 -> 0.9791 | 0.2902 -> 0.8542 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | TPRec | 0.4502 -> 0.9451 | 0.4948 -> 0.9704 | 0.2874 -> 0.7301 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | KGGLM | 0.3161 -> 0.3161 | 0.4791 -> 0.4791 | 0.0950 -> 0.0950 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| ML-1M | PEARLM | 0.4225 -> 0.4272 | 0.5094 -> 0.5266 | 0.0984 -> 0.0989 | Yes | Complete + figures | reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv | Values shown as alpha=0 -> alpha=1 from NDCG alpha-sweep CSVs; keep separate from strict accuracy JSON values. |
| Amazon-Book KGAT | PGPR | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Complete | runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |
| Amazon-Book KGAT | UCPR | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Blocked | reports/tables/canonical_native_path_status_matrix.md | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |
| Amazon-Book KGAT | CAFE | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Blocked | reports/tables/canonical_native_path_status_matrix.md | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |
| Amazon-Book KGAT | TPRec | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Blocked | reports/tables/canonical_native_path_status_matrix.md | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |
| Amazon-Book KGAT | KGGLM | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Complete | runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1/accuracy.json | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |
| Amazon-Book KGAT | PEARLM | N/A | N/A | N/A | Yes if complete row; blocked otherwise | Complete | runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1/accuracy.json | Amazon explanation alpha sweeps are N/A until an approved timestamp/SEP/ETD denominator exists; blocked rows have no formal export/accuracy. |

## Key Findings

1. LastFM and ML-1M have complete LIR/SEP/ETD alpha-sweep evidence for all six native-path models.
2. Amazon-Book KGAT has completed native-path exports for KGGLM, PEARLM, and PGPR, but LIR/SEP/ETD alpha-sweep comparisons are N/A under the current evidence because timestamp and denominator semantics are not approved.
3. Blocked Amazon UCPR/CAFE/TPRec rows must not receive post-hoc or invented explanation scores.
4. The alpha-sweep CSVs are useful for accuracy-explainability trade-off analysis, but their `ndcg/hr/precision/recall` columns should not replace the strict accuracy summary from per-row `accuracy.json` files.

## Generated Files

- `thesis_analysis_pack/goal_6_explanation_metric_summary.md`
- `thesis_analysis_pack/final_explanation_summary_table.md`

## Next Goal

Goal 7: Validation and quality-control audit.
