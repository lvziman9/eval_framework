# Academic Figure Redraw Report

## 1. Output Package

The academic redraw is versioned under:

`paper/full_dissertation_draft/figure_table_final_production_v2/`

The previous production package remains unchanged. The new assembly is:

`FULL_DISSERTATION_FIGURE_TABLE_READY_V3.md`

The V3 assembly is an exact textual copy of V2, so chapter prose, captions, tables, citations, figure numbering, and evidence boundaries are unchanged. Its relative figure links resolve to the new academic redraw assets.

## 2. Software Environment

| Component | Version / setting |
| --- | --- |
| Python | 3.11.15 |
| NumPy | 2.4.6 |
| pandas | 3.0.3 |
| Matplotlib | 3.11.0 |
| Seaborn | 0.13.2 |
| Graphviz Python | 0.21 |
| Graphviz `dot` | 14.1.2 |
| CairoSVG | 2.9.0 |
| Pillow | 12.3.0 |
| Font | DejaVu Sans |

No additional package was installed during the redraw.

## 3. Figure Inventory

| Figure | Production method | Primary evidence / specification | PNG size |
| --- | --- | --- | --- |
| Figure 3.1 framework overview | Graphviz formal dataflow | Chapter 3 framework and export-contract specification | 3600 x 1668 |
| Figure 3.2 alpha-sweep design | Graphviz three-stream diagram | Strict, sweep, and ablation evidence separation | 3600 x 1827 |
| Figure 3.3 validation gate | Graphviz top-down decision flow | Registered export integrity, path fidelity, and metric sanity checks | 3200 x 2253 |
| Figure 4.1 strict NDCG@10 | Matplotlib two-panel bar chart | `reports/tables/canonical_native_path_status_matrix.csv` | 4249 x 1714 |
| Figure 4.2 endpoint summary | Matplotlib 2-by-3 endpoint plot | Six canonical LastFM/ML-1M trade-off CSVs | 4351 x 2994 |
| Figure 4.3 LIR trade-off | Matplotlib two-panel trajectory plot | Canonical LastFM and ML-1M LIR CSVs | 4270 x 1845 |
| Figure 4.4 SEP trade-off | Matplotlib two-panel trajectory plot | Canonical LastFM and ML-1M SEP CSVs | 4270 x 1845 |
| Figure 4.5 ETD trade-off | Matplotlib two-panel trajectory plot | Canonical LastFM and ML-1M ETD CSVs | 4270 x 1845 |
| Figure 5.1 PGPR/UCPR ablation | Matplotlib two-panel retention plot | `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv` | 4251 x 1894 |
| Figure 5.2 status matrix | Matplotlib status-cell matrix | Canonical native-path status matrix | 4123 x 1289 |
| Figure C.1 Amazon boundary flow | Graphviz top-down decision flow | Registered Amazon-Book KGAT boundary logic | 3200 x 2833 |

Each figure exists as a matching SVG and PNG pair under `figures/svg/` and `figures/png/`.

## 4. Academic Redraw Decisions

- Removed oversized figure titles and embedded explanatory paragraphs from quantitative figures.
- Replaced the console bitmap typography with embedded DejaVu Sans.
- Standardised panel labels, margins, axis labels, tick sizes, grid treatment, and legends.
- Applied the Okabe-Ito palette with marker and line-style redundancy.
- Kept strict NDCG@10 separate from sweep NDCG.
- Retained one objective per LIR, SEP, and ETD figure.
- Preserved the repository-specific SEP wording boundary in the assembly caption.
- Kept the ablation figure explicitly limited to PGPR/UCPR.
- Displayed Amazon blocked cells as `BLOCKED / N/A`, using both text and hatching.
- Reorganised Figure 3.3 checks into three labelled gates without removing any registered check category.

## 5. Reproducibility

The redraw script is stored at:

`scripts/regenerate_academic_figures.py`

Run it from the repository root with:

```bash
MPLCONFIGDIR=/tmp/matplotlib-paper conda run -n paper python paper/full_dissertation_draft/figure_table_final_production_v2/scripts/regenerate_academic_figures.py
```

The script reads existing CSV evidence only. It does not train models, run recommendation experiments, or modify datasets, exports, reports, or checkpoints.

## 6. Verification

- 11 SVG and 11 PNG files generated.
- All PNG widths are at least 3200 pixels.
- All SVG files use DejaVu Sans and contain no monospace font declaration.
- All 11 V3 image links resolve.
- V3 contains 16 unchanged pipe tables and 29 unchanged citation keys.
- The strict figure contains NDCG@10 only.
- LIR, SEP, and ETD figures contain both datasets and all six models.
- The status matrix preserves PASS and BLOCKED / N/A states.
- Nine source and assembly hashes were checked after generation; none changed.
- Contact-sheet and original-resolution visual checks found no blank output, clipping, overlap, or unreadable labels.
