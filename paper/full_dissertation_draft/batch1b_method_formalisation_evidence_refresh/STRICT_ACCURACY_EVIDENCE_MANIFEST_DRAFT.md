# Strict Accuracy Evidence Manifest Draft

## 1. Current Status

Strict accuracy for the complete LastFM and ML-1M six-model scope has draft-level provenance through two accessible and exactly matching summaries. The twelve expected row-level primary accuracy JSON artifacts are not accessible in the current worktree (`0/12`). This manifest records the present evidence state; it does not recreate, infer, or verify the missing primary artifacts.

The accessible summaries support continued dissertation drafting with an explicit provenance caveat. They do not support a statement that primary JSON evidence was directly inspected.

## 2. Accessible Evidence Sources

| Source | Path | Role | Hash if computed | Status |
| --- | --- | --- | --- | --- |
| Canonical native-path status matrix | `reports/tables/canonical_native_path_status_matrix.csv` | Machine-readable source for row status and strict HR@10, NDCG@10, Precision@10, and Recall@10 values | SHA-256 `7df79e2ae51ea2eaba45e22b9dee45cd906bb324a8504b9e2f8fe21ce6af8bbe` | Accessible; current canonical summary |
| Final accuracy summary table | `thesis_analysis_pack/final_accuracy_summary_table.md` | Human-readable dissertation presentation of the strict values | SHA-256 `c6311d63589f9b5ad1ed01f12f112d8b76a6dcd497e1df1663628581390af2a2` | Accessible; matches the canonical matrix |
| Strict-accuracy provenance closure | `paper/drafts_ch3_6/STRICT_ACCURACY_PROVENANCE_CLOSURE.md` | Read-only audit of expected primary paths, accessible fallbacks, and allowed wording | Not recomputed for this manifest | Accessible; supporting audit |
| Export validation manifest and row summaries | `reports/tables/canonical_export_validation/manifest.json`; `reports/tables/canonical_export_validation/*.json` | Establish PASS status, coverage, and export conformity | Not computed in Batch 1B | Accessible; not a source of strict metric values |
| Thesis traceability log | `paper/drafts_ch3_6/THESIS_WRITING_TRACEABILITY_LOG.md` | Cross-chapter evidence register and stream-separation record | Not computed in Batch 1B | Accessible; supporting register |

## 3. Missing Primary Artifacts

| Expected artifact type | Expected count | Accessible count | Impact | Current caveat |
| --- | ---: | ---: | --- | --- |
| LastFM row-level strict accuracy JSON | 6 | 0 | Primary lineage cannot be inspected for the six LastFM models. | Use the two matching accessible summaries and do not claim primary JSON verification. |
| ML-1M row-level strict accuracy JSON | 6 | 0 | Primary lineage cannot be inspected for the six ML-1M models. | Use the two matching accessible summaries and do not claim primary JSON verification. |
| Total row-level strict accuracy JSON | 12 | 0 | Final archival and primary-artifact closure remain incomplete. | Recover the original artifacts and register their hashes before final submission. |

The expected paths are listed in `paper/drafts_ch3_6/STRICT_ACCURACY_PROVENANCE_CLOSURE.md` and in the `primary_evidence` column of the canonical status matrix. Batch 1B does not create substitutes for those files.

## 4. Equality Check Summary

The provenance closure records a field-by-field comparison of the twelve LastFM and ML-1M rows. Dataset, model, HR@10, NDCG@10, Precision@10, and Recall@10 match exactly between `reports/tables/canonical_native_path_status_matrix.csv` and `thesis_analysis_pack/final_accuracy_summary_table.md`.

The SHA-256 values recomputed for Batch 1B are the same as those recorded by the prior closure audit:

| File | Equality-check role | SHA-256 |
| --- | --- | --- |
| `reports/tables/canonical_native_path_status_matrix.csv` | Canonical machine-readable summary | `7df79e2ae51ea2eaba45e22b9dee45cd906bb324a8504b9e2f8fe21ce6af8bbe` |
| `thesis_analysis_pack/final_accuracy_summary_table.md` | Matching dissertation summary | `c6311d63589f9b5ad1ed01f12f112d8b76a6dcd497e1df1663628581390af2a2` |

This equality check demonstrates consistency between two accessible summaries. It does not independently recover or verify the twelve missing primary JSON files.

## 5. Wording Allowed in Dissertation

The following wording is allowed at the current evidence level:

> strict accuracy values are traceable to the accessible canonical status matrix and matching dissertation summary table

Additional safe wording is:

- The twelve LastFM and ML-1M rows match exactly across the two accessible summaries.
- Strict accuracy and alpha-sweep ranking metrics are separate evidence streams.
- Rankings are descriptive comparisons of the values recorded in the accessible canonical summaries.
- Canonical exports passed the registered validation checks for completed rows; validation PASS does not independently verify strict metric values.

## 6. Wording Not Allowed

The following wording is not allowed:

> strict accuracy values were verified from the twelve primary JSON artifacts

The draft must also avoid stating that the primary JSON files were directly inspected, that strict-accuracy provenance is fully archived, that summary agreement is an independent experimental replication, or that alpha-sweep or ablation NDCG replaces strict NDCG@10.

## 7. Required Action Before Final Submission

1. Recover the twelve original row-level strict accuracy JSON files from the experiment archive, or conduct a separately approved reproducibility task without overwriting registered outputs.
2. Register each recovered path, SHA-256 hash, file size, timestamp, evaluator version, and relevant input-export hashes in an immutable manifest.
3. Reproduce the canonical status matrix from the recovered primary files and record the exact command and environment.
4. Repeat the field-by-field comparison against the dissertation summary.
5. Retain descriptive wording unless a separately registered statistical-significance artifact is added.
6. Do not remove the current caveat until primary-artifact recovery and manifest verification are complete.
