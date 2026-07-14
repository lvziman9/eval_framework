# Literature Review Status

## 1. Overall Status

The Chapter 2 literature-review evidence base and English draft are complete at draft level. All eight required artifacts have been generated under `paper/literature/review_outputs/`. The work used the read-only PDF corpus, the verified citation register, the Chapter 3--6 story-revised drafts, and the thesis traceability log. No source PDF, Chapter 3--6 draft, dataset, checkpoint, model output, export, experiment, or report was modified.

## 2. PDF Corpus Coverage

- Source directory: `/mnt/d/Desktop/survey/`
- PDFs discovered: 30
- Manifest records: 30
- Corpus index records: 30
- Evidence-matrix records: 30
- Local text extraction: 30 of 30 succeeded with Poppler `pdftotext` 24.02.0
- OCR operations: 0
- Source PDF modifications: 0

Each PDF has a stable corpus identifier, absolute source path, file size, modified time, SHA256 value, extraction status, and literature-index record. First-page titles, authors, abstracts, and embedded publication identifiers were checked locally; authoritative records were used to confirm or complete bibliographic metadata.

## 3. Verified Citations

- Corpus identities verified: 30 of 30
- Existing verified BibTeX entries reused without duplication: 5
- New BibTeX entries generated: 25
- New entries duplicated against the existing verified register: 0
- Chapter 2 citation keys unresolved against the combined registers: 0

The 30 papers are classified as 11 core, 8 secondary, 7 background, and 4 out of scope. Verification means that the cited title, authors, year, and publication identity were matched to local PDF text and an authoritative bibliographic source where required. It does not convert arXiv-only records into final-venue citations.

## 4. Citations Requiring Manual Check

No corpus paper used in the Chapter 2 draft requires a manual identity check. ArXiv-only additions are recorded as arXiv works, and no final venue is asserted for `song2019ekar`, `nori2019interpretml`, `kokhlikyan2020captum`, `yuan2020gnnExplainability`, `chen2021drlRecSurvey`, `wei2022chainOfThought`, `kojima2022zeroShotReasoning`, `plaat2024multistepReasoning`, `peng2025llmAgentsRec`, `lopezAvila2025llmMultimodalRec`, or `raja2025llmRecChallenges`.

The Chapter 2 draft reuses the existing `balloccu2023pearlm` record. Its arXiv identity is verified, but its final venue and publisher DOI remain unverified in the existing citation register and still require manual verification before final submission. The existing `chen2022measuringWhy` caveat is unchanged; that citation is not used in this Chapter 2 draft.

## 5. Out-of-Scope Papers

The following four corpus papers have verified metadata but are excluded from direct Chapter 2 claim support:

- `huang2023llmReasoningSurvey`: general LLM reasoning survey
- `wei2022chainOfThought`: general chain-of-thought prompting
- `kojima2022zeroShotReasoning`: general zero-shot reasoning
- `plaat2024multistepReasoning`: general multi-step LLM reasoning survey

They do not directly establish KG recommender comparability, native recommendation-path faithfulness, or path-quality evaluation. Their presence in the corpus is retained for traceability rather than used to broaden the dissertation claim boundary.

## 6. Chapter 2 Draft Readiness

**Draft generated and ready for narrative integration**

The draft follows the required six-section structure and synthesises literature by thesis function rather than by paper. Each section opens with a thematic claim, develops a cross-paper synthesis, and states the relationship to the dissertation. The draft positions the contribution as canonical native-path evaluation and controlled trade-off analysis, not as a new recommender model. It does not introduce repository experiment values or claim universal or state-of-the-art performance.

## 7. Remaining Risks

- The research-gap statement is explicitly bounded to the 30-paper corpus and must not be rewritten as an exhaustive absence claim.
- Exact LIR, SEP, and ETD formulas are repository-specific even though their conceptual dimensions are related to XRecSys; final text must preserve both external and implementation provenance.
- Automated path metrics do not establish user-perceived usefulness, clarity, trust, or causal faithfulness; no user-study claim should be inferred.
- Recent arXiv records may later receive revised versions or final venues. Their current BibTeX entries intentionally assert only verified arXiv metadata.
- PEARLM final-venue metadata remains a pre-submission manual check in the existing citation register.

## 8. Recommended Next Goal

The recommended next goal is **Chapter 1--2 and Chapter 3--6 full dissertation integration**. That goal should reconcile terminology, citation style, narrative transitions, and contribution wording across the complete dissertation while preserving the existing evidence boundaries. It has not been started as part of this literature-review goal.
