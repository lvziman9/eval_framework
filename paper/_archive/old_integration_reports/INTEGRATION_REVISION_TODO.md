# Integration Revision TODO

## 1. Must Fix Before Final Submission

- [ ] Recover or formally archive the 12 expected LastFM/ML-1M strict-accuracy JSON artifacts. If recovery is impossible, obtain an explicit decision that the two matching summary sources and caveat are acceptable.
- [ ] Freeze an immutable evidence manifest containing hashes, sizes, timestamps, evaluator versions, export hashes, and the command that verified equality between the canonical status matrix and final accuracy summary.
- [ ] Refresh Table 3.6, Table 5.2, and Table 5.4 before insertion into the final thesis source. Their older standalone Markdown versions predate strict-provenance or citation closure.
- [ ] Preserve the separation of strict accuracy, six-model alpha sweeps, PGPR/UCPR ablation, validation, and Amazon boundary evidence after every formatting conversion.
- [ ] Confirm that Amazon-Book KGAT remains a partial boundary case and that no blocked row is assigned a score or rank.
- [ ] Run a final claim-to-evidence audit after all tables, figures, captions, and bibliography entries are inserted.

## 2. Should Fix Before Supervisor Review

- [ ] Conduct a focused internal review of Chapter 1 objectives and contributions against `RESEARCH_OBJECTIVES_AND_CONTRIBUTIONS_MAP.md`.
- [ ] Review Chapter 2 for chapter balance and remove any literature detail that does not advance the canonical-evaluation gap.
- [ ] Review Chapter 3–6 transitions using `CHAPTER_TRANSITION_MAP.md` and perform one final grammar/style pass without changing facts or evidence roles.
- [ ] Check total word count, chapter balance, paragraph density, and duplication between Chapters 1, 2, and 6.
- [ ] Decide the exact supervisor-review package: assembled Markdown only, chapter-separated files, evidence maps, or a later formatted DOCX package.
- [ ] Confirm with the supervisor whether summary-level strict-accuracy provenance is acceptable for review while primary JSON recovery remains open.

## 3. Citation and Bibliography Tasks

- [ ] Merge `BIBTEX_VERIFIED_OR_REQUIRES_CHECK.bib` and `CHAPTER2_BIBTEX_ADDITIONS.bib` into one final, deduplicated bibliography after citation usage is frozen.
- [ ] Apply final multiline BibTeX formatting and the NTU-required bibliography style.
- [ ] Manually verify PEARLM final venue and publisher DOI; retain the verified arXiv citation until resolved.
- [ ] Check final venues for any arXiv-only Chapter 2 sources before replacing their verified arXiv entries.
- [ ] Decide whether the “Measuring Why” survey is used or omitted. If used, retain its arXiv caveat unless final venue/DOI metadata is verified.
- [ ] Confirm that PGPR uses `xian2019pgpr`, KPRN uses `wang2019kprn`, and `wang2018pgpr` does not appear.
- [ ] Render all Pandoc-style citation keys and verify that no unresolved key remains.

## 4. Formatting and NTU Template Tasks

- [ ] Add NTU template front matter only in a later approved formatting goal.
- [ ] Draft and approve the abstract, acknowledgements, declaration pages, table of contents, lists of figures/tables, abbreviation list, and other required front matter later.
- [ ] Apply final heading numbering, margins, fonts, line spacing, page breaks, caption styles, cross-references, and bibliography formatting.
- [ ] Convert the approved Markdown source to Word or LaTeX only after evidence and citation freeze.
- [ ] Run final grammar, punctuation, spelling, and style checks on the formatted source.

## 5. Figure and Table Tasks

- [ ] Insert Tables 3.1–3.6, 4.1–4.2, and 5.1–5.4 in the approved main-text positions.
- [ ] Decide whether Table 3.7 and Table 4.3 remain in the main text, move to the appendix, or are omitted as integration records.
- [ ] Insert Figures 3.1–3.2, 4.1–4.4, and 5.1–5.2 with final captions and source/provenance checks.
- [ ] Assemble Figure 5.1 from the two existing SVG panels without altering plotted data.
- [ ] Decide whether optional Figures 4.5–4.6 belong in Chapter 4 or the appendix.
- [ ] Check final image resolution, panel labels, axis labels, metric notation, caption evidence roles, and accessibility in the target format.
- [ ] Verify that Chapter 6 introduces no new table or figure.

## 6. Appendix Tasks

- [ ] Select extended SEP/ETD trade-off figures, ablation details, validation matrices, and Amazon readiness records for the appendix.
- [ ] Decide whether the traceability log, evidence-source tables, and artifact hashes appear in the dissertation appendix or only in the reproducibility package.
- [ ] Include historical or superseded material only when needed for provenance and label it clearly as non-authoritative.
- [ ] Add recovered strict-accuracy primary artifact references to the appendix evidence index if recovery succeeds.

## 7. Optional Improvements

- [ ] Add a compact Chapter 2 literature-to-gap table only if it improves navigation without duplicating Section 2.6.
- [ ] Consider a separate post-hoc explanation baseline study as future work, not as a retrofit to the current native-path results.
- [ ] Consider a pre-registered statistical analysis and repeated-run protocol in a separately approved research task.
- [ ] Consider a user study for perceived usefulness, clarity, surprise, and trust while keeping those outcomes separate from LIR, SEP, and ETD.
- [ ] Revisit the dissertation title after the supervisor reviews the integrated argument.

## 8. Recommended Next Goal

Recommended next goal: **Internal dissertation review and supervisor-review package preparation**. It should resolve table/caption insertion, citation freeze, language consistency, word-count balance, and the review-package decision while preserving the current evidence boundaries. Final NTU Word/PDF formatting should remain a later goal.
