# DOCX Build Status

## 1. Overall Status

The NTU-template DOCX draft was generated, post-processed, rendered, and copied to the Windows folder. Three self-check iterations were completed. Serious table-layout defects remain.

## 2. Files Created in Project

- `paper/docx_build/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`
- `paper/docx_build/DOCX_BUILD_REPORT.md`
- `paper/docx_build/DOCX_SELF_CHECK_REPORT.md`
- `paper/docx_build/DOCX_BUILD_STATUS.md`
- `paper/docx_build/intermediate/DISSERTATION_FOR_DOCX.md`
- `paper/docx_build/intermediate/DISSERTATION_PANDOC_RAW.docx`
- `paper/docx_build/rendered_pages/` with 84 final-check PNG pages
- `paper/docx_build/reports/TEMPLATE_INSPECTION_REPORT.md`

## 3. Files Copied to Windows Folder

- `/mnt/d/Desktop/paper/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`
- `/mnt/d/Desktop/paper/DOCX_BUILD_REPORT.md`
- `/mnt/d/Desktop/paper/DOCX_SELF_CHECK_REPORT.md`
- `/mnt/d/Desktop/paper/DOCX_BUILD_STATUS.md`

The three report copies are completed during final delivery after this status file is generated.

## 4. DOCX Output

Project output:

`paper/docx_build/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`

Windows output:

`/mnt/d/Desktop/paper/DISSERTATION_NTU_TEMPLATE_DRAFT.docx`

SHA-256:

`694cded5e78c5254af2e06b0709a79405afe836822901dffc876ec77514eaad8`

## 5. Self-check Result

**FAIL**

Structural checks pass, but final render checks fail for wide-table wrapping and the near-blank page 13.

## 6. Iterations Performed

Three iterations were performed, which is the maximum allowed by this Goal.

## 7. Remaining Manual Steps

- Run a dedicated DOCX table-layout repair pass.
- Remove the near-blank page caused by a horizontal rule/page-break interaction.
- Fill approved personal, programme, date, and declaration metadata.
- Update TOC, List of Figures, and List of Tables fields in Microsoft Word.
- Confirm final NTU page size and margins.
- Verify PEARLM final venue and DOI metadata.

## 8. Readiness

**Requires DOCX layout fixes**

## 9. Recommended Next Step

Run a DOCX layout fix pass before manual inspection.

Do not generate the final submission PDF until the repaired DOCX has passed a new Microsoft Word layout check.
