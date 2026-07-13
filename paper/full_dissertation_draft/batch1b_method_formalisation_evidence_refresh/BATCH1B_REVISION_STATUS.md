# Batch 1B Revision Status

## 1. Overall Status

**Readiness:** Batch 1B generated but requires formula/configuration verification

Batch 1B was generated from the Batch 1 Chapter 3-5 outputs. It adds evaluation-framework formalisation and refreshes evidence-role wording without changing the Batch 1 findings, experimental values, chapter boundaries, source chapters, datasets, checkpoints, outputs, reports, or figures.

The package is complete as a targeted revision output but is not yet ready to be treated as a frozen internal-review or submission package. Formula confidence and unresolved evidence boundaries remain explicit in the accompanying inventory and manifest.

## 2. Files Created

1. `CHAPTER3_FRAMEWORK_IMPLEMENTATION_BATCH1B_FORMALISED_V3.md`
2. `CHAPTER4_TRADEOFF_RESULTS_BATCH1B_FORMALISED_FINDINGS_V3.md`
3. `CHAPTER5_ANALYSIS_BOUNDARY_LIMITATIONS_BATCH1B_FORMALISED_V3.md`
4. `FULL_DISSERTATION_DRAFT_BATCH1B_V3.md`
5. `METHOD_FORMALISATION_NOTES.md`
6. `FORMULA_INVENTORY_AND_EVIDENCE_MAP.md`
7. `TABLE_FIGURE_EVIDENCE_REFRESH_PLAN.md`
8. `REVISED_TABLES_AND_CAPTIONS.md`
9. `STRICT_ACCURACY_EVIDENCE_MANIFEST_DRAFT.md`
10. `BATCH1B_REVISION_STATUS.md`

All files are under `paper/full_dissertation_draft/batch1b_method_formalisation_evidence_refresh/`.

## 3. Method Formalisation Added

The package now defines canonical datasets, users, items, graphs, model-dataset rows, identifier mappings, top-k lists, native paths, path validity, the three-file evidence package, validation eligibility, strict metrics, repository-specific LIR/SEP/ETD anchors and aggregation, abstract alpha-sweep output, endpoint deltas, ablation preservation and retention, constrained operating points, and evidence eligibility / boundary sets.

The formulas formalise the evaluation framework. They do not define a new recommender model or model-internal training objective.

No universal linear alpha-sweep formula was added. Code inspection verified linear candidate weighting for LIR and SEP, whereas ETD uses path-type bins and an unseen-type bonus; the shared sweep score remains abstract and implementation-specific.

SEP anchor extraction is verified, but its weight direction requires manual verification. The guide specifies lower-degree / higher-weight semantics, while the accessible matrix-generation code appears to assign increasing EMA weight after ascending degree sorting. Batch 1B records this discrepancy without altering existing SEP values or findings.

## 4. Chapter 3 Changes

Chapter 3 retains Sections 3.1-3.6 and all Batch 1 prose and values. Added material includes:

- a notation table and canonical identifier mappings;
- formal recommendation-list, native-path, validity, and export-package definitions;
- a binary validation gate and explicit reportability boundary;
- strict HR@K, Precision@K, Recall@K, DCG@K, and NDCG@K definitions;
- repository-specific LIR, SEP, ETD, and aggregation definitions;
- abstract alpha-sweep top-k notation and a five-row evidence-separation table.

The Batch 1 experiment-configuration table is retained. Missing checkpoint identities, seeds, and model-native settings are not reconstructed.

## 5. Chapter 4 Changes

Chapter 4 retains Sections 4.1-4.7, every Batch 1 finding, the empirical pattern summary, and all reported values. Added notation defines explanation-objective endpoint deltas and paired sweep-NDCG deltas, with light references in the LIR, SEP, and ETD sections.

The deltas are descriptive endpoint differences. No new result, efficiency ratio, significance test, causal explanation, or strict-accuracy substitution was introduced. A targeted SEP caveat records the unresolved guide/code direction without changing any endpoint or curve value.

## 6. Chapter 5 Changes

Chapter 5 retains Sections 5.1-5.5, the registered PGPR/UCPR ablation findings, the descriptive mechanism boundary, and the partial Amazon-Book KGAT case. Added formulas define alpha-zero baseline preservation, ablation NDCG retention, the existing 95% constrained operating point, and reportable / boundary evidence sets.

PGPR/UCPR remains the stronger registered ablation evidence. CAFE, TPRec, KGGLM, and PEARLM mechanism interpretations remain descriptive rather than causal.

## 7. Tables and Captions Refreshed

Standalone revisions were prepared for Table 3.6, Table 5.2, and Table 5.4. The revised wording records the accessible strict summaries and `0/12` primary-JSON caveat, updated UCPR/KGGLM/XRecSys citation status, PEARLM's unresolved final venue / DOI, incomplete configuration provenance, and all human-evaluation, significance, Amazon, metric-implementation, bibliography, and packaging limits.

Evidence-aware captions were prepared for Figures 3.1, 3.2, 4.1-4.6, 5.1, and 5.2. Existing assets were not regenerated or modified, and optional Figures 4.5 and 4.6 remain appendix candidates.

## 8. Strict Accuracy Manifest Status

The manifest records:

- `0/12` expected primary LastFM / ML-1M row-level strict accuracy JSON artifacts accessible;
- exact agreement between the canonical status matrix and final accuracy summary for the twelve main rows;
- SHA-256 `7df79e2ae51ea2eaba45e22b9dee45cd906bb324a8504b9e2f8fe21ce6af8bbe` for the canonical status matrix;
- SHA-256 `c6311d63589f9b5ad1ed01f12f112d8b76a6dcd497e1df1663628581390af2a2` for the final accuracy summary;
- wording allowed and not allowed at the current provenance level;
- required primary-artifact recovery actions before final submission.

No missing JSON artifact was generated or inferred.

## 9. Evidence and Caveats Preserved

Strict accuracy, alpha-sweep, ablation, and boundary evidence remain separate. Amazon-Book KGAT remains a partial boundary case. LIR, SEP, and ETD retain XRecSys as their verified conceptual source and the repository guide/code as the source of exact evaluated behaviour.

No statistical-significance artifact or user-study artifact is available. PEARLM final venue and publisher DOI require manual verification. Exact checkpoint paths and hashes, seeds, and several model-native hyperparameters remain unavailable or require manual verification. External papers continue to support context rather than repository experimental values. The SEP guide/code weight direction remains unresolved and must be reconciled before the rarity-oriented interpretation is frozen.

## 10. Remaining Risks

1. Checkpoint paths and hashes are incomplete.
2. Seeds are not fully frozen.
3. Some model-native hyperparameters require manual verification.
4. The twelve strict primary JSON artifacts are unavailable.
5. PEARLM final venue and publisher DOI are pending.
6. Final BibTeX formatting is pending.
7. Final Markdown, Word, and NTU formatting are pending.
8. Figure insertion is pending.
9. The intended SEP low-degree / high-weight interpretation must be reconciled with the accessible matrix-generation code.

## 11. Recommended Batch 2

SEP formula / implementation reconciliation, followed by Markdown formatting cleanup and supervisor-review preparation

This recommendation does not include automatic Word, PDF, LaTeX, supervisor-package, or final-submission generation.
