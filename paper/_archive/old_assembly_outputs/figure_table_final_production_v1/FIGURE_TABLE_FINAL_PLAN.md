# Figure/Table Final Plan

## 1. Figure Inventory

| Current figure | Current source | Current status | Problem | Final action | Final location |
| --- | --- | --- | --- | --- | --- |
| Figure 3.1 framework overview | `paper/drafts_ch3_6/figures/figure_3_1_framework_overview.png` | Draft raster | Draft-resolution conceptual diagram | Redraw as formal vector diagram and high-resolution preview | Main text, Figure 3.1 |
| Figure 3.2 alpha-sweep design | `paper/drafts_ch3_6/figures/figure_3_2_alpha_sweep_design.png` | Draft raster | Draft-resolution conceptual diagram | Redraw with explicit evidence-stream separation | Main text, Figure 3.2 |
| Figure 3.3 validation gate | Mermaid block in assembly V1 | Draft-only source | Mermaid cannot remain as the final dissertation figure | Redraw as formal SVG/PNG flow diagram | Main text, Figure 3.3 |
| Figures 4.1 and 4.2 strict accuracy | `reports/figures/thesis_final/*_accuracy_hr_ndcg.png` | Existing mixed-metric rasters | HR@10 and NDCG@10 are mixed; panel and caption style do not match the final rule | Replace with one two-panel strict NDCG@10 figure | Main text, Figure 4.1 |
| Figure 4.3 endpoint summary | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Existing raster | Numbering and styling need alignment with the final result set | Regenerate from canonical alpha-sweep CSV endpoints | Main text, Figure 4.2 |
| Figure 4.4 LIR trade-off | Existing thesis-final raster and canonical LIR CSVs | Source data available | Style differs from SEP/ETD assets | Regenerate as a two-panel objective figure | Main text, Figure 4.3 |
| Figure 4.5 SEP trade-off | Two dataset-specific PNGs and canonical SEP CSVs | Source data available | Split links and inconsistent final layout | Regenerate as one two-panel figure with frozen SEP boundary wording | Main text, Figure 4.4 |
| Figure 4.6 ETD trade-off | Two dataset-specific PNGs and canonical ETD CSVs | Source data available | Split links and optional/draft presentation | Regenerate as one two-panel figure | Main text, Figure 4.5 |
| Figure 5.1 PGPR/UCPR ablation | Two dataset-specific SVGs and ablation CSV | Source data available | Split links and model-subset boundary needs emphasis | Regenerate as one two-panel figure | Main text, Figure 5.1 |
| Figure 5.2 status matrix | `reports/figures/thesis_final/experiment_status_matrix.png` | Existing raster | Final typography and boundary legend need alignment | Regenerate from the canonical status matrix | Main text, Figure 5.2 |
| Figure 5.3 Amazon decision flow | Mermaid block in assembly V1 | Draft-only source | Mermaid cannot remain; the process flow is secondary to Table 5.3 | Redraw and move to appendix | Appendix C, Figure C.1 |

## 2. Table Inventory

| Current table | Current status | Problem | Final action | Final location |
| --- | --- | --- | --- | --- |
| Table 1.1 | Complete pipe table | Caption above table | Move caption below; preserve every cell | Main text |
| Table 2.1 | Complete pipe table | Caption above table | Move caption below; preserve every cell | Main text |
| Tables 3.1-3.6 | Complete pipe tables | Captions above tables | Move captions below; preserve every cell | Main text |
| Table 4.1 | Complete pipe table | Caption already below | Retain values and source caveat | Main text |
| Table 4.2 | Complete pipe table | Caption already below | Retain values and alpha-sweep boundary | Main text |
| Table 4.3 | Complete pipe table | Caption above table | Move caption below; preserve every cell | Main text |
| Tables 5.1-5.4 | Complete pipe tables | Captions already below | Retain values and evidence boundaries | Main text |
| Table 6.1 | Complete pipe table | Caption above table | Move caption below; preserve every cell | Main text |

## 3. Required Regeneration

The final production set regenerates Figures 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, and the former Figure 5.3. Each figure has an SVG primary asset and a high-resolution PNG preview. Quantitative figures use existing CSV evidence only.

## 4. Figures Safe to Use As-Is

No V1-linked image is used unchanged as a final figure. Existing figures remain evidence references, but the final assembly links a consistently regenerated figure set. The V1 pipe-table data are safe to retain and are copied without cell changes.

## 5. Figures Moved to Appendix

The former Figure 5.3 Amazon boundary decision flow is moved to Appendix C as Figure C.1. Table 5.3 and Figure 5.2 remain in Chapter 5, so the main text retains the full boundary evidence without a second process-flow visual.

## 6. Figures Removed or Replaced

- The two mixed HR@10/NDCG@10 strict-accuracy rasters are replaced by one strict NDCG@10 figure.
- The separate dataset links for LIR, SEP, ETD, and PGPR/UCPR ablation are replaced by unified two-panel figures.
- Both Mermaid blocks are replaced by formal figure files; no Mermaid remains in V2.
- No separate HR@10 appendix figure is produced because Table 4.1 already preserves HR@10, Precision@10, and Recall@10 details.

## 7. Caption Placement Rule

In the Markdown assembly V2, both figure captions and table captions should appear below the figure/table for consistency with the user's requested display convention. Final NTU template formatting may override placement if required.
