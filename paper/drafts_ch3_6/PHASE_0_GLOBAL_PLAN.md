# Phase 0 Global Plan

## Purpose

This draft package covers Chapter 3 to Chapter 6 of the dissertation:

**A Canonical Framework for Accuracy-Explainability Trade-off Analysis in Native-Path Knowledge Graph Recommenders**

The package is evidence-driven. It uses repository evidence for experimental claims and external literature only for background, model context, and related-work support. It does not retrain models, rerun pipelines, or modify experiment outputs.

## Execution Boundary

Only writing outputs are created under `paper/drafts_ch3_6/`. Existing experiment files, datasets, checkpoints, adapters, and evaluation scripts are treated as read-only evidence.

The recommended execution strategy is followed in this pass:

1. Phase 0: global plan and boundary audit.
2. Phase 1: external citation audit.
3. Phase 2: Chapter 3 draft package.
4. Pause before Chapter 4.

## Evidence Hierarchy

Primary internal evidence:

- `thesis_analysis_pack/FINAL_THESIS_HANDOFF.md`
- `thesis_analysis_pack/final_accuracy_summary_table.md`
- `thesis_analysis_pack/final_explanation_summary_table.md`
- `thesis_analysis_pack/validation_status_table.md`
- `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`
- `docs/guides/CANONICAL_DATASET_STANDARD.md`
- `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- `docs/guides/PATH_METRICS_GUIDE.md`
- `reports/tables/canonical_export_validation/manifest.json`
- `reports/tables/canonical_native_path_status_matrix.md`

Secondary internal evidence:

- `thesis_analysis_pack/goal_10_insight_notes.md`
- `thesis_analysis_pack/goal_11_chapter_5_material_pack.md`
- `thesis_analysis_pack/goal_13_limitations_and_risks.md`
- `reports/tables/ablation/pgpr_ucpr_path_module/`
- `reports/figures/thesis_final/`

External evidence is used only where repository files do not establish background facts, model origins, or related-work context.

## Chapter Plan

Chapter 3 explains the implemented framework, validation-first export contract, canonical dataset/view design, metrics, verification results, and setup for later trade-off and ablation experiments.

Chapter 4 reports the main results. It separates strict accuracy results from alpha-sweep explanation/trade-off results. LastFM and ML-1M are the main complete datasets. Amazon-Book KGAT is excluded from the main trade-off analysis.

Chapter 5 discusses ablation, mechanisms, interaction patterns, boundary cases, and limitations. It does not repeat all Chapter 4 result tables.

Chapter 6 concludes and recommends further research. It introduces no new results.

## Risk Controls

- Do not claim a new recommender model.
- Do not claim state-of-the-art performance.
- Do not cite README TODOs as completed evidence.
- Keep native-path explanations separate from post-hoc path recovery.
- Keep strict accuracy JSON evidence separate from alpha-sweep CSV evidence.
- Treat Amazon-Book KGAT as a partial stress test and boundary case.

