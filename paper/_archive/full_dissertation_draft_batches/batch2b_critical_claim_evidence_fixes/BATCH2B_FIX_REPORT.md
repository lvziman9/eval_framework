# Batch 2B Fix Report

## 1. Purpose

This batch fixes the high-risk claim wording and source-of-truth conflicts identified by the Batch 2A audit. It creates a V6 dissertation copy for later Markdown cleanup without rewriting the argument, changing experimental values, generating figures, or performing formatting work.

## 2. Inputs Used

The authoritative body input was `FULL_DISSERTATION_DRAFT_SEP_TREND_V5.md`, with its dedicated V5 Chapter 3–5 files and matching stable Chapter 1, 2, and 6 files. The audit used the Batch 2A reports, SEP freeze report, formula/evidence inventory, strict-accuracy provenance closure, citation closure, thesis traceability log, final accuracy/explanation summaries, validation status, and figure/diagram plans.

The authoritative table and caption decisions came from:

- `REVISED_TABLES_AND_CAPTIONS_SEP_TREND.md`;
- `FIGURE_PLACEMENT_DECISION_SEP_TREND.md`.

## 3. SEP Wording Fixes

| Chapter | Issue found | Fix applied | Risk after fix |
| --- | --- | --- | --- |
| Chapter 1 | Introductory terminology implied popularity or serendipity semantics. | Defined SEP as the repository-specific bridge-entity score and operational explanation-side metric. | Low; conceptual and implementation provenance remain separated. |
| Chapter 2 | Literature synthesis transferred rarity/serendipity semantics to the implementation. | Kept XRecSys as conceptual inspiration and bounded the implemented SEP construct. | Low; no semantic guarantee or user-perception validation is claimed. |
| Chapter 6 | Conclusion used "degree-derived serendipity." | Replaced it with the implemented repository-specific score and retained strong operational trend language. | Low; trend remains clear without an explanation-quality claim. |

## 4. Source-of-Truth Fixes

Figure 4.5 is frozen as a Chapter 4.5 main-text SEP–NDCG alpha-sweep figure. V5 SEP tables, captions, and placement decisions supersede older optional-placement and stronger-semantic wording for final integration. The strict-accuracy source remains the canonical status matrix plus the matching dissertation summary, with the twelve inaccessible primary JSON artifacts explicitly disclosed.

## 5. Internal Label Removal

Thirteen internal production-label occurrences were removed from Chapters 3–5. They were replaced with neutral references to the dataflow, appendix trace, flowcharts, schematics, or evidence provenance record. No technical evidence role was removed.

## 6. Chapter 6 Objective Closure

Section 6.1 now includes a concise table mapping the registered objectives to how they were addressed, the main evidence chapter, and the applicable boundary. The table closes O1–O8 and cross-objective limitations without adding a result or changing the objective count.

## 7. Caveats Preserved

- Strict accuracy: the twelve primary row-level JSON artifacts are not accessible; two matching summaries provide current draft-level provenance.
- PEARLM: the arXiv identity is verified, while final venue and publisher DOI require manual checking.
- Statistical inference: no statistical-significance artifact is registered.
- Human evidence: no user-study artifact is registered.
- Amazon-Book KGAT: partial boundary case only, with no approved explanation sweeps.
- Metrics: exact LIR, SEP, and ETD implementation and data assumptions remain repository-specific.
- Mechanism: non-PGPR/UCPR interpretations remain descriptive rather than causal.
- Reproducibility: exact checkpoints, hashes, seeds, and several model-native settings remain incomplete in the current evidence package.

## 8. Files Created

Thirteen Markdown files were created in `paper/full_dissertation_draft/batch2b_critical_claim_evidence_fixes/`: six revised chapters, one assembled full draft, four focused decision/fix logs, this fix report, and the status report. No file outside the directory was modified.

## 9. Remaining Issues Not Fixed in This Batch

- General Markdown cleanup, table integration, caption formatting, and cross-reference normalisation remain for Batch 2C.
- Title page, abstract, final references, and selected appendix content were intentionally not generated.
- Figure insertion and rendering were intentionally deferred; Figure 4.5 placement is recorded but no image was inserted.
- The twelve strict primary JSON files remain unavailable.
- PEARLM final venue/DOI, exact checkpoint identities, hashes, seeds, and several model-native settings remain manual-verification items.
- Existing historical plans remain in the repository and must not override the frozen V5 source-of-truth decisions during later integration.
