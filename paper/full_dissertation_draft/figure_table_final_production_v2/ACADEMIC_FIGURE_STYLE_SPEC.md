# Academic Figure Style Specification

## 1. Scope

This specification governs the 11 dissertation figures in the versioned academic redraw package. It follows the local `matplotlib` and `scientific-visualization` skill guidance while preserving the dissertation-specific evidence boundaries.

## 2. Figure Geometry

- Quantitative two-panel figures use a 7.2-inch nominal page width.
- Multi-panel endpoint figures use a 7.2-inch width with a 2-by-3 aligned grid.
- Panels use consistent margins, title placement, axis weights, and inter-panel spacing.
- Figure-level titles are omitted because the dissertation caption supplies the title and evidence role.
- Panel labels use bold lowercase letters and dataset names, for example `(a) LastFM` and `(b) ML-1M`.

## 3. Typography

- Font family: DejaVu Sans, embedded as text in SVG.
- Base size: 8 pt.
- Axis labels: 8.5 pt.
- Tick labels: 7.2 pt.
- Panel labels: 8.5 pt, bold.
- Legends: 7.2 pt, frameless.
- Sentence case is used for axis and diagram labels.
- No console bitmap, monospace, decorative, or handwritten font is used.

## 4. Colour and Redundant Encoding

The model palette is based on the colourblind-safe Okabe-Ito family:

| Model | Colour | Marker | Line style |
| --- | --- | --- | --- |
| PGPR | Blue `#0072B2` | Circle | Solid |
| UCPR | Vermillion `#D55E00` | Square | Dashed |
| CAFE | Bluish green `#009E73` | Triangle | Dash-dot |
| TPRec | Reddish purple `#CC79A7` | Diamond | Dotted |
| KGGLM | Near black `#222222` | Filled plus | Long dash |
| PEARLM | Orange `#E69F00` | X | Dash-dot variant |

Colour is never the only encoding. Marker shape and line style preserve model identity in grayscale. Status cells additionally use text and hatching.

## 5. Quantitative Figure Rules

- Use the Matplotlib object-oriented API.
- Remove top and right spines.
- Use restrained horizontal grid lines only.
- Avoid three-dimensional effects, shadows, gradients, and chart decoration.
- Use one objective per alpha-sweep figure.
- Keep the fixed model order: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.
- Keep the fixed dataset order: LastFM, ML-1M.
- Label strict results as `Strict NDCG@10`.
- Label alpha-sweep ranking values as `Sweep NDCG`.
- Do not add significance markers because no statistical-significance artifact is registered.
- Do not imply that PGPR/UCPR ablation covers all six models.

## 6. Diagram Rules

- Graphviz provides consistent box, diamond, arrow, font, border, and spacing treatment.
- Blue-tinted nodes indicate canonical/reportable processing stages.
- Green-tinted nodes indicate PASS outcomes.
- Amber-tinted nodes indicate BLOCKED, PARTIAL, or boundary outcomes.
- All validation and boundary flow diagrams read from top to bottom.
- Diagram labels describe evidence eligibility and do not introduce performance claims.

## 7. Export Rules

- SVG is the primary formal figure format.
- SVG text remains editable and uses DejaVu Sans.
- PNG is a high-resolution compatibility preview.
- Matplotlib line art is exported at 600 DPI.
- Graphviz SVG is converted with CairoSVG to 3200-3600 pixel-wide PNG.
- Backgrounds are white and non-transparent.
- JPEG, screenshots, Word, PDF, and LaTeX outputs are not used in this pass.

## 8. Caption Boundary

Captions remain outside the figure assets and below each image in the Markdown assembly. Existing strict/sweep/ablation/boundary and SEP interpretation caveats remain unchanged.
