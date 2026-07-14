# Formula and Metric Consistency Audit

The formula audit uses the V5 Chapter 3 text and `FORMULA_INVENTORY_AND_EVIDENCE_MAP_SEP_TREND.md` as the immediate sources. It assesses internal consistency and evidential interpretation; it does not recompute any result.

| Formula / notation | Location | Consistent? | Risk | Fix needed |
| --- | --- | --- | --- | --- |
| Core user, item, dataset, model, and relation notation | Chapter 3 notation table and Sections 3.2–3.4 | Yes | Low | Keep symbol definitions in one authoritative notation table and preserve canonical/model-specific distinctions. |
| Top-K recommendation list notation | Sections 3.3–3.4 | Yes | Low | State how short or empty native-path lists enter averaging, consistent with the existing no-padding evaluator. |
| Native path notation and endpoint mapping | Section 3.3 | Yes | Low | Preserve the canonical endpoint and recommendation-explanation alignment conditions. |
| Validation gate \(V_{m,d}\) | Section 3.4 | Partly | Medium | Define explicitly how PASS, BLOCKED, PARTIAL, and N/A states map to the binary gate; do not change current eligibility. |
| Strict HR@K, Precision@K, Recall@K, and NDCG@K formulas | Section 3.4 | Yes, with edge conditions unstated | Medium | Document the registered evaluator's handling of users with zero relevant items and zero IDCG; do not infer an unverified convention. |
| LIR path and list aggregation | Section 3.4 | Yes | Medium | Clarify the behaviour for missing temporal anchors and empty recommendation/path lists, including the applicable denominator. |
| SEP path and list aggregation | Section 3.4 | Formula yes; interpretation inconsistent elsewhere | High | Keep \(\sigma_d\) as a repository-specific bridge-entity score. Do not infer rarity, direction, or user-perceived serendipity while the historical cache is unavailable. |
| ETD set and normalisation | Section 3.4 | Yes | Medium | State the registered legal path-type taxonomy and denominator source; clarify empty-list handling. |
| Alpha-sweep notation | Section 3.6 | Yes | Low | Retain the abstract objective-specific protocol and the 21-point registered grid; do not introduce a universal linear score formula. |
| Endpoint delta notation | Sections 3.6 and 4.4–4.6 | Yes | Low | Keep metric-specific superscripts and retain the distinction between sweep NDCG deltas and strict NDCG@10. |
| Ablation NDCG-retention formula | Sections 3.6 and 5.2 | Yes | Low | Add the applicability condition that the registered baseline denominator is nonzero; keep the 95% rule confined to the ablation stream. |
| Evidence eligibility sets \(\mathcal{A}\) and \(\mathcal{B}\) | Section 3.5 | Partly | Medium | Explain how the binary sets relate to PARTIAL and N/A labels so formal notation does not hide status granularity. |
| Absence of a universal linear alpha formula | Sections 3.6 and 4.1 | Yes | Low | Preserve the current abstract protocol; do not invent a coefficient equation not verified by the registered implementation. |
| Absence of a composite explanation score | Sections 3.4, 4.3, and 5.5 | Yes | Low | Continue reporting LIR, SEP, and ETD separately and avoid cross-scale arithmetic. |
| Absence of statistical-test formulas | Chapters 4–6 | Yes | Low | Keep results descriptive until repeated-run and inferential artifacts exist; do not add p-values, confidence intervals, or test formulas without evidence. |

The formal core is internally coherent. The required revisions are edge-condition and status-mapping clarifications plus the high-priority SEP interpretation repair; none requires changing a registered formula or numerical result.
