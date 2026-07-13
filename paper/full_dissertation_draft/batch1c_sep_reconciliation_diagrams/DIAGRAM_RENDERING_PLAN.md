# Diagram Rendering Plan

## 1. Purpose

This plan records how the ten Batch 1C diagram specifications may later become publication-ready assets. It does not authorise rendering, change figure numbering, or alter any experimental artifact.

## 2. Rendering Strategy

Use Mermaid for readable draft review and Graphviz DOT as the preferred reproducible source for simple monochrome process diagrams. Use draw.io only where manual alignment materially improves the metric-anchor or quadrant schematic. Preserve the captions and evidence-role statements during any later conversion.

| Diagram | Draft source | Preferred final source | Final format | Rendering tool | Main text / appendix | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Framework dataflow | Mermaid + DOT | DOT | SVG | graphviz dot | Main text | Monochrome; preserve PASS versus boundary branches. |
| Validation flowchart | Mermaid + DOT | DOT | SVG | graphviz dot | Main text | Decision nodes must remain distinct from performance reporting. |
| Metric anchor schematic | Mermaid + DOT | DOT or draw.io | SVG | graphviz / draw.io | Main text or appendix | Freeze SEP wording before rendering. |
| Single-example trace | Markdown table | Word table / vector schematic | DOCX table + SVG | later formatting batch | Main text | Keep abstract placeholders unless a validated source row is recovered. |
| Alpha-sweep process | Mermaid + DOT | DOT | SVG | graphviz dot | Main text | Label paired sweep NDCG explicitly. |
| Evidence-stream separation | Mermaid + DOT | DOT | SVG | graphviz dot | Main text | Give all evidence streams equal visual weight. |
| Trade-off pattern schematic | Markdown matrix / DOT | vector schematic | SVG | graphviz / draw.io | Main text | Consider retaining as a table; do not plot pseudo-data. |
| Ablation evidence flow | Mermaid + DOT | DOT | SVG | graphviz dot | Main text | Retain PGPR/UCPR and frozen-item-set scope. |
| 95% retention operating point | Mermaid + DOT | DOT | SVG | graphviz dot | Main text or appendix | Threshold applies only to ablation. |
| Amazon boundary flow | Mermaid + DOT | DOT | SVG | graphviz dot | Main text or appendix | Preserve partial-boundary wording. |

## 3. Recommended Final Rendering Order

1. Framework dataflow.
2. Validation flowchart.
3. Evidence-stream separation.
4. Alpha-sweep process.
5. Ablation evidence flow.
6. Amazon boundary flow.
7. Metric anchor schematic after SEP wording freeze.
8. 95% retention operating point if retained in the main text.
9. Trade-off pattern schematic if not kept as a table.
10. Single-example vector schematic only if the Markdown table is insufficient.

## 4. Diagrams to Keep as Tables Instead of Figures

The single-example trace is clearest as aligned Markdown or Word tables. The empirical trade-off pattern can remain a 2-by-2 table if a vector quadrant would imply quantitative coordinates. These decisions avoid unnecessary figure density.

## 5. Diagrams Requiring Supervisor Decision

- Metric anchor schematic: main text or appendix.
- Trade-off pattern schematic: table or numbered figure.
- 95% retention operating point: main text or appendix.
- Amazon boundary flow: main text or appendix alongside the existing status matrix.
- Single-example trace: table only or table plus vector schematic.

## 6. Do Not Render Yet

This batch does not render figures. Rendering is deferred until chapter wording and figure placement are frozen.

No PNG, SVG, PDF, DOCX, or other rendered artifact is produced by this plan. Final rendering must also preserve the unresolved historical SEP matrix-cache caveat and the separation of strict accuracy, alpha-sweep, ablation, and boundary evidence.
