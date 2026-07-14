# Citation and Provenance Closure Report

## 1. Overall Status

The citation audit is substantially closed at draft level. Primary sources and publication metadata were verified for PGPR, UCPR, CAFE, TPRec, KGGLM, KGAT, KGIN, LightGCN, XRecSys/LIR/SEP/ETD, the explainable-recommendation survey, and the knowledge-graph recommender survey. The original `wang2018pgpr` seed was found to be a KPRN citation and is unsafe under a PGPR label.

Two bibliography items remain partial: PEARLM and the "Measuring Why" survey have verified arXiv records but no verified final publisher DOI in this audit. Strict-accuracy provenance remains incomplete at the primary-artifact layer because all 12 expected LastFM/ML-1M row-level JSON files are absent. Their values remain traceable at draft level to two accessible, exactly matching summary tables.

## 2. Academic Skills Usage Summary

| Skill | Used? | Contribution | Limitation |
| :--- | :--- | :--- | :--- |
| `research-writing-skill` | yes | Checked claim-to-source fit, supplied cautious wording, and preserved external/internal evidence separation. | It cannot resolve missing artifacts or publisher records without evidence. |
| `scientific-toolkit-skill` | yes | Guided primary-source searching, multi-source metadata verification, BibTeX normalization, and reproducibility audit. | Search access varied by publisher; unresolved metadata remains flagged. |
| `office-academic-skill` | loaded only | Confirmed that final office packaging belongs to a later Goal. | No office artifact was requested or generated. |

## 3. External Citation Verification Summary

| Target | Status | Safe to cite? | Required action |
| :--- | :--- | :--- | :--- |
| PGPR | verified | yes, as `xian2019pgpr` | Replace the incorrect seed label in the final bibliography. |
| Seed `wang2018pgpr` | do not cite as PGPR | no | Use `wang2019kprn` only for KPRN. |
| UCPR | verified | yes | Use external paper for model context and internal evidence for repository behavior. |
| CAFE | verified | yes | No citation-provenance action remains. |
| TPRec | verified | yes | No citation-provenance action remains. |
| KGGLM | verified | yes | Use external paper for mechanism context only. |
| PEARLM | partially verified | yes, as arXiv only | Manually verify final venue/DOI before final submission. |
| KGAT | verified | yes | Keep outside native-path explanation evidence. |
| KGIN | verified | yes | Use as background/accuracy-reference context only. |
| LightGCN | verified | yes | Use as background/accuracy-reference context only. |
| XRecSys/LIR/SEP/ETD | verified | yes | Cite SIGIR 2022 for conceptual origin and the internal guide/code for exact implementation. |
| Explainable recommendation survey | verified | yes | Use the 2020 journal record. |
| Measuring "Why" survey | partially verified | yes, as arXiv only | Verify any final venue/DOI before replacing the arXiv entry. |
| Knowledge graph recommender survey | verified | yes | Use the 2022 IEEE TKDE record. |

## 4. Strict Accuracy Provenance Summary

| Issue | Status | Final decision | Required action |
| :--- | :--- | :--- | :--- |
| Twelve expected primary JSON files | `0/12` accessible | Do not claim primary JSON verification. | Recover/archive before final submission if primary provenance is required. |
| Canonical status matrix | accessible | Current machine-readable strict-accuracy source. | Preserve and hash in the final evidence package. |
| Dissertation summary table | accessible | Current human-readable presentation source. | Retain with canonical-matrix citation. |
| Cross-source value comparison | passed | All 12 LastFM/ML-1M rows match field by field across the two accessible tables. | Record the comparison command in final reproducibility notes. |
| Export validation evidence | accessible | Supports validation/coverage claims, not metric values. | Do not use it as a substitute metric source. |
| Statistical significance | not available | Accuracy comparisons remain descriptive. | Add analysis only in a separately approved future task. |

## 5. Metrics Citation Summary

| Metric / concept | External source status | Internal source status | Recommended thesis wording |
| :--- | :--- | :--- | :--- |
| LIR | verified through Balloccu et al., SIGIR 2022 | Defined for this evaluation in `docs/guides/PATH_METRICS_GUIDE.md` and implemented in `xrecsys/metrics.py` | "The dissertation follows the framework's internal LIR implementation and cites the SIGIR 2022 paper for conceptual origin." |
| SEP | verified through the same source | Internal guide and code accessible | Use the same external-origin/internal-implementation separation. |
| ETD | verified through the same source | Internal guide and code accessible | Use the same external-origin/internal-implementation separation. |
| Native-path explanation boundary | Supported by repository architecture and model papers | Internal architecture and validation documents accessible | "External papers describe model mechanisms; repository evidence determines eligibility and evaluated behavior." |
| Strict accuracy | No external citation is required for repository result values | Two matching summaries accessible; primary JSONs absent | "Values are traceable to the canonical status matrix and matching dissertation summary table." |

## 6. Remaining Risks

| Risk | Severity | Affected chapters | Mitigation |
| :--- | :--- | :--- | :--- |
| Twelve strict-accuracy primary JSON artifacts are absent | critical | Ch.4; Ch.6 synthesis | Recover and archive them, or retain explicit summary-level provenance and avoid direct-inspection claims. |
| PEARLM final venue/DOI is unverified | medium | Ch.3; Ch.5 | Cite arXiv:2310.16452 and manually verify proceedings metadata before submission. |
| "Measuring Why" final venue/DOI is unverified | low | Ch.1-3 | Retain the verified arXiv citation. |
| The old PGPR seed can silently produce a wrong citation | high | Ch.1; Ch.3; Ch.5 | Remove the mislabelled key from the final bibliography and use the corrected PGPR/KPRN entries. |
| External model papers may be mistaken for experiment evidence | high | Ch.3-6 | Preserve the external-context/internal-experiment distinction in prose and traceability. |
| No statistical-significance or user-study artifact exists | high | Ch.4-6 | Keep result comparisons descriptive and human-centred benefits prospective. |

## 7. Recommendation Before Chapter 1-2 Integration

Readiness classification: **Ready for Chapter 1-2 integration with citation caveats**.

Chapter 1-2 drafting may use the verified bibliography and explicit arXiv-only flags. It must not use the old `wang2018pgpr` seed as PGPR, must keep external literature separate from repository result evidence, and must preserve the strict-accuracy primary-artifact caveat. Final bibliography freezing and final dissertation submission are not ready until the critical provenance task is resolved or formally accepted as a documented limitation.
