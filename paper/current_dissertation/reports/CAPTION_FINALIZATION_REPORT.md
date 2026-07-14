# Caption Finalization Report

## 1. Scope

This pass finalizes caption interpretation and placement for `FULL_DISSERTATION_FIGURE_TABLE_FINAL_V4.md`. It does not revise chapter arguments, experimental values, citations, figure numbering, or table content.

## 2. Caption Placement

- All 11 figure captions appear as standalone paragraphs below their image links.
- All 16 table captions appear as standalone paragraphs below their pipe tables.
- No caption is compressed into an image link, table row, heading, or body paragraph.

## 3. Figure Caption Finalization

| Figure | Finalization action | Preserved boundary |
| --- | --- | --- |
| Figure 4.2 | Retained in the main text and expanded the panel-scale note | Panel scales are metric-specific and should not be compared as a shared y-axis scale; endpoints remain alpha-sweep evidence |
| Figure 4.3 | Added the dataset-dependent panel x-axis range note | Paired NDCG remains alpha-sweep evidence, not strict NDCG@10 |
| Figure 4.4 | Added the dataset-dependent panel x-axis range note and restored the complete frozen SEP sentence | SEP is the implemented repository-specific score and is not independently validated user-perceived serendipity |
| Figure 4.5 | Added the dataset-dependent panel x-axis range note and standardized the paired-NDCG sentence | Paired NDCG remains alpha-sweep evidence; ETD remains a registered path-type diversity measure, not complete explanation quality |
| Figure 5.1 | Added the linear x-axis and near-origin cluster note | The figure remains PGPR/UCPR-only ablation evidence and does not establish six-model superiority |

The exact alpha-sweep panel note appears in Figures 4.3, 4.4, and 4.5:

> Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent.

The Figure 5.1 note explains that the linear axis preserves the largest gain magnitude and that near-origin clusters represent smaller but valid movements. It does not reinterpret those movements as statistical significance or model superiority.

## 4. Table Caption Finalization

| Table | Finalization action | Evidence boundary |
| --- | --- | --- |
| Table 3.4 | Added an explicit eligibility sentence | Validation status is not model performance |
| Table 4.1 | Retained without change | Accessible canonical status matrix and matching dissertation summary; expected primary row-level JSON unavailable |
| Table 4.2 | Added the repository-specific implementation qualifier | Endpoints remain alpha-sweep evidence, not strict accuracy or user-study evidence |
| Table 5.1 | Retained without change | Registered frozen-item-set PGPR/UCPR subset only |
| Table 5.3 | Added the partial-boundary sentence | Amazon-Book is not a complete main benchmark and blocked rows are not performance results |

All other table captions are unchanged.

## 5. Content Integrity

The 16 V3 and V4 pipe-table blocks are byte-for-byte identical. All 29 citation keys are retained. No result, claim status, evidence path, citation status, or chapter boundary changed.
