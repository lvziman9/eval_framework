# Figure Caption Final Report

## 1. Placement Result

All 11 displayed figure captions in `FULL_DISSERTATION_FIGURE_TABLE_READY_V2.md` are separate paragraphs immediately below their image links. PNG links are used for Markdown compatibility; matching SVG primary assets are listed in `FIGURE_REGENERATION_REPORT.md`.

## 2. Final Captions and Boundaries

| Figure | Final caption summary | Evidence boundary | Placement |
| --- | --- | --- | --- |
| Figure 3.1 | Implemented canonical native-path evaluation framework and reportability flow | Evaluation framework only; no new recommender architecture | Below figure |
| Figure 3.2 | Alpha-sweep experiment design and evidence separation | Sweep ranking metrics are not strict HR@10, NDCG@10, Precision@10, or Recall@10 | Below figure |
| Figure 3.3 | Validation gate for a model-dataset export package | BLOCKED or PARTIAL is not low performance | Below figure |
| Figure 4.1 | Strict NDCG@10 comparison | Strict evidence stream; not sweep NDCG; primary row-level JSON unavailable | Below figure |
| Figure 4.2 | LIR, SEP, and ETD endpoints at alpha=0 and alpha=1 | Alpha-sweep evidence; panel scales are metric-specific; no strict accuracy or user-study inference | Below figure |
| Figure 4.3 | LIR-oriented trade-off curves for LastFM and ML-1M | Paired NDCG is sweep evidence, not strict NDCG@10 | Below figure |
| Figure 4.4 | SEP-oriented trade-off curves under the implemented repository-specific SEP objective | Implemented SEP movement is not independently validated user-perceived serendipity; paired NDCG is not strict NDCG@10 | Below figure |
| Figure 4.5 | ETD-oriented trade-off curves for LastFM and ML-1M | ETD is path-type diversity under the registered taxonomy, not a complete explanation-quality measure | Below figure |
| Figure 5.1 | PGPR/UCPR ablation trade-offs under the frozen original top-k item set | PGPR/UCPR subset only; no six-model ablation or superiority inference | Below figure |
| Figure 5.2 | Validation-status matrix including partial Amazon-Book KGAT | Validation status, not comparative performance | Below figure |
| Figure C.1 | Decision flow for the partial Amazon-Book KGAT boundary case | Boundary-case status, not a full benchmark | Below figure |

## 3. Required Safety Wording

- Figure 4.1 states that strict NDCG@10 should not be confused with sweep NDCG.
- Figure 4.4 uses the frozen implemented-SEP and non-user-perceived-serendipity wording.
- Figure 5.1 states that PGPR/UCPR ablation is not all-six-model ablation evidence.
- Figure C.1 states that the Amazon flow is boundary-case status rather than full benchmark performance.

No caption introduces a significance, user-study, state-of-the-art, or new-model claim.
