# DOCX Build Report

## 1. Inputs

| Input | Path | SHA-256 |
| --- | --- | --- |
| Current dissertation Markdown | `paper/current_dissertation/FULL_DISSERTATION_CURRENT.md` | `90e782afa0d7d400bd45c7b80cda6fbe5a0ac67e1dfd79ccdf1b514df1dadb7c` |
| Current bibliography | `paper/current_dissertation/references/REFERENCES_CURRENT.bib` | `3c05b30da758ea8f60ceef4f68c9f73753818f90057d3955ec113fd6a02baf82` |
| NTU template candidate | `/mnt/d/Desktop/paper/Template_MSc-Diss_v2.docx` | `cd82dc0a40d8a8a6e3b093b144c8f3573578c83ed3f2990913a94d8ca2cdaff4` |

## 2. Windows Template Source

The requested `NTU_template.docx` filename was absent. The user confirmed continuation with `/mnt/d/Desktop/paper/Template_MSc-Diss_v2.docx`, which was inspected as the NTU MSc dissertation template candidate. The Windows source was not overwritten.

## 3. Project Template Copy

The exact template copy is stored at `paper/templates/NTU_template.docx`. Its SHA-256 matches the Windows source.

## 4. Conversion Method

Pandoc 3.10 generated `paper/docx_build/intermediate/DISSERTATION_PANDOC_RAW.docx` using the project template, the current bibliography, citeproc, and the 11 validated PNG figure paths.

The Markdown reader disabled implicit figures because the dissertation already contains explicit figure-caption paragraphs. Citeproc completed successfully. Automatic bibliography insertion was suppressed to avoid duplicating the existing verified 29-entry display list; in-text citations were formatted while the manually audited References section and caveats were retained.

## 5. Post-processing Applied

`python-docx` 1.2.0 and targeted OOXML operations were used to:

- Apply Title and Heading 1/2 hierarchy.
- Preserve Chapter 1-6, References, and Appendices.
- Add and apply Caption style to 11 figure and 16 table captions.
- Limit all 11 inline figures to the template text width.
- Set table grid widths, wrapping, header repetition, and compact table fonts.
- Insert updateable Table of Contents, List of Figures, and List of Tables fields.
- Register existing captions through hidden Word TC fields.
- Preserve author, supervisor, date, declaration, and acknowledgement placeholders.

No experimental value, claim, figure content, source citation key, or caveat was changed.

## 6. Figures Included

All 11 PNG figures referenced by the current dissertation are embedded. The final DOCX contains 11 inline body images and 11 Figure captions. SVG files remain recorded as vector sources but were not used as DOCX display assets.

## 7. Tables Included

All 16 Markdown tables are present as editable Word tables with 16 Table captions. Structural preservation passed, but the final render still shows severe narrow-column wrapping in several wide tables.

## 8. Citation / Reference Handling

- Pandoc citeproc: successful.
- Citation fallback: not used.
- Source citation-key set: preserved in `DISSERTATION_FOR_DOCX.md`.
- DOCX in-text citations: converted to formatted author-year citations.
- References heading: present.
- Verified display-list entries: 29.
- PEARLM final venue and publisher DOI: still requires manual verification.

## 9. TOC / Fields Handling

Three Word fields were inserted for the Table of Contents, List of Figures, and List of Tables. Placeholder field results remain visible until fields are updated in Microsoft Word. No page number was fabricated.

Open the DOCX in Microsoft Word and update all fields before final PDF export.

## 10. Windows Output Copy

The DOCX was copied successfully to:

`/mnt/d/Desktop/paper/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`

The project and Windows copies share SHA-256:

`694cded5e78c5254af2e06b0709a79405afe836822901dffc876ec77514eaad8`

## 11. Output Files

- `paper/docx_build/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`
- `paper/docx_build/DOCX_BUILD_REPORT.md`
- `paper/docx_build/DOCX_SELF_CHECK_REPORT.md`
- `paper/docx_build/DOCX_BUILD_STATUS.md`
- `paper/docx_build/rendered_pages/` containing 84 final-check PNG pages
- `paper/docx_build/reports/TEMPLATE_INSPECTION_REPORT.md`

No QA PDF, final PDF, or LaTeX output was created. Temporary internal render PDFs were deleted after PNG generation.

## 12. Known Limitations

- Wide tables still produce one-word-per-line columns in the LibreOffice render and require a dedicated Word layout pass.
- Rendered page 13 is near blank except for a horizontal rule.
- TOC, List of Figures, and List of Tables fields must be updated in Microsoft Word.
- Author, supervisor, date, official declaration wording, acknowledgements, programme metadata, and final school metadata remain placeholders or require confirmation.
- The template carries a Letter page-size definition; final NTU page-size compliance needs manual confirmation.
- Microsoft Word may reflow tables differently from LibreOffice, so Windows inspection remains mandatory.
