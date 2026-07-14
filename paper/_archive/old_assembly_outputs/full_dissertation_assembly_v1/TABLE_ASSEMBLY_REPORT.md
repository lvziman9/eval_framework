# Table Assembly Report

## 1. Assembly Summary

The assembled dissertation contains 16 numbered Markdown tables. Every table is a multiline pipe table with a standalone caption. No table is compressed into one physical line, and no experimental value was recalculated or changed.

## 2. Table Decisions

| Table | Assembly action | Evidence source | Value or claim boundary | Status |
| --- | --- | --- | --- | --- |
| Table 1.1 | Numbered the existing V7 objective table. | Batch 2C V7 Chapter 1 | Objective wording and chapter mapping unchanged. | Included |
| Table 2.1 | Added a concise literature synthesis from existing Chapter 2 themes and citation keys. | Batch 2C V7 Chapter 2 | Bounded to the reviewed corpus; no exhaustive-literature claim. | Included |
| Table 3.1 | Reproduced the registered four-row dataset summary. | `dataset_summary_table.md` | Amazon remains partial; `beauty_legacy_v1` remains historical/appendix only. | Included |
| Table 3.2 | Reproduced the registered ten-row model scope. | `model_scope_table.md` | Non-native-path rows are not assigned explanation metrics. | Included |
| Table 3.3 | Converted the existing three-file export contract into a display table. | V7 Chapter 3 | No new export artifact or requirement. | Included |
| Table 3.4 | Converted the existing validation checks into a display table. | V7 Chapter 3 | Validation failure is not low model performance. | Included |
| Table 3.5 | Numbered and repositioned the existing V7 configuration table. | V7 Chapter 3 | Missing seeds, checkpoints, and settings remain unavailable. | Included |
| Table 3.6 | Inserted the frozen evidence-boundary table. | `REVISED_TABLES_AND_CAPTIONS_SEP_TREND.md` | Strict accuracy, sweeps, ablation, and boundary evidence remain separate. | Included |
| Table 4.1 | Selected the 12 LastFM/ML-1M rows and six display columns from the registered summary. | `final_accuracy_summary_table.md` | The expected 12 primary row-level JSON artifacts remain inaccessible. | Included |
| Table 4.2 | Selected the 12 LastFM/ML-1M endpoint rows and five display columns. | `final_explanation_summary_table.md` | Endpoints are alpha-sweep evidence; SEP semantics remain frozen. | Included |
| Table 4.3 | Numbered the existing V7 empirical-pattern table. | Batch 2C V7 Chapter 4 | Descriptive patterns are not causal or statistically significant. | Included |
| Table 5.1 | Joined exact alpha-zero status with exact selected operating-point fields for all 12 eligible combinations. | Two registered PGPR/UCPR ablation CSVs | Applies only to the frozen-item-set ablation. | Included |
| Table 5.2 | Inserted the frozen mechanism-boundary table. | `REVISED_TABLES_AND_CAPTIONS_SEP_TREND.md` | Non-PGPR/UCPR mechanism accounts remain descriptive. | Included |
| Table 5.3 | Selected all six Amazon rows and their exact validation fields. | `validation_status_table.md` | Three PASS and three BLOCKED / N/A rows; no performance ranking. | Included |
| Table 5.4 | Inserted the frozen limitations table. | `REVISED_TABLES_AND_CAPTIONS_SEP_TREND.md` | All open caveats remain visible. | Included |
| Table 6.1 | Numbered the existing V7 objective-closure table. | Batch 2C V7 Chapter 6 | No new conclusion or evidence was added. | Included |

## 3. Formatting Verification

The assembled file contains 16 contiguous pipe-table blocks and 16 unique captions numbered Table 1.1 through Table 6.1. The Chapter 3 notation material was converted from an unnumbered pipe table to an equivalent definition list so that every remaining pipe table has an explicit number and caption.

## 4. Evidence Safety

Strict values are reproduced from the accessible final summary, explanation endpoints from the registered endpoint summary, and ablation values from the two registered CSVs. Amazon values and statuses are not promoted into the complete main comparison. No table introduces statistical-significance, user-study, universal-superiority, or new-model claims.

