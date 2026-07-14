# Chapter-by-Chapter Audit

## Chapter 1 Introduction

### Role in dissertation

Chapter 1 defines the heterogeneous-comparison problem, states the validation-first response, lists objectives and contributions, fixes the no-new-model boundary, and previews the chapter sequence.

### Strengths

- The central comparability gap is stated early and connected to canonical identifiers, exports, validation, and evidence separation.
- O1–O8 are explicit and mapped to specifications and chapters.
- Contributions are bounded away from state-of-the-art and new-recommender claims.
- The organisation section accurately distinguishes results in Chapter 4 from interpretation in Chapter 5.

### Problems

- "Shared entity popularity or serendipity (SEP)" is broader than the frozen operational definition and may prime a user-perceived interpretation.
- Eight objectives and eight contributions produce some duplication and make the central contribution clusters less visible.
- The chapter contains no concise umbrella research question or equivalent thesis-question statement.
- The strict-primary JSON caveat is defensible but unusually implementation-facing for the contribution section.

### Required fixes

- Align the first SEP definition with the repository-specific bridge-entity score wording used in Chapters 3–5.
- Keep the eight registered items if required, but group their closure under framework feasibility, trade-off analysis, ablation/mechanism, and boundary/traceability.
- Confirm title, abstract, and thesis statement consistency after those package elements exist.

### Optional improvements

- Add one bounded umbrella research question before O1–O8.
- Move detailed artifact wording to a provenance note while retaining the caveat in concise form.
- Cleanup readiness: **not yet**; targeted terminology alignment should occur first.

## Chapter 2 Literature Review

### Role in dissertation

Chapter 2 synthesises knowledge graph recommendation, path reasoning, explanation types, multidimensional explanation properties, trade-offs, and benchmarking into the evaluative gap addressed by Chapter 3.

### Strengths

- The organisation is thematic and argumentative rather than a sequence of paper summaries.
- Native-path, latent, post-hoc, and generated explanation forms are distinguished.
- The gap is bounded to the reviewed corpus and leads directly to five framework requirements.
- PGPR and KPRN are treated as separate works, and the six target model families receive appropriate conceptual context.

### Problems

- Section 2.3 states that SEP concerns "rarity or serendipity associated with the bridge entity." This conflicts with the frozen weak-semantics position and is a high-risk overinterpretation.
- Recent survey sources rely on the literature-review provenance package and should remain auditable through the final bibliography.
- The bridge from the general trade-off literature to the repository-specific alpha protocol could be made more visibly conditional.

### Required fixes

- Replace the unsafe SEP sentence with the frozen operational definition and retain the distinction between conceptual source and repository implementation.
- Generate the final bibliography only from verified or explicitly caveated BibTeX records.

### Optional improvements

- Add one cross-reference from the trade-off synthesis to the registered evidence-stream separation in Chapter 3.
- Cleanup readiness: **not yet** because SEP semantics require correction first.

## Chapter 3 Framework Implementation and Verification

### Role in dissertation

Chapter 3 formalises the canonical evaluation architecture, model-specific views, export contract, validation gate, metrics, alpha sweeps, ablation separation, and provenance boundary.

### Strengths

- The methodology is formal enough to support replication at the framework-contract level.
- It explicitly denies proposing a new recommender model.
- Notation and formulas cover recommendation lists, paths, validation, strict metrics, LIR, SEP, ETD, endpoint deltas, and ablation retention.
- Strict accuracy, sweeps, ablation, and boundary evidence are separated in both prose and tables.
- Validation status is interpreted as reportability rather than model quality.

### Problems

- At roughly 400 lines, the chapter is disproportionately long and repeats evidence-boundary language.
- Multiple references to "Batch 1C" and the "current evidence package" are production notes rather than supervisor-facing prose.
- The binary validation gate and evidence sets do not explicitly map PASS, BLOCKED, PARTIAL, and N/A labels into the formal binary decision.
- Zero-denominator and empty-list behaviour is not stated beside all affected metric formulas.
- Diagram references are present without integrated figures.

### Required fixes

- Neutralise internal workflow labels and point to final figure, appendix, or provenance locations.
- Clarify status-to-gate mapping and formula edge conditions without changing the registered implementation.
- Remove only redundant boundary prose that can be replaced by stable cross-references.
- Integrate Figures 3.1 and 3.2 under an authoritative figure manifest.

### Optional improvements

- Move detailed configuration/provenance tables to the appendix if Chapter 3 remains too long after cleanup.
- Cleanup readiness: **after targeted fixes**.

