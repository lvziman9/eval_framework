# Chapter 3 Figure Specifications

## Figure 3.1 Overview of the Implemented Canonical Native-Path Evaluation Framework

Type: Conceptual pipeline diagram.

Status: Planned, not generated in this phase.

Evidence basis:

- `thesis_analysis_pack/goal_12_chapter_3_material_pack.md`
- `docs/guides/CANONICAL_DATASET_STANDARD.md`
- `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- `reports/tables/canonical_export_validation/manifest.json`

Required content:

1. Raw/preprocessed dataset and KG sources.
2. Canonical dataset layer: shared `uid`, `pid`, splits, labels, KG provenance.
3. Model-specific views: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM.
4. Native model inference output.
5. Canonical export contract: `uid_topk.csv`, `pred_paths.csv`, `uid_pid_explanation.csv`.
6. Validation gate: coverage, leakage, endpoint consistency, alignment.
7. Evaluation metrics: HR@10, NDCG@10, Precision@10, Recall@10, LIR, SEP, ETD.
8. Report layer: status matrix, accuracy table, explanation table, trade-off figures.

Caption draft:

Figure 3.1 shows the implemented canonical native-path evaluation framework. The framework standardises dataset truth and exported evidence while allowing each model to use its own internal view. Reportable results must pass the validation gate before accuracy or explanation metrics are interpreted.

## Figure 3.2 Alpha-Sweep Trade-off Experiment Design

Type: Conceptual experiment-design diagram.

Status: Planned, not generated in this phase.

Evidence basis:

- `thesis_analysis_pack/final_explanation_summary_table.md`
- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`

Required content:

1. Strict accuracy source: accuracy JSON / final accuracy table.
2. Alpha-sweep source: trade-off CSVs.
3. Alpha=0 endpoint.
4. Intermediate alpha values.
5. Alpha=1 endpoint.
6. Separate output panels for LIR, SEP, and ETD.
7. Warning label: alpha-sweep metrics are trade-off evidence, not strict accuracy replacement.

Caption draft:

Figure 3.2 illustrates the alpha-sweep design used for trade-off analysis. Strict accuracy values are kept separate from alpha-sweep evidence, which is used to inspect how explanation-oriented objectives affect ranking and path properties.

