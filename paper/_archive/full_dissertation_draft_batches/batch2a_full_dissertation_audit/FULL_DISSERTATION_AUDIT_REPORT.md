# Full Dissertation Audit Report

## 1. Overall Assessment

The V5 dissertation draft has a coherent evaluative thesis: heterogeneous native-path knowledge graph recommenders require a canonical, validation-first framework before their ranking and explanation evidence can be compared. Chapters 1 and 2 establish that problem, Chapter 3 formalises the framework, Chapter 4 reports strict and sweep results, Chapter 5 interprets ablation, mechanisms, and boundaries, and Chapter 6 closes the supported contribution without claiming a new recommender.

The draft is not yet ready for direct Markdown cleanup. Two high-risk SEP statements in Chapters 2 and 6 conflict with the frozen weak-semantics position used in Chapters 3–5. The supervisor-facing document is also incomplete because it has no title page or abstract, references and appendix remain placeholders, tables and figure assets are not integrated, and internal workflow labels such as "Batch 1C" remain in the prose. These are targeted revision issues rather than evidence for rewriting the dissertation argument.

## 2. Major Strengths

- The research problem, framework contribution, and non-model boundary are explicit and consistent across the principal chapter transitions.
- Chapter 1 states eight objectives and maps each objective to a specification and evidential chapter.
- Chapter 2 is organised as a thematic synthesis that leads to an evaluative gap instead of a paper-by-paper catalogue.
- Chapter 3 gives formal definitions for the canonical dataset, model views, exports, validation gate, strict metrics, LIR, SEP, ETD, alpha sweeps, deltas, and ablation retention.
- Chapter 4 functions as results plus findings: it reports strict accuracy, explanation endpoints, metric-specific sweep profiles, and cross-dataset patterns without turning associations into causal mechanisms.
- Chapter 5 is distinct from Chapter 4: it uses PGPR/UCPR ablation for bounded controllability, keeps other mechanism accounts descriptive, and treats Amazon-Book KGAT as a partial boundary case.
- Strict accuracy, alpha-sweep ranking values, ablation retention, and boundary validation are assigned different evidence roles.
- Caveats concerning unavailable primary strict JSON, absent significance artifacts, absent user-study evidence, incomplete checkpoint provenance, and PEARLM publication metadata are retained.

## 3. Major Risks

1. Chapter 2 describes SEP as concerning "rarity or serendipity," and Chapter 6 says SEP uses "degree-derived serendipity." Both statements exceed the frozen interpretation of SEP as a repository-specific bridge-entity score and operational explanation-side metric.
2. The twelve expected LastFM and ML-1M row-level strict-accuracy JSON artifacts are unavailable. Strict rankings are reproducible at draft level from two matching summary sources, but not from direct inspection of the declared primary artifacts.
3. The full draft references tables and figures without integrating a complete, authoritative table and figure set. Earlier plans conflict with the V5 decision that Figure 4.5 belongs in the main text.
4. References and Appendix are placeholders, and the draft has no title page or abstract. Title, thesis-statement, abstract, bibliography, and appendix consistency therefore cannot be assessed as a complete submission package.
5. Internal production labels, evidence-package language, and later-goal notes reduce supervisor-facing readability and should be neutralised without changing their caveats.
6. Chapter 3 is much longer than the result and conclusion chapters and repeats several evidence-boundary explanations. This is a readability risk, not a methodological defect.
7. Chapter 6 closes three broad contribution groups but does not explicitly close O1–O8, making the otherwise strong alignment less visible to a supervisor.

No current draft claim requires a `Blocker` classification if all existing caveats remain. The two SEP conflicts and strict-primary provenance gap are `High` risks that require explicit treatment before sharing.

## 4. Chapter Flow Assessment

The progression from comparability problem to literature gap, formal framework, empirical findings, interpretation, and conclusion is logically sound. Chapter-ending transitions generally state the evidence role of the next chapter. Chapter 4 appropriately defers mechanism claims to Chapter 5, and Chapter 5 explicitly bounds the conclusion by coverage and provenance limitations.

The main flow weakness is documentary rather than argumentative. Chapter 3 includes internal references to diagram-production batches, while the diagrams themselves are not inserted. Chapter 6 summarises three contribution groups but does not provide an explicit objective closure. A concise O1–O8 closure device would strengthen the final transition from evidence to conclusion without adding a new claim.

## 5. Argument Coherence

The central argument is coherent: model heterogeneity creates a comparability problem; a shared external contract enables validation; validated outputs permit separate ranking and explanation analyses; bounded ablation and boundary evidence constrain interpretation. The draft consistently states that it contributes evaluation, validation, and analysis infrastructure rather than a new recommendation algorithm.

No exact long-paragraph duplication was detected. There is, however, conceptual repetition of evidence-stream separation, missing-artifact caveats, and noncausal boundaries across Chapters 3–5. Those repetitions are defensible for auditability but should be reduced where a cross-reference can carry the same constraint.

## 6. Evidence Coherence

The main LastFM and ML-1M scope contains six validated model rows per dataset. Strict values are kept separate from sweep NDCG; metric-specific alpha sweeps are kept separate from PGPR/UCPR ablation; and Amazon-Book KGAT remains a three-PASS, three-BLOCKED/N/A partial boundary. LIR, SEP, and ETD are not collapsed into a composite explanation score.

The strongest unresolved provenance risk is strict accuracy: the canonical status matrix and final accuracy summary match, but none of the twelve declared row-level primary JSON artifacts is accessible. The draft correctly avoids inferential claims because no statistical-significance artifact is registered and avoids user-perceived claims because no user-study artifact exists. These caveats must remain visible in every supervisor-facing table or summary that reports the affected claims.

## 7. Readiness Judgment

**Requires targeted revision before cleanup**

The argument and evidence boundaries are mature enough for a focused repair batch. Markdown cleanup should follow, not precede, correction of the frozen SEP wording, source-of-truth conflicts, table/figure integration plan, objective closure, and internal workflow language.

## 8. Required Revision Before Supervisor Review

1. Replace the two unsafe SEP statements in Chapters 2 and 6 with the frozen repository-specific, operational wording; audit Chapter 1 terminology at the same time.
2. Preserve the strict-primary JSON caveat and distinguish it from the two matching summary sources wherever strict rankings appear.
3. Establish one authoritative table and figure manifest, with Figure 4.5 in the main text and Figure 4.6 optional or appendix-level.
4. Replace internal batch labels with neutral references to figures, diagrams, appendices, or provenance records.
5. Add a title, abstract, verified bibliography, and selected appendix content before supervisor-package generation.
6. Make Chapter 6's closure of O1–O8 explicit without introducing results or stronger claims.
7. Resolve isolated pipe-line formatting and integrate the missing tables and figure placeholders before Word conversion.
8. Retain all caveats on primary JSON, significance, human evidence, Amazon coverage, metric semantics, and incomplete run provenance.
