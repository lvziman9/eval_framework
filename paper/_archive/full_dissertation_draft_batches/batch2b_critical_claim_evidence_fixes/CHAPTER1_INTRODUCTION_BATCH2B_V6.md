# Chapter 1 Introduction

## 1.1 Background

Recommender systems reduce information overload by ranking items according to evidence about user preferences and item relevance. Conventional collaborative and content-based methods organise this evidence primarily through interactions and attributes. Knowledge graph recommender systems extend that setting by representing users, items, entities, and relations in a structured graph, allowing recommendation methods to exploit semantic context and higher-order connectivity [@guo2022kgsurvey]. This structure can improve the information available to a recommender, but the use of a knowledge graph does not by itself make the recommendation process inspectable.

Explainable recommendation addresses the need to communicate why an item was recommended, support model inspection, and distinguish recommendation quality from the quality of its accompanying evidence [@zhang2020explainableSurvey]. Explanations may be intrinsic to a model or reconstructed after prediction. In a knowledge graph setting, a native-path explanation is a path produced or retained within the recommendation or path-selection workflow. A post-hoc explanation is generated after the recommendation decision by a separate attribution, search, or explanatory procedure. The distinction matters because an intelligible path recovered after prediction need not represent the evidence used to produce the recommendation.

Path-reasoning recommenders make this distinction operational. Methods such as PGPR and CAFE traverse or construct graph paths as part of recommendation and can expose those paths as explanation candidates [@xian2019pgpr; @xian2020cafe]. A native path can connect a user and historical interaction to a recommended item through graph entities and relations, making endpoints, path types, and intermediate evidence available for validation. However, a visible path is not automatically faithful, useful, recent, serendipitous, or diverse. These properties require explicit definitions and separate checks.

Recommendation accuracy is therefore necessary but insufficient for evaluating native-path systems. HR@10, NDCG@10, Precision@10, and Recall@10 describe ranking outcomes, whereas path properties such as linked interaction recency (LIR), the repository-specific bridge-entity score (SEP), and explanation type diversity (ETD) describe different aspects of the associated explanation evidence. SEP is used as an operational explanation-side metric rather than as direct evidence of user-perceived serendipity. The conceptual origin of these path properties is provided by XRecSys, while the exact formulas and data assumptions evaluated in this dissertation are repository-specific [@balloccu2022xrecsys]. A defensible evaluation must retain this separation rather than collapse ranking and explanation evidence into a single score.

## 1.2 Motivation

The evaluation problem begins with model heterogeneity. Knowledge graph recommenders use different graph schemas, identifier systems, training views, search procedures, path representations, and output formats. Some produce native recommendation paths; others expose latent graph signals or require post-hoc explanation. Even among native-path systems, the available candidate paths, relation vocabularies, temporal requirements, and selection mechanisms can differ. Raw model outputs are consequently not directly comparable.

The problem is compounded when accuracy and explanation quality are evaluated through disconnected protocols. Ranking values may refer to one user population while path metrics refer to another export, or an explanation may not terminate at the item reported in the recommendation list. Alpha-sweep ranking values may also be mistaken for strict accuracy, and ablation results may be presented as though they were the six-model main comparison. These errors change the evidential meaning of a result even when the numerical values themselves are reproduced correctly.

Fair comparison therefore requires a canonical dataset that defines shared users, items, splits, labels, and knowledge graph provenance; model-specific views that preserve legitimate implementation requirements; a native-path export contract that returns outputs to canonical identifiers; and validation gates that determine whether each model-dataset row is admissible. It also requires shared ranking and path-metric definitions and an evidence register that keeps strict accuracy, alpha-sweep, ablation, validation, and boundary-case claims separate. Benchmarking literature similarly shows that dataset and protocol choices can materially affect recommender comparisons [@shevchenko2024recsysBenchmarking].

This dissertation responds to that need by developing and verifying a canonical native-path evaluation framework. It does not propose a new recommender model. The framework makes accuracy–explainability trade-offs measurable through registered metrics, comparable through canonical identifiers and common contracts, and auditable through validation and provenance records. Its empirical role is to reveal model-, dataset-, and metric-dependent profiles while making unsupported or incomplete comparisons explicit.

## 1.3 Objectives and Specifications

The research objectives are:

1. To design a canonical evaluation framework for native-path knowledge graph recommender systems.
2. To construct canonical datasets and model-specific views without forcing heterogeneous models into an invalid common internal representation.
3. To define a native-path export contract for recommendations, candidate paths, and user-item explanations.
4. To validate exported recommendations and explanations before admitting them to comparative reporting.
5. To evaluate strict recommendation accuracy through HR@10, NDCG@10, Precision@10, and Recall@10.
6. To evaluate explanation evidence through the separate LIR, SEP, and ETD dimensions.
7. To perform controlled, metric-specific accuracy–explainability trade-off analysis through alpha sweeps.
8. To analyse ablation evidence, mechanism dependence, dataset dependence, and boundary cases without exceeding the registered evidence.

