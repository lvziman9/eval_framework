
# Generated Figure Captions

## Goal 9: Thesis-Ready Figures

All figures below were generated from existing CSV/JSON/MD result files. No training, model export, checkpoint writing, or evaluation pipeline mutation was performed.

| Generated figure | Data source | Recommended chapter | Caption | Caveat |
| --- | --- | --- | --- | --- |
| reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png | reports/tables/canonical_native_path_status_matrix.csv | Chapter 4 | LastFM HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol. | Accuracy values come from strict per-row accuracy evidence indexed by the status matrix. |
| reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png | reports/tables/canonical_native_path_status_matrix.csv | Chapter 4 | ML-1M HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol. | Accuracy values come from strict per-row accuracy evidence indexed by the status matrix. |
| reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png | reports/tables/canonical_native_path_status_matrix.csv | Chapter 4 | Amazon-Book KGAT HR@10 and NDCG@10 comparison for completed native-path model rows under the canonical evaluation protocol. | Accuracy values come from strict per-row accuracy evidence indexed by the status matrix. |
| reports/figures/thesis_final/explanation_metric_alpha_endpoints.png | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/*_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/*_ndcg_models.csv | Chapter 5 | Endpoint comparison of LIR, SEP, and ETD at alpha=0 and alpha=1 for LastFM and ML-1M native-path models. | Endpoint values come from alpha-sweep CSVs and should be interpreted as trade-off evidence, not strict standalone accuracy. |
| reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png | reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv; reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv | Chapter 5 | Accuracy-explainability trade-off curves showing LIR against the NDCG sweep metric on LastFM and ML-1M. | Use as trade-off evidence; strict accuracy is reported separately from per-row accuracy JSON files. |
| reports/figures/thesis_final/experiment_status_matrix.png | reports/tables/canonical_native_path_status_matrix.csv | Chapter 4 or Chapter 5 | Status matrix for canonical native-path experiments, separating complete rows from blocked Amazon-Book KGAT rows. | Blocked means not honestly reportable under the current validation and model-support gates. |

## Metrics

- HR@10: whether at least one relevant test item appears in the top-10 recommendation list.
- NDCG@10: rank-sensitive recommendation quality against canonical test labels.
- LIR: recency of the path's linked historical interaction.
- SEP: serendipity/low-degree quality of the bridge entity.
- ETD: diversity of explanation path types in top-k recommendations.

## Caveat

Generated accuracy figures use strict status-matrix accuracy values. Generated explanation/trade-off figures use alpha-sweep CSVs and should be interpreted as trade-off evidence rather than replacements for strict accuracy JSON values.
