# Figure Regeneration Report

## 1. Production Method

All final figures were regenerated from existing text specifications or existing CSV evidence. No experiment or training process was run. No new package was installed. A Python standard-library renderer produced structured SVG and high-resolution RGB PNG files; SVG is the primary formal asset.

## 2. Generated Figure Set

| Display figure | SVG / PNG basename | Evidence source | Method | PNG dimensions | Status |
| --- | --- | --- | --- | --- | --- |
| Figure 3.1 | `figure_3_1_framework_overview_final` | Chapter 3 framework text and diagram specifications | Formal box-and-arrow redraw | 2400 x 1470 | Complete |
| Figure 3.2 | `figure_3_2_alpha_sweep_design_final` | Chapter 3 evidence-stream specification | Formal evidence-flow redraw | 2400 x 1350 | Complete |
| Figure 3.3 | `figure_3_3_validation_gate_flow_final` | V1 Mermaid specification and validation-gate table | Formal decision-flow redraw | 2400 x 1680 | Complete |
| Figure 4.1 | `figure_4_1_strict_ndcg_comparison_final` | Canonical status matrix; 12 complete strict rows | Two-panel bar chart | 2400 x 1230 | Complete |
| Figure 4.2 | `figure_4_2_explanation_endpoint_summary_final` | Six canonical alpha-sweep CSVs; alpha=0 and alpha=1 only | Six-panel endpoint chart | 2400 x 1650 | Complete |
| Figure 4.3 | `figure_4_3_lir_tradeoff_final` | LastFM and ML-1M LIR CSVs; 126 rows per CSV | Two-panel trade-off curves | 2400 x 1290 | Complete |
| Figure 4.4 | `figure_4_4_sep_tradeoff_final` | LastFM and ML-1M SEP CSVs; 126 rows per CSV | Two-panel trade-off curves | 2400 x 1290 | Complete |
| Figure 4.5 | `figure_4_5_etd_tradeoff_final` | LastFM and ML-1M ETD CSVs; 126 rows per CSV | Two-panel trade-off curves | 2400 x 1290 | Complete |
| Figure 5.1 | `figure_5_1_pgpr_ucpr_ablation_final` | PGPR/UCPR ablation long CSV; 252 rows | Two-panel subset ablation chart | 2400 x 1320 | Complete |
| Figure 5.2 | `figure_5_2_experiment_status_matrix_final` | Canonical status matrix; 18 model-dataset rows | Validation-status matrix redraw | 2400 x 975 | Complete |
| Figure C.1 | `figure_5_3_amazon_boundary_flow_final` | V1 Mermaid specification and Table 5.3 evidence | Formal boundary-flow redraw | 2100 x 1350 | Complete |

Each basename exists under both `figures/svg/` and `figures/png/`.

## 3. Result-Figure Controls

- Figure 4.1 contains strict NDCG@10 only; HR@10 is not mixed into the chart.
- Figures 4.3-4.5 use one objective per figure and two dataset panels.
- All Chapter 4 model legends follow PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.
- Figure 4.4 labels the horizontal axis as the implemented SEP score.
- Figure 5.1 displays PGPR/UCPR only and is labelled as subset ablation evidence.
- Figure 5.2 and Figure C.1 encode validation and boundary status, not performance ranking.

## 4. Visual Inspection

The generated PNGs were checked at original resolution for blank output, cropping, connector visibility, legend overlap, panel alignment, and label overflow. The formal SVG files retain exact metric names such as `NDCG@10`; PNG is a compatibility preview and not the primary vector source.
