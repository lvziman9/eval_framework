# Storytelling Diagnosis for Chapter 3–6

## 1. Dissertation-Level Narrative Diagnosis

| Narrative component | Current status | Evidence in draft | Weakness | Revision direction |
|---|---|---|---|---|
| Central argument | Present but distributed | Chapters 3–6 consistently define the work as an evaluation and analysis framework rather than a new recommender. | The reader must reconstruct how implementation, results, mechanism analysis, and conclusion form one cumulative argument. | Restate the progression from canonical evidence, to measurable trade-offs, to bounded interpretation, to qualified closure. |
| Evidence progression | Evidentially sound | Validation, strict accuracy, alpha sweeps, ablation, and boundary evidence are correctly separated. | Section boundaries do not always state why one evidence type motivates the next. | Use unresolved questions to connect evidence eligibility, comparison, interpretation, and limitation. |
| Claim hierarchy | Mostly controlled | Claims are cautious and linked to evidence files and status records. | Detailed observations sometimes precede the analytical question or main claim. | Lead important sections and paragraphs with the claim that the evidence will establish. |
| Interpretation | Uneven across chapters | Chapter 5 contains careful mechanism interpretation and caveats; Chapters 3 and 4 contain more procedural and result listing. | The meaning of comparability, auditability, and metric-specific trade-offs is less prominent than the evidence permits. | Follow evidence with interpretation and a clear consequence for the dissertation argument. |
| Cross-chapter transitions | Present but weak | Each chapter states its scope and generally names the next chapter. | Transitions do not always identify the unresolved question that motivates the next stage. | End each chapter with the question answered by the following chapter. |
| Limitation control | Complete but dispersed | Citation, provenance, significance, user-study, mechanism, and Amazon-Book caveats appear across evidence and status files. | The narrative can appear more complete than the underlying citation and provenance layer. | Preserve caveats at the point where the affected claim is interpreted and consolidate them in Chapters 5 and 6. |

The current package has a defensible evidential structure. Its storytelling weakness is that the reader is often shown what was implemented or observed before being reminded which dissertation-level problem the evidence resolves. The revision should therefore foreground the sequence from comparability, to multidimensional trade-off evidence, to bounded mechanism interpretation, and finally to qualified conclusions.

## 2. Chapter-Level Story Function

| Chapter | Current story function | Problem | Desired story function | Revision priority |
|---|---|---|---|---|
| Chapter 3 | Describes framework implementation, native exports, validation, metrics, and verification. | Several passages read as component inventories or procedural checklists. | Establish that heterogeneous native-path models can be normalised, exported, validated, and compared under one canonical framework. | High |
| Chapter 4 | Reports strict accuracy and LIR, SEP, and ETD alpha-sweep results for six models on LastFM and ML-1M. | Long model-by-model enumerations obscure the absence of a universal winner and common explanation response. | Show what becomes visible under the framework: accuracy and explanation metrics move differently across models and datasets. | High |
| Chapter 5 | Presents PGPR and UCPR ablation, mechanism interpretation, metric synthesis, and the Amazon-Book boundary case. | The link from Chapter 4 patterns to controllability, mechanism limits, and boundary detection can be sharper. | Explain why the patterns matter through controllability, cautious mechanism interpretation, boundary detection, and limitations. | High |
| Chapter 6 | Summarises contributions and gives recommendations. | The conclusion partly follows chapter order instead of closing the dissertation argument. | Close the argument by linking framework contribution, empirical findings, evidence boundaries, and future work. | Medium |

## 3. Section-Level Storytelling Problems

