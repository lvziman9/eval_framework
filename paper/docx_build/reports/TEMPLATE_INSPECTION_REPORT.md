# Template Inspection Report

## 1. Template Identification

The requested Windows filename `NTU_template.docx` was not present. The user confirmed continuation with the only dissertation-template candidate:

`/mnt/d/Desktop/paper/Template_MSc-Diss_v2.docx`

The document contains Nanyang Technological University dissertation cover material, declaration sections, front-matter examples, and dissertation chapter examples.

## 2. Project Copy

The template was copied without modifying the Windows source:

`paper/templates/NTU_template.docx`

Both files have SHA-256:

`cd82dc0a40d8a8a6e3b093b144c8f3573578c83ed3f2990913a94d8ca2cdaff4`

## 3. Package and Open Check

- DOCX ZIP/OOXML package: readable.
- `word/document.xml`: present.
- `word/styles.xml`: present.
- Non-empty template paragraphs inspected: 191.
- Opened successfully through `python-docx`.

## 4. Style Check

| Required style | Result | Notes |
| --- | --- | --- |
| Normal | PASS | Present. |
| Heading 1 | PASS | Present. |
| Heading 2 | PASS | Present. |
| Heading 3 | PASS | Present. |
| Heading 4-9 | PASS | Present. |
| Title | PASS | Present. |
| Caption | MISSING | Added to the generated DOCX during post-processing. |

## 5. Placeholder Check

No `[[TITLE]]`, `[[ABSTRACT]]`, `[[DISSERTATION_BODY]]`, or `[[REFERENCES]]` tokens were found. The template instead contains visible examples and placeholders such as:

- `DISSERTATION TITLE`
- `AUTHOR'S NAME`
- `202X`
- `[Input Date Here]`
- `[Input Name Here & Sign above]`
- `[Input Supervisor Name Here & Sign above]`

The template body also contains declaration instructions and example authorship-attribution text. These body paragraphs were not copied into the dissertation. Pandoc used the document only as a reference DOCX for styles, page properties, and related formatting.

## 6. Reference-DOCX Suitability

The template is suitable as a Pandoc reference DOCX with post-processing. `python-docx` and targeted OOXML operations were required for Caption style creation, heading correction, image limits, table controls, and Word field insertion.

## 7. Manual Template Checks Required

- Confirm the final programme, school, degree, author, supervisor, submission date, and declaration wording.
- Confirm whether the template-defined Letter page size is acceptable for the final NTU submission.
- Update all Word fields before final PDF export.

## 8. Inspection Result

**PASS_WITH_NOTES**
