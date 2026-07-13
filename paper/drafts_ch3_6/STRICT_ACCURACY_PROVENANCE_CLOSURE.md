# Strict-Accuracy Provenance Closure

## 1. Purpose

This file closes the provenance status of strict accuracy evidence used in Chapter 4 and the revised Chapter 3-6 package.

The check was read-only. It did not rerun evaluation, reconstruct artifacts, alter reports, or generate new experimental values.

## 2. Primary JSON Artifact Check

| Dataset | Model | Expected primary JSON path | Exists? | Notes |
| :--- | :--- | :--- | :--- | :--- |
| LastFM | PGPR | `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| LastFM | UCPR | `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| LastFM | CAFE | `runs/debug_compare/2026-06-20_native_path_expansion/cafe_lastfm_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| LastFM | TPRec | `runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_lastfm_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| LastFM | KGGLM | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_lastfm_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| LastFM | PEARLM | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_lastfm_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | PGPR | `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | UCPR | `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | CAFE | `runs/debug_compare/2026-06-20_native_path_expansion/cafe_ml1m_accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | TPRec | `runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_ml1m_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | KGGLM | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_ml1m_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |
| ML-1M | PEARLM | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_ml1m_v1/accuracy.json` | no | Absent from the current worktree and not present at this path in `HEAD`. |

Result: `0/12` expected primary strict-accuracy JSON artifacts are accessible in the current worktree. No duplicate file with the same terminal name and canonical dataset path was found elsewhere in the repository.

## 3. Accessible Accuracy Evidence Sources

| Source path | Evidence type | Covers datasets/models | Can be used as final provenance? | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `reports/tables/canonical_native_path_status_matrix.csv` | Machine-readable canonical status and accuracy summary | All six models on LastFM and ML-1M; partial Amazon rows | yes, as the current accessible canonical summary source | Contains HR@10, NDCG@10, Precision@10, Recall@10, row status, validation path, and expected primary evidence path. It does not replace the missing row-level JSON lineage. SHA-256 at audit: `7df79e2ae51ea2eaba45e22b9dee45cd906bb324a8504b9e2f8fe21ce6af8bbe`. |
| `thesis_analysis_pack/final_accuracy_summary_table.md` | Human-readable dissertation accuracy summary | All six models on LastFM and ML-1M; partial Amazon rows | yes, as the current accessible presentation source | Its 12 LastFM/ML-1M metric rows match the canonical CSV exactly in a field-by-field comparison. SHA-256 at audit: `c6311d63589f9b5ad1ed01f12f112d8b76a6dcd497e1df1663628581390af2a2`. |
| `thesis_analysis_pack/goal_5_accuracy_summary.md` | Narrative extraction record | Same accuracy rows and evidence paths | supporting only | Confirms that strict accuracy was extracted from the status matrix and expected per-row JSON paths; it is not an independent primary measurement artifact. |
| `reports/tables/canonical_export_validation/manifest.json` and per-row JSON files | Export-validation evidence | 12 main rows plus three completed Amazon rows | no, not for metric values | Establishes PASS status and coverage/export counts. It does not contain HR@10, NDCG@10, Precision@10, or Recall@10. |
| `reports/tables/canonical_native_path_artifact_manifest.json` | Artifact manifest | Selected core files and Amazon readiness artifacts | supporting only | It hashes the status matrix and selected artifacts but does not register the 12 missing LastFM/ML-1M accuracy JSON files. |
| `paper/drafts_ch3_6/chapter4_evidence_used.md` | Chapter evidence map | Chapter 4 strict-accuracy claims | supporting only | Correctly records the accessible-summary fallback and the missing-primary-JSON caveat. |
| `paper/drafts_ch3_6/THESIS_WRITING_TRACEABILITY_LOG.md` | Cross-chapter provenance register | Chapter 3-6 package | supporting only | Separates strict accuracy, alpha-sweep, and ablation evidence and retains the primary-path caveat. |

## 4. Final Provenance Decision

| Accuracy claim type | Final evidence source | Required thesis wording | Caveat |
| :--- | :--- | :--- | :--- |
| Exact LastFM and ML-1M strict HR@10, NDCG@10, Precision@10, and Recall@10 values | `reports/tables/canonical_native_path_status_matrix.csv`, presented through `thesis_analysis_pack/final_accuracy_summary_table.md` | "Strict accuracy values are currently traceable to the accessible canonical status matrix and the matching dissertation summary table." | Do not state that the 12 primary JSON artifacts were inspected or verified. |
| Dataset/model ranking statements derived from those values | The same two matching accessible tables | "Rankings are descriptive comparisons of the values recorded in the accessible canonical summaries." | No statistical-significance artifact is registered. |
| Export completeness and validation status | `reports/tables/canonical_export_validation/manifest.json` and per-row validation JSON files | "Canonical exports passed the registered validation checks for the completed rows." | Validation PASS does not independently verify accuracy values. |
| Alpha-sweep trade-off values | Canonical trade-off CSV bundles and `final_explanation_summary_table.md` | "Alpha-sweep metrics are a separate evidence stream from strict accuracy." | Never substitute sweep NDCG or ablation NDCG for strict NDCG@10. |
| PGPR/UCPR ablation values | `reports/tables/ablation/pgpr_ucpr_path_module/` | "Ablation evidence evaluates controllability under its registered preservation protocol." | It is not the six-model strict-accuracy source. |

Final decision: the Chapter 4 strict values have draft-level traceability through two matching accessible summaries, but primary-artifact closure is incomplete. This is adequate for continued Chapter 1-2 drafting with an explicit provenance caveat, not for claiming primary JSON verification or final archival completeness.

## 5. Required Updates Before Final Submission

| Issue | Required action | Priority |
| :--- | :--- | :--- |
| Twelve expected row-level accuracy JSON files are absent | Recover the original files from the experiment archive, or rerun only under a separately approved reproducibility task that preserves outputs and records commands, versions, and hashes. | critical |
| Current artifact manifest does not cover the 12 expected files | Add recovered JSON paths, SHA-256 hashes, sizes, and timestamps to a final immutable artifact manifest. | high |
| Summary-table lineage is not independently reproducible from accessible row-level metrics | Archive the command and evaluator version used to generate the canonical matrix, together with input export hashes. | high |
| Draft prose may imply stronger provenance than is available | Retain the wording above and avoid "primary JSON verified" or "directly inspected" until recovery is complete. | high |
| No significance artifact is registered | Keep accuracy comparisons descriptive unless a valid statistical analysis artifact is added. | medium |
