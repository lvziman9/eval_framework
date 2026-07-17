# DOCX V2 Build Report

## Root Cause of the Failed Draft

The previous draft used the NTU DOCX only as Pandoc's `--reference-doc`. That operation copied selected styles but did not preserve or correctly reconstruct the template's cover, forms, front matter, page-number sections, or body layout. The old output collapsed the template's 35 sample sections into one section, left the contents pages as placeholders, and retained a self-check status of `FAIL` while still being copied to the delivery folder.

## V2 Assembly Method

The V2 build uses the original NTU template as the authoritative source for:

- the NTU logo asset;
- cover and title-page hierarchy;
- Statement of Originality wording;
- Supervisor Declaration structure;
- Authorship Attribution structure;
- Letter page size and binding-side margin convention;
- front-matter and dissertation-body organisation.

The original template package contains malformed sample section geometry that also renders incorrectly outside Microsoft Word. V2 therefore uses a sanitised DOCX container while reproducing the template's required assets, forms, layout hierarchy, and page parameters. The template source itself was not modified.

## Content Conversion

- Pandoc 3.10 and citeproc converted the dissertation body.
- All 29 cited sources were rendered as author-year in-text citations.
- The References section contains 29 formatted bibliography entries rather than BibTeX keys used as display labels.
- All 11 dissertation PNG figures were embedded unchanged.
- All 16 Markdown tables were rebuilt as editable Word tables because direct Pandoc table XML caused LibreOffice to discard landscape sections.
- Rebuilt table cell text matches the Pandoc source cell-for-cell, including all values and evidence paths.
- Fourteen wide tables use landscape sections; one long table spans two landscape pages.

## Formatting Applied

- Times New Roman 12 pt body text with 1.5 line spacing.
- Black Heading 1-3 hierarchy with chapter page breaks.
- Black 10.5 pt captions, with table captions above tables and figure captions below figures.
- Repeating grey table headers, restrained black/grey borders, fixed column widths, and compact table typography.
- Roman front-matter page numbering and Arabic body page numbering.
- Populated Table of Contents, List of Figures, and List of Tables with final-render page numbers.
- Hanging-indent 10 pt reference entries with DOI or URL hyperlinks where available.

## Content Integrity

The source Markdown, bibliography, and NTU template retain their original SHA-256 hashes. No experimental value, evidence path, chapter boundary, citation caveat, or result claim was changed. The missing-primary-artifact, significance, user-study, Amazon boundary, and PEARLM metadata caveats remain visible in the dissertation.

## Output

Primary DOCX:

`paper/docx_build_v2/DISSERTATION_NTU_TEMPLATE_DRAFT_V2.docx`

SHA-256:

`7ee8ebfeb715ce9c1d0625365918619b81ca6f6ffe4d644d38fc0ea4fb06214b`

The failed V1 draft was not overwritten.

## Remaining Author Actions

- Fill author, supervisor, submission date, programme, and approved school metadata.
- Select and complete the applicable AI-use declaration option.
- Complete the authorship attribution statement using verified publication details.
- Replace the acknowledgement placeholder.
- Recheck the static contents-page numbers after any substantive Word edits.
- Complete the existing PEARLM final venue and publisher DOI manual check before submission.

