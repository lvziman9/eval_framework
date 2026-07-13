# BibTeX Verification Notes

## 1. Academic Skills Used

| Skill | Used? | Purpose |
| :--- | :--- | :--- |
| `research-writing-skill` | yes | Checked whether each citation supports the proposed thesis use and supplied cautious wording for unresolved metadata. |
| `scientific-toolkit-skill` | yes | Cross-checked titles, authors, years, venues, DOI records, arXiv identifiers, and source URLs. |
| `office-academic-skill` | no artifact generation | Read for later dissertation packaging constraints only. |

## 2. Verified Entries

| Citation key | Source | Verification evidence | Notes |
| :--- | :--- | :--- | :--- |
| `xian2019pgpr` | SIGIR 2019 / arXiv:1906.05237 | DOI 10.1145/3331184.3331203; DBLP and arXiv metadata agree | Correct primary PGPR entry. |
| `wang2019kprn` | AAAI 2019 / arXiv:1811.04540 | DOI 10.1609/aaai.v33i01.33015329; AAAI and arXiv metadata agree | Corrected replacement for the seed key `wang2018pgpr`; this paper is KPRN, not PGPR. |
| `xian2020cafe` | CIKM 2020 / arXiv:2010.15620 | DOI 10.1145/3340531.3412038 is linked by arXiv and publisher metadata | Verified. |
| `tai2021ucpr` | SIGIR 2021 | DOI 10.1145/3404835.3462847; proceedings metadata and author order verified | Resolves the prior UCPR citation gap. |
| `zhao2022tprec` | ACM TOIS / arXiv:2108.02634 | DOI 10.1145/3531267 is linked as the related journal DOI on arXiv | Minimal verified journal fields are used; uncertain issue/article fields were omitted. |
| `balloccu2024kgglm` | RecSys 2024 | DOI 10.1145/3640457.3691703 and complete citation are supplied by the official repository | Resolves the prior KGGLM citation gap. |
| `wang2019kgat` | KDD 2019 / arXiv:1905.07854 | DOI 10.1145/3292500.3330989 and proceedings metadata verified | Verified. |
| `wang2021kgin` | The Web Conference 2021 / arXiv:2102.07057 | DOI 10.1145/3442381.3450133 and DBLP record verified | Verified. |
| `he2020lightgcn` | SIGIR 2020 / arXiv:2002.02126 | DOI 10.1145/3397271.3401063 and DBLP record verified | Verified. |
| `balloccu2022xrecsys` | SIGIR 2022 / arXiv:2204.11241 | DOI 10.1145/3477495.3532041; ACM, DBLP, arXiv, and local XRecSys README agree | Primary conceptual source for LIR, SEP, and ETD; exact evaluated implementation remains internally defined. |
| `zhang2020explainableSurvey` | Foundations and Trends in Information Retrieval / arXiv:1804.11192 | DOI 10.1561/1500000066 and publisher metadata verified | Journal year is 2020, replacing the seed's preprint year. |
| `guo2022kgsurvey` | IEEE TKDE / arXiv:2003.00911 | DOI 10.1109/TKDE.2020.3028705 and final volume/page metadata verified | Final publication year is 2022; DOI registration and arXiv preprint date are earlier. |

## 3. Entries Requiring Manual Check

| Citation key | Problem | Required action |
| :--- | :--- | :--- |
| `balloccu2023pearlm` | The arXiv title, authors, year, and identifier are verified, but a stable final publisher DOI was not found. A retrieved conference-formatted manuscript still contained DOI placeholders. | Cite arXiv:2310.16452 for drafting; manually check the final RecSys proceedings record before final submission. |
| `chen2022measuringWhy` | The arXiv record is verified, but DBLP still classifies it as a CoRR item and no final publisher DOI was found. | Retain the arXiv entry or replace it only after a publisher record is verified. |

## 4. Entries Not Safe to Cite Yet

| Citation target | Reason | Recommendation |
| :--- | :--- | :--- |
| `wang2018pgpr` as PGPR | arXiv:1811.04540 and DOI 10.1609/aaai.v33i01.33015329 identify the KPRN paper, not the PGPR paper. | Do not use the seed key for PGPR. Use `xian2019pgpr`; use `wang2019kprn` only if KPRN is discussed. |
| PEARLM final-venue claim | A final publisher DOI and stable proceedings metadata were not verified. | Avoid naming a final venue unless manually checked; the arXiv citation is safe for the model description. |
| Measuring "Why" final-venue claim | Only the arXiv publication is verified. | Avoid a journal or conference claim until a primary publisher record is found. |

## 5. Seed Preservation

`BIBTEX_SEED.bib` was not modified. The corrected and expanded bibliography is stored separately in `BIBTEX_VERIFIED_OR_REQUIRES_CHECK.bib`, and unresolved entries retain explicit warning notes.
