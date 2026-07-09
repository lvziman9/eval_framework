
# Goal 3: Model and Method Audit

## Goal Number

Goal 3

## Current Task

Identify models represented in the repository, separate native-path models from non-native-path or accuracy-only references, and define each model's dissertation role.

## Key Findings

1. The main comparison set is six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.
2. LastFM and ML-1M have complete rows for all six models, with accuracy metrics, export validation, and alpha-sweep figure bundles.
3. Amazon-Book KGAT has complete formal rows only for KGGLM, PEARLM, and PGPR. UCPR, CAFE, and TPRec must be written as blocked/N/A, not missing values to be filled.
4. KGIN, KGAT, LightGCN, MKR, CKE, and RippleNet are discussed in docs as strong non-path or accuracy-only candidates. They should not enter LIR/SEP/ETD comparison unless a faithful native path mechanism is available.
5. TransE appears in logs and validation as an embedding/preprocessing component, not as a final recommender row for dissertation comparison.

## Model Scope Table

| Model | Native path available? | Datasets completed | Accuracy metrics available? | Explanation metrics available? | Dissertation role | Evidence file paths |
| --- | --- | --- | --- | --- | --- | --- |
| PGPR | Yes | LastFM, ML-1M, Amazon-Book KGAT | Yes | Yes for LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | Native RL/path reasoning baseline; main comparison model | reports/tables/canonical_native_path_status_matrix.md; docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md |
| UCPR | Yes | LastFM, ML-1M | Yes | Yes for completed LastFM/ML-1M; blocked on Amazon | Native path baseline on LastFM/ML-1M; Amazon blocked | reports/tables/canonical_native_path_status_matrix.md; reports/tables/amazon_classic_port_readiness.json |
| CAFE | Yes | LastFM, ML-1M | Yes | Yes for completed LastFM/ML-1M; blocked on Amazon | Native path baseline on LastFM/ML-1M; Amazon blocked pending port | reports/tables/canonical_native_path_status_matrix.md; reports/tables/amazon_classic_port_readiness.json |
| TPRec | Yes where timestamps are valid | LastFM, ML-1M | Yes | Yes for completed LastFM/ML-1M; blocked on Amazon | Temporal native-path baseline on LastFM/ML-1M; Amazon blocked by sentinel timestamps | docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md; reports/tables/amazon_classic_port_readiness.json |
| KGGLM | Yes | LastFM, ML-1M, Amazon-Book KGAT | Yes | Yes for LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | Path-language-model native-path baseline; main comparison model | docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md; reports/tables/canonical_native_path_status_matrix.md |
| PEARLM | Yes | LastFM, ML-1M, Amazon-Book KGAT | Yes | Yes for LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | KG-constrained path-language-model baseline; main comparison model | docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md; reports/tables/canonical_native_path_status_matrix.md |
| KGIN | No native recommendation path | N/A | Deferred / N/A | No | Accuracy-only reference / optional appendix, not LIR/SEP/ETD | README.md; docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md; docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md |
| KGAT | No native recommendation path in current protocol | N/A | Deferred / N/A | No | Accuracy-only reference / optional appendix | README.md; docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md; docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md |
| LightGCN | No native KG path | N/A | Deferred / N/A | No | Accuracy-only reference / optional appendix | README.md; docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md; docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md |
| TransE | No: embedding component | N/A | Deferred / N/A | No | Training/preprocessing component, not a recommender row | docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md; reports/tables/amazon_classic_port_readiness.json |

## Dissertation Placement

- Main Chapter 4 comparison: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM on LastFM and ML-1M.
- Secondary boundary comparison: KGGLM, PEARLM, PGPR on Amazon-Book KGAT.
- Limitations or appendix: Amazon UCPR/CAFE/TPRec blocked rows; non-path accuracy-only models.
- Method chapter: model-specific views and adapters rather than model novelty.

## Generated Files

- `thesis_analysis_pack/goal_3_model_audit.md`
- `thesis_analysis_pack/model_scope_table.md`

## Next Goal

Goal 4: Final result file inventory.
