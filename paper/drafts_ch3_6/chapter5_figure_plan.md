# Chapter 5 Figure Plan

## Figure Inventory

| Figure | Proposed caption | Existing asset path | Evidence role | Placement | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Figure 5.1(a) | PGPR and UCPR explanation-objective trade-offs under the strict baseline-preserving ablation protocol on LastFM. | `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg` | Ablation evidence; visualises NDCG against LIR, SEP, and ETD across alpha settings. | Section 5.1, after Table 5.1. | Existing; use without regeneration. |
| Figure 5.1(b) | PGPR and UCPR explanation-objective trade-offs under the strict baseline-preserving ablation protocol on ML-1M. | `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg` | Ablation evidence; visualises NDCG against LIR, SEP, and ETD across alpha settings. | Section 5.1, paired with Figure 5.1(a). | Existing; use without regeneration. |
| Figure 5.2 | Validation status across the canonical native-path experiment matrix. PASS indicates a reportable validated row; BLOCKED / N/A indicates an incomplete experimental contract rather than failed recommender performance. | `reports/figures/thesis_final/experiment_status_matrix.png` | Boundary-case and validation evidence. | Section 5.4, after Table 5.3. | Existing; use without regeneration. |

## Use Notes

Figure 5.1 should be assembled as a two-panel figure from the two existing SVG assets. The plotted NDCG belongs to the ablation protocol over the frozen original top-k item set. It must not be captioned as a replacement for strict final accuracy or for the Chapter 4 six-model alpha-sweep results.

Figure 5.2 should retain the status labels in the existing asset. Its purpose is to show validation coverage and the Amazon boundary, not to rank models.

No new figure data, recalculation, plotting library, or generated image is required for Goal 4.
