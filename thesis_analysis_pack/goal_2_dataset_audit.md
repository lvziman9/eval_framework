
# Goal 2: Dataset and Experiment Scope Audit

## Goal Number

Goal 2

## Current Task

Identify datasets used by the project, separate main experiment datasets from secondary, partial, blocked, or historical datasets, and state how each should be used in the dissertation.

## Key Findings

1. LastFM and ML-1M are the main dissertation datasets. Both have six complete rows in `reports/tables/canonical_native_path_status_matrix.csv`: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
2. Amazon-Book KGAT is useful as a larger native-KG stress test, but it is not a fully symmetric six-model explanation experiment. KGGLM, PEARLM, and PGPR have complete formal accuracy/export rows; UCPR, CAFE, and TPRec remain blocked.
3. Amazon alpha-sweep figures and LIR/SEP/ETD trade-off claims are N/A under the current evidence because no approved timestamp/SEP/ETD denominator exists.
4. Beauty-related artifacts should be treated as historical/reference or appendix material, not as the main Amazon-Book KGAT experiment.
5. The dissertation should not hide blocked rows. Blocked rows are part of the framework evaluation: they show where native-path compatibility, timestamp semantics, or model-specific schema support are required before a fair comparison exists.

## Dataset Summary

| Dataset | Role in dissertation | Models available | Metrics available | Validation status | Limitations | Evidence file paths |
| --- | --- | --- | --- | --- | --- | --- |
| LastFM | Main experiment dataset | PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM | HR@10, NDCG@10, Precision@10, Recall@10; Accuracy plus LIR/SEP/ETD alpha-sweep evidence | PASS for complete rows | Use canonical status matrix and trade-off bundles; avoid older duplicate figure folders | reports/tables/canonical_native_path_status_matrix.md; docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md |
| ML-1M | Main experiment dataset | PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM | HR@10, NDCG@10, Precision@10, Recall@10; Accuracy plus LIR/SEP/ETD alpha-sweep evidence | PASS for complete rows | Use canonical status matrix and trade-off bundles; avoid older duplicate figure folders | reports/tables/canonical_native_path_status_matrix.md; docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md |
| Amazon-Book KGAT | Secondary stress-test / boundary dataset | KGGLM, PEARLM, PGPR | HR@10, NDCG@10, Precision@10, Recall@10; Accuracy complete for KGGLM/PEARLM/PGPR; LIR/SEP/ETD alpha sweeps N/A | PASS for complete rows; blocked rows: UCPR, CAFE, TPRec | No approved timestamp/SEP/ETD denominator; UCPR/CAFE/TPRec blocked | reports/tables/canonical_native_path_status_matrix.md; docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md |
| beauty_legacy_v1 | Historical/reference or appendix only | Historical CAFE/PGPR references in docs; not a current main result row | Not part of final status matrix | N/A in current canonical native-path status matrix | Compatibility protocol with empty validation split; should not be presented as large Amazon-Book KGAT result | docs/guides/CANONICAL_DATASET_STANDARD.md; docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md |

## Suggested Dissertation Use

- Chapter 3: Use all three canonical datasets to explain framework scope, but emphasize canonical LastFM and ML-1M as the complete evaluation design.
- Chapter 4: Use LastFM and ML-1M as the primary empirical accuracy and explanation results. Use Amazon-Book KGAT as a secondary formal comparison for completed rows only.
- Chapter 5: Discuss Amazon-Book KGAT as a boundary case demonstrating validation-first evaluation and honest blocked/N/A handling.
- Appendix: Place historical Beauty or legacy material there if needed for provenance.

## Generated Files

- `thesis_analysis_pack/goal_2_dataset_audit.md`
- `thesis_analysis_pack/dataset_summary_table.md`

## Next Goal

Goal 3: Model and method audit.
