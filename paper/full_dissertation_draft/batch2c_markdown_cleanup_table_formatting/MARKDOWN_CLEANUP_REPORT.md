# Markdown Cleanup Report

## 1. Purpose

This report records the diagnosis and cleanup applied to the Batch 2B V6 dissertation Markdown before supervisor-package assembly. The work addresses Markdown structure, table boundaries, display-math safety, placeholders, captions, and two specified consistency issues. It does not expand the empirical content or perform final document formatting.

## 2. Input Version

The sole body source was:

`paper/full_dissertation_draft/batch2b_critical_claim_evidence_fixes/FULL_DISSERTATION_DRAFT_BATCH2B_V6.md`

The six matching Batch 2B chapter files were used to produce the six clean V7 chapter copies. Batch 2A audits and the frozen SEP table, caption, and Figure 4.5 placement decisions were used only to control formatting and evidence-role wording.

## 3. Cleanup Rules Applied

- Preserve Chapter 1–6 order, heading hierarchy, research-objective count, citations, formulas, experimental values, evidence paths, and caveats.
- Keep each heading, paragraph, display-math block, table, placeholder, and caption on an unambiguous Markdown boundary.
- Use multi-line pipe tables with blank lines before and after each table.
- Use equivalent `\lvert` and `\rvert` LaTeX delimiters where raw vertical bars could be mistaken for Markdown table syntax.
- Use standalone italic placeholders and standalone bold figure or table captions; do not insert image links or rendered assets.
- Keep strict accuracy, alpha-sweep, ablation, and boundary evidence labels explicit.
- Limit content-level editing to the required Chapter 4.5 repetition compression and Chapter 6 O8 consolidation.

## 4. Formatting Issues Found

| Issue type | Location | Risk | Action |
| --- | --- | --- | --- |
| Compressed headings | Chapters 1–6 | None detected in V6 | Preserved one heading per line with blank-line separation. |
| Compressed pipe tables | Existing V6 chapter tables | None detected | Revalidated every table as a multi-line block with consistent column counts. |
| Broken table spacing | Existing V6 chapter tables | Low | Preserved or added blank lines around table captions and table blocks. |
| Raw vertical bars in display formulas | Chapter 3 strict metrics and explanation aggregation | Medium | Replaced absolute-value bars with equivalent `\lvert` and `\rvert` delimiters. |
| Repeated blank lines | Chapters 1–6 | None detected | Preserved a single blank line between adjacent Markdown blocks. |
| Implicit figure locations without standalone placeholders or captions | Chapters 3–5 | Medium | Added text-only placeholders and frozen evidence-bounded captions for Figures 3.1–5.2. |
| Referenced but non-integrated tables | Chapters 4–5 | Medium | Added consistent text-only placeholders and standalone captions; data-table insertion remains deferred. |
| Broken list formatting | Chapters 1 and 3 | None detected | Preserved valid ordered and unordered list structure. |
| Paragraph concatenation | Chapters 1–6 | None detected | No paragraph was split solely by line length; Chapter 4.5 was compressed only for specified conceptual repetition. |
| References and Appendix placeholders | Full draft trailer | Low | Retained both as separate level-one headings with standalone placeholder paragraphs. |
| Chapter numbering | Chapters 1–6 | None detected | Preserved the complete and ordered Chapter 1–6 sequence. |
| Cross-reference and caption form | Chapters 3–5 | Medium | Standardised numbered figure placeholders and captions; marked final numbering and insertion as deferred. |
| Duplicate objective identifier | Chapter 6 objective-closure table | Medium | Consolidated mechanism, ablation, and boundary analysis into one O8 row without adding O9. |

## 5. Content Boundaries

No experiment was run and no dataset, export, report, checkpoint, source figure, or Batch 2B file was modified. No experimental value, citation key, evidence path, chapter boundary, or research-objective count was changed. The strict-primary JSON, PEARLM metadata, statistical-significance, user-study, Amazon partial-boundary, repository-metric, mechanism, and reproducibility caveats remain in the revised body.

## 6. Files Cleaned

1. `CHAPTER1_INTRODUCTION_BATCH2C_CLEAN_V7.md`
2. `CHAPTER2_LITERATURE_REVIEW_BATCH2C_CLEAN_V7.md`
3. `CHAPTER3_FRAMEWORK_IMPLEMENTATION_BATCH2C_CLEAN_V7.md`
4. `CHAPTER4_TRADEOFF_RESULTS_BATCH2C_CLEAN_V7.md`
5. `CHAPTER5_ANALYSIS_BOUNDARY_LIMITATIONS_BATCH2C_CLEAN_V7.md`
6. `CHAPTER6_CONCLUSION_RECOMMENDATIONS_BATCH2C_CLEAN_V7.md`
7. `FULL_DISSERTATION_DRAFT_BATCH2C_CLEAN_V7.md`

## 7. Remaining Formatting Risks

- Authoritative result tables referenced by placeholders still require controlled insertion during supervisor-package assembly.
- Figure assets are not inserted; final panel composition, numbering, cross-references, and caption typography remain deferred.
- Wide tables and long evidence descriptions require Word-layout testing after package assembly.
- The title, abstract, final bibliography, selected appendix content, and final NTU formatting remain outside Batch 2C.
- Final Word/PDF conversion behaviour has not been tested because document generation is explicitly outside this batch.
