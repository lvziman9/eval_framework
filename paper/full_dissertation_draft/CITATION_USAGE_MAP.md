# Citation Usage Map

| Citation key | Used for | Chapters | Verification status | Caveat |
| --- | --- | --- | --- | --- |
| `afsar2022rlRecSurvey` | RL recommender objectives, environment, and evaluation heterogeneity | 2 | verified | External survey context only. |
| `balloccu2022xrecsys` | Conceptual origin of recency, shared-entity popularity/serendipity, explanation-type diversity, and explanation-oriented re-ranking | 1–3; 5 | verified | Exact LIR, SEP, and ETD implementation remains repository-specific. |
| `balloccu2022xrecsysFramework` | Reusable path-quality assessment and optimisation framework | 2 | verified | Does not independently standardise this dissertation's canonical export contract. |
| `balloccu2023pearlm` | PEARLM path-language-modelling context | 2–3; 5 | partially verified | ArXiv identity is verified; final venue and publisher DOI require manual checking. |
| `balloccu2024kgglm` | KGGLM mechanism context | 2–3; 5 | verified | External paper does not verify repository experimental values or cause observed curve shapes. |
| `chen2021drlRecSurvey` | DRL recommender evaluation challenges | 2 | verified as arXiv | No final venue asserted. |
| `ge2025trustworthyRecSurvey` | Multidimensional trustworthy recommendation and distinct evaluation properties | 2 | verified | Broad taxonomy, not a native-path metric contract. |
| `guo2022kgsurvey` | Knowledge graph recommender background and model-family taxonomy | 1–2 | verified | Background evidence only. |
| `kokhlikyan2020captum` | General post-hoc attribution context | 2 | verified as arXiv | Not recommendation-specific native-path evidence. |
| `lin2024rlRecSurvey` | RL recommender scope and evaluation challenges | 2 | verified | External survey context only. |
| `lin2025llmRecSurvey` | LLM roles and risks across recommender pipelines | 2 | verified | Generated rationales are not assumed to be native KG paths. |
| `lopezAvila2025llmMultimodalRec` | Multimodal LLM recommender background | 2 | verified as arXiv | Secondary background; no final venue asserted. |
| `lu2023vrkg4rec` | Representation-oriented KG recommendation example | 2 | verified | Does not establish a native-path explanation contract. |
| `markchom2026graphExplainableSurvey` | Graph-based explainable-recommender taxonomy and evaluation heterogeneity | 2 | verified | Synthesis source, not repository experiment evidence. |
| `nori2019interpretml` | General intrinsic/post-hoc interpretability distinction | 2 | verified as arXiv | General ML tooling, not KG recommender evidence. |
| `peng2025llmAgentsRec` | LLM-powered recommender-agent context | 2 | verified as arXiv | Recent arXiv source; no final venue asserted. |
| `raja2025llmRecChallenges` | LLM recommender trade-off context | 2 | verified as arXiv | Does not provide this dissertation's controlled native-path experiment. |
| `rossiiev2025rlRecSurvey` | RL recommender evaluation and explainability challenges | 2 | verified | Recent workshop survey; background only. |
| `shevchenko2024recsysBenchmarking` | Dataset-sensitive and multi-dataset recommender benchmarking | 1–2 | verified | Supports protocol discipline, not this repository's validation results. |
| `song2019ekar` | Sequential path discovery for explainable KG recommendation | 2 | verified as arXiv | No final venue asserted. |
| `tai2021ucpr` | UCPR user-centric path-reasoning context | 2–3; 5 | verified | Repository-specific ablation behaviour requires internal evidence. |
| `wang2018ripplenet` | KG preference propagation and representation-oriented recommendation | 2 | verified | Used as contrast with explicit native-path export. |
| `wang2019kprn` | KPRN path encoding and aggregation | 2 | verified | Use only for KPRN; never use the old `wang2018pgpr` label for PGPR. |
| `wang2021kgin` | Latent-intent and relational KG recommendation context | 2 | verified | Interpretation is model-specific and not a common native path. |
| `wang2022multilevelReasoning` | Multi-level ontology/instance path reasoning | 2 | verified | Method-specific graph and path extraction context. |
| `xian2019pgpr` | PGPR policy-guided path reasoning and model context | 1–3; 5 | verified | Correct PGPR key. External paper does not verify repository values. |
| `xian2020cafe` | CAFE coarse-to-fine neural-symbolic path reasoning | 1–3; 5 | verified | No CAFE-specific module ablation is registered in this dissertation. |
| `yuan2020gnnExplainability` | GNN explanation taxonomy, metrics, and benchmark context | 2 | verified as arXiv | Not recommender-specific. |
| `zhang2020explainableSurvey` | Explainable recommendation taxonomy, purposes, and intrinsic/post-hoc distinction | 1–2 | verified | General literature framing only. |
| `zhao2022tprec` | TPRec time-aware path-reasoning context | 2–3; 5 | verified | Amazon temporal boundary is established by repository evidence, not the paper. |
| `chen2022measuringWhy` | Not used in the integrated Chapter 1–6 draft | -- | partially verified | ArXiv identity is verified; decide whether to omit or use cautiously after final venue/DOI checking. |

## Citation Controls

- PGPR uses `xian2019pgpr`.
- KPRN uses `wang2019kprn` only where KPRN is explicitly discussed.
- `wang2018pgpr` is not an approved citation key and must not appear in the integrated draft.
- UCPR uses `tai2021ucpr`; KGGLM uses `balloccu2024kgglm`.
- XRecSys uses `balloccu2022xrecsys` for the conceptual origin of LIR, SEP, and ETD; internal documentation and code govern the exact evaluated formulas.
- PEARLM uses `balloccu2023pearlm` with its arXiv-only final-publication caveat.
- External literature is not used as evidence for repository strict accuracy, alpha-sweep, ablation, validation, or Amazon boundary values.
- No DOI, venue, arXiv identifier, author, year, or title was added outside the two verified BibTeX registers.
