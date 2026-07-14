# Result Figure Style Guide

## 1. General Style

- Academic, clean, and print-friendly presentation.
- SVG is the primary formal asset; high-resolution PNG is the Markdown preview.
- Chapter 4 uses consistent widths, panel margins, typography, grid treatment, and legend placement.
- Model and legend order is fixed: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.
- Dataset and panel order is fixed: (a) LastFM, (b) ML-1M.
- Metric names are fixed: HR@10, NDCG@10, Precision@10, Recall@10, LIR, SEP, ETD.
- Use "sweep NDCG" for alpha-sweep ranking values.
- Use "strict NDCG@10" only for the strict accuracy evidence stream.
- Colour is reinforced by marker shape and line-dash differences so interpretation does not depend on colour alone.
- Figures must remain legible in grayscale and at normal dissertation page width.

## 2. Strict Accuracy Figures

- The main text uses one two-panel strict NDCG@10 comparison figure.
- HR@10 and NDCG@10 are not combined in the same bar chart.
- Table 4.1 carries HR@10, Precision@10, and Recall@10 details.
- No HR@10 appendix figure is required because the table supports the existing textual claims without adding another main comparison visual.
- The y-axis label is `Strict NDCG@10`; it must not be labelled as sweep NDCG.

## 3. Alpha-Sweep Figures

- Use one figure per objective: LIR, SEP, or ETD.
- Each objective figure has two panels: (a) LastFM and (b) ML-1M.
- Model and legend order are identical across all three figures.
- The x-axis is the implemented objective value: `LIR`, `Implemented SEP score`, or `ETD`.
- The y-axis is `Sweep NDCG`.
- Captions state that sweep NDCG is not strict NDCG@10.
- No significance marker is shown because no registered statistical-significance artifact is available.

## 4. SEP Caption Boundary

The SEP caption must state both boundaries:

1. SEP is the implemented repository-specific SEP objective or score.
2. Movement along SEP is not independently validated user-perceived serendipity.

The final Figure 4.4 caption uses the frozen wording and makes no user-study claim.

## 5. Export Rules

- Preserve vector geometry and text in SVG.
- Export PNG previews at 2100-2400 pixels wide, depending on the figure layout.
- Use white backgrounds, restrained grid lines, and stable panel dimensions.
- Do not use screenshots, Mermaid output blocks, or raster upscaling as formal sources.
- Keep captions in Markdown rather than embedding the full caption into the figure image.
