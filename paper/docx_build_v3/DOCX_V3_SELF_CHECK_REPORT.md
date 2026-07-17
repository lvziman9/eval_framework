# DOCX V3 Self-check Report

| Iteration | Render result | Issues found | Fixes applied | Outcome |
|---|---|---|---|---|
| Iteration 1 | 72 pages; blank=0; edge_touch=0; author_year=0; broken_formula=0; table_margin_risk=0 | Static TOC/LOF/LOT page-number map had not yet been applied. Long decimals detected only in References pages. | Built `PAGINATION_MAP.json` from iteration-1 render text and regenerated the DOCX. | Proceeded to later correction renders. |
| Iteration 4 | 73 pages; blank=0; edge_touch=0; author_year=0; broken_formula=0; table_margin_risk=0 | No layout overflow, missing image, author-year citation, broken formula, short duplicate figure title, or repository-path exposure detected. Long decimals remained References-only. | Table captions were kept below tables, image alt text was suppressed as a visible caption source, and path-heavy prose was converted to log/file-name level wording. | PASS. |

## Structural checks

| Check | Result | Notes |
|---|---|---|
| DOCX zip integrity | PASS | `DISSERTATION_NTU_TEMPLATE_DRAFT_V3.docx` opens as a valid DOCX package. |
| Template mother document | PASS | `template_used_as_mother_document=true`. |
| Sections | PASS | 3 sections; 0 landscape sections. |
| Chapters | PASS | 6 Chapter 1-6 headings. |
| TOC/LOF/LOT page numbers | PASS | 49 TOC entries and 28 list entries complete. |

## Table checks

| Check | Result | Notes |
|---|---|---|
| Native Word tables | PASS | 17 tables in DOCX. |
| Table image conversion | PASS | No table image conversion was used. |
| Widths | PASS | All table widths are <= 8640 twips. |
| Caption position | PASS | 17 table captions below tables; 0 same-table captions above tables. |
| Header repeat | PASS | 17 repeated header rows. |
| Render margin risk | PASS | 0 table margin-risk pages. |

## Citation checks

| Check | Result | Notes |
|---|---|---|
| Numbered citations | PASS | Numbered citation patterns found in text/render. |
| Author-year patterns | PASS | 0 remaining in final render. |
| References | PASS | 29 entries, numbered [1]-[29]. |

## Formula checks

| Check | Result | Notes |
|---|---|---|
| Display formulas | PASS | 31 / 31 display formulas converted to OMML. |
| Inline formulas | PASS | 57 inline OMML equations. |
| Broken formula markers | PASS | 0 in DOCX audit and 0 render pages. |

## Numeric precision checks

| Check | Result | Notes |
|---|---|---|
| Intermediate long decimals | PASS | 0 remaining. |
| Final render long decimals | PASS | Pages [68, 69] are References-only. |
| Presentation-only policy | PASS | Source Markdown and evidence files unchanged. |

## Cohesion/coherence checks

| Check | Result | Notes |
|---|---|---|
| Prose edits | PASS | 22 targeted changes. |
| Boundary preservation | PASS | SEP, sweep, Amazon boundary, missing statistical/user-study artifacts, and causal limits retained. |

## Figure checks

| Check | Result | Notes |
|---|---|---|
| Body figures | PASS | 11 body figures. |
| Figure captions | PASS | 11 captions. |
| Image render | PASS | 0 missing-image markers. |
| Duplicate short figure titles | PASS | 0 short alt-title remnants. |

## Remaining manual checks

- Fill NTU front-matter placeholders.
- Open the DOCX in Microsoft Word and confirm/update fields if the institution requires dynamic fields.
- Do not treat the temporary internal render PDF under `/tmp` as a deliverable.
