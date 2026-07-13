# Chapter 4 Tables

## Table 4.1 Strict Accuracy Results on LastFM and ML-1M

| Dataset | Model | HR@10 | NDCG@10 | Precision@10 | Recall@10 | Evidence path |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| LastFM | PGPR | 0.186389 | 0.030905 | 0.025356 | 0.017731 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | UCPR | 0.216416 | 0.037377 | 0.031129 | 0.023155 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | CAFE | 0.180233 | 0.030214 | 0.025718 | 0.018639 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | TPRec | 0.188919 | 0.038981 | 0.032736 | 0.022307 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | KGGLM | 0.125855 | 0.021319 | 0.016409 | 0.014191 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | PEARLM | 0.099590 | 0.015960 | 0.012736 | 0.009047 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | PGPR | 0.511258 | 0.101896 | 0.092914 | 0.042342 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | UCPR | 0.441887 | 0.086215 | 0.066391 | 0.037913 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | CAFE | 0.554305 | 0.116655 | 0.107119 | 0.052024 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | TPRec | 0.474503 | 0.094220 | 0.089702 | 0.043772 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | KGGLM | 0.168874 | 0.033649 | 0.019305 | 0.010506 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | PEARLM | 0.214735 | 0.035303 | 0.027119 | 0.011040 | `reports/tables/canonical_native_path_status_matrix.csv` |

**Table 4.1.** Strict top-10 accuracy results for the six validated native-path model rows on LastFM and ML-1M. Values are present in both `thesis_analysis_pack/final_accuracy_summary_table.md` and the accessible canonical status matrix; they are not alpha-sweep values.

The source summary records a primary per-row accuracy JSON path for each model. Those JSON files are not present in the current worktree and require manual checking before final submission.

## Table 4.2 Explanation Metric Endpoint Summary

| Dataset | Model | LIR alpha=0 -> alpha=1 | SEP alpha=0 -> alpha=1 | ETD alpha=0 -> alpha=1 | Evidence path |
| :--- | :--- | ---: | ---: | ---: | :--- |
| LastFM | PGPR | 0.0062 -> 0.0219 | 0.5688 -> 0.9877 | 0.1396 -> 0.3552 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| LastFM | UCPR | 0.0050 -> 0.0118 | 0.5170 -> 0.9336 | 0.1196 -> 0.1856 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| LastFM | CAFE | 0.0012 -> 0.0042 | 0.7308 -> 0.9890 | 0.2314 -> 0.3728 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| LastFM | TPRec | 0.0056 -> 0.0111 | 0.5499 -> 0.9132 | 0.1766 -> 0.3983 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| LastFM | KGGLM | 0.0007 -> 0.0009 | 0.6963 -> 0.7187 | 0.1265 -> 0.1294 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| LastFM | PEARLM | 0.0011 -> 0.0014 | 0.5267 -> 0.6106 | 0.1111 -> 0.1117 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` |
| ML-1M | PGPR | 0.4655 -> 0.9627 | 0.4798 -> 0.9833 | 0.1611 -> 0.5191 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |
| ML-1M | UCPR | 0.4568 -> 0.7342 | 0.4935 -> 0.7406 | 0.2088 -> 0.2555 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |
| ML-1M | CAFE | 0.3949 -> 0.6986 | 0.4619 -> 0.9791 | 0.2902 -> 0.8542 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |
| ML-1M | TPRec | 0.4502 -> 0.9451 | 0.4948 -> 0.9704 | 0.2874 -> 0.7301 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |
| ML-1M | KGGLM | 0.3161 -> 0.3161 | 0.4791 -> 0.4791 | 0.0950 -> 0.0950 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |
| ML-1M | PEARLM | 0.4225 -> 0.4272 | 0.5094 -> 0.5266 | 0.0984 -> 0.0989 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` |

**Table 4.2.** Explanation-metric endpoints from the canonical NDCG alpha-sweep CSVs. Each cell reports alpha=0 followed by alpha=1. These values are trade-off evidence and do not replace strict accuracy results.

The LastFM directory contains `tradeoff_lastfm_LIR_ndcg_models.csv`, `tradeoff_lastfm_SEP_ndcg_models.csv`, and `tradeoff_lastfm_ETD_ndcg_models.csv`. The ML-1M directory contains `tradeoff_ml1m_LIR_ndcg_models.csv`, `tradeoff_ml1m_SEP_ndcg_models.csv`, and `tradeoff_ml1m_ETD_ndcg_models.csv`.

## Table 4.3 Trade-off Figure Inventory Used in Chapter 4

| Figure | File path | Dataset | Metric focus | Used in section | Caption draft | Evidence type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Figure 4.1 | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | LastFM | HR@10 and NDCG@10 | 4.2 | LastFM HR@10 and NDCG@10 comparison for six validated native-path model rows under the strict canonical evaluation protocol. | Strict accuracy figure |
| Figure 4.2 | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | ML-1M | HR@10 and NDCG@10 | 4.2 | ML-1M HR@10 and NDCG@10 comparison for six validated native-path model rows under the strict canonical evaluation protocol. | Strict accuracy figure |
| Figure 4.3 | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | LastFM and ML-1M | LIR, SEP, and ETD endpoints | 4.3 | Endpoint comparison of LIR, SEP, and ETD at alpha=0 and alpha=1 for the six native-path models on LastFM and ML-1M. | Alpha-sweep figure |
| Figure 4.4 | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | LastFM and ML-1M | LIR versus NDCG sweep metric | 4.4 | LIR-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M. | Alpha-sweep figure |
| Optional Figure 4.5 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.png` | LastFM and ML-1M | SEP versus NDCG sweep metric | 4.5 or appendix | SEP-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M. | Alpha-sweep figures |
| Optional Figure 4.6 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.png` | LastFM and ML-1M | ETD versus NDCG sweep metric | 4.6 or appendix | ETD-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M. | Alpha-sweep figures |

**Table 4.3.** Inventory and provenance of the core and optional figures used to support Chapter 4.
