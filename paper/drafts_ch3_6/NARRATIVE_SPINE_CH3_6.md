# Narrative Spine for Chapter 3–6

## 1. Dissertation Argument Spine

This dissertation argues that knowledge graph recommender models cannot be compared responsibly through isolated accuracy scores or a single explanation metric. It develops and verifies a canonical native-path evaluation framework, then uses that framework to show that accuracy-explainability trade-offs are measurable, model-dependent, dataset-dependent, and bounded by the native path-generation and selection conditions represented in validated outputs. The framework also exposes boundary cases in which incomplete native-path evidence prevents fair comparison.

The Chapter 3–6 argument proceeds in four steps. Chapter 3 establishes the evidence conditions required for fair comparison. Chapter 4 uses those conditions to show that accuracy and explanation responses are heterogeneous across models, datasets, metrics, and alpha settings. Chapter 5 tests selected trade-offs through registered ablation, distinguishes evidence-backed findings from plausible mechanism interpretation, and uses Amazon-Book to expose the framework's coverage boundary. Chapter 6 concludes that the value of the framework lies not in naming a universal winner, but in making recommendation evidence measurable, comparable, auditable, and explicitly bounded.

## 2. Chapter 3 Narrative Spine

Sentence 1: Heterogeneous recommendation models produce outputs, explanations, and execution artifacts that are not directly comparable.

Sentence 2: The framework constructs canonical data and model views, preserves native explanation exports, and applies validation before admitting evidence to comparison.

Sentence 3: The registered implementation and verification artifacts show that the common pipeline can process supported LastFM and ML-1M cases while identifying blocked or incomplete cases.

Sentence 4: Chapter 4 can compare accuracy and explanation trade-offs only because Chapter 3 defines which evidence is valid and how it is represented.

## 3. Chapter 4 Narrative Spine

Sentence 1: Chapter 4 asks whether validated explanation-aware recommenders exhibit a universal accuracy winner or a common explainability response to alpha.

Sentence 2: Strict accuracy results and separate LIR, SEP, and ETD alpha sweeps cover six models on LastFM and ML-1M.

Sentence 3: Performance leadership and explanation response vary by model, dataset, metric, and alpha; strict accuracy and alpha-sweep evidence therefore support different claims.

Sentence 4: Evaluation requires multidimensional trade-off profiles, and the observed heterogeneity motivates a more careful examination of mechanisms in Chapter 5.

## 4. Chapter 5 Narrative Spine

Sentence 1: Chapter 5 asks which observed trade-offs can be tied to tested controls, which can only be interpreted descriptively, and where the framework ceases to support comparison.

Sentence 2: Registered PGPR and UCPR ablations test selected alpha effects; cross-model evidence supports cautious mechanism grouping; Amazon-Book validation records three passing and three blocked models.

Sentence 3: Alpha-zero preservation and retained-accuracy selections demonstrate controlled trade-offs within the ablation scope, while broader architectural explanations remain plausible rather than causal and Amazon-Book remains a partial boundary case.

Sentence 4: The framework supports graded claims whose strength depends on validation, provenance, and experimental design rather than on narrative confidence.

## 5. Chapter 6 Narrative Spine

Sentence 1: The dissertation contributes a reproducible evaluation and analysis framework, not a new recommender or a claim of universal model superiority.

Sentence 2: Its evidence shows that recommendation quality, explanation recency, popularity exposure, and entity-type diversity must be evaluated separately under controlled and validated conditions.

Sentence 3: Citation verification, primary JSON provenance, statistical significance, user-facing evaluation, non-targeted mechanism tests, and complete Amazon-Book coverage remain unresolved.

Sentence 4: Future work should expand evidence coverage and robustness while preserving the framework's separation of evidence types and explicit validity boundaries.

## 6. Cross-Chapter Transition Plan

| Transition | Purpose | Required wording direction |
|---|---|---|
| Chapter 3 → Chapter 4 | Move from admissible evidence to the empirical question enabled by that evidence. | Close by asking whether the validated models share a performance and explanation profile; open Chapter 4 with strict accuracy and separate LIR, SEP, and ETD tests. |
| Chapter 4 → Chapter 5 | Move from observed heterogeneity to the evidential limits of mechanism explanation. | State that comparative curves do not establish causes; open Chapter 5 with registered ablation and cautious mechanism interpretation. |
| Chapter 5 → Chapter 6 | Move from graded findings and boundaries to qualified closure and future work. | State that conclusions remain bounded by validation, provenance, and scope; open Chapter 6 by consolidating the framework contribution. |
