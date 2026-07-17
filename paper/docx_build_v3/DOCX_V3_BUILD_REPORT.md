# DOCX V3 Build Report

## 1. Inputs

| Input | Path | SHA-256 / Status |
|---|---|---|
| Source Markdown | `paper/current_dissertation/FULL_DISSERTATION_CURRENT.md` | `90e782afa0d7d400bd45c7b80cda6fbe5a0ac67e1dfd79ccdf1b514df1dadb7c` |
| References BibTeX | `paper/current_dissertation/references/REFERENCES_CURRENT.bib` | `3c05b30da758ea8f60ceef4f68c9f73753818f90057d3955ec113fd6a02baf82` |
| IEEE CSL | `paper/styles/ieee.csl` | `b4c7619fc16c45a31e4cc3271eab94ffe83192d3b4c7fc729470a3b459448de3` |
| NTU template copy | `paper/templates/NTU_template.docx` | `cd82dc0a40d8a8a6e3b093b144c8f3573578c83ed3f2990913a94d8ca2cdaff4` |

## 2. Template Use

The V3 DOCX was assembled with the NTU template copy as the mother document. The template sample body was removed before assembly, while the template logo, front-matter wording, page geometry, and section structure were retained.

| Check | Result |
|---|---|
| Template used as mother document | PASS |
| Template sample body removed | PASS |
| Original source Markdown unchanged | PASS |
| Original bibliography unchanged | PASS |
| Original template copy unchanged | PASS |

## 3. Major Fixes

| Area | V3 result |
|---|---|
| Tables | 17 native Word tables; no table images; all table widths <= 8640 twips. |
| Citations | IEEE numbered citations generated with citeproc; 29 numbered references. |
| Formulas | 31 display formulas converted to Word OMML. |
| Numeric precision | 240 presentation-layer numeric changes; long decimals remaining in V3 intermediate main text: 0. |
| Cohesion/coherence | 22 targeted prose revisions with claim boundaries preserved. |
| TOC/LOF/LOT | 49 TOC entries and 28 list entries include static page numbers. |

## 4. Tables

All main-text tables remain editable Word-native tables. Table 5.3 was split into Table 5.3a and Table 5.3b. Header rows repeat, vertical borders are removed, and the final render audit found no table margin-risk pages.

## 5. Citations

IEEE numbered citations were produced by Pandoc citeproc using the official IEEE CSL file. Author-year citation patterns remaining: 0. References are numbered contiguously from [1] to [29].

## 6. Formulas

Pandoc emitted Word OMML equations for all registered display formulas. Broken formula marker pages in the final render: 0.

## 7. Numeric Precision

Main-text values are rounded for readability only. Full precision remains available in the registered evidence files and build reports. Long decimal pages in the final render are [68, 69], and the final audit classifies them as References-only.

## 8. Cohesion and Coherence

The V3 source applies limited prose polish to reduce repeated caution wording while preserving SEP, strict-accuracy versus sweep, Amazon-Book KGAT, statistical-significance, user-study, and causal-claim boundaries.

## 9. Figures and Captions

The document contains 11 body figures and 11 figure captions. Source figure hashes remain embedded unchanged. Figure captions are below figures and table captions are below tables.

## 10. Known Limitations

- Candidate name, supervisor, date, submission year, acknowledgements, and AI/authorship declaration placeholders still require manual completion.
- Final inspection should be performed in Microsoft Word before submission, especially field updates and institutional front-matter choices.
- No final PDF or LaTeX output was generated in this V3 goal.
