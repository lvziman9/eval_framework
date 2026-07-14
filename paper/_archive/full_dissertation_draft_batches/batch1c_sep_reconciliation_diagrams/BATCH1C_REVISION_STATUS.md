# Batch 1C Revision Status

## 1. Overall Status

**Readiness:** Batch 1C generated but SEP still requires manual verification.

Batch 1C is complete at the specification and Markdown-draft level. It reconciles the accessible SEP guide/code chain to safe dissertation wording, adds ten diagram specifications, integrates their references into Chapter 3-5 copies, and assembles a new full-draft copy. It does not run experiments, change experimental values, render figures, or alter Batch 1B outputs.

## 2. Files Created

1. `SEP_RECONCILIATION_REPORT.md`
2. `SEP_FINAL_WORDING_DECISION.md`
3. `FORMULA_INVENTORY_AND_EVIDENCE_MAP_BATCH1C.md`
4. `DIAGRAM_SPECIFICATIONS.md`
5. `CHAPTER3_DATAFLOW_AND_VALIDATION_DIAGRAMS.md`
6. `CHAPTER4_TRADEOFF_PATTERN_DIAGRAMS.md`
7. `CHAPTER5_ABLATION_AND_BOUNDARY_DIAGRAMS.md`
8. `SINGLE_EXAMPLE_TRACE.md`
9. `DIAGRAM_RENDERING_PLAN.md`
10. `CHAPTER3_FRAMEWORK_IMPLEMENTATION_BATCH1C_V4.md`
11. `CHAPTER4_TRADEOFF_RESULTS_BATCH1C_V4.md`
12. `CHAPTER5_ANALYSIS_BOUNDARY_LIMITATIONS_BATCH1C_V4.md`
13. `FULL_DISSERTATION_DRAFT_BATCH1C_V4.md`
14. `TABLE_FIGURE_EVIDENCE_REFRESH_PLAN_BATCH1C.md`
15. `REVISED_TABLES_AND_CAPTIONS_BATCH1C.md`
16. `BATCH1C_REVISION_STATUS.md`

All files are under `paper/full_dissertation_draft/batch1c_sep_reconciliation_diagrams/`.

## 3. SEP Reconciliation Result

**Decision:** guide wording appears stale.

The accessible generator sorts bridge entities by ascending degree, assigns increasing ordinal EMA weights, and stores those increasing weights in that order. Runtime metrics and the main and ablation optimisers use the stored SEP value directly and favour larger values. The guide's lower-degree / higher-weight wording therefore does not describe the accessible generator direction.

The historical `sep_matrix.pkl` caches used for the registered sweep outputs are not accessible. The artifact-level direction is consequently not closed. The allowed dissertation wording is:

> SEP is a repository-specific degree-derived bridge-entity score.

The chapters and refreshed captions do not interpret higher SEP as lower degree, rarity, novelty, usefulness, or user-perceived explanation quality.

## 4. Chapter 3 Diagram Additions

- Framework overview and dataflow: Mermaid and DOT specifications; main-text placement in Section 3.1.
- Single-example user-item-path trace: schematic tables plus Mermaid and DOT; main-text placement in Section 3.3.
- Validation gate flowchart: Mermaid and DOT specifications; main-text placement in Section 3.4.
- LIR / SEP / ETD metric-anchor schematic: Mermaid and DOT specifications; main-text or appendix placement in Section 3.4.
- Evidence-stream separation: Mermaid and DOT specifications; main-text placement in Section 3.6.

These diagrams describe evaluation, artifact alignment, metric anchors, and evidence roles. They do not define a recommender architecture or add results.

## 5. Chapter 4 Diagram Additions

- Alpha-sweep process: Mermaid and DOT specifications; main-text placement in Section 4.1.
- Empirical trade-off pattern schematic: Markdown matrix, Mermaid, and DOT; main-text placement in Section 4.7 or retention as a table.

The alpha-sweep caption explicitly separates paired sweep NDCG from strict NDCG@10. The pattern schematic adds no metric, threshold, significance claim, or causal interpretation.

## 6. Chapter 5 Diagram Additions