## Chapter 4 Accuracy–Explainability Trade-off Results

### Role in dissertation

Chapter 4 reports the complete LastFM and ML-1M six-model results, then derives descriptive findings about strict rankings, explanation endpoints, objective-specific sweep profiles, and dataset dependence.

### Strengths

- It is results plus findings rather than a raw results dump.
- Strict HR@10, NDCG@10, Precision@10, and Recall@10 are kept separate from paired sweep ranking values.
- LIR, SEP, and ETD are treated as separate dimensions and not as an overall explanation score.
- The SEP section uses the frozen operational wording and explicitly excludes user-perceived serendipity and explanation-quality claims.
- Cross-dataset findings are descriptive and defer mechanism attribution to Chapter 5.

### Problems

- Referenced Tables 4.1 and 4.2 and Figures 4.1–4.6 are not integrated into the full Markdown draft.
- The earlier Chapter 4 figure plan marks Figure 4.5 as optional or appendix-level, conflicting with the V5 main-text placement decision.
- "Batch 1C" diagram references are not supervisor-facing.
- Strict ranking statements depend on summary-level provenance because row-level primary JSON is unavailable.

### Required fixes

- Integrate authoritative tables and captions without altering values.
- Make Figure 4.5 a main-text SEP figure and preserve Figure 4.6 as optional or appendix-level.
- Keep the primary-JSON and no-significance caveats attached to strict comparative findings.
- Replace internal batch references with final figure references.

### Optional improvements

- Reduce repeated warnings after one clear evidence-role paragraph and precise caption-level reminders.
- Cleanup readiness: **after table/figure source consolidation**.

## Chapter 5 Ablation, Mechanism Analysis, and Boundary Cases

### Role in dissertation

Chapter 5 interprets the Chapter 4 profiles through registered PGPR/UCPR ablation, bounded mechanism context, the Amazon-Book KGAT boundary, and explicit limitations.

### Strengths

- It does not repeat Chapter 4's result role; it asks what the registered evidence can support about control, mechanism, and scope.
- Ablation retention is confined to PGPR and UCPR and is not used as six-model superiority evidence.
- Non-PGPR/UCPR mechanism accounts remain descriptive or hypothetical rather than causal.
- Amazon-Book KGAT is consistently a partial boundary with three PASS and three BLOCKED/N/A rows.
- Missing significance and user-study evidence are clearly disclosed.

### Problems

- Some evidence-boundary prose repeats Chapter 3 and Chapter 4.
- The older `chapter5_tables.md` contains stale citation status and SEP wording that conflict with the V5 revised table source.
- Internal diagram-production labels remain in the prose.
- Figure and table integration is incomplete.

### Required fixes

- Use the V5 revised Tables 5.2 and 5.4 as the authoritative wording source and retire stale table variants from the integration path.
- Keep causal limits explicit while removing production labels.
- Integrate Tables 5.1–5.4 and Figures 5.1–5.2 with evidence-specific captions.

### Optional improvements

- Consolidate repeated evidence caveats into one limitations table plus cross-references.
- Cleanup readiness: **after authoritative table selection**.

## Chapter 6 Conclusion and Recommendations

### Role in dissertation

Chapter 6 consolidates the supported framework, measurement, and bounded-interpretation contributions and recommends work on evidence coverage, robustness, metrics, human evaluation, grounded generation, post-hoc baselines, citation closure, and reproducibility.

### Strengths

- It introduces no new empirical result and repeats the no-new-model boundary.
- Strict, sweep, ablation, and Amazon evidence remain separate.
- The recommendations directly follow the limitations established in Chapter 5.
- Primary-JSON, significance, human-evidence, citation, and reproducibility caveats remain visible.

### Problems

- "SEP uses degree-derived serendipity of the bridge entity" violates the frozen weak-semantics rule and is a high-risk wording defect.
- The conclusion groups contributions as first, second, and third but does not explicitly close O1–O8.
- Title/abstract consistency cannot be checked because those elements are absent from the full draft.
- The bibliography and appendix remain future placeholders.

### Required fixes

- Replace the unsafe SEP phrase with the frozen repository-specific, operational wording.
- Add an explicit O1–O8 closure map or concise closure paragraph without adding claims.
- Complete title, abstract, references, and appendix selection before supervisor-package generation.

### Optional improvements

- Tighten recommendation grouping after objective closure is made explicit.
- Cleanup readiness: **not yet** because the SEP statement must be corrected first.
