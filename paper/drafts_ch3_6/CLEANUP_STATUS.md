# Cleanup Status

## Scope

This cleanup pass covered the Phase 0-2 draft package under `paper/drafts_ch3_6/`.

No facts, numbers, evidence paths, citation status, chapter boundaries, or arguments were changed. No Chapter 4 drafting was performed.

## Files Checked

| File | Cleanup status | Notes |
| --- | --- | --- |
| `PHASE_0_GLOBAL_PLAN.md` | Checked | Markdown structure retained. |
| `CHAPTER_BOUNDARY_MAP.md` | Checked | Chapter boundary table retained. |
| `FIGURE_TABLE_MASTER_PLAN.md` | Updated | Figure 3.1 and Figure 3.2 paths added. |
| `CITATION_NEEDS_INITIAL.md` | Checked | Citation status retained. |
| `EXTERNAL_CITATION_AUDIT.md` | Checked | Citation facts and caveats retained. |
| `BIBTEX_SEED.bib` | Checked | BibTeX entries retained; no metadata changed. |
| `THESIS_WRITING_TRACEABILITY_LOG.md` | Updated | Generated figure paths added. |
| `chapter3_framework_implementation_and_verification_v2.md` | Checked | Chapter 3 prose retained. |
| `chapter3_tables.md` | Checked | Tables retained. |
| `chapter3_figure_specs.md` | Updated | Generated figure paths added. |
| `chapter3_evidence_used.md` | Checked | Evidence map retained. |

## Generated Figures

| Figure | Path | Type | Evidence basis |
| --- | --- | --- | --- |
| Figure 3.1 | `paper/drafts_ch3_6/figures/figure_3_1_framework_overview.png` | Black-and-white conceptual diagram | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` |
| Figure 3.2 | `paper/drafts_ch3_6/figures/figure_3_2_alpha_sweep_design.png` | Black-and-white conceptual diagram | `thesis_analysis_pack/final_explanation_summary_table.md`; canonical trade-off CSV bundle descriptions |

## Tooling Note

`matplotlib`, Pillow, Graphviz, and ImageMagick were not available in the environment. The two PNG files were generated with a minimal local PNG writer and simple black-and-white drawing primitives.

## Stop Point

Cleanup completed after Phase 0-2. The next writing phase remains Phase 3: Generate Chapter 4.
