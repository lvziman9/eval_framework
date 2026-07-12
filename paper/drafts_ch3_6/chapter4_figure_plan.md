# Chapter 4 Figure Plan

## Core Figures

| Figure | Title | Existing file | Data source | Intended section | Status | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Figure 4.1 | LastFM accuracy comparison | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | Strict per-row accuracy evidence indexed by `reports/tables/canonical_native_path_status_matrix.csv` | 4.2 | Existing; use without regeneration | Displays HR@10 and NDCG@10 only; Table 4.1 supplies Precision@10 and Recall@10. |
| Figure 4.2 | ML-1M accuracy comparison | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | Strict per-row accuracy evidence indexed by `reports/tables/canonical_native_path_status_matrix.csv` | 4.2 | Existing; use without regeneration | Displays HR@10 and NDCG@10 only; Table 4.1 supplies Precision@10 and Recall@10. |
| Figure 4.3 | Explanation metric alpha endpoints | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Canonical LastFM v4 six-model and ML-1M v2 LIR/SEP/ETD NDCG alpha-sweep CSVs | 4.3 | Existing; use without regeneration | Endpoints are alpha-sweep evidence, not strict accuracy. |
| Figure 4.4 | LIR-NDCG trade-off | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv` | 4.4 | Existing; use without regeneration | NDCG is the alpha-sweep ranking metric and must remain separate from strict NDCG@10. |

## Optional or Appendix Figures

| Figure | Title | Existing files | Intended section | Status | Selection note |
| --- | --- | --- | --- | --- | --- |
| Optional Figure 4.5 | SEP-oriented trade-off results | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.png` | 4.5 or appendix | Existing; no composite figure generated | Use as two dataset panels if the final chapter has space; otherwise retain as appendix candidates. |
| Optional Figure 4.6 | ETD-oriented trade-off results | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.png` | 4.6 or appendix | Existing; no composite figure generated | Use as two dataset panels if the final chapter has space; otherwise retain as appendix candidates. |

## Draft Captions

**Figure 4.1.** LastFM HR@10 and NDCG@10 comparison for six validated native-path model rows under the strict canonical evaluation protocol.

**Figure 4.2.** ML-1M HR@10 and NDCG@10 comparison for six validated native-path model rows under the strict canonical evaluation protocol.

**Figure 4.3.** Endpoint comparison of LIR, SEP, and ETD at alpha=0 and alpha=1 for the six native-path models on LastFM and ML-1M. Endpoint values are taken from the NDCG alpha-sweep evidence and are not strict accuracy values.

**Figure 4.4.** LIR-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M.

**Optional Figure 4.5.** SEP-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M.

**Optional Figure 4.6.** ETD-oriented alpha-sweep trade-off curves against the NDCG sweep metric on LastFM and ML-1M.

## Excluded Figure

`reports/figures/thesis_final/amazon_book_accuracy_hr_ndcg.png` is not included in Chapter 4 because Amazon-Book KGAT is excluded from the main trade-off result analysis. Its partial boundary-case role is reserved for Chapter 5.
