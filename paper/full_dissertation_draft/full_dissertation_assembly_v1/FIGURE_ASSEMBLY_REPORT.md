# Figure Assembly Report

## 1. Discovery Summary

The requested directories contain 100 unique image assets: 98 PNG files and 2 SVG files. Six assets are under `reports/figures/thesis_final/`, two conceptual diagrams are under `paper/drafts_ch3_6/figures/`, and no image asset is currently present under `paper/full_dissertation_draft/figures/`. Thirteen existing files are linked in the assembled draft; two additional diagrams are embedded from registered Mermaid specifications.

## 2. Candidate Figure Decisions

| Candidate figure | Existing file path | Used in draft? | Proposed number | Chapter | Evidence role | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| Framework overview | `paper/drafts_ch3_6/figures/figure_3_1_framework_overview.png` | Yes | Figure 3.1 | 3 | Evaluation architecture | Existing authoritative conceptual asset and V7 caption. |
| Alpha-sweep design | `paper/drafts_ch3_6/figures/figure_3_2_alpha_sweep_design.png` | Yes | Figure 3.2 | 3 | Evidence-stream separation | Existing authoritative conceptual asset and V7 caption. |
| Validation gate | No rendered image; Mermaid in `CHAPTER3_DATAFLOW_AND_VALIDATION_DIAGRAMS.md` | Yes, as Mermaid | Figure 3.3 | 3 | Reportability checks | The registered specification is displayable without fabricating an image. |
| LastFM strict accuracy | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | Yes | Figure 4.1 | 4 | Strict accuracy | Selected final figure; primary JSON caveat retained in caption. |
| ML-1M strict accuracy | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | Yes | Figure 4.2 | 4 | Strict accuracy | Selected final figure; primary JSON caveat retained in caption. |
| Explanation endpoints | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Yes | Figure 4.3 | 4 | Alpha-sweep endpoints | Displays LIR, SEP, and ETD endpoints with the frozen SEP boundary. |
| LIR trade-off | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | Yes | Figure 4.4 | 4 | Alpha-sweep trade-off | Existing combined final view; sweep NDCG boundary retained. |
| LastFM SEP trade-off | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.png` | Yes | Figure 4.5a | 4 | Main SEP trade-off | Canonical six-model LastFM asset. |
| ML-1M SEP trade-off | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.png` | Yes | Figure 4.5b | 4 | Main SEP trade-off | Canonical six-model ML-1M asset. |
| LastFM ETD trade-off | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.png` | Yes | Figure 4.6a | 4 | Optional ETD trade-off | Canonical six-model LastFM asset. |
| ML-1M ETD trade-off | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.png` | Yes | Figure 4.6b | 4 | Optional ETD trade-off | Canonical six-model ML-1M asset. |
| LastFM PGPR/UCPR ablation | `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg` | Yes | Figure 5.1a | 5 | Registered ablation | Uses only eligible PGPR/UCPR ablation evidence. |
| ML-1M PGPR/UCPR ablation | `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg` | Yes | Figure 5.1b | 5 | Registered ablation | Uses only eligible PGPR/UCPR ablation evidence. |
| Experiment-status matrix | `reports/figures/thesis_final/experiment_status_matrix.png` | Yes | Figure 5.2 | 5 | Validation and boundary status | It is explicitly captioned as non-performance evidence. |
| Amazon boundary flow | No rendered image; Mermaid in `CHAPTER5_ABLATION_AND_BOUNDARY_DIAGRAMS.md` | Yes, as Mermaid | Figure 5.3 | 5 | Partial boundary-case decision | Preserves Amazon-Book KGAT as a partial boundary case. |

The remaining 87 discovered image files are historical, duplicate, diagnostic, or supplementary candidates. They were not inserted because the selected canonical/final assets already fill the registered V7 figure roles. In particular, older duplicate trade-off folders were excluded rather than mixed with the canonical LastFM and ML-1M bundles.

## 3. Caption and Evidence Checks

- Figure 4.5 remains the main figure in Section 4.5 and states that paired NDCG is alpha-sweep evidence, not strict NDCG@10.
- Figure 4.5 describes SEP only as movement along the implemented repository-specific score and does not infer user-perceived serendipity.
- Figures 3.3 and 5.2 describe validation status, not recommendation performance.
- Figure 5.1 is limited to the registered PGPR/UCPR ablation and does not establish six-model superiority.
- Figures 5.2 and 5.3 retain Amazon-Book KGAT as partial boundary evidence.

## 4. Rendering Status

All 13 Markdown image links resolve to existing files. Figures 3.3 and 5.3 are Mermaid blocks and should be rendered to SVG or PNG during final PDF preparation. No unresolved figure placeholder remains in the assembled dissertation.