- PGPR/UCPR ablation evidence flow: Mermaid and DOT specifications; main-text placement in Section 5.1.
- 95% NDCG-retention operating point: Mermaid and DOT specifications; main-text or appendix placement in Section 5.1.
- Amazon boundary decision flow: Mermaid and DOT specifications; main-text or appendix placement in Section 5.4.

The ablation diagrams remain limited to the registered frozen-item-set PGPR/UCPR protocol. The Amazon flow preserves its partial boundary status and does not rank PASS against BLOCKED / N/A rows.

## 7. Single-Example Trace Status

No safe validated `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` example set was found in the accessible worktree. The trace therefore uses only `u*`, `i*`, `seed_item*`, `bridge_entity*`, `recommended_item*`, and `relation*` placeholders.

The file states: “This is an illustrative schematic example, not an experimental result.” It assigns no real identifier, path, score, metric value, validation status, checkpoint, seed, or hyperparameter.

## 8. Diagram Rendering Plan

Ten Mermaid specifications and ten Graphviz DOT specifications are present. DOT/SVG is the preferred final source for most process diagrams; the single-example trace and trade-off matrix may remain tables. Rendering is explicitly deferred until wording and placement are frozen.

No PNG, SVG, PDF, DOCX, or LaTeX artifact was generated. The current environment has neither the `dot` executable nor the `pydot` package, so DOT blocks received textual structural review but not parser-based validation. No dependency was installed.

## 9. Updated Chapter 3-5 Status

- Chapter 3: framework dataflow, schematic trace, validation flow, metric-anchor, and evidence-stream references integrated; SEP wording downgraded to the approved degree-derived description.
- Chapter 4: alpha-sweep and trade-off-pattern references integrated; all Batch 1 / Batch 1B numerical findings retained; SEP semantic interpretation downgraded.
- Chapter 5: ablation, retention, and Amazon decision-flow references integrated; mechanism claims remain bounded and Amazon evidence status is unchanged.
- Full draft: Chapter 1-6 are present in order, followed by one References placeholder and one Appendix placeholder. Chapter 1, Chapter 2, and Chapter 6 use the unchanged stable source files.

Verification confirmed that the experimental decimal-token multisets in the revised Chapter 3-5 copies match their Batch 1B baselines. The formula inventory retains all 26 entries, and all detected Markdown pipe tables have consistent column structure.

## 10. Evidence and Caveats Preserved

- Strict accuracy primary JSON artifacts: `0/12` accessible.
- Current strict accuracy provenance: `reports/tables/canonical_native_path_status_matrix.csv` plus the matching final accuracy summary.
- PEARLM final venue and publisher DOI require manual verification.
- No statistical-significance artifact is registered.
- No user-study artifact is registered.
- Amazon-Book KGAT remains a partial boundary case.
- LIR, SEP, and ETD definitions and data assumptions remain repository-specific.
- Non-PGPR/UCPR mechanism explanations remain descriptive rather than causal.
- Exact checkpoint paths and hashes, seeds, and several model-native hyperparameters require manual verification.
- Strict accuracy, explanation endpoints, alpha sweeps, ablation, and boundary-validation evidence remain separate.

## 11. Remaining Risks

1. SEP is reconciled at current-code level but not at historical matrix-cache level; the original `sep_matrix.pkl` files and their provenance remain unavailable.
2. Exact checkpoint paths and hashes are incomplete.
3. Random seeds are not fully frozen.
4. Some model-native hyperparameters require manual verification.
5. The 12 expected strict primary JSON artifacts are unavailable.
6. PEARLM final venue and publisher DOI are pending.
7. Final BibTeX formatting is pending.
8. Final Markdown, Word, and NTU formatting is pending.
9. Figure rendering and insertion are pending because all new diagrams remain Mermaid, DOT, table, or caption specifications only.

## 12. Recommended Next Batch

**SEP manual verification and wording freeze.**

Recover and hash the historical SEP matrix and matching knowledge-graph cache before freezing SEP interpretation. After that decision, perform the separately authorised Markdown cleanup and supervisor-review preparation. Do not begin rendering or final Word/PDF/NTU packaging until wording and figure placement are approved.