| Section | Main issue | Example pattern | Why it weakens the thesis | Revision recommendation |
|---|---|---|---|---|
| 3.1 | Framework rationale competes with implementation detail. | Components are introduced before their full comparative purpose is established. | The contribution can appear procedural rather than problem-driven. | Open with the comparability problem and frame the architecture as its response. |
| 3.2 | Canonical views read as transformations. | Dataset and model views are described in sequence. | The reader sees process but not its role in controlling unfair variation. | Explain how canonical truth preserves fairness while model views preserve native execution. |
| 3.3 | Artifact listing dominates. | Export filenames carry much of the paragraph structure. | The native-path fidelity argument is less visible than the file contract. | Place the artifacts after the claim that native evidence must remain faithful and auditable. |
| 3.4 | Validation and metrics are checklist-heavy. | Checks and metric definitions follow one another without a strong argumentative hierarchy. | Validation appears technical rather than a condition for admissible claims. | Present validation as the evidence gate and the metrics as separate dimensions admitted after that gate. |
| 3.5 | Verification reads as a status report. | Passing and blocked rows are listed before their meaning is stated. | The framework's ability to expose unsupported comparisons is underemphasised. | Interpret both passing and blocked rows as evidence about framework feasibility and boundaries. |
| 3.6 | The transition question is implicit. | Later chapters are named by content. | The reader is not directly shown what remains unresolved after verification. | End by asking whether validated models exhibit a common or heterogeneous trade-off profile. |
| 4.1 | The chapter test is understated. | Scope and evidence streams precede the central empirical question. | The results can seem inventory-led. | State that the chapter tests universal versus model-, dataset-, and metric-specific behaviour. |
| 4.2 | Model-value listing delays the claim. | Separate leader values are reported before the cross-dataset conclusion. | The no-universal-winner result is less salient than individual scores. | Lead with the conclusion and use Table 4.1 for exhaustive detail. |
| 4.3 | Definitions dominate the opening. | LIR, SEP, and ETD are introduced before the multidimensional claim. | The section can read as metric documentation. | State first that explainability is not one outcome, then define the dimensions. |
| 4.4 | Repeated trajectories obscure LIR profiles. | Each model is described as an endpoint movement. | Comparative ranking cost and preservation patterns are hard to scan. | Group costly, preserved, and limited responses while retaining exact values. |
| 4.5 | SEP is presented as individual trajectories. | Model endpoints are listed in the same form as LIR. | The distinct meaning of bridge-entity rarity is weakened. | Emphasise that SEP movement and paired ranking cost differ from recency behaviour. |
| 4.6 | ETD repeats the prior result form. | Endpoint changes are again listed model by model. | The implication of path-type diversity is not prominent. | Lead with the diversity question and conclude with its metric-specific implication. |
| 4.7 | Synthesis does not fully motivate analysis. | Cross-dataset differences are restated before the next chapter is named. | The need for ablation and cautious mechanism interpretation remains implicit. | Close with the distinction between observed patterns and their untested causes. |
| 5.1 | Table values are duplicated in prose. | Multiple PGPR and UCPR points repeat Table 5.1. | The tested controllability inference is diluted by detail. | Lead with alpha-zero preservation and the 95% rule, then retain only decisive exact examples. |
| 5.2 | Mechanism discussion is not always anchored to Chapter 4. | Architecture families are described before their evidential level is restated. | Descriptive context may be mistaken for causal explanation. | Begin from observed heterogeneity and label direct, descriptive, and hypothetical evidence levels. |
| 5.3 | Metric definitions partly repeat Chapter 4. | LIR, SEP, and ETD are redefined at length. | Repetition displaces synthesis. | Focus on why the combined profile prevents one-dimensional evaluation. |
| 5.4 | Claim admissibility is implicit. | PASS and BLOCKED / N/A states are described operationally. | The analytical value of blocked evidence can be missed. | Explain that validation failure prevents unsupported ranking and is itself a boundary result. |
| 5.5 | The closing transition is weak. | Limitations end as a consolidated list. | Chapter 6 recommendations appear adjacent rather than derived. | Map limitation categories directly to the recommendation groups in Chapter 6. |
| 6.1 | Conclusion follows chapter order. | Contributions are summarised as successive chapter outputs. | Closure around the central dissertation argument is weaker than the evidence allows. | Organise around comparability, multidimensional measurement, bounded interpretation, and auditability. |
| 6.2 | Recommendations read as separate tasks. | Ten future-work paragraphs have limited connective grouping. | Their direct relationship to limitations is less visible. | Connect the existing recommendations through coverage, robustness, human evidence, and reproducibility. |

## 4. Data Listing Diagnosis

| Location | Current pattern | What is missing | Rewrite direction |
|---|---|---|---|
| Chapter 3, Sections 3.2–3.4 | Consecutive descriptions of views, exports, checks, and metrics | A claim explaining the evidence-quality problem solved by each component | Place each list after its comparative or validity rationale. |
| Chapter 4, Section 4.2 | Accuracy values listed model by model and dataset by dataset | The immediate conclusion that no model is a universal winner | Lead with the claim, retain decisive values, and refer exhaustive detail to Table 4.1. |
| Chapter 4, Sections 4.4–4.6 | Repeated alpha-zero and alpha-one trajectories | Comparative response profiles and their metric-specific meaning | Group models by observed pattern and use tables and figures for exhaustive values. |
| Chapter 5, Section 5.1 | Multiple ablation values repeated from Table 5.1 | The tested inference about baseline preservation and constrained control | Lead with the two tests and use exact examples only to demonstrate contrasting response ranges. |
| Chapter 6, Section 6.2 | Ten future-work items in consecutive paragraphs | A visible mapping from limitation categories to recommendations | Preserve every recommendation and add connective category logic. |

## 5. Claim–Evidence–Implication Gap

| Claim | Evidence present? | Interpretation present? | Implication present? | Required revision |
|---|---|---|---|---|
| Chapter 3: heterogeneous recommenders can be evaluated through a common framework. | Yes: canonical views, native exports, validation, metrics, and verification cases | Partial | Partial | Explain that the contract reduces format-driven differences without erasing model-specific execution and makes Chapter 4 comparison admissible. |
| Chapter 4: no single model or explanation setting dominates all conditions. | Yes: strict accuracy and six-model LIR, SEP, and ETD sweeps | Partial | Partial | State that evaluation requires a multidimensional profile rather than one aggregate winner. |
| Chapter 5: selected trade-offs can be tested while broader mechanisms remain descriptive. | Yes: PGPR/UCPR ablation, mechanism audit, and metric synthesis | Yes, with caveats | Partial | Label direct ablation, repository-supported description, and untested hypothesis as distinct evidence levels. |
| Chapter 5: Amazon-Book exposes a framework coverage boundary. | Yes: three passing and three blocked model validations | Partial | Partial | Explain that blocked validation prevents unsupported comparison and makes coverage limits auditable. |
| Chapter 6: the framework provides a disciplined basis for native-path evaluation. | Yes: cumulative Chapter 3–5 evidence | Yes | Partial | Close the argument through measurable, comparable, auditable, and explicitly bounded evidence. |
