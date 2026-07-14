# Terminology Consistency Map

| Preferred term | Avoid / variant | Meaning | Used in chapters | Notes |
| --- | --- | --- | --- | --- |
| native-path explanation | native explanation; faithful path without qualification | A path emitted by or retained from the model's recommendation or path-selection workflow. | 1–6 | Native origin does not automatically establish causal faithfulness or user usefulness. |
| post-hoc explanation | recovered path treated as native; reconstructed native path | An explanation produced after recommendation by a separate attribution, search, or explanatory process. | 1–3; 5–6 | Keep outside the main native-path LIR/SEP/ETD comparison. |
| canonical dataset | common dataset; unified internal graph | The shared users, items, splits, labels, KG provenance, and mapping requirements used for evaluation. | 1–3; 5–6 | It standardises evaluation truth, not every model's internal representation. |
| model-specific view | model dataset; private dataset | A model-compatible projection or remapping derived from canonical truth. | 1–3; 5–6 | Outputs must map back to canonical identifiers. |
| native-path export contract | common output format; path export format | The required recommendation, path, explanation, identifier, and alignment semantics for a reportable native-path row. | 1–3; 5–6 | Required artifacts include `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv`. |
| strict accuracy | baseline accuracy; final accuracy without source label | HR@10, NDCG@10, Precision@10, and Recall@10 from the registered strict-accuracy evidence stream. | 1; 3–6 | Current draft values come from two matching summaries; do not imply primary JSON inspection. |
| alpha-sweep | alpha experiment; trade-off accuracy | A controlled trajectory in which alpha changes an explanation-oriented objective and paired metrics are recorded. | 1–6 | Hyphenate consistently. Sweep ranking metrics are not strict accuracy. |
| LIR | recency score; interaction recency without definition | Linked interaction recency under the repository implementation. | 1–6 | Conceptual origin: XRecSys; exact formula and timestamp assumptions: internal guide/code. |
| SEP | popularity score; novelty score | Shared entity popularity/serendipity under the repository implementation, operationalised through bridge-entity degree or rarity. | 1–6 | Do not equate automatically with all forms of novelty or unexpectedness. |
| ETD | diversity score; explanation diversity | Explanation type diversity across the path types represented in a recommendation list. | 1–6 | Depends on a declared path taxonomy and denominator. |
| ablation | alpha-sweep ablation; main six-model ablation | The separate PGPR/UCPR frozen-item-set, baseline-preserving control experiment. | 1; 3; 5–6 | Not the Chapter 4 six-model main result and not a strict-accuracy source. |
| boundary case | failed experiment; incomplete model | A supported test of where the current evaluation contract admits or blocks evidence. | 1; 3; 5–6 | Amazon-Book KGAT is the partial boundary case. BLOCKED is not poor performance. |
| validation-first framework | validated framework; validation pipeline alone | A framework in which evidence eligibility is checked before comparative reporting. | 1; 3; 5–6 | PASS establishes contract conformity, not universal correctness. |
| accuracy–explainability trade-off | accuracy/explanation tradeoff; explainability gain | The metric-specific relationship between a ranking measure and a declared explanation property under controlled evidence. | 1–6 | Use an en dash and hyphenate `trade-off`; do not imply a universal inverse relationship. |
| explanation property | explanation quality score; explainability | A specifically defined computational property such as LIR, SEP, or ETD. | 1–6 | Prefer this term when user-facing quality has not been measured. |
| evidence stream | result source; evidence type used interchangeably | A provenance class such as strict accuracy, alpha-sweep, ablation, validation, or boundary evidence. | 1; 3–6 | The streams support different claims and must not be merged. |
| reportable row | completed model; successful model | A model-dataset output that satisfies the registered export and validation contract. | 1; 3–6 | Reportability is not a claim of superior accuracy. |

Capitalisation is fixed as `LastFM`, `ML-1M`, `Amazon-Book KGAT`, `PGPR`, `UCPR`, `CAFE`, `TPRec`, `KGGLM`, and `PEARLM`. Use `alpha=0` and `alpha=1` for endpoint labels and `alpha sweep` only when the phrase is not used attributively.
