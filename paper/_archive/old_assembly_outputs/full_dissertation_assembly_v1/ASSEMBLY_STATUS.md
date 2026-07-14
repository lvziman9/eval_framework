# Full Dissertation Assembly Status

## 1. Outcome

The Batch 2C clean V7 dissertation has been assembled into one displayable Markdown draft with front matter, a 345-word abstract, Chapters 1–6, visible figures, numbered tables, retained citation keys, a display reference list, and an appendix plan. No experiment was run and no Batch 2C or evidence source was modified.

## 2. Required Checks

| Check | Result | Verification |
| --- | --- | --- |
| 1. Full assembled draft created | PASS | `FULL_DISSERTATION_ASSEMBLED_DRAFT_V1.md` exists and contains 1,242 physical lines. |
| 2. Front matter created | PASS | Title, degree, school, author/supervisor/date placeholders, declaration placeholder, acknowledgements placeholder, and list placeholders are present. |
| 3. Abstract created | PASS | 345 words under the assembly tokenizer; required framework and SEP boundary statements are present. |
| 4. Chapter 1–6 included in correct order | PASS | Six chapter headings occur once in numerical order. |
| 5. Figures included | PASS | 13 existing image links resolve and two registered Mermaid diagrams are embedded. |
| 6. Figure 4.5 in Chapter 4.5 main text | PASS | Both canonical SEP panels occur in Section 4.5 with the frozen evidence-safe caption. |
| 7. Tables visible as Markdown tables | PASS | 16 structurally valid multiline pipe-table blocks have 16 unique numbered captions. |
| 8. Citation keys scanned | PASS | 29 unique citation keys and 89 citation-key occurrences were found in Chapters 1–6; metric labels such as `HR@10` were excluded. |
| 9. BibTeX assembled | PASS | 39 entries, 39 unique keys, balanced braces, and no duplicate-key conflict. |
| 10. Display references list created | PASS | All 29 cited keys have display entries; no missing-key placeholder is required. |
| 11. Appendix plan created | PASS | Appendices A–F are planned without fabricated appendix data. |
| 12. No experiment value changed | PASS | Tables 4.1, 4.2, 5.1, and 5.3 match their registered source rows exactly; source hashes match 55/55. |
| 13. No forbidden SEP wording introduced | PASS | All six forbidden formulations are absent; SEP remains a repository-specific bridge-entity score. |
| 14. No unsupported SOTA claim introduced | PASS | State-of-the-art wording appears only in explicit non-claim boundaries and one cited publication title. |
| 15. No Word/PDF/LaTeX generated | PASS | The output directory contains only Markdown and BibTeX files. |
| 16. No V7 files overwritten | PASS | SHA-256 comparison matches all 55 registered V7, evidence, citation, table, and figure inputs. |

## 3. Additional Structural Checks

- All headings are on independent physical lines; no compressed heading line was detected.
- Formula delimiters are balanced: 31 display pairs and 57 inline pairs.
- No figure or table insertion placeholder remains in the assembled dissertation.
- Figure numbering is ordered as 3.1–3.3, 4.1–4.6, and 5.1–5.3.
- Table numbering is ordered as 1.1, 2.1, 3.1–3.6, 4.1–4.3, 5.1–5.4, and 6.1.
- The only remaining use of the word “placeholders” in the body describes the intentionally abstract single-example trace; it is not an unresolved assembly placeholder.

## 4. Retained Evidence Boundaries

- The twelve expected primary row-level strict-accuracy JSON artifacts remain inaccessible; draft-level values are supported by two exactly matching accessible summaries.
- No statistical-significance artifact or user-study artifact is registered.
- Paired alpha-sweep NDCG remains separate from strict NDCG@10.
- PGPR/UCPR ablation evidence remains separate from the six-model comparison.
- Amazon-Book KGAT remains a partial boundary case with three PASS and three BLOCKED / N/A rows and no approved explanation sweeps.
- PEARLM final venue and publisher DOI, exact checkpoints and hashes, random seeds, and several model-native settings remain manual-verification items.

## 5. Remaining Work Before PDF

Render Figures 3.3 and 5.3 from Mermaid to SVG or PNG, verify PEARLM publication metadata, apply the final NTU bibliography style, fill authorised front-matter fields, and complete Word/NTU-template layout checks. These are formatting and provenance-closure tasks; they do not authorise new experimental claims.

## 6. Readiness

**Ready for figure rendering before PDF formatting.**

Recommended next step: **Figure rendering and insertion before PDF preparation.**

