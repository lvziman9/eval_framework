# Iterative Revision Plan

This plan sequences later work only. Batch 2A does not authorise or execute any listed revision.

## Batch 2B：Critical Claim and Evidence Fixes

| Task | Input | Output | Risk addressed | Do before supervisor? |
| --- | --- | --- | --- | --- |
| Correct frozen SEP terminology in Chapters 1, 2, and 6 | V5 full draft; SEP freeze report | Targeted V6 text with only approved semantic repairs | High-risk SEP overinterpretation | Yes |
| Make O1–O8 closure explicit in Chapter 6 | Chapter 1 objective map; Chapter 6 conclusion | Objective-closure paragraph or table | Incomplete visible alignment | Yes |
| Freeze authoritative table sources | Chapter 3–5 table files; V5 revised tables | Single integration manifest | Stale citation and SEP wording; duplicate sources | Yes |
| Freeze figure placement and captions | Old figure plans; V5 placement decision and captions | Authoritative figure manifest | Figure 4.5 placement conflict; caption overclaim | Yes |
| Neutralise internal batch and production labels | V5 Chapters 3–5 | Supervisor-facing references to figures, appendices, and provenance | Readability and package-status leakage | Yes |
| Preserve strict-primary provenance language | Strict provenance closure; Chapters 1, 3, 4, 5, and 6 | Consistent summary-level caveat | Missing `0/12` primary JSON | Yes |
| Confirm title, thesis statement, and abstract scope | Revised full draft and registered contributions | Draft title/abstract scope record | Package-level argument mismatch | Yes |

## Batch 2C：Markdown Cleanup and Table Formatting

| Task | Input | Output | Risk addressed | Do before supervisor? |
| --- | --- | --- | --- | --- |
| Integrate authoritative tables | Batch 2B table manifest and full draft | Multi-line pipe tables in chapter order | Missing tables and source conflict | Yes |
| Integrate captions and figure placeholders | Batch 2B figure manifest | Stable captions and insertion points | Inconsistent asset references | Yes |
| Normalise headings, paragraphs, and cross-references | Targeted-revised Markdown | Clean supervisor-facing Markdown | Conversion and navigation risk | Yes |
| Make display math conversion-safe | Chapter 3 formulas | Renderer-safe LaTeX with unchanged formulas | Leading-pipe and delimiter risk | Yes |
| Format long evidence paths and wide tables | Tables 3.6, 4.1–4.3, 5.1–5.4 | Readable main tables plus evidence notes/appendix references | Word pagination and wrapping | Yes |
| Generate verified reference section | Registered BibTeX sources | Deduplicated references with caveats preserved | References placeholder | Yes |
| Select appendix material | Audit recommendations and evidence registers | Structured Markdown appendix | Appendix placeholder | Yes |
| Run Markdown structural checks | Cleaned full draft | Heading, table, math, numbering, and reference check log | False cleanup claims | Yes |

## Batch 2D：Supervisor Review Package

| Task | Input | Output | Risk addressed | Do before supervisor? |
| --- | --- | --- | --- | --- |
| Assemble revised full draft | Batch 2C output | Supervisor-review Markdown draft | Fragmented source files | Yes |
| Prepare objective/contribution map | Alignment audit and revised Chapter 6 | One-page supervisor aid | Hidden closure logic | Yes |
| Prepare claim-evidence caveat sheet | Claim and provenance audits | Concise caveat register | Misreading evidence strength | Yes |
| Prepare table/figure source manifest | Frozen manifests | Supervisor-facing visual inventory | Unclear evidence provenance | Yes |
| List decision questions | Readiness assessment | Focused supervisor agenda | Unstructured feedback | Yes |
| Verify package contents only | Batch 2D files | Package status report | Missing or stale artifacts | Yes |

## Batch 2E：Figure Rendering and Insertion

| Task | Input | Output | Risk addressed | Do before supervisor? |
| --- | --- | --- | --- | --- |
| Consolidate Figure 3.1 and Figure 3.2 concepts | Existing assets and merged diagram decisions | Final framework/evidence visuals | Duplicate conceptual diagrams | No |
| Render selected validation diagram | Frozen D3.2 specification | Monochrome SVG | Validation gate readability | No |
| Retain table-form diagrams | D3.3 and D4.2 specifications | Formatted tables, not pseudo-plots | Figure density and implied quantitative coordinates | No |
| Render selected appendix diagrams | D3.4, D5.1, D5.2, D5.3 as approved | Monochrome SVG appendix assets | Protocol readability | No |
| Insert existing result figures | Authoritative figure manifest | Numbered figure placements with frozen captions | Missing visuals | No, unless required for the first supervisor package |
| Verify source and caption fidelity | Figure assets and manifests | Figure audit log | Evidence-stream or SEP overclaim | No |

## Batch 3：Word / PDF / NTU Formatting

| Task | Input | Output | Risk addressed | Do before supervisor? |
| --- | --- | --- | --- | --- |
| Apply NTU document structure and styles | Approved supervisor draft and template | Styled DOCX | Institutional formatting compliance | No |
| Convert equations, tables, captions, and references | Clean Markdown and final assets | Editable Word content | Conversion breakage | No |
| Resolve pagination and appendix layout | Styled DOCX | Stable page layout | Wide-table and figure overflow | No |
| Generate and inspect PDF | Final DOCX | Submission PDF | Rendering, font, and cross-reference defects | No |
| Run final claim/provenance regression audit | Word/PDF against approved Markdown | Final consistency report | Semantic drift during formatting | No |

The recommended next batch is Batch 2B. Batch 2C should begin only after claim wording and source-of-truth decisions are frozen.