| Objective | Specification | Evidence / chapter |
| --- | --- | --- |
| O1. Canonical evaluation framework | Separate canonical truth, model execution, export, validation, and reporting concerns. | Framework architecture and verification, Chapter 3. |
| O2. Canonical and model-specific views | Define common users, items, splits, labels, and mappings while allowing model-specific graph and identifier views. | Canonical dataset and model-view construction, Section 3.2. |
| O3. Native-path export contract | Require canonical recommendation, path, and explanation artifacts for native-path rows. | Export contract and implementation, Section 3.3. |
| O4. Validation before reporting | Check coverage, duplicates, leakage, endpoints, recommendation–explanation alignment, candidate consistency, and score ranges. | Evaluation and validation pipeline, Sections 3.4–3.5. |
| O5. Strict accuracy evaluation | Report HR@10, NDCG@10, Precision@10, and Recall@10 from the registered strict-accuracy evidence stream. | Strict accuracy results, Section 4.2. |
| O6. Multidimensional explanation evaluation | Report LIR, SEP, and ETD separately under the repository definitions and verified conceptual provenance. | Sections 3.4 and 4.3–4.6. |
| O7. Controlled trade-off analysis | Use metric-specific alpha sweeps while keeping sweep ranking measures separate from strict accuracy. | Sections 3.6 and 4.4–4.7. |
| O8. Ablation and boundary analysis | Use PGPR/UCPR ablation for bounded controllability evidence, descriptive mechanism context for other models, and Amazon-Book KGAT as a partial boundary case. | Chapter 5. |

The specifications establish evidence conditions rather than performance targets. A model-dataset row is reportable only when its required export and validation contract is supported. A blocked or not-applicable row remains visible as an evaluation boundary and is not interpreted as poor model performance.

## 1.4 Major Contribution

The dissertation makes eight connected contributions.

1. It provides a canonical native-path evaluation framework that separates shared dataset truth from heterogeneous model execution.
2. It establishes a validation-first export contract in which recommendation and native-path artifacts must return to canonical identifiers and pass registered checks before scoring.
3. It preserves a strict separation between ranking accuracy and the LIR, SEP, and ETD explanation dimensions, preventing one evidence type from substituting for another.
4. It supports controlled alpha-sweep analysis that records metric-specific trade-off trajectories without assuming a universal coefficient or operating point.
5. It supplies PGPR/UCPR ablation evidence for framework controllability under an exact alpha=0 baseline and a declared NDCG-retention rule; this is not presented as improvement of the underlying recommenders.
6. It provides mechanism-level and dataset-level interpretation through graded claims: registered ablation supports bounded control statements, while non-targeted model explanations remain descriptive rather than causal.
7. It identifies Amazon-Book KGAT as a partial boundary case with reportable and blocked rows, demonstrating how validation prevents incomplete contracts from entering a full comparison.
8. It assembles a traceable dissertation evidence package connecting claims, metrics, tables, figures, citations, validation states, and source paths while retaining unresolved provenance caveats.

These contributions concern evaluation, validation, and analysis infrastructure. They do not constitute a new recommendation algorithm, a claim of universal model superiority, or evidence of state-of-the-art performance. The current strict-accuracy values are traceable at draft level to two matching summary sources, while the twelve expected primary row-level JSON artifacts remain unavailable and must not be described as directly inspected.

## 1.5 Organisation

Chapter 2 reviews knowledge graph recommendation, path reasoning, native and post-hoc explanation, multidimensional explanation quality, accuracy–explainability trade-offs, and fair evaluation. It synthesises the literature into the evaluative gap addressed by the dissertation and leads directly to the framework requirements.

Chapter 3 defines the implemented framework. It presents canonical datasets and model-specific views, the native-path export contract, the validation-first pipeline, framework verification, and the separation of strict accuracy, alpha-sweep, and ablation evidence.

Chapter 4 reports the main empirical results for the complete LastFM and ML-1M six-model scope. It presents strict accuracy, explanation endpoints, LIR-, SEP-, and ETD-oriented alpha sweeps, and cross-dataset comparison while keeping mechanism claims outside the result evidence.

Chapter 5 examines the evidence needed to interpret those profiles. It analyses the registered PGPR/UCPR ablation, provides cautious mechanism-level context, distinguishes accuracy and explanation interactions, treats Amazon-Book KGAT as a partial boundary case, and states the limitations of the current framework and experiments.

Chapter 6 consolidates the supported conclusions and recommends further work on evidence coverage, robustness, metric sensitivity, native-path coverage, human evaluation, grounded explanation generation, post-hoc baselines, citation closure, and reproducibility. It introduces no new result.

The next chapter establishes the literature basis for these choices. It first distinguishes major knowledge graph recommendation and explanation families, then shows why their outputs and evaluation objectives require the canonical, validation-first framework specified in Chapter 3.
