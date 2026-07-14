# Markdown Formatting Risk Audit

The audit inspected the raw V5 full draft. It found 39 headings, balanced display-math delimiters (`31` opening and `31` closing), no fenced code blocks, and no exact long-paragraph duplicates. The findings below concern later cleanup and conversion; no source Markdown was changed.

| Formatting issue | Location | Risk | Fix priority | Recommended cleanup action |
| --- | --- | --- | --- | --- |
| Compressed headings | Full draft | None detected | Low | Preserve the current one-heading-per-line structure and blank lines around headings. |
| Pipe-table structure | Five multi-row table blocks in the full draft | Current blocks are structurally consistent | Low | Validate column counts again after the missing chapter tables are integrated. |
| Formula lines beginning with a vertical bar | Strict Precision/Recall and ETD display formulas | Markdown parsers may misread absolute-value lines as table syntax | Medium | During cleanup, use unambiguous LaTeX absolute-value delimiters while preserving the formulas. |
| Broken LaTeX display blocks | Chapter 3 | None detected; delimiters are balanced | Low | Run Pandoc/Word conversion smoke checks after cleanup because balanced delimiters do not guarantee target-renderer compatibility. |
| Repeated paragraphs | Chapters 3–5 | No exact long duplicates; conceptual caveats recur | Medium | Replace only redundant repetitions with stable cross-references; do not remove evidential boundaries. |
| Missing title and abstract | Start of full draft | Supervisor-facing package is incomplete | High | Add verified title and abstract in a later targeted revision, then audit them against the thesis statement and conclusions. |
| Figure placeholders and insertion | Chapters 3–5 | Figures are referenced but not embedded | High | Insert authoritative assets and frozen captions after source-of-truth consolidation; do not regenerate existing result figures in cleanup. |
| Table integration | Chapters 3–5 | Most numbered research tables live in separate files rather than the full draft | High | Integrate authoritative table versions as true multi-line pipe tables without changing values or evidence paths. |
| Chapter numbering | Chapters 1–6 | Consistent | Low | Preserve numbering; validate table and figure sequences after insertion. |
| Figure numbering and source-plan conflict | Figure 4.5 | Old plan says optional; V5 says main text | High | Make the V5 decision authoritative and update or retire stale integration sources. |
| Cross-references | Figure and table mentions throughout Chapters 3–5 | Plain-text references have no stable anchors | Medium | Use one consistent cross-reference convention suitable for later Word conversion. |
| Internal workflow labels | Multiple "Batch 1C" and "Batch 1" references | Reduces supervisor-facing readability | High | Replace with final figure, appendix, or provenance references without deleting caveats. |
| Internal evidence-package wording | Chapters 3–6 | Reads as production status rather than dissertation prose | Medium | Convert to neutral provenance or limitation wording while preserving factual status. |
| References placeholder | End of draft | No rendered bibliography | High | Replace with a deduplicated bibliography generated from verified/caveated BibTeX sources. |
| Appendix placeholder | End of draft | No selected appendix material | High | Select traceability, extended tables, optional figures, and configuration/provenance material through an explicit appendix plan. |
| Wide tables and long evidence paths | Tables 3.6, 4.1–4.3, and 5.1–5.4 | Likely poor Word/PDF pagination and wrapping | Medium | Shorten display labels, move full paths to notes or an evidence appendix, and test landscape/split layouts without altering paths in the source register. |
| Chapter 3 length and formula density | Chapter 3 | May impede supervisor scanning and Word pagination | Medium | Use concise transitions, stable equation numbering, and appendix placement for verification detail; avoid substantive method rewriting. |
| Caption placement | Separate table/figure source files | Captions are not yet consistently integrated as standalone paragraphs | Medium | Place each caption as a separate paragraph adjacent to its asset and preserve evidence-stream labels. |
| Word/PDF conversion readiness | Full draft | Not tested in this audit and explicitly outside scope | Medium | After Batch 2C, run non-destructive conversion checks for equations, tables, captions, page breaks, and cross-references. |

The source is structurally cleaner than the missing-package elements suggest. The dominant cleanup risks are integration, source conflicts, long tables, and conversion behaviour, not compressed headings or globally broken Markdown.
