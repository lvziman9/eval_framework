# Citation and Provenance Audit

The audit separates publication provenance from repository result provenance. External papers support model and metric context; they do not verify the dissertation's experimental values.

| Citation / source | Location | Status | Risk | Required action |
| --- | --- | --- | --- | --- |
| PGPR, `xian2019pgpr` | Chapters 1–3 and mechanism context | Verified primary publication metadata | Low | Use this key for PGPR throughout the final bibliography. |
| KPRN, `wang2019kprn` | Chapter 2 path-reasoning context | Verified and distinct from PGPR | Low | Keep KPRN separate; never reuse the old mislabelled `wang2018pgpr` seed as PGPR. |
| UCPR, `tai2021ucpr` | Chapter 2 and Chapter 5 context | Verified primary source | Low | Use the paper for model context and internal artifacts for repository behaviour and ablation values. |
| KGGLM, `balloccu2024kgglm` | Chapter 2 and Chapter 5 context | Verified primary publication | Low | Use for mechanism context only; do not treat publication claims as experimental provenance. |
| XRecSys, `balloccu2022xrecsys` | Chapters 1–6 | Verified conceptual source for the LIR/SEP/ETD family | Low | Cite XRecSys for conceptual origin and internal guide/code for exact formulas, assumptions, and implementation. |
| XRecSys framework, `balloccu2022xrecsysFramework` | Chapter 2 | Verified and distinct from the SIGIR study | Low | Preserve the software-framework versus conceptual-study distinction. |
| PEARLM, `balloccu2023pearlm` | Chapters 2, 3, 5, and 6 | Partially verified: arXiv identity verified; final venue and publisher DOI unverified | Medium | Cite as arXiv only until final publication metadata is manually verified. |
| CAFE and TPRec primary sources | Chapters 1–3 and 5 | Verified | Low | Keep model context external and result evidence internal. |
| Strict-accuracy row-level JSON | Chapters 1, 3, 4, 5, and 6 | Incomplete: `0/12` expected LastFM/ML-1M primary files accessible | High | Do not state that primary JSON was inspected. Recover and archive the files or retain the explicit summary-level limitation. |
| Canonical strict status matrix | Chapter 4 strict results | Accessible summary source | Medium | Treat as the current canonical summary, not a substitute for row-level lineage. Preserve its audit hash in provenance records. |
| Final accuracy summary table | Chapter 4 strict results | Accessible and exactly matches the canonical status matrix | Medium | Use as presentation-level support with the primary-artifact caveat. |
| Sweep CSVs and ablation artifacts | Chapters 4–5 | Registered internal evidence | Low | Keep sweep and ablation provenance separate from strict accuracy and from external publications. |
| Chapter 2 local PDF corpus and citation matrix | Chapter 2 | Thirty-paper corpus audited; used identities verified or explicitly arXiv-only | Low | Preserve arXiv-only status for recent or non-final works and do not infer future venue metadata. |
| Dissertation citation keys | Full draft | Twenty-nine used lower-case Pandoc keys found; all occur across the two registered BibTeX sources | Low | Merge into one final, deduplicated bibliography and validate key resolution after integration. |
| Final BibTeX bibliography | References | Not yet generated; two source BibTeX files remain | Medium | Create one authoritative bibliography in a later approved batch; normalise formatting without upgrading unverified metadata. |
| References placeholder | End of full draft | Placeholder only | High | Replace with the generated verified bibliography before supervisor-package creation. |
| "Measuring Why" survey | Citation register; not used in current full draft | ArXiv identity verified; final venue/DOI unverified | Low | Retain the caveat if introduced later; do not add it merely to complete metadata. |
| Unsupported external-source claims | Chapter 2 gap statement | Bounded to the reviewed corpus | Low | Keep the bounded-corpus wording and avoid "first," "only," or exhaustive absence claims. |

Citation provenance is substantially closed at draft level, but bibliography integration and strict-primary artifact closure are not. The final references must not silently convert arXiv records into venue publications or conflate external model papers with internal result evidence.
