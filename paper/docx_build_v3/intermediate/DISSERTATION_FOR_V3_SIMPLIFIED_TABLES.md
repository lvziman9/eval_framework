# Abstract

Knowledge graph recommender systems use structured entities and relations to support recommendation, but heterogeneous graph schemas, identifier spaces, path formats, and evaluation procedures make their outputs difficult to compare. The problem is especially acute for native-path recommenders, whose recommendation paths can provide inspectable evidence only when they remain aligned with the evaluated users, items, and ranked outputs.

This dissertation does not propose a new recommender model. Instead, it develops and applies a canonical evaluation framework for native-path knowledge graph recommender systems. The framework separates canonical dataset truth from model-specific execution views, requires recommendations and native paths to return to shared identifiers through a three-file export contract, and applies validation gates before admitting a model-dataset row to comparative reporting. It evaluates strict recommendation accuracy through HR@10, NDCG@10, Precision@10, and Recall@10, while linked interaction recency (LIR), the repository-specific bridge-entity score (SEP), and explanation type diversity (ETD) remain separate explanation-side dimensions. SEP is treated as a repository-specific bridge-entity score rather than as direct evidence of user-perceived serendipity.

The empirical analysis covers six native-path models on the complete LastFM and ML-1M scopes. Objective-specific alpha sweeps describe how LIR, SEP, or ETD and paired sweep ranking measures change under controlled re-ranking; these sweep measures remain separate from strict accuracy. A registered PGPR/UCPR ablation examines baseline preservation and bounded controllability under an NDCG-retention rule, while broader mechanism accounts remain descriptive. Amazon-Book KGAT is retained only as a partial boundary case because three model rows are blocked or not applicable and no approved explanation sweeps are available.

The results support model-, dataset-, metric-, and objective-dependent profiles rather than universal dominance. Strict accuracy leadership changes across datasets and metrics, and explanation-objective movement carries different paired ranking costs. These conclusions remain descriptive. The twelve expected primary strict-accuracy JSON artifacts are unavailable, no statistical-significance or user-study artifact is registered, PEARLM final publication metadata requires manual verification, and exact checkpoints, hashes, seeds, and several model-native settings remain incomplete. The contribution is therefore an auditable basis for controlled comparison with explicit limits, not a claim of state-of-the-art performance or complete archival reproducibility.

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

| Objective | Short specification | Evidence location |
| --- | --- | --- |
| O1. Canonical evaluation framework | Separate canonical truth, model execution, export, validation, and reporting concerns. | Framework architecture and verification, Chapter 3. |
| O2. Canonical and model-specific views | Define common users, items, splits, labels, and mappings while allowing model-specific graph and identifier views. | Canonical dataset and model-view construction, Section 3.2. |
| O3. Native-path export contract | Require canonical recommendation, path, and explanation artifacts for native-path rows. | Export contract and implementation, Section 3.3. |
| O4. Validation before reporting | Check coverage, duplicates, leakage, endpoints, recommendation–explanation alignment, candidate consistency, and score ranges. | Evaluation and validation pipeline, Sections 3.4–3.5. |
| O5. Strict accuracy evaluation | Report HR@10, NDCG@10, Precision@10, and Recall@10 from the registered strict-accuracy evidence stream. | Strict accuracy results, Section 4.2. |
| O6. Multidimensional explanation evaluation | Report LIR, SEP, and ETD separately under the repository definitions and verified conceptual provenance. | Sections 3.4 and 4.3–4.6. |
| O7. Controlled trade-off analysis | Use metric-specific alpha sweeps while keeping sweep ranking measures separate from strict accuracy. | Sections 3.6 and 4.4–4.7. |
| O8. Ablation and boundary analysis | Use PGPR/UCPR ablation for bounded controllability evidence, descriptive mechanism context for other models, and Amazon-Book KGAT as a partial boundary case. | Chapter 5. |

**Table 1.1.** Research objectives, concise specifications, and evidence locations.

The specifications establish evidence conditions rather than performance targets. A model-dataset row is reportable only when its required export and validation contract is supported. A blocked or not-applicable row remains visible as an evaluation boundary and is not interpreted as poor model performance.

## 1.4 Major Contribution

The dissertation makes eight connected contributions.

1. It provides a canonical native-path evaluation framework that separates shared dataset truth from heterogeneous model execution.
2. It establishes a validation-first export contract in which recommendation and native-path artifacts must return to canonical identifiers and pass registered checks before scoring.
3. It preserves a strict separation between ranking accuracy and the LIR, SEP, and ETD explanation dimensions, preventing one evidence type from substituting for another.
4. It supports controlled alpha-sweep analysis that records metric-specific trade-off trajectories without assuming a universal coefficient or operating point.
5. It supplies PGPR/UCPR ablation evidence for framework controllability under an exact alpha=0.00 baseline and a declared NDCG-retention rule; this is not presented as improvement of the underlying recommenders.
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

# Chapter 2 Literature Review

Chapter 1 identified comparability as the central problem addressed by this dissertation. Knowledge graphs, explicit path reasoning, and language-model-based generation have expanded the design space of recommender systems beyond conventional user-item prediction, but this expansion has also made evaluation more difficult. Models can use graph structure as latent side information, expose graph paths during recommendation, reconstruct explanations after prediction, or generate language that describes a recommendation. These outputs are not equivalent, and their quality cannot be established through ranking accuracy alone.

This chapter reviews the literature through the evaluation problem addressed by this dissertation. The central argument is that existing research provides strong model families, explanation taxonomies, path-quality objectives, and benchmarking principles, but these components are not automatically comparable across heterogeneous native-path recommenders. The review therefore progresses from KG recommendation to explicit path reasoning, multidimensional explanation quality, accuracy–explainability trade-offs, and reproducible evaluation. It then positions the dissertation as a canonical evaluation and controlled analysis framework rather than as a new recommender model.

## 2.1 Knowledge Graph Recommendation

Knowledge-graph recommendation uses structured entities and relations to enrich the signals available for matching users and items. Compared with an interaction matrix alone, a KG can represent item attributes, semantic relations, and higher-order connectivity. This additional structure can be incorporated into recommendation in several ways. RippleNet, for example, propagates user preferences from historically interacted items through KG links, while KGIN models user intents and long-range relational dependencies through graph aggregation [@wang2018ripplenet; @wang2021kgin]. VRKG4Rec instead groups relations into virtual relational graphs before encoding items and users [@lu2023vrkg4rec]. These approaches illustrate that KG use is not one method but a family of representation and inference strategies.

A central distinction concerns whether graph structure remains latent or produces an inspectable reasoning object. Representation-oriented approaches can improve or enrich user and item embeddings without exporting the route by which a recommended item is connected to a user's history. Even when a model provides attention weights, influential intents, or relational interpretation, those signals do not necessarily form a complete user-to-item path that can be checked against the recommended item. Surveys of KG and graph-based explainable recommendation consequently distinguish embedding-based, path-based, and hybrid learning approaches, as well as node-, path-, meta-path-, and implicit explanation types [@guo2022kgsurvey; @markchom2026graphExplainableSurvey].

The recent use of large language models further increases this heterogeneity. LLMs may support feature construction, representation encoding, scoring, interaction, or pipeline control, and they may also generate natural-language rationales [@lin2025llmRecSurvey]. Agent-oriented and multimodal surveys describe still broader combinations of language, memory, planning, interaction, and heterogeneous item content [@peng2025llmAgentsRec; @lopezAvila2025llmMultimodalRec]. These developments are relevant to language-model-based recommenders, but a generated rationale or textual sequence should not be assumed to be equivalent to a verified KG path. The relation between generated language, graph structure, and the recommendation mechanism must be specified by each system.

The synthesis for this dissertation is that KG recommenders share a data resource but not a common evidential form. Graph propagation, intent aggregation, relation clustering, policy search, neural-symbolic reasoning, and language modelling impose different data views and output semantics. A fair comparison must therefore preserve legitimate model-specific representations while establishing a shared evaluation space outside the models. This requirement motivates the separation between canonical dataset truth and model-specific views developed in Chapter 3.

## 2.2 Path Reasoning and Native-Path Explainability

Path-reasoning recommenders are especially relevant to explainability because their recommendation process can expose a sequence of relations connecting a user, historical evidence, graph entities, and a candidate item. PGPR formulates recommendation as policy-guided search over a KG and returns sampled reasoning paths with its recommendations [@xian2019pgpr]. Ekar uses a related sequential-decision formulation in which graph edges define actions and policy-gradient learning discovers paths from users to items [@song2019ekar]. These methods make the path structurally inspectable rather than leaving all high-order connectivity inside a latent representation.

Path reasoning nevertheless contains substantial methodological variation. KPRN encodes candidate paths and aggregates their contributions for recommendation [@wang2019kprn]. CAFE constructs coarse user profiles that guide fine-grained neural-symbolic path finding [@xian2020cafe]. UCPR introduces a user-centric path-reasoning design, while TPRec adds time-aware path reasoning and therefore depends on temporal information that is not required by every KG recommender [@tai2021ucpr; @zhao2022tprec]. Multi-level reasoning over ontology- and instance-view KGs provides another example in which the graph hierarchy and the path extraction process are specific to the model [@wang2022multilevelReasoning]. The literature therefore supports explicit paths as explanation candidates, but it also shows that path length, relation vocabulary, search constraints, graph views, and candidate construction can differ materially.

Language modelling introduces a further path-generation family. KGGLM uses a generative language-model formulation for KG representation learning in recommendation [@balloccu2024kgglm]. PEARLM is described in its verified arXiv record as a faithful path-language-modelling approach for explainable recommendation over KGs [@balloccu2023pearlm]. The latter citation should remain cautious because a final venue and publisher DOI have not been verified. More generally, evidence that language models can produce intermediate reasoning in other tasks does not establish that a generated recommendation path exists in the source graph or faithfully records the recommender's decision process. Faithfulness must be defined and checked in the recommendation setting rather than inferred from the presence of a reasoning-like sequence.

This dissertation therefore uses an operational distinction between native and post-hoc paths. A native path is emitted by, or retained from, the model's recommendation or path-selection workflow. A post-hoc path is reconstructed after an item has already been selected, for example through attribution, graph search, or a separate explanatory model. Explainable-recommendation taxonomies recognise both model-intrinsic and post-hoc approaches [@zhang2020explainableSurvey], while general tools such as InterpretML and Captum illustrate how a separate method can explain an existing prediction [@nori2019interpretml; @kokhlikyan2020captum]. Post-hoc explanations may be useful, but they do not provide the same evidence about how a native-path recommender generated its output.

The synthesis is that native paths create an opportunity for model-aligned explanation, not an automatic guarantee of explanation quality. The path must terminate at the reported item, remain aligned with the ranked output, use valid graph entities and relations, and satisfy the model's own candidate constraints. Because the reviewed methods expose different path structures, Chapter 3 defines a common export and validation contract without replacing their internal reasoning mechanisms.

## 2.3 Explainable Recommendation and Explanation Quality

Explanation quality is multidimensional because explanations serve different purposes and stakeholders. Explainable recommendation can support transparency, persuasion, trust, satisfaction, debugging, or control, and these goals do not imply the same preferred explanation form [@zhang2020explainableSurvey]. Trustworthy-recommendation research places explainability alongside fairness, privacy, robustness, and controllability, further indicating that system quality cannot be reduced to one undifferentiated property [@ge2025trustworthyRecSurvey]. Reviews of graph-based explainable recommendation similarly distinguish learning methods, explaining methods, explanation types, datasets, and qualitative and quantitative evaluation practices [@markchom2026graphExplainableSurvey].

The distinction between native and post-hoc explanation is one part of this multidimensionality. Another is the property measured within an explanation. Feature attribution asks which inputs influenced a prediction. Counterfactual explanation asks what would need to change for a different result. A graph path can instead be evaluated through its entities, relations, historical anchor, structural rarity, type pattern, length, or consistency with the recommendation. Evaluation concepts developed for one form should not be transferred to another without an explicit definition. General GNN-explainability work reinforces this point by documenting multiple explanation objects, benchmarks, and metrics rather than a single accepted measure [@yuan2020gnnExplainability].

For path-reasoning recommendation, XRecSys develops a focused family of explanation properties. Its SIGIR study examines the recency of the linked interaction, the popularity of a shared entity, and diversity among explanation types, and it uses re-ranking to optimise these properties while monitoring recommendation utility [@balloccu2022xrecsys]. The related software article presents XRecSys as a framework for assessing and optimising recommendation and explanation outputs from path-reasoning systems [@balloccu2022xrecsysFramework]. These sources motivate the dissertation's use of separate path-property dimensions rather than a generic explanation score.

The dissertation operationalises this family through LIR, SEP, and ETD. LIR concerns the recency of the historical interaction linked by a path. Following the XRecSys-style explanation-metric setting, SEP is a repository-specific bridge-entity score interpreted through the implemented repository metric pipeline. The dissertation does not independently validate SEP as a user-perceived serendipity construct. ETD concerns diversity among explanation path types across a recommendation list. These definitions are related to the XRecSys conceptual source, but their exact formulas and data assumptions remain repository-specific. They must therefore be traced both to the external conceptual publication and to the implementation and metric guide used by the dissertation.

The synthesis is that movement in one explanation dimension does not establish overall explanatory superiority. A path may be recent but structurally common, rare but repetitive in type, or diverse without being persuasive to a user. Automated path metrics also do not substitute for human evaluation of usefulness, clarity, or trust. Accordingly, this dissertation reports LIR, SEP, and ETD separately, avoids an unsupported composite explanation score, and treats user-facing explanation quality as an area for future validation rather than as a completed empirical result.

## 2.4 Accuracy–Explainability Trade-off in Recommendation

Ranking accuracy and explanation quality are distinct objectives, so their relationship should be measured rather than assumed. A model can achieve strong ranking performance while providing limited inspectable evidence, and an explanation-oriented re-ranking step can change the order of otherwise relevant items. Conversely, an explicit reasoning path does not establish that the associated item is accurately ranked. Explainable-recommendation and trustworthy-recommendation surveys therefore motivate joint consideration of recommendation effectiveness and explanation properties without treating them as one quantity [@zhang2020explainableSurvey; @ge2025trustworthyRecSurvey].

The XRecSys work provides direct evidence that explanation-oriented properties can be placed in a re-ranking objective while recommendation utility is monitored separately [@balloccu2022xrecsys]. This formulation is important because it avoids defining an explanation property as a replacement for ranking quality. It also exposes the possibility of different operating points: a system designer may choose how strongly to favour a path property subject to an explicit utility condition. However, this literature does not justify a universal claim that explanation improvement always causes an accuracy loss, nor does it establish that one coefficient has the same meaning for every model, dataset, or explanation property.

RL and LLM recommender surveys broaden the trade-off context. RL systems can optimise immediate or long-term rewards and differ in state, action, reward, and environment construction [@afsar2022rlRecSurvey; @lin2024rlRecSurvey]. LLM-based systems introduce additional concerns such as training efficiency, inference latency, hallucination, privacy, fairness, and explainability [@lin2025llmRecSurvey]. These literatures show that recommender objectives are plural and implementation-dependent. They do not, however, provide a common native-path experiment in which heterogeneous models are evaluated under the same path-property control and validation rules.

The synthesis for this dissertation is a controlled, metric-specific view of trade-off. Strict ranking results and explanation-oriented sweeps answer different questions and must remain separate evidence streams. The former describe validated recommendation outputs under the registered strict evaluation; the latter describe how a ranking-related measure and one explanation property respond as a control parameter changes. Chapter 3 defines this separation, while later empirical chapters analyse the resulting profiles without assuming a universal ordering, a linear relation, or a single globally appropriate operating point.

## 2.5 Evaluation Protocols, Reproducibility, and Fair Comparison

Fair recommender comparison requires control over datasets, outputs, metrics, and evidence eligibility. Recommender rankings can vary with dataset characteristics, and evaluations over a narrow or arbitrary dataset selection can give an incomplete view of algorithm behaviour. Multi-dataset benchmarking work explicitly demonstrates this sensitivity and argues for more stable comparison practices [@shevchenko2024recsysBenchmarking]. RL recommender surveys likewise identify environment construction, reward definition, offline evaluation, and scalability as recurring methodological challenges [@afsar2022rlRecSurvey; @chen2021drlRecSurvey; @rossiiev2025rlRecSurvey].

Native-path evaluation adds requirements that ranking-only protocols do not cover. It is not sufficient to compute a ranking metric from one file and an explanation metric from another without checking whether they refer to the same users and items. A reportable native-path output must preserve the ranked item, connect valid endpoints, align the explanation with the recommendation, and use a documented path representation. Duplicate recommendations, seen-item leakage, incomplete user coverage, invalid path endpoints, and candidate-path inconsistencies can otherwise be mistaken for model behaviour. XRecSys provides reusable path-quality evaluation components, while graph-explanation surveys document fragmented datasets and evaluation practices [@balloccu2022xrecsysFramework; @markchom2026graphExplainableSurvey]. The literature motivates stronger protocol discipline, but the exact validation gates remain part of this dissertation's methodological design.

Reproducibility also requires a distinction between shared truth and model-specific execution. Forcing every model to consume an identical internal graph may invalidate models with different relation vocabularies, pruning rules, temporal requirements, or search procedures. Allowing every model to define its own evaluation population creates the opposite problem: metrics no longer refer to the same task. A defensible protocol therefore preserves internal model views while requiring a return to canonical users, items, labels, and output semantics at evaluation time.

Boundary detection is a related part of fair comparison. A model-dataset row may be unsupported because required timestamps, graph relations, export routines, or candidate paths are unavailable. Such a row should not be assigned a poor score or silently omitted. It should be marked as blocked or not applicable, with the reason retained as evidence about the evaluation boundary. This approach aligns benchmarking with validation: only supported outputs enter comparative reporting, while unsupported combinations remain visible without being misinterpreted as measured model performance.

The synthesis is that reproducibility in this setting is not only the ability to rerun a metric. It is the ability to trace a reported value to a canonical population, a model output, a valid native path, a metric definition, and a passed validation state. This dissertation's canonical dataset layer, model-view separation, export contract, validation pipeline, and evidence register are designed to provide that chain.

## 2.6 Research Gap and Positioning of This Dissertation

The reviewed literature provides the main components needed to study explainable KG recommendation, but it leaves them distributed across separate research strands. KG representation methods exploit structured side information but may not expose complete reasoning paths [@wang2018ripplenet; @wang2021kgin; @lu2023vrkg4rec]. Native-path methods generate or score paths, but their graph views, search mechanisms, and outputs are model-specific [@xian2019pgpr; @xian2020cafe; @tai2021ucpr; @zhao2022tprec; @wang2022multilevelReasoning]. Explainability surveys and XRecSys provide taxonomies and path-quality dimensions, while benchmarking research establishes the importance of dataset and protocol control [@zhang2020explainableSurvey; @balloccu2022xrecsys; @balloccu2022xrecsysFramework; @shevchenko2024recsysBenchmarking; @markchom2026graphExplainableSurvey].

Within this reviewed corpus, no single work combines all of the following elements: canonical dataset truth, model-specific execution views, a common native-path export schema, validation before reporting, strict ranking evaluation, multiple non-interchangeable explanation properties, controlled accuracy–explainability analysis, and explicit boundary states for unsupported rows. This is a bounded literature synthesis, not a claim that no related framework exists outside the corpus. It also does not imply that the dissertation proposes a new recommender architecture.

| Theme | Representative sources | Dissertation use | Boundary |
| --- | --- | --- | --- |
| KG representation and propagation | RippleNet, KGIN, and VRKG4Rec [@wang2018ripplenet; @wang2021kgin; @lu2023vrkg4rec] | Motivates model-specific graph views within a canonical evaluation space. | A KG signal is not automatically an inspectable native path. |
| Native-path reasoning | PGPR, KPRN, CAFE, UCPR, TPRec, and multi-level reasoning [@xian2019pgpr; @wang2019kprn; @xian2020cafe; @tai2021ucpr; @zhao2022tprec; @wang2022multilevelReasoning] | Motivates a shared export and endpoint-validation contract. | Different path structures and search procedures remain model-specific. |
| Path-language modelling | KGGLM and PEARLM [@balloccu2024kgglm; @balloccu2023pearlm] | Extends the native-path comparison to language-model-style path generation or scoring. | Generated sequences require graph and recommendation alignment; PEARLM final venue and DOI remain a manual check. |
| Explainability and post-hoc methods | Explainable-recommendation surveys, InterpretML, and Captum [@zhang2020explainableSurvey; @nori2019interpretml; @kokhlikyan2020captum] | Supports an explicit distinction between native and post-hoc evidence. | A post-hoc path is not treated as evidence of the native recommendation mechanism. |
| Multidimensional path quality | XRecSys and its framework [@balloccu2022xrecsys; @balloccu2022xrecsysFramework] | Motivates separate LIR, SEP, and ETD reporting. | SEP remains a repository-specific bridge-entity score, not direct user-perceived serendipity. |
| Benchmarking and reproducibility | Recommender benchmarking and graph-explanation surveys [@shevchenko2024recsysBenchmarking; @markchom2026graphExplainableSurvey] | Motivates canonical populations, validation before reporting, and visible blocked states. | Validation status is not a performance ranking. |

**Table 2.1.** Literature synthesis and dissertation positioning.

The table summarises the bounded literature synthesis used to derive the framework requirements; it does not claim exhaustive coverage beyond the reviewed corpus.

The research gap is therefore evaluative and evidential. Heterogeneous native-path models cannot be compared reliably when identifiers, populations, paths, metrics, and validation criteria differ or remain implicit. Explanation quality cannot be reduced to the presence of a path, and ranking quality cannot be replaced by an explanation metric. A controlled analysis must retain the native evidence produced by each model while placing all reportable outputs under a common contract.

This dissertation addresses that gap through a canonical native-path evaluation and analysis framework. The framework separates canonical datasets from model-specific views, maps outputs back to shared identifiers, retains model-native recommendation paths, validates recommendation and explanation artifacts before scoring, and keeps strict accuracy, explanation-property sweeps, and ablation evidence in distinct roles. It evaluates LIR, SEP, and ETD as separate path properties and records blocked or not-applicable combinations as boundaries rather than model failures.

The resulting contribution is a method for auditable comparison and controlled trade-off analysis across heterogeneous native-path recommenders. The literature synthesis establishes five requirements for the next chapter: canonical dataset truth, model-specific execution views, native-path export semantics, validation before reporting, and explicit separation of ranking, explanation, and ablation evidence. Chapter 3 specifies and verifies that framework contract. Chapters 4 and 5 use the validated evidence to analyse ranking and explanation behaviour and to examine mechanism and coverage boundaries. Chapter 6 synthesises the supported conclusions and recommendations. This progression preserves the boundary established by the literature review: the dissertation contributes evaluation, validation, and analysis infrastructure, not a claim to a new recommender model or universal state-of-the-art performance.

# Chapter 3 Framework Implementation and Verification

## 3.1 Overview of the Implemented Framework

Chapter 2 showed that existing knowledge graph recommendation, path-reasoning, explainability, and benchmarking research supplies complementary methods and evaluation concepts without making heterogeneous native-path outputs automatically comparable. Fair comparison therefore requires more than applying the same ranking metrics to raw model outputs. The models can differ in graph schema, identifier space, search procedure, path format, and export behaviour, so an uncontrolled comparison can confound model performance with differences in data preparation and representation. This chapter addresses that comparability problem by describing the evaluation framework used in the later empirical chapters. The framework does not introduce a new recommender model; it provides a shared evaluation and verification contract for heterogeneous native-path recommenders.

The implemented architecture separates five concerns: canonical dataset truth, model-specific views, native-path export, validation gates, and metric reporting. Each concern resolves a distinct source of ambiguity. The canonical layer defines the shared evaluation population and labels. Model-specific views preserve the internal representations required by individual recommenders. Native exports retain the paths produced within the recommendation process. Validation determines whether those exports meet the common contract, and metric reporting keeps ranking and explanation evidence in their proper roles.

Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit. The framework dataflow expands that workflow from canonical dataset truth through native-path exports and validation to the separate Chapter 4 and Chapter 5 evidence roles; it describes an evaluation process rather than a new recommender architecture.

![](paper/current_dissertation/figures/png/figure_3_1_framework_overview_final.png)

**Figure 3.1.** Implemented canonical native-path evaluation framework. Canonical dataset truth and model-specific views feed the three-file native-path export contract; only rows passing the registered validation gate enter metric reporting. The diagram formalises evaluation and evidence eligibility rather than a new recommender architecture.

The workflow therefore begins from a canonical dataset layer containing shared user identifiers, item identifiers, interaction splits, labels, and knowledge-graph provenance. Individual models build the training views they require from this layer, but their outputs must return to canonical `uid` and `pid` space before evaluation. The validation layer then checks whether the recommendations and explanation paths are complete and internally consistent. Only rows that pass these checks are admitted as reportable experimental evidence.

This validation-first design makes evidence eligibility explicit. A model-dataset row can be complete, blocked, or not applicable. A blocked row is not evidence of poor recommendation performance; it means that the current repository does not support faithful scoring for that row. The framework thus defines both how supported results can be compared and where comparison must stop.

The notation used to formalise this evaluation contract is summarised below.

**Core notation used in the framework.**

- \(\mathcal{D}\): Set of datasets considered in the framework.
- \(d\): Dataset index.
- \(\mathcal{U}_d\): Canonical user set for dataset \(d\).
- \(\mathcal{I}_d\): Canonical item set for dataset \(d\).
- \(\mathcal{G}_d\): Knowledge graph associated with dataset \(d\).
- \(\mathcal{M}\): Set of native-path models evaluated in the main experiments.
- \(m\): Model index.
- \(\hat{R}_{u}^{K,m,d}\): Top-\(K\) recommendation list for user \(u\), model \(m\), dataset \(d\).
- \(p_{u,i}^{m,d}\): Native path associated with recommendation item \(i\) for user \(u\).
- \(V_{m,d}\): Validation eligibility indicator for model-dataset row \((m,d)\).
- \(q\): Explanation objective, one of LIR, SEP, or ETD.
- \(\alpha\): Trade-off control parameter.

These definitions formalise the evaluation framework. They do not define a new recommender model.

## 3.2 Canonical Dataset and Model View Construction

The first requirement for controlled comparison is a model-independent evaluation space. For each dataset, the canonical layer specifies users, products, train/validation/test interactions, evaluation labels, upstream knowledge-graph assets, and mapping requirements. This design is documented in `docs/guides/CANONICAL_DATASET_STANDARD.md` and provides the shared truth against which model exports are evaluated.

Canonicalisation does not require every recommender to consume an identical internal graph. Such a requirement would be incompatible with native-path models that depend on different relation vocabularies, entity-pruning strategies, compact identifiers, or path-search constraints. The framework instead standardises the comparison contract while allowing model-specific execution.

For a model-dataset row \((m,d) \in \mathcal{M} \times \mathcal{D}\), the canonical return mappings are

\[
\phi_U^{m,d}: \tilde{\mathcal{U}}_{m,d} \rightarrow \mathcal{U}_d
\]

and

\[
\phi_I^{m,d}: \tilde{\mathcal{I}}_{m,d} \rightarrow \mathcal{I}_d.
\]

Here, \(\tilde{\mathcal{U}}_{m,d}\) and \(\tilde{\mathcal{I}}_{m,d}\) denote model-specific internal user and item spaces. The mapping functions return every reportable artifact to canonical user and item identifiers. The framework standardises evaluation identifiers and outputs, not the internal representation spaces of heterogeneous models.

Model views are generated from the canonical layer for PGPR, UCPR, CAFE, hopwise, and RecBole-oriented workflows. External model papers establish the architectural context for PGPR, UCPR, CAFE, TPRec, and KGGLM, while PEARLM is cited through its verified arXiv record because final venue and DOI metadata remain unresolved [@xian2019pgpr; @tai2021ucpr; @xian2020cafe; @zhao2022tprec; @balloccu2024kgglm; @balloccu2023pearlm]. These views may remap identifiers internally, but the reported artifacts must return to canonical identifiers. In particular, exported `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` files must use canonical `uid` and `pid` values even when the training and inference code uses a different internal namespace. This rule separates legitimate implementation variation from variation that would make outputs incomparable.

The resulting dataset scope is also explicit. LastFM and ML-1M form the complete six-model native-path comparisons used for the main dissertation results. Amazon-Book KGAT remains a partial stress test and boundary case: KGGLM, PEARLM, and PGPR have complete rows, whereas UCPR, CAFE, and TPRec are blocked under the current evidence. Canonical construction therefore supports both the main comparison and the later analysis of incomplete coverage.

| Dataset | Role | Native-path rows | Metrics | Boundary |
| --- | --- | --- | --- | --- |
| LastFM | Main experiment | 6 complete | Strict accuracy; LIR/SEP/ETD sweeps | Complete six-model scope |
| ML-1M | Main experiment | 6 complete | Strict accuracy; LIR/SEP/ETD sweeps | Complete six-model scope |
| Amazon-Book KGAT | Secondary stress test | 3 PASS; 3 BLOCKED / N/A | Strict accuracy for PASS rows; sweeps N/A | Partial boundary case; no approved explanation sweeps |
| beauty_legacy_v1 | Historical / appendix | Historical only | Not in final status matrix | Not a current result row |

**Table 3.1.** Dataset scope and evidence role.

Source note: this table reproduces the registered dataset scope in `thesis_analysis_pack/dataset_summary_table.md`; validation status is an evidence-eligibility result, not a performance ranking.

| Model | Native-path role | Completed datasets | Explanation metrics | Boundary |
| --- | --- | --- | --- | --- |
| PGPR | RL/path reasoning baseline | LastFM, ML-1M, Amazon-Book KGAT | LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | LastFM/ML-1M complete; Amazon sweeps N/A |
| UCPR | User-centric path baseline | LastFM, ML-1M | LastFM/ML-1M; Amazon blocked | LastFM/ML-1M complete; Amazon blocked |
| CAFE | Coarse-to-fine path baseline | LastFM, ML-1M | LastFM/ML-1M; Amazon blocked | LastFM/ML-1M complete; Amazon blocked |
| TPRec | Temporal path baseline | LastFM, ML-1M | LastFM/ML-1M; Amazon blocked | LastFM/ML-1M complete; Amazon blocked by sentinel timestamps |
| KGGLM | Path-language-model baseline | LastFM, ML-1M, Amazon-Book KGAT | LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | LastFM/ML-1M complete; Amazon sweeps N/A |
| PEARLM | KG-constrained path-language baseline | LastFM, ML-1M, Amazon-Book KGAT | LastFM/ML-1M; Amazon LIR/SEP/ETD N/A | LastFM/ML-1M complete; Amazon sweeps N/A |

**Table 3.2.** Main-text native-path model scope.

Source note: this table reproduces `thesis_analysis_pack/model_scope_table.md`. Accuracy-only and component rows are not assigned native-path explanation metrics.

## 3.3 Native-Path Export Contract and Implementation

Comparable identifiers are necessary but insufficient when the explanation itself is part of the model evidence. The export contract therefore defines the minimum artifacts required for a complete native-path row:

- `uid_topk.csv`, containing ranked recommendation lists for canonical users;
- `pred_paths.csv`, containing candidate or selected recommendation paths;
- `uid_pid_explanation.csv`, containing the path used to explain each user-item recommendation.

| Artifact | Required content | Canonical requirement | Evaluation role |
| --- | --- | --- | --- |
| `uid_topk.csv` | Ranked recommendation lists for canonical users | Canonical `uid` and `pid` values | Strict ranking evaluation and recommendation alignment |
| `pred_paths.csv` | Candidate or selected recommendation paths | Canonical endpoints and registered relation/entity representation | Candidate-path and endpoint validation |
| `uid_pid_explanation.csv` | Path used to explain each user-item recommendation | Same canonical user-item pair as the recommendation export | Native-path explanation metrics and recommendation-explanation alignment |

**Table 3.3.** Canonical native-path export contract.

Formally, the ranked recommendation list is

\[
\hat{R}_{u}^{K,m,d}
=
[i_{u,1}, i_{u,2}, \ldots, i_{u,K}],
\quad
i_{u,j} \in \mathcal{I}_d.
\]

A native path associated with a reportable recommendation is represented as

\[
p_{u,i}^{m,d}
=
\left[
(r_0,t_0,e_0),
(r_1,t_1,e_1),
\ldots,
(r_L,t_L,e_L)
\right],
\]

subject to the endpoint conditions

\[
(r_0,t_0,e_0) = (\mathrm{self\_loop}, \mathrm{user}, u)
\]

and

\[
e_L = i.
\]

The corresponding validity predicate is

\[
\mathrm{ValidPath}(p_{u,i}^{m,d}) =
\mathbf{1}
\left[
e_0 = u
\land
e_L = i
\land
i \in \hat{R}_{u}^{K,m,d}
\right].
\]

A native path is reportable only when it is aligned with the same canonical user-item pair that appears in the recommendation export.

The minimum export evidence package for each row is

\[
\mathcal{E}_{m,d}
=
\left(
T_{m,d},
P_{m,d},
X_{m,d}
\right),
\]

where

\[
T_{m,d} = \texttt{uid\_topk.csv},
\quad
P_{m,d} = \texttt{pred\_paths.csv},
\quad
X_{m,d} = \texttt{uid\_pid\_explanation.csv}.
\]

The explanation export is the set

\[
X_{m,d}
=
\{(u,i,p_{u,i}^{m,d}) : u \in \mathcal{U}_{test}, i \in \hat{R}_{u}^{K,m,d}\}.
\]

The export contract is a minimum evidence contract. It does not require all models to share the same internal scoring architecture.

For non-path recommenders or accuracy-reference models, `uid_topk.csv` is sufficient for accuracy evaluation, but explanation metrics are not assigned. This boundary protects explanation fidelity. A post-hoc path recovered after recommendation is not treated as equivalent to a path produced by the model's recommendation mechanism, because the recovered path need not represent how the recommendation was generated.

The evaluation layer represents each path as a sequence of relation/entity-type/entity-id triples. In LastFM and ML-1M, the standard path starts from a user, traverses a seed interaction in that user's training history, passes through a knowledge-graph bridge entity, and ends at the recommended item. LIR, SEP, and ETD operate on properties of this structure, so preserving the native path and its canonical endpoints is essential to the meaning of the later metrics.

The single-example trace in the appendix material illustrates this alignment with abstract placeholders for a canonical user, seed item, bridge entity, and recommended item. It is a schematic dataflow aid rather than an experimental row, and it assigns no identifier, score, validation status, or performance value.

The contract is implemented through export and validation scripts rather than through a new model architecture. The registered validation evidence shows that LastFM and ML-1M satisfy the required export checks for all six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. These exports provide the model-faithful evidence on which Chapters 4 and 5 depend.

## 3.4 Evaluation and Validation Pipeline

The pipeline must determine not only how evidence is scored, but whether it is admissible. It therefore computes strict accuracy and explanation metrics from separate evidence sources and applies validation before either stream is interpreted.

Strict accuracy is computed from canonical labels and the recommendation export. The reported metrics are HR@10, NDCG@10, Precision@10, and Recall@10. Explanation metrics are computed from native paths through the xrecsys path-metric stack documented in `docs/guides/PATH_METRICS_GUIDE.md`. The dissertation cites XRecSys for the conceptual origin of recency, shared-entity scoring, and explanation-type diversity, while the exact evaluated LIR, SEP, and ETD formulas remain repository-specific [@balloccu2022xrecsys]. LIR measures whether the path is anchored in recent linked user interactions, and ETD measures the diversity of explanation path types across a user's recommendations. SEP is a repository-specific bridge-entity score. SEP follows the XRecSys-style explanation-metric setting but is interpreted here through the implemented repository metric pipeline. These dimensions remain separate because they describe different path properties rather than one generic explanation score.

Before reporting, the validation pipeline checks canonical test-user coverage, top-k coverage, duplicate recommendations, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate-path consistency, and score ranges. The current validation status table contains 15 passing export-validation rows and 3 blocked Amazon-Book KGAT rows. Passing status establishes conformity with the registered contract; blocked status prevents unsupported rows from entering the comparison.

| Validation gate | Check | Failure interpretation |
| --- | --- | --- |
| Coverage | Canonical test-user and top-k coverage are complete. | BLOCKED or PARTIAL evidence; not low recommendation performance. |
| Duplicates | Each top-k list contains unique recommended items. | Export-contract failure. |
| Seen-item leakage | Recommended items do not leak from the registered seen set. | Evaluation-integrity failure. |
| Canonical identifiers | Exported `uid` and `pid` values are consistent with canonical mappings. | Identifier-alignment failure. |
| Path endpoints | Each native path begins at the canonical user and terminates at the reported item. | Path-fidelity failure. |
| Recommendation-explanation alignment | Top-k and explanation rows refer to the same user-item pairs. | Artifact-alignment failure. |
| Candidate consistency | Selected explanations are consistent with the registered candidate paths. | Candidate-contract failure. |
| Score sanity | Registered scores fall within their expected ranges. | Metric or export validation failure. |

**Table 3.4.** Validation gates applied before comparative reporting. Validation status is not model performance.

These checks are represented by the binary validation gate

\[
V_{m,d}
=
G_{\mathrm{cov}}
\cdot
G_{\mathrm{dup}}
\cdot
G_{\mathrm{seen}}
\cdot
G_{\mathrm{end}}
\cdot
G_{\mathrm{align}}
\cdot
G_{\mathrm{cand}}
\cdot
G_{\mathrm{score}},
\quad
G_{\cdot} \in \{0,1\}.
\]

Only rows with \(V_{m,d}=1\) are eligible for main result reporting. Rows that fail or remain incomplete are treated as boundary evidence rather than performance evidence. This gate admits the twelve complete LastFM and ML-1M rows to the main comparison while retaining the incomplete Amazon-Book KGAT rows as a partial boundary case.

The validation-gate flowchart expands these checks as a reportability decision sequence. Its PASS and BLOCKED or PARTIAL terminals describe evidence eligibility and do not represent recommendation-performance levels.

Let \(R_u^+\) denote the relevant canonical test items for user \(u\). The strict ranking metrics are

\[
\mathrm{HR@K}
=
\frac{1}{\lvert \mathcal{U}_{test} \rvert}
\sum_{u \in \mathcal{U}_{test}}
\mathbf{1}
\left[
\hat{R}_{u}^{K,m,d}
\cap
R_u^+
\neq
\varnothing
\right],
\]

\[
\mathrm{Precision@K}
=
\frac{1}{\lvert \mathcal{U}_{test} \rvert}
\sum_{u \in \mathcal{U}_{test}}
\frac{
\lvert \hat{R}_{u}^{K,m,d} \cap R_u^+ \rvert
}{K},
\]

\[
\mathrm{Recall@K}
=
\frac{1}{\lvert \mathcal{U}_{test} \rvert}
\sum_{u \in \mathcal{U}_{test}}
\frac{
\lvert \hat{R}_{u}^{K,m,d} \cap R_u^+ \rvert
}{
\lvert R_u^+ \rvert
},
\]

\[
\mathrm{DCG@K}(u)
=
\sum_{j=1}^{K}
\frac{
\mathbf{1}[i_{u,j} \in R_u^+]
}{
\log_2(j+1)
},
\]

and

\[
\mathrm{NDCG@K}
=
\frac{1}{\lvert \mathcal{U}_{test} \rvert}
\sum_{u \in \mathcal{U}_{test}}
\frac{
\mathrm{DCG@K}(u)
}{
\mathrm{IDCG@K}(u)
}.
\]

Here, \(\mathrm{IDCG@K}(u)\) uses \(\min(K,\lvert R_u^+ \rvert)\) relevant gains, as required by the canonical evaluator. Short native-path lists preserve missing positions as non-hits rather than introducing non-path padding. These are strict accuracy metrics. They are reported separately from alpha-sweep paired ranking metrics.

For explanation scoring, the repository-specific path anchors are

\[
a(p_{u,i}) = e_1,
\quad
b(p_{u,i}) = e_{L-1},
\quad
\tau(p_{u,i}) = r_L.
\]

The function \(a(p_{u,i})\) denotes the linked historical seed item, \(b(p_{u,i})\) denotes the bridge entity, and \(\tau(p_{u,i})\) denotes the path type used for diversity. The metric-anchor schematic maps these three path positions to LIR, SEP, and ETD. It is a definition aid and preserves the repository-specific boundary of each metric. The corresponding path-level definitions are

\[
\mathrm{LIR}(p_{u,i})
=
\rho_u(a(p_{u,i})),
\quad
\rho_u(\cdot) \in [0,1],
\]

and

\[
\mathrm{SEP}(p_{u,i})
=
\sigma_d(b(p_{u,i})),
\quad
\sigma_d(\cdot) \in [0,1].
\]

In the repository implementation, \(a(p_{u,i})\) is the seed item at the path position used by the path-metric guide, and \(\rho_u\) is derived from the user's training interaction timestamps. The exact implementation is repository-specific. \(\sigma_d\) denotes the repository-specific bridge-entity score used by the implemented SEP metric. This dissertation treats SEP as an operational explanation-side metric following the XRecSys-style metric setting, rather than as an independently validated measure of user-perceived serendipity.

ETD is defined at user level as

\[
\mathrm{ETD}(u)
=
\frac{
\left\lvert
\left\{
\tau(p_{u,i}) : i \in \hat{R}_{u}^{K,m,d}
\right\}
\right\rvert
}{
\lvert \mathcal{T}_d \rvert
},
\]

where \(\mathcal{T}_d\) denotes the legal path-type set for dataset \(d\). ETD is user-level path-type diversity over the top-\(K\) explanation set.

For \(q \in \{\mathrm{LIR},\mathrm{SEP}\}\), user- and dataset-level aggregation are

\[
Q_{u,m,d}^{q}
=
\frac{1}{\lvert \hat{R}_{u}^{K,m,d} \rvert}
\sum_{i \in \hat{R}_{u}^{K,m,d}}
q(p_{u,i}^{m,d})
\]

and

\[
Q_{m,d}^{q}
=
\frac{1}{\lvert \mathcal{U}_{test} \rvert}
\sum_{u \in \mathcal{U}_{test}}
Q_{u,m,d}^{q}.
\]

For ETD, the user-level quantity is the diversity ratio defined above rather than a simple average of path-level scores. These definitions follow the validated path alignment contract; the exact missing-anchor and normalisation behaviour remains governed by the repository implementation.

The pipeline also separates strict accuracy from alpha-sweep trade-off evidence. The strict values used in this draft are currently traceable to `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`. The twelve expected row-level primary accuracy JSON files are not accessible in the current worktree and must not be described as directly inspected. Alpha-sweep values come from trade-off CSVs in which an alpha parameter varies the recommendation objective. The former describe validated ranking outputs, while the latter describe response trajectories under an explanation-oriented control. Alpha-sweep values are therefore not substitutes for strict accuracy results.

Figure 3.2 summarises this design by showing how the alpha sweep generates metric-specific trade-off evidence after the baseline and evaluation contract have been established. The separation of sources ensures that later chapters can state exactly whether a claim concerns strict performance, sweep behaviour, or ablation.

![](paper/current_dissertation/figures/png/figure_3_2_alpha_sweep_design_final.png)

**Figure 3.2.** Alpha-sweep experiment design and evidence separation. Strict accuracy is traceable to the accessible canonical status matrix and matching final summary, while objective-specific alpha sweeps and PGPR/UCPR ablation form separate evidence streams. Sweep ranking metrics must not be interpreted as strict HR@10, NDCG@10, Precision@10, or Recall@10.

![](paper/current_dissertation/figures/png/figure_3_3_validation_gate_flow_final.png)

**Figure 3.3.** Validation gate for a model-dataset export package. This flowchart shows validation eligibility, not recommendation performance. BLOCKED or PARTIAL status must not be interpreted as a low-performing model result.

## 3.5 Framework Verification Results

Verification tests whether the implemented contract can support the intended comparison and identify cases in which it cannot. For the two main datasets, the result is complete: LastFM passes validation for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM, and ML-1M passes for the same six models. These rows establish the empirical basis for the strict accuracy and trade-off analysis in Chapter 4.

Amazon-Book KGAT demonstrates the other function of verification. KGGLM, PEARLM, and PGPR pass validation, whereas UCPR, CAFE, and TPRec are blocked or not applicable under the current evidence. The blocked rows record implementation and data-contract limitations, not measured recommendation quality. By distinguishing these statuses before comparison, the framework prevents absent or unsupported results from being interpreted as model outcomes.

The strict accuracy snapshot follows the same boundary. LastFM and ML-1M contain complete strict accuracy values for all six native-path models. Amazon-Book KGAT contains strict values only for the three complete rows and has no valid explanation alpha sweeps in the current evidence pack. It can therefore support a partial boundary analysis, but not a complete six-model trade-off experiment.

Representative endpoints additionally verify that the trade-off pipeline operates on the two complete datasets. LastFM PGPR LIR moves from 0.006 at alpha=0.00 to 0.022 at alpha=1.00, while ML-1M PGPR LIR moves from 0.466 to 0.963. At this stage, these values confirm computation and export continuity. Their interpretation as model behaviour belongs to Chapters 4 and 5.

## 3.6 Trade-off and Ablation Experiment Setup

With the evidence contract verified, the next question is whether supported models exhibit common or heterogeneous relationships between ranking utility and explanation properties. The trade-off experiments address this question on LastFM and ML-1M using the six native-path models that pass validation on both datasets. Recommendation exports are evaluated at top-k 10, and strict ranking is reported through HR@10, NDCG@10, Precision@10, and Recall@10. The same canonical user, item, label, export, and validation contract is applied across models, while model-native training and inference remain heterogeneous.

The framework standardises the evaluation contract, exported artifacts, validation gates, and metric computation. It does not claim that heterogeneous models share identical internal hyperparameter spaces. PGPR, UCPR, and CAFE are represented by registered canonical exports and implementation-log provenance, whereas the accessible TPRec, KGGLM, and PEARLM pipeline scripts declare more of their stage, architecture, and inference configuration directly. The generated historical run tree and checkpoint files are not present in the current evidence package, so exact checkpoint identities and several model-native optimiser settings cannot be re-inspected. Detailed model-native hyperparameters are retained in their respective configuration or execution sources where available; parameters not accessible in the current evidence package are not reconstructed or inferred.

| Configuration item | Setting | Evidence tag | Boundary |
| --- | --- | --- | --- |
| Main datasets and models | LastFM and ML-1M; six validated native-path models on each dataset | canonical status matrix | Amazon-Book KGAT is a partial boundary case, not a third complete main experiment. |
| Model-native training and inference | Heterogeneous model-specific pipelines; directly available settings are recorded in the evidence provenance record | provenance record | The framework does not impose or imply one shared hyperparameter space. |
| Canonical recommendation cut-off | Top-k 10 | validation scripts | Short native-path lists may remain short; non-path recommendations are not used for padding. |
| Strict ranking evaluation | HR@10, NDCG@10, Precision@10, and Recall@10 | canonical status matrix | The twelve expected primary row-level accuracy JSON files are unavailable. |
| Explanation objectives | Separate LIR-, SEP-, and ETD-oriented sweeps | sweep runner | The exact metric implementation and data assumptions remain repository-specific. |
| Alpha grid | 0.00 to 1.00 inclusive at 0.05 intervals, yielding 21 points | sweep validator | Paired sweep ranking metrics are not substitutes for strict accuracy. |
| Validation gate | Exact canonical test-user coverage, unique top-k items, leakage checks, endpoint checks, candidate consistency, and explanation alignment | validation scripts | PASS establishes conformity with the registered contract rather than universal correctness. |
| Random seeds and exact checkpoint identities | Not available in the current evidence package for the complete six-model set | provenance record | Missing values are not inferred from framework or library defaults. |
| PGPR/UCPR ablation | Frozen original top-k item set with exact alpha=0.00 preservation and a declared NDCG-retention analysis | ablation folder | Separate from both the six-model sweep and strict final accuracy. |

**Table 3.5.** Experiment configuration and provenance boundary.

The main alpha-sweep protocol evaluates a baseline and then runs separate LIR-, SEP-, and ETD-oriented objectives. Each objective uses 21 alpha values from 0.00 to 1.00 inclusive in steps of 0.05. The required outputs include paired NDCG, HR, Recall, and Precision together with LIR, SEP, and ETD. This metric-specific organisation is necessary because LIR concerns interaction recency, SEP concerns the implemented repository-specific bridge-entity score, and ETD concerns explanation-type diversity. Movement in one dimension cannot be interpreted as equivalent movement in another, and none of the three is treated as a complete explanation-quality score. The paired ranking metrics generated inside these sweeps remain separate from the strict-accuracy evidence stream.

The sweep output for objective \(q\) is represented abstractly as

\[
\hat{R}_{u,\alpha}^{K,m,d,q}
=
\operatorname{TopK}
\left(
S_{\alpha}^{m,d,q}(u,i,p)
\right),
\]

where

\[
\alpha \in [0,1],
\quad
q \in \{\mathrm{LIR}, \mathrm{SEP}, \mathrm{ETD}\}.
\]

\(S_{\alpha}^{m,d,q}\) denotes the sweep scoring function used to generate a top-\(K\) list under explanation objective \(q\). Unless a linear score-combination rule is directly verified from implementation files, this dissertation treats \(S_{\alpha}^{m,d,q}\) as an implementation-specific sweep score. The implementation directly verifies linear candidate-score weighting for the LIR and SEP optimisers, but the ETD optimiser uses path-type bins and an unseen-type bonus. Because one linear score-combination rule does not cover all three registered objectives, this dissertation does not introduce a universal linear formula.

The evidence streams used by the later chapters are separated as follows.

| Evidence stream | Used for | Status | Not used for |
| --- | --- | --- | --- |
| Strict accuracy | Main LastFM and ML-1M HR@10, NDCG@10, Precision@10, and Recall@10 comparison | Two summaries match; 0/12 primary row JSON accessible | Claiming that primary JSON files were inspected; replacing alpha-sweep trajectories |
| Explanation endpoints | LIR, SEP, and ETD endpoint response | Available for complete LastFM/ML-1M scope | Strict accuracy reporting; user-perceived explanation quality |
| Alpha-sweep curves | Paired ranking and explanation-property response over the registered alpha grid | Three objective-specific 21-point sweeps available | Strict model ranking; causal mechanism; statistical inference |
| PGPR/UCPR ablation | Alpha-zero preservation and bounded controllability under the 95% NDCG-retention protocol | Registered PGPR/UCPR evidence only | Six-model superiority; mechanism claims for CAFE, TPRec, KGGLM, or PEARLM |
| Amazon readiness and validation | Boundary-case and reportability analysis | 3 PASS; 3 BLOCKED / N/A; no approved sweeps | Complete third-dataset comparison; ranking blocked rows |
| Model-native configuration | Document settings that can be directly inspected | Incomplete across the six-model scope | Inferring absent values from defaults or transferring settings across datasets |
| Reproducibility identifiers | Register known output identities and accessible hashes | Checkpoint hashes, seeds, and settings incomplete | Claiming complete run-level reproducibility |

**Table 3.6.** Evidence streams and interpretation boundaries.

The evidence-stream separation diagram visualises these five roles. It is intentionally separate from the alpha-sweep process diagram so that strict accuracy, explanation endpoints, main sweeps, PGPR/UCPR ablation, and boundary validation cannot be read as interchangeable measurements.

The configuration and provenance boundary is summarised below. The detailed model-by-dataset audit is retained in `EXPERIMENT_CONFIGURATION_PROVENANCE.md` for later appendix use.



The ablation experiments therefore form a separate evidence stream. The PGPR/UCPR path-module evidence is stored under `reports/tables/ablation/pgpr_ucpr_path_module/` and `reports/figures/ablation/pgpr_ucpr_path_module/`. Chapter 5 uses these files to examine bounded controllability and mechanism-level effects; they do not replace the six-model trade-off comparison or supply mechanism evidence for CAFE, TPRec, KGGLM, or PEARLM.

Chapter 4 uses the verified strict accuracy, explanation endpoint, and alpha-sweep evidence to report empirical patterns and result-level findings. Chapter 5 then asks which observations can be strengthened by the registered ablation, which mechanism interpretations remain descriptive, and where dataset coverage reaches a boundary. Chapter 6 synthesises those findings without introducing new experimental results.

# Chapter 4 Accuracy–Explainability Trade-off Results

## 4.1 Experimental Scope and Result Organisation

Chapter 3 established which native-path outputs satisfy the common export and validation contract. This chapter uses that admissible evidence to test whether validated native-path recommenders exhibit a universal accuracy leader or a common explanation response. The evidence covers the two complete main datasets, LastFM and ML-1M, and the six implementations that pass the Chapter 3 validation gates on both datasets: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. This chapter reports empirical results and result-level interpretation. Mechanism-level causal explanation is reserved for Chapter 5.

Two evidence streams remain separate throughout the analysis. Strict accuracy results come from the accessible canonical status matrix and the exactly matching final accuracy summary presented in Table 4.1; the twelve expected row-level primary JSON files remain unavailable. Alpha-sweep results come from the canonical trade-off CSVs and describe changes in LIR, SEP, ETD, and their paired sweep ranking metrics as alpha varies. Alpha-sweep ranking values are not used as substitutes for strict accuracy. All explanation results concern paths produced natively within the recommendation workflow; the main comparison contains no post-hoc explanations.

Amazon-Book KGAT is excluded because the current evidence does not contain a complete six-model alpha-sweep result set. Chapter 5 treats it only as a partial boundary case. The present chapter first establishes the strict accuracy pattern, then examines explanation endpoints and metric-specific trade-offs, and finally compares the resulting profiles across datasets. Ablation and mechanism-level interpretation remain separate and are deferred to Chapter 5. This chapter does not claim statistical significance, user-perceived usefulness, causal mechanism, or universal model superiority.

The alpha-sweep process diagram shows how objective-specific endpoint movement and paired sweep NDCG movement are carried into the result-level analysis. It does not define a universal score function, and its sweep NDCG must not be interpreted as strict NDCG@10.

For an explanation objective \(q\), endpoint movement is summarised by

\[
\Delta q_{m,d}
=
Q_{m,d}^{q}(\alpha=1.00)
-
Q_{m,d}^{q}(\alpha=0.00)
\]

and

\[
\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}
=
\mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}(\alpha=1.00)
-
\mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}(\alpha=0.00).
\]

A positive \(\Delta q\) with negative \(\Delta \mathrm{NDCG}^{\mathrm{sweep}}\) indicates an empirical trade-off under the selected sweep objective. This does not replace strict NDCG@10. The deltas are descriptive endpoint differences, not statistical estimates or tests.

## 4.2 Strict Accuracy Results

The strict results do not identify a universal winner across datasets and metrics. Table 4.1 reports HR@10, NDCG@10, Precision@10, and Recall@10, while Figure 4.1 visualises NDCG@10 for LastFM and ML-1M. This section uses no alpha-sweep evidence.

| Dataset | Model | HR@10 | NDCG@10 | Precision@10 | Recall@10 |
| --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | 0.186 | 0.031 | 0.025 | 0.018 |
| LastFM | UCPR | 0.216 | 0.037 | 0.031 | 0.023 |
| LastFM | CAFE | 0.180 | 0.030 | 0.026 | 0.019 |
| LastFM | TPRec | 0.189 | 0.039 | 0.033 | 0.022 |
| LastFM | KGGLM | 0.126 | 0.021 | 0.016 | 0.014 |
| LastFM | PEARLM | 0.100 | 0.016 | 0.013 | 0.009 |
| ML-1M | PGPR | 0.511 | 0.102 | 0.093 | 0.042 |
| ML-1M | UCPR | 0.442 | 0.086 | 0.066 | 0.038 |
| ML-1M | CAFE | 0.554 | 0.117 | 0.107 | 0.052 |
| ML-1M | TPRec | 0.475 | 0.094 | 0.090 | 0.044 |
| ML-1M | KGGLM | 0.169 | 0.034 | 0.019 | 0.011 |
| ML-1M | PEARLM | 0.215 | 0.035 | 0.027 | 0.011 |

**Table 4.1.** Strict accuracy on LastFM and ML-1M. Values are rounded for main-text readability; full precision remains in the registered evidence files.

![](paper/current_dissertation/figures/png/figure_4_1_strict_ndcg_comparison_final.png)

**Figure 4.1.** Strict NDCG@10 comparison. This figure belongs to the strict accuracy evidence stream and should not be confused with sweep NDCG from the alpha-sweep analysis. Values are traceable to the accessible canonical status matrix and matching dissertation summary; the expected primary row-level JSON artifacts are not accessible.

LastFM divides leadership between two models. UCPR records the highest HR@10 at 0.216 and the highest Recall@10 at 0.023. TPRec records the highest NDCG@10 at 0.039 and the highest Precision@10 at 0.033. PGPR, CAFE, KGGLM, and PEARLM are lower than these metric-specific leaders on all four measures. The result is therefore a metric-dependent ordering rather than a single LastFM leader.

ML-1M produces a different pattern. CAFE leads all four strict metrics, with HR@10 of 0.554, NDCG@10 of 0.117, Precision@10 of 0.107, and Recall@10 of 0.052. PGPR is second on HR@10 and NDCG@10, while TPRec is second on Precision@10 and Recall@10. The leading identity thus changes from the split UCPR and TPRec result on LastFM to CAFE on ML-1M. Any assessment of model performance must consequently remain conditional on dataset and metric.

The result-level finding is that there is no universal strict-accuracy winner. Leadership depends first on dataset and then, on LastFM, on the ranking metric being considered. This prevents a single strict ranking from being carried unchanged into the explanation analysis. It also means that a model's strict position cannot be used to predict how far its native paths will move under LIR-, SEP-, or ETD-oriented control: strict accuracy and explanation controllability are different observed properties.

This conclusion applies only to the registered strict evidence stream. The paired NDCG values reported later are generated inside individual alpha sweeps and characterise those trajectories; they are not alternative measurements of the strict NDCG@10 values in Table 4.1. Keeping the two sources separate is necessary even when their metric names appear similar.

## 4.3 Explanation Metric Endpoint Results

The next question is whether explanation behaviour can be reduced to a single dimension or common response pattern. Table 4.2 and Figure 4.2 report alpha=0.00 and alpha=1.00 endpoints from the NDCG alpha-sweep summaries for three distinct properties. LIR measures the recency of the linked historical interaction used by a path, and ETD measures diversity among explanation path types. SEP is a repository-specific bridge-entity score. SEP follows the XRecSys-style explanation-metric setting but is interpreted here through the implemented repository metric pipeline. Movement in one dimension does not establish overall explanation superiority.

| Dataset | Model | LIR | SEP | ETD |
| --- | --- | --- | --- | --- |
| LastFM | PGPR | 0.006 → 0.022 | 0.569 → 0.988 | 0.140 → 0.355 |
| LastFM | UCPR | 0.005 → 0.012 | 0.517 → 0.934 | 0.120 → 0.186 |
| LastFM | CAFE | 0.001 → 0.004 | 0.731 → 0.989 | 0.231 → 0.373 |
| LastFM | TPRec | 0.006 → 0.011 | 0.550 → 0.913 | 0.177 → 0.398 |
| LastFM | KGGLM | 0.001 → 0.001 | 0.696 → 0.719 | 0.127 → 0.129 |
| LastFM | PEARLM | 0.001 → 0.001 | 0.527 → 0.611 | 0.111 → 0.112 |
| ML-1M | PGPR | 0.466 → 0.963 | 0.480 → 0.983 | 0.161 → 0.519 |
| ML-1M | UCPR | 0.457 → 0.734 | 0.494 → 0.741 | 0.209 → 0.256 |
| ML-1M | CAFE | 0.395 → 0.699 | 0.462 → 0.979 | 0.290 → 0.854 |
| ML-1M | TPRec | 0.450 → 0.945 | 0.495 → 0.970 | 0.287 → 0.730 |
| ML-1M | KGGLM | 0.316 → 0.316 | 0.479 → 0.479 | 0.095 → 0.095 |
| ML-1M | PEARLM | 0.423 → 0.427 | 0.509 → 0.527 | 0.098 → 0.099 |

**Table 4.2.** Explanation-metric endpoints from alpha=0.00 to alpha=1.00.

![](paper/current_dissertation/figures/png/figure_4_2_explanation_endpoint_summary_final.png)

**Figure 4.2.** LIR, SEP, and ETD endpoints at alpha=0.00 and alpha=1.00 for validated LastFM and ML-1M rows. Panel scales are metric-specific and should not be compared as a shared y-axis scale. SEP denotes the implemented repository-specific bridge-entity score. These endpoints are alpha-sweep evidence and do not establish strict accuracy or user-perceived explanation quality.

On LastFM, PGPR shows the largest LIR endpoint movement, from 0.006 to 0.022. SEP increases for all six models, reaching alpha=1.00 values from 0.611 for PEARLM to 0.989 for CAFE. ETD responses are more varied: TPRec has the largest movement, while PGPR and CAFE also move visibly and KGGLM and PEARLM change only slightly. Table 4.2 retains the complete endpoint set.

ML-1M yields both larger movements and a different ordering in several cases. PGPR and TPRec show large LIR responses, and PGPR, CAFE, and TPRec all approach the upper end of the SEP scale at alpha=1.00. CAFE records the largest ETD movement, from 0.290 to 0.854, followed by visible TPRec and PGPR changes. KGGLM has identical alpha=0.00 and alpha=1.00 values for all three metrics, and PEARLM changes only slightly. Explanation-objective controllability is therefore conditional on metric, model, and dataset rather than captured by one endpoint ranking.

The endpoints establish that LIR, SEP, and ETD are non-interchangeable. A model can move strongly on one dimension and moderately or minimally on another, so an endpoint increase cannot be converted into a claim of global explanation superiority. The same restriction applies to flat or restricted responses. Such profiles are informative because they show that the registered sweep exposes little movement for that model-objective-dataset combination; they do not show that the model has poor explanations or reveal why the response is restricted.

These endpoint values are alpha-sweep results rather than strict accuracy results. They describe computational properties of validated native paths, not user-perceived explanation quality. Their conceptual dimensions follow XRecSys, while the exact LIR, SEP, and ETD computations and data assumptions evaluated here remain repository-specific.

## 4.4 LIR-oriented Trade-off Results

The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.3 plots LIR against the NDCG sweep metric for both datasets. These NDCG values belong to the alpha-sweep evidence stream and are distinct from the strict NDCG@10 results in Section 4.2.

![](paper/current_dissertation/figures/png/figure_4_3_lir_tradeoff_final.png)

**Figure 4.3.** LIR-oriented trade-off curves for (a) LastFM and (b) ML-1M. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent.

LastFM separates a costly LIR response from more strongly preserved or limited responses. PGPR increases LIR from 0.006 to 0.022 while sweep NDCG changes from 0.113 to 0.068. UCPR increases LIR from 0.005 to 0.012 with a much smaller NDCG change, from 0.126 to 0.123. CAFE and TPRec also increase LIR, whereas KGGLM and PEARLM show only small movement and essentially unchanged sweep NDCG endpoints. Figure 4.3 retains the complete trajectories.

The ML-1M profiles differ in both scale and ranking cost. PGPR moves from 0.466 to 0.963 in LIR while NDCG changes from 0.102 to 0.062. UCPR again preserves more of the paired ranking metric, moving from 0.457 to 0.734 in LIR and from 0.086 to 0.083 in NDCG. TPRec and CAFE show substantial LIR movement with larger paired ranking changes than UCPR, while KGGLM is unchanged and PEARLM moves only slightly. The curves establish distinct LIR trade-off profiles without selecting a universal operating point.

Viewed as curves rather than endpoints alone, the LIR results expose three empirical response types. PGPR combines a large LIR gain with a visible paired-NDCG cost at the upper part of the sweep. UCPR provides the contrasting profile of a moderate LIR gain with stronger preservation of paired NDCG. KGGLM and PEARLM show flat or restricted movement, while CAFE and TPRec occupy intermediate profiles whose movement and ranking cost vary by dataset.

The observed profiles also show that LIR response is dataset-dependent. The scale and ordering of movement on ML-1M do not reproduce the LastFM profiles, even though the evaluation contract and alpha grid are shared. At the result level, this indicates that recency-oriented control cannot be summarised by one model ordering or one expected cost. It does not by itself establish a causal mechanism; Chapter 5 considers which interpretations are supported by ablation and which remain descriptive.

In the notation above, these profiles compare \(\Delta \mathrm{LIR}_{m,d}\) with \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{LIR}}\). The notation records the direction and magnitude already shown by the registered endpoints; it does not add a new result or infer a mechanism.

## 4.5 SEP-oriented Trade-off Results

SEP asks a different question: how does ranking change when paths assigned larger values under the implemented repository-specific bridge-entity score are favoured? It records the response of that operational explanation-side score rather than interaction recency or path-type diversity. Figure 4.4 presents the canonical SEP-NDCG trajectories as a main-text Chapter 4 figure because they provide a visually clear example of implemented objective movement under the alpha-sweep design.

![](paper/current_dissertation/figures/png/figure_4_4_sep_tradeoff_final.png)

**Figure 4.4.** SEP-oriented trade-off curves under the implemented repository-specific SEP objective. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent. The SEP axis reflects movement along the implemented repository-specific SEP score, not independently validated user-perceived serendipity.

On LastFM, PGPR increases SEP from 0.569 to 0.988 while sweep NDCG changes from 0.113 to 0.068. UCPR reaches SEP 0.934 from 0.517 while NDCG changes only from 0.126 to 0.124. CAFE and TPRec also reach high SEP endpoints, whereas KGGLM and PEARLM show smaller movement. The contrast shows that similar directional SEP gains can carry different paired ranking costs.

On ML-1M, PGPR, CAFE, and TPRec again reach high alpha=1.00 SEP values but incur different NDCG changes. UCPR increases SEP from 0.494 to 0.741 while NDCG changes only from 0.086 to 0.083. KGGLM remains unchanged on both measures, and PEARLM records a small SEP increase with nearly unchanged NDCG. Figure 4.4 retains the complete trajectories.

The SEP-oriented sweep provides one of the clearest empirical trade-off profiles in the alpha-sweep results. Several models move substantially along the implemented SEP objective, while paired sweep NDCG changes at model- and dataset-dependent rates. This makes SEP useful for analysing framework controllability under an explanation-side objective, while the flatter KGGLM and PEARLM profiles retain the contrasting evidence of restricted movement.

SEP remains a repository-specific bridge-entity score interpreted through the implemented metric pipeline. Movement in \(\Delta \mathrm{SEP}_{m,d}\) and its paired \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{SEP}}\) is descriptive evidence of objective response, not statistical inference or causal mechanism evidence. It is not direct evidence of user-perceived serendipity, surprise, novelty, usefulness, or explanation quality.

## 4.6 ETD-oriented Trade-off Results

ETD adds a third perspective by measuring the diversity of explanation path types within a user's recommendation list. Its sweep tests whether this diversity can increase while the paired ranking metric is preserved. Figure 4.5 identifies the existing dataset-specific ETD-NDCG views supporting the section.

![](paper/current_dissertation/figures/png/figure_4_5_etd_tradeoff_final.png)

**Figure 4.5.** ETD-oriented trade-off curves for (a) LastFM and (b) ML-1M. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent. The figure records path-type diversity under the registered taxonomy; ETD is not a complete explanation-quality measure.

On LastFM, TPRec has the largest ETD endpoint increase, from 0.177 to 0.398, while its sweep NDCG changes from 0.118 to 0.114. PGPR and CAFE also increase ETD with comparatively limited paired NDCG changes. UCPR has a smaller increase, and KGGLM and PEARLM show minimal endpoint movement. The profile differs from both LIR and SEP, confirming that path-type diversity adds separate information.

ML-1M again changes the scale and ordering. CAFE records the largest ETD movement, from 0.290 to 0.854, while its sweep NDCG changes from 0.112 to 0.086. TPRec and PGPR also move substantially. UCPR increases ETD from 0.209 to 0.256 with a smaller NDCG change from 0.101 to 0.099, while KGGLM remains unchanged and PEARLM changes only slightly. Figure 4.5 retains the complete trajectories. These results establish differences in ETD controllability; they do not by themselves establish the mechanism causing those differences.

ETD therefore behaves differently from LIR and SEP. Increasing path-type diversity does not reproduce an identical paired-ranking-cost pattern, and the largest mover changes from TPRec on LastFM to CAFE on ML-1M. Some profiles show substantial diversity movement with limited paired-NDCG change, while others show a larger cost or almost no movement. This makes ETD a separate control dimension rather than a substitute for recency or the implemented SEP objective.

Movement in ETD is also narrower than a claim about overall explanation quality. It establishes that more path types are represented under the declared taxonomy and denominator; it does not establish that the resulting paths are more understandable, useful, or persuasive. Chapter 5 uses the registered PGPR/UCPR ablation to strengthen only the mechanism claims that the ablation can support and keeps the remaining model explanations descriptive.

The ETD trajectories are therefore summarised by \(\Delta \mathrm{ETD}_{m,d}\) together with \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{ETD}}\). As in the LIR and SEP sections, this notation formalises an observed endpoint trade-off without creating an efficiency ratio, significance claim, or causal conclusion.

## 4.7 Cross-Dataset Comparison

Across the two evidence streams, the central empirical result is heterogeneity rather than universal dominance. Strict accuracy leadership changes by dataset and metric: UCPR and TPRec lead different measures on LastFM, while CAFE leads all four measures on ML-1M. Explanation endpoints likewise do not yield one model ordering across LIR, SEP, and ETD, and the paired NDCG response differs across models.

The datasets also change the scale and pattern of movement. PGPR, UCPR, CAFE, and TPRec generally show larger absolute LIR changes on ML-1M than on LastFM. CAFE, TPRec, and PGPR have substantial ETD movement on ML-1M, but their ordering and magnitude differ on LastFM. KGGLM and PEARLM provide contrasting cases with limited movement in several sweeps. A model's trade-off profile is thus conditional on both the dataset and the explanation property being controlled.

No single model dominates all strict accuracy measures, explanation dimensions, and datasets. The common native-path contract instead reveals multiple trade-off profiles whose evidence roles must remain distinct. Comparative curves alone, however, cannot establish why those profiles differ. Chapter 5 therefore examines the registered PGPR and UCPR ablation, uses model mechanisms only as cautious interpretive context, and treats Amazon-Book KGAT separately as a coverage boundary.

The empirical trade-off pattern schematic groups the already reported profiles as flat or stable, efficient movement, restricted costly, or high-gain high-cost. These labels summarise descriptive pattern types only; they do not create a new metric, assign statistical significance, or establish mechanism.

The empirical findings can be summarised without converting the observed associations into mechanism claims:

| Pattern | Evidence | Interpretation | Boundary |
| --- | --- | --- | --- |
| No universal strict-accuracy winner | UCPR and TPRec lead different LastFM metrics; CAFE leads all four ML-1M metrics. | Accuracy leadership depends on dataset and metric. | Primary row JSON unavailable; no significance artifact. |
| Accuracy and explanation movement differ | Strict leaders differ from models showing the largest LIR, SEP, or ETD movement. | Strict rank does not predict explanation controllability. | Sweep endpoints are not strict accuracy. |
| Shared objectives have different paired costs | PGPR and UCPR retain different paired NDCG trajectories under shared LIR/SEP objectives. | A shared objective can impose different utility costs. | Descriptive only; no significance or causal evidence. |
| Metric orderings differ | Largest movements differ across LIR, SEP, and ETD; examples include PGPR, TPRec, and CAFE. | The metrics expose non-interchangeable path properties. | Metric scales differ; no endpoint proves overall explanation superiority. |
| Flat profiles remain informative | KGGLM and PEARLM show identical or small endpoint movement in several registered sweeps. | The available control produces limited movement in those rows. | A flat profile does not identify cause or explanation quality. |
| Profiles are dataset-dependent | Movement scale, ordering, and paired cost differ between LastFM and ML-1M. | One dataset's profile is not a universal model property. | Only two datasets have complete six-model trade-off evidence. |
| Mechanism claims need stronger evidence | PGPR/UCPR have registered ablation; other model mechanisms have descriptive context only. | Chapter 4 findings motivate but do not replace mechanism analysis. | Stronger statements are limited to the registered ablation scope. |

**Table 4.3.** Cross-dataset empirical patterns and evidence limits.

This summary closes the result-level analysis. It identifies what the validated outputs show while leaving causal attribution, ablation-supported controllability, and dataset-boundary interpretation to Chapter 5.

# Chapter 5 Ablation, Mechanism Analysis, and Boundary Cases

## 5.1 Ablation Analysis of Framework Controllability

Chapter 4 established heterogeneous trade-off profiles, but comparative curves alone cannot show whether an explanation-oriented control begins from the registered baseline or can satisfy an explicit ranking-utility condition. The ablation addresses that narrower question. It tests framework controllability for PGPR and UCPR; it is not designed to show that either model becomes a stronger recommender after modification. Its evidence remains separate from the strict six-model accuracy results and the main alpha sweeps in Chapter 4.

The ablation evidence-flow diagram makes this scope explicit: interpretation proceeds only after alpha-zero baseline preservation, an objective-specific ablation sweep, and paired NDCG-retention assessment. The flow does not extend the evidence to the other four models.

The experiment uses a strict baseline-preserving canonical alpha sweep over the frozen original top-k item set. PGPR is the main ablation model and UCPR is an auxiliary replication. On both LastFM and ML-1M, the alpha=0.00 checks pass for LIR, SEP, and ETD. The exported top-k rankings and explanation pairs are preserved exactly, with a maximum metric difference of 0.0 from the original result. The control mechanism therefore begins from the registered baseline rather than a separately reconstructed ranking.

Baseline preservation is formalised as

\[
D_{\mathrm{base}}
=
\max_{u}
\mathbf{1}
\left[
\hat{R}_{u,\alpha=0.00}^{K,\mathrm{abl}}
\neq
\hat{R}_{u}^{K,\mathrm{base}}
\right].
\]

When \(D_{\mathrm{base}}=0\), the ablation sweep preserves the alpha-zero baseline recommendation list under the tested condition.

The second test selects the maximum explanation gain subject to NDCG retention greater than or equal to 95%. All twelve dataset-model-objective combinations in Table 5.1 have an operating point satisfying this rule. The selected alpha varies with the objective: some settings choose alpha=1.00; PGPR SEP chooses 0.75 on LastFM and 0.95 on ML-1M; and intermediate settings also occur for ML-1M PGPR LIR and ML-1M UCPR SEP. This variation is the relevant controllability result because the operating point follows the joint response of the explanation objective and NDCG rather than a fixed endpoint.

| Dataset | Model | Objective | Selected alpha | NDCG retention (%) | Explanation gain (%) |
| --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 1.00 | 99.94 | 502.17 |
| LastFM | PGPR | SEP | 0.75 | 95.13 | 35.06 |
| LastFM | PGPR | ETD | 1.00 | 98.86 | 3.47 |
| LastFM | UCPR | LIR | 1.00 | 99.96 | 124.76 |
| LastFM | UCPR | SEP | 0.90 | 101.10 | 41.10 |
| LastFM | UCPR | ETD | 1.00 | 99.90 | 17.41 |
| ML-1M | PGPR | LIR | 0.55 | 99.08 | 56.31 |
| ML-1M | PGPR | SEP | 0.95 | 95.10 | 47.71 |
| ML-1M | PGPR | ETD | 1.00 | 99.38 | 15.27 |
| ML-1M | UCPR | LIR | 1.00 | 97.17 | 44.49 |
| ML-1M | UCPR | SEP | 0.75 | 96.93 | 33.39 |
| ML-1M | UCPR | ETD | 1.00 | 98.66 | 5.91 |

**Table 5.1.** PGPR/UCPR operating points under the 95% NDCG-retention rule. All listed rows passed alpha=0.00 preservation. Values are rounded for main-text readability.

For the ablation evidence stream, NDCG retention is

\[
\mathrm{Retention}_{m,d,q}(\alpha)
=
\frac{
\mathrm{NDCG}_{m,d,q}^{\mathrm{abl}}(\alpha)
}{
\mathrm{NDCG}_{m,d,q}^{\mathrm{abl}}(0)
}.
\]

The constrained operating point is

\[
\alpha^{*}
=
\arg\max_{\alpha}
Q_{m,d}^{q}(\alpha)
\quad
\mathrm{s.t.}
\quad
\mathrm{Retention}_{m,d,q}(\alpha) \ge 0.95.
\]

This formalises the operating-point selection used in the ablation evidence stream. It does not define six-model superiority and must not be mixed with strict accuracy results.

The 95% retention operating-point diagram restates this constrained selection as a decision flow. The threshold applies only to the registered ablation stream and is not a general model-ranking criterion.

The scale of movement is also objective-dependent. The selected LastFM PGPR LIR setting records a 502.17% explanation gain with 99.94% NDCG retention, whereas the selected ETD setting records a 3.47% gain with 98.86% retention. These percentages are not directly comparable because LIR and ETD use different scales and represent different path properties. They demonstrate that the same retention rule can expose different response ranges across objectives.

UCPR supplies an auxiliary protocol check rather than a second main ablation claim. Its alpha=0.00 preservation passes on both datasets, and each selected point satisfies the 95% NDCG-retention rule. Agreement in protocol behaviour across PGPR and UCPR supports a framework-level statement about auditable control. It does not establish improvement of the underlying recommender, because the experiment controls path or explanation selection over a frozen original item set.

Figure 5.1 presents the registered PGPR/UCPR trade-off curves for LastFM and ML-1M. Together with Table 5.1, the evidence supports a bounded conclusion: the framework provides an auditable control variable, exactly preserves the registered ranking at alpha=0.00, and identifies explanation-oriented operating points under an explicit NDCG-retention constraint.

![](paper/current_dissertation/figures/png/figure_5_1_pgpr_ucpr_ablation_final.png)

**Figure 5.1.** PGPR/UCPR ablation trade-offs on LastFM and ML-1M under the frozen original top-k item set. This figure summarises PGPR/UCPR ablation evidence and should not be interpreted as ablation evidence for all six native-path models. The x-axis is intentionally kept linear to preserve the magnitude of the largest gain; clustered points near the origin indicate smaller but still valid objective movements. The ablation does not replace strict accuracy or establish model superiority.

## 5.2 Mechanism-Level Comparison of Native-Path Models

The ablation establishes controllability only within its registered scope. Interpreting the broader Chapter 4 patterns requires a different evidential level. The six models differ in candidate-path generation, constraints, and selection, and the repository architecture and candidate audit support the mechanism groupings below. These differences provide plausible context, but they do not independently demonstrate causality. External model papers support architectural context only; repository evidence determines the behaviour evaluated in this dissertation. Table 5.2 summarises the mechanism groupings, evidence grades, and current citation status.

| Mechanism | Models / metrics | Evidence grade | Boundary |
| --- | --- | --- | --- |
| Reinforcement-learning path search | PGPR; UCPR | Stronger internal evidence for the registered ablation; architectural context from primary papers | Does not show that reinforcement learning causes all curve differences or improves the underlying recommenders. |
| Coarse-to-fine neural-symbolic reasoning | CAFE | Descriptive mechanism context | No CAFE-specific module ablation establishes the cause of the curve shape. |
| Time-aware path reasoning | TPRec | Descriptive mechanism context plus internal boundary evidence | The block is not evidence of poor recommendation performance. |
| Language-model-style path generation or scoring | KGGLM; PEARLM | Descriptive mechanism context | Candidate flexibility was not independently measured, so the observed movement is not causally attributed to the architecture. |
| Recency, implemented bridge-entity scoring, and explanation-type diversity | LIR; SEP; ETD | External conceptual source verified; internal metric implementation available; SEP semantic direction conservatively bounded | The historical cached SEP matrix is unavailable, and computational path metrics do not establish human-perceived explanation quality. SEP trend analysis is retained as movement along the implemented objective. |

**Table 5.2.** Mechanism context and evidence grade. PGPR/UCPR support is limited to the registered ablation; other mechanism interpretations remain descriptive.

PGPR and UCPR form the reinforcement-learning path-search family, with UCPR additionally treated in the repository as a user-centric variant [@xian2019pgpr; @tai2021ucpr]. Their registered ablation directly shows that the path-selection layer can be redirected towards LIR, SEP, or ETD while preserving the alpha=0.00 baseline. It does not show that reinforcement learning or user-centric modelling causes every difference between the two models. That stronger interpretation would require targeted evidence; the verified primary papers establish model context, not the cause of repository-specific curve differences.

CAFE represents the coarse-to-fine neural-symbolic reasoning family in the repository audit [@xian2020cafe]. Chapter 4 shows substantial movement for CAFE in some ML-1M explanation dimensions while CAFE also leads the strict ML-1M accuracy metrics. This evidence establishes that high strict accuracy and visible explanation movement can coexist. It does not establish coarse-to-fine reasoning as the cause of the curve shape, because the evidence pack contains no CAFE-specific module ablation. The verified primary paper supports the family description; the interpretation of the observed curve remains descriptive.

TPRec represents time-aware path reasoning [@zhao2022tprec]. Because LIR depends on valid interaction timestamps, temporal data availability becomes part of the evaluation contract. TPRec participates in the complete LastFM and ML-1M comparisons, but its Amazon row is blocked: the canonical Amazon timestamps are sentinel -1, and no formal temporal reward is approved. This contrast shows that a model requirement can determine whether an experiment is reportable. The external citation supports model context, while the Amazon status is established by internal validation evidence.

KGGLM and PEARLM form the language-model-style path generation or scoring group [@balloccu2024kgglm; @balloccu2023pearlm]. The candidate audit records constrained decoding for PEARLM and path-language-model infrastructure for both models. Their limited endpoint movement in several Chapter 4 sweeps is consistent with a more restricted set of available or selected paths. Candidate-path flexibility was not independently measured, however, so constrained generation cannot be claimed as the demonstrated cause of smaller movement. KGGLM publication metadata is verified. PEARLM is cited through its verified arXiv record, while its final venue and publisher DOI still require manual verification.

The mechanism comparison therefore supports two different levels of statement. The experiments directly establish that observed controllability varies across models and datasets. Repository architecture supplies plausible context through path-generation and path-selection constraints. Model-specific causal explanations remain hypotheses until they are supported by targeted ablations and verified primary sources.

## 5.3 Accuracy–Explainability Interaction Patterns

Chapter 4 established the empirical trade-off patterns; this section asks which parts can be strengthened by ablation or mechanism-level evidence. The interpretive task is therefore not to repeat the curve summary, but to grade the support available for statements about control and possible model context.

The PGPR/UCPR ablation supplies the stronger evidence in this chapter. It verifies exact alpha=0.00 preservation over the frozen original top-k item set and selects objective-specific operating points under the declared 95% NDCG-retention rule. Because the selected alpha and explanation gain vary by model, objective, and dataset, the ablation supports a bounded claim that the registered path or explanation selection layer is controllable under this protocol. It does not establish improvement of the underlying recommenders or a mechanism shared by all six models.

The evidence for CAFE, TPRec, KGGLM, and PEARLM remains descriptive. Their Chapter 4 profiles can be placed alongside documented architectural or execution constraints, but no targeted module ablation isolates those constraints as the cause of a curve shape. Statements about coarse-to-fine reasoning, temporal requirements, path-language modelling, constrained generation, or candidate availability therefore remain contextual explanations or hypotheses rather than demonstrated causal findings.

Dataset dependence has the same evidential boundary. The PGPR/UCPR ablation confirms that operating points and gains differ between LastFM and ML-1M under one controlled protocol. The datasets also differ in interactions, timestamps, graph structure, bridge-entity degrees, path types, and candidate paths, but the current experiments do not isolate the contribution of each property. The observed differences can therefore motivate targeted future tests without assigning a single dataset characteristic as their cause.

These findings depend on the separation of evidence streams. Strict HR@10, NDCG@10, Precision@10, and Recall@10 describe validated baseline recommendation outputs. The main alpha sweeps describe six-model trade-off trajectories. The PGPR/UCPR ablation applies a frozen-item-set, baseline-preserving protocol to test control of the explanation or path module. Neither sweep NDCG nor ablation NDCG can replace the strict final-accuracy table.

This separation is the practical value of the canonical framework. It makes clear whether an observed difference is a validated baseline result, an explanation-objective trajectory, an ablation outcome, or an experiment that current evidence cannot support. Without common identifiers, validation gates, metric definitions, path-fidelity rules, and evidence roles, those categories could be incorrectly combined.

## 5.4 Amazon-Book KGAT as a Boundary Case

The validation gate from Chapter 3 partitions the registered model-dataset rows into the eligible set

\[
\mathcal{A}
=
\{(m,d): V_{m,d}=1\}
\]

and the boundary set

\[
\mathcal{B}
=
\{(m,d): V_{m,d}=0\}.
\]

Chapter 4 reports rows in \(\mathcal{A}\). Chapter 5 discusses selected rows in \(\mathcal{B}\) as boundary evidence rather than performance evidence.

The Amazon decision-flow specification in Appendix C, Figure C.1 follows export completeness, validation status, and explanation-sweep availability to distinguish boundary, partial, and main-style eligibility. It records reportability only and leaves the existing Amazon evidence status unchanged.

Amazon-Book KGAT tests where the framework can support comparison and where it must stop. It is a partial stress test, not a complete main experiment. The validation register contains PASS rows for KGGLM, PEARLM, and PGPR. Each covers 70,591 canonical test users, although the models produce different numbers of path and explanation records. The result establishes that several native-path exports can be validated in the larger Amazon setting.

The remaining UCPR, CAFE, and TPRec rows are BLOCKED / N/A for different contract reasons. UCPR has completed several port and smoke checks but lacks the required formal full-user export and strict-accuracy outputs. CAFE requires an Amazon-compatible schema and data-builder path, including a compatible UCPR view and checkpoint. TPRec has structural support, but the canonical interaction timestamps are sentinel -1 and do not support an approved formal temporal reward. None of these statuses is evidence of poor recommender performance.

Amazon explanation alpha sweeps are N/A because the current evidence contains no approved timestamp, SEP, and ETD denominator protocol for the dataset. The three passing rows therefore cannot be expanded into a six-model explanation comparison, and the blocked models cannot be ranked. Table 5.3 records the available and unavailable evidence for each row.

| Model | Status | Test users | Pred-path rows | Explanation rows |
| --- | --- | --- | --- | --- |
| KGGLM | PASS | 70591 | 1326486 | 655285 |
| PEARLM | PASS | 70591 | 885270 | 578518 |
| PGPR | PASS | 70591 | 4109983 | 705846 |

**Table 5.3a.** Amazon-Book KGAT reportable rows.

| Model | Status | Main blocking reason | Interpretation |
| --- | --- | --- | --- |
| UCPR | BLOCKED / N/A | Formal full-user export and strict-accuracy outputs remain pending | Boundary evidence; not a performance result |
| CAFE | BLOCKED / N/A | Amazon-compatible schema/data-builder and supporting checkpoint are unavailable | Boundary evidence; not a performance result |
| TPRec | BLOCKED / N/A | Sentinel timestamps do not support the approved temporal protocol | Boundary evidence; not a performance result |

**Table 5.3b.** Amazon-Book KGAT blocked rows. BLOCKED / N/A rows are not comparative performance results.

Figure 5.2 visualises the experiment-status matrix. The figure captures a methodological result: validation is itself part of the empirical outcome. Recording PASS and BLOCKED / N/A before comparative reporting prevents partial ports, unsupported temporal assumptions, and absent explanation denominators from being presented as comparable model evidence.

![](paper/current_dissertation/figures/png/figure_5_2_experiment_status_matrix_final.png)

**Figure 5.2.** Validation-status matrix for canonical native-path experiments, including the partial Amazon-Book KGAT boundary. This figure records validation status rather than comparative recommendation performance; BLOCKED / N/A rows must not be ranked against PASS rows.



## 5.5 Limitations of the Current Framework and Experiments

The framework's conclusions are first bounded by coverage. Only LastFM and ML-1M provide complete six-model native-path comparisons. Amazon-Book KGAT has three PASS and three BLOCKED / N/A rows, and its explanation alpha sweeps are not reportable. Main comparative conclusions must therefore remain tied to the two complete datasets, with Amazon used only to demonstrate a boundary.

The explanation metrics add operational limitations. LIR requires valid timestamps and a recoverable interaction anchor. SEP is adopted as an implemented explanation-side metric rather than independently validated as a user-perceived serendipity construct. ETD depends on a declared taxonomy and denominator for legal path types. LIR / SEP / ETD exact implementation is repository-specific. These definitions are auditable but do not exhaust explanation quality and cannot be collapsed into one latent construct. Their conceptual source is verified through XRecSys, while the exact formulas and data assumptions evaluated here remain repository-specific [@balloccu2022xrecsys]. The historical cached SEP matrix is not available in the current evidence package, and no causal mechanism claim is inferred from SEP movement.

Native-path fidelity also affects strict accuracy. When a model cannot produce ten unique unseen path-ending items, the evaluator preserves the short or empty list, counts missing slots as non-hits, and reports slot coverage instead of padding with non-path recommendations. This policy protects the native-path contract, but strict accuracy can consequently reflect both recommendation quality and native-path candidate availability.

The current package contains no user study and therefore supports claims about computational path properties, not perceived usefulness, understanding, persuasiveness, or trust. No statistical-significance test artifact has been identified, and its final status requires manual checking. Numerical differences in Chapters 4 and 5 must remain observed experimental differences rather than inferential population claims.

Evidence quality also depends on model ports, canonical ID recovery, export completeness, and path validation. A blocked row may result from an incomplete data contract or unsupported mechanism requirement rather than weak model performance. Conversely, a PASS row establishes conformity with the registered evaluation contract, not universal correctness outside it.

Finally, the external citation layer is closed at draft level but not frozen for final submission. Primary sources for PGPR, UCPR, CAFE, TPRec, KGGLM, and XRecSys/LIR/SEP/ETD are verified. PEARLM remains safe as an arXiv citation, but its final venue and publisher DOI require manual checking. The same final-publication caveat applies to the “Measuring Why” survey if it is introduced later. These metadata gaps do not change the internal evidence, and external papers continue to support model or metric context rather than repository experimental values.

Table 5.4 consolidates these limitations, their implications, and possible mitigations. They define the valid scope of the current results and motivate the evidence-coverage, robustness, human-evaluation, and reproducibility recommendations in Chapter 6.

| Limitation | Affected evidence | Retained wording | Status |
| --- | --- | --- | --- |
| No user-study artifact | Human-facing explanation claims | Report computational path properties only; human-facing claims require a separate study. | Open caveat |
| No statistical-significance artifact | Chapter 4 and 5 comparisons | Describe numerical differences without significance language. | Open caveat |
| Amazon-Book KGAT coverage is partial | Dataset generalisation and boundary analysis | Retain 3 PASS and 3 BLOCKED / N/A rows; use Amazon only as a boundary case. | Open boundary |
| LIR / SEP / ETD exact implementation is repository-specific | Explanation metric interpretation | Keep metric definitions operational; SEP is not user-perceived serendipity or explanation quality. | Wording frozen; historical artifact caveat retained |
| Twelve strict primary JSON artifacts are unavailable | Strict accuracy provenance | State 0/12 accessible; do not claim primary JSON verification. | Critical before final submission |
| Checkpoint paths / hashes, seeds, and several model-native hyperparameters are incomplete | Reproducibility and configuration freeze | Retain manual-verification status; do not infer absent settings. | Open caveat |
| PEARLM final venue / DOI and final BibTeX cleanup remain pending | Final bibliography | Use verified arXiv metadata until final venue and DOI are checked. | Manual verification required |
| Figure insertion and final NTU formatting | Dissertation packaging | V3 inserts registered figures and NTU structure; final Microsoft Word inspection remains manual. | V3 packaging addressed; manual Word check pending |

**Table 5.4.** Retained evidence, reproducibility, citation, and packaging limitations.

# Chapter 6 Conclusion and Recommendations

## 6.1 Conclusion

Building on the evidence boundaries established in Chapter 5, this dissertation addressed a comparison problem in knowledge graph recommendation. Native-path recommenders can differ in data representation, identifier space, path format, and inference procedure, making raw outputs unsuitable for direct comparison. The work therefore developed and evaluated a canonical native-path evaluation and analysis framework. It did not introduce a new recommender model.

The framework's first contribution is comparability. A canonical dataset layer defines shared users, items, interaction splits, labels, knowledge-graph provenance, and mapping requirements, while model-specific views preserve the flexibility required by individual implementations. Recommendations and native paths must return to canonical user and item identifiers through a shared export contract. Validation gates then determine whether each model-dataset row is complete and internally consistent enough to support reporting.

Chapter 3 established that this validation-first design can support the intended empirical programme. It specified recommendation and path exports, separated native explanation from post-hoc path recovery, and registered distinct evidence streams for strict accuracy, alpha-sweep trade-offs, and ablation. LastFM and ML-1M provide complete six-model native-path experiment sets. Blocked and not-applicable rows are reported as incomplete evaluation contracts rather than interpreted as poor model performance.

The second contribution is multidimensional measurement. Chapter 4 compared PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM on the two complete datasets. Strict accuracy leadership changes with dataset and metric, and the model leading a strict measure is not necessarily the model with the largest explanation-metric movement. The evidence therefore supports model-, dataset-, and metric-specific trade-off profiles rather than a universal ordering.

LIR, SEP, and ETD make different parts of those profiles visible. LIR concerns the recency of the historical interaction linked by a path, SEP uses the repository-specific bridge-entity score implemented by the registered metric pipeline, and ETD represents diversity among path types. The SEP-oriented results show clear movement along the implemented SEP objective, making SEP useful for analysing operational trade-off behaviour. This movement is not direct evidence of user-perceived serendipity or explanation quality. The three metrics have different endpoint movements across models and datasets, and no movement in one metric can be treated as equivalent movement in another or as a complete measure of explanation quality.

The third contribution is bounded interpretation. Chapter 5 tested whether explanation-oriented objectives could be controlled under an explicit ranking-utility condition. The PGPR/UCPR ablation preserves the registered alpha=0.00 baseline and identifies operating points under the declared NDCG-retention rule. This demonstrates framework controllability over the registered path or explanation selection protocol. It does not establish improvement in the underlying recommender and does not replace the six-model main results.

The mechanism synthesis further distinguishes observation from explanation. Trade-off behaviour varies with model, dataset, and explanation metric, and path-generation or path-selection mechanisms provide useful interpretive context. Beyond the registered ablation, however, the current evidence does not support causal attribution. This graded claim structure prevents architectural descriptions or plausible hypotheses from being reported as demonstrated mechanisms.

Amazon-Book KGAT makes the same principle visible at the dataset boundary. KGGLM, PEARLM, and PGPR have reportable rows, while UCPR, CAFE, and TPRec are blocked or not applicable under the current evidence. No approved Amazon explanation alpha sweeps are available. Amazon-Book is therefore a partial stress test rather than a complete main experiment. Its contribution is to show that validation can expose incomplete model ports, unsupported timestamp semantics, and missing metric contracts before they enter a comparison.

Taken together, the framework makes the accuracy–explainability trade-off of native-path knowledge graph recommenders measurable, comparable, and auditable under a shared contract. Explicit ranking and path metrics provide measurability. Canonical identifiers, common validation gates, and separated evidence roles provide comparability. Export checks, provenance records, figure and table sources, and explicit unsupported-row statuses provide auditability. The resulting contribution is a reproducible basis for evaluation without a claim of a new recommendation algorithm or universal model superiority.

The conclusion remains bounded by the registered evidence. The twelve expected LastFM and ML-1M row-level strict-accuracy JSON artifacts are not accessible; the draft values are currently traceable to the canonical status matrix and the exactly matching final accuracy summary. No statistical-significance artifact or user-study artifact is registered, so numerical comparisons remain descriptive and the computational path metrics do not establish user-perceived explanation quality.

The relationship between the registered objectives and the supported evidence is summarised below.

| Objective | Addressed by | Evidence chapter | Boundary |
| --- | --- | --- | --- |
| O1. Framework feasibility | Defined and verified a canonical native-path evaluation and analysis framework. | Chapter 3 | Feasibility is established for the registered scope, not as universal framework validity. |
| O2–O4. Canonical export and validation protocol | Constructed canonical and model-specific views, required canonical native-path exports, and applied validation before reporting. | Chapter 3 | PASS establishes contract conformity; BLOCKED or not-applicable rows are not performance results. |
| O5. Strict accuracy evaluation | Reported HR@10, NDCG@10, Precision@10, and Recall@10 for the complete LastFM and ML-1M six-model scope. | Chapter 4 | Values are traceable to two matching summaries; the twelve primary JSON artifacts are not accessible. |
| O6. Explanation metric evaluation | Evaluated LIR, SEP, and ETD separately under the repository-specific metric definitions. | Chapters 3–4 | Computational path properties do not establish user-perceived explanation quality. |
| O7. Accuracy–explainability trade-off | Analysed objective-specific alpha-sweep trajectories while keeping sweep ranking measures separate from strict accuracy. | Chapter 4 | Results are descriptive and do not define a universal operating point. |
| O8. Mechanism, ablation, and boundary analysis | Chapter 5 analyses PGPR/UCPR ablation evidence, mechanism-level interpretation, and Amazon-Book KGAT boundary-case evidence. | Chapter 5 | The ablation does not establish six-model superiority or causal explanations for other models; Amazon remains a partial stress test rather than a complete third main experiment and has no approved explanation sweeps. |
| Cross-objective limitations and recommendations | Recorded provenance, metric, significance, human-evidence, coverage, citation, and reproducibility limits and derived corresponding future-work priorities. | Chapters 5–6 | Recommendations do not add experimental results or remove existing caveats. |

**Table 6.1.** Objective-closure summary.

## 6.2 Recommendations for Further Research

The first group of recommendations concerns evidence coverage. Amazon-Book KGAT ports should be completed without weakening the validation contract. UCPR requires a formal pipeline, full-user export, and strict validation. CAFE requires an Amazon-compatible schema and data-builder path with the necessary supporting view and checkpoint. TPRec requires valid interaction timestamps for its temporal mechanism or a separately defined and clearly labelled non-temporal protocol. Explanation sweeps should remain unavailable until timestamp semantics and SEP and ETD denominators are approved.

Coverage should then extend to additional datasets through the same canonical process. Before model comparison, each extension should register interaction splits, identifier mappings, knowledge-graph provenance, timestamp semantics, legal path types, and metric denominators. This would test whether the model- and dataset-dependent patterns observed on LastFM and ML-1M persist under different graph structures and interaction domains, without treating dataset expansion as evidence by itself.

The second group concerns evaluation robustness. Future experiments should use a pre-registered statistical analysis protocol defining repeated-run requirements for stochastic training or path search, the unit of analysis, uncertainty intervals, significance tests, and corrections for multiple model-metric comparisons. Until such evidence is registered, differences should continue to be described as observed results rather than inferential claims.

The operational assumptions of LIR, SEP, and ETD also require sensitivity analysis. LIR should be tested under validated timestamp coverage and alternative recency normalisations. SEP should be assessed against alternative degree or popularity definitions and graph sparsity. ETD should use a registered path taxonomy, denominator audit, and sensitivity analysis. These tests would distinguish changes in explanation behaviour from changes introduced by dataset construction or normalisation.

Short or empty native-path recommendation lists need further methodological treatment. The current evaluator preserves such lists and counts missing positions as non-hits rather than padding with non-path items. Future reports should present slot coverage, affected-user counts, and candidate-path exhaustion alongside strict accuracy. Separate coverage and ranking components may be considered, but a fallback policy should remain outside the native-path result unless it also supplies faithful path evidence.

The third group concerns human-facing explanation evidence. A user study should complement the computational metrics by examining whether explanations are understandable, useful for decision making, appropriately surprising, and faithful from the user's perspective. These subjective outcomes must remain separate from LIR, SEP, and ETD because the current metrics operationalise path properties rather than perceived explanation quality.

Natural-language generation is another possible extension, provided that generated text remains grounded in the validated native path. A future module should map path entities and relations into readable statements, preserve the original user-item path evidence, and verify that no absent entity or relation is introduced. Readability and usefulness would then require human evaluation; generation alone does not establish a benefit.

Post-hoc explanation baselines could broaden the comparison but should form a separate evaluation group. Native paths arise within recommendation or reasoning, while post-hoc paths are recovered after a recommendation score has been produced. Future work should label this distinction, apply fidelity measures appropriate to post-hoc explanations, and avoid assigning native-path LIR, SEP, or ETD as though both evidence types were equivalent.

The final group concerns citation closure and reproducibility. Primary publication metadata is verified for PGPR, UCPR, CAFE, TPRec, KGGLM, and the XRecSys conceptual source for LIR, SEP, and ETD. PEARLM remains verified only at the arXiv level, and its final venue and publisher DOI require manual checking. The “Measuring Why” survey has the same final-publication caveat if it is used in a later revision. Repository implementation documents remain the source for experimental values and exact metric behaviour; external papers supply model and conceptual context.

The reproducibility package should be consolidated around the current source of truth. It should include canonical data-construction and validation scripts, model-view and export configurations, environment and seed records, metric settings, figure-generation commands, artifact manifests, and the thesis traceability log. Historical or superseded materials should be separated from the final package. A single documented execution order and evidence index would allow every dissertation table, figure, and claim to be traced to its registered input without rerunning unsupported experiments.

# References

::: {#refs}
:::

# Appendices

This plan identifies dissertation material that can be inserted during final formatting. It does not fabricate unavailable appendix data or alter the evidence boundaries of Chapters 1–6.

## Appendix A: Canonical Export Contract and Validation Details

Planned contents: the three-file native-path export contract, field-level requirements, canonical identifier recovery, and the registered validation gates. Supporting material is available in `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` and the repository validation scripts. Full command outputs are to be selected during final formatting.

## Appendix B: Full Metric Definitions and Notation

Planned contents: framework notation and the repository-specific definitions and assumptions for strict accuracy, LIR, SEP, and ETD. The conceptual source for LIR, SEP, and ETD and the repository implementation must remain distinguished. No additional metric interpretation is introduced here.

## Appendix C: Additional Trade-off Curves

Planned contents: supplementary LIR-, SEP-, and ETD-oriented alpha-sweep figures for LastFM and ML-1M that are not required in the main-text figure set. Only existing validated figure assets should be inserted. Paired sweep NDCG must remain separate from strict NDCG@10.

![](paper/current_dissertation/figures/png/figure_c_1_amazon_boundary_flow_final.png)

**Figure C.1.** Decision flow for the partial Amazon-Book KGAT boundary case. This figure records boundary-case status rather than full benchmark performance. Current validated rows remain partial evidence because the complete explanation-sweep protocol is unavailable.

## Appendix D: Ablation Supplementary Tables

Planned contents: the complete PGPR/UCPR alpha-zero preservation and 95% NDCG-retention records from `reports/tables/ablation/pgpr_ucpr_path_module/`. These records remain specific to the registered ablation and must not be generalised to the six-model main comparison.

## Appendix E: Boundary-Case and Reproducibility Caveats

Planned contents: the detailed Amazon-Book KGAT validation register, unavailable explanation-sweep conditions, native-path slot-coverage caveats, unavailable twelve primary strict-accuracy JSON artifacts, checkpoint and seed gaps, and the absence of registered statistical-significance and user-study artifacts. Amazon-Book remains a partial boundary case.

## Appendix F: Citation and Provenance Notes

Planned contents: citation verification notes, strict-accuracy provenance closure, the citation-to-claim map, and unresolved publication-metadata checks. PEARLM remains verified at arXiv level unless final venue and publisher DOI metadata are manually confirmed. Relevant sources are under `paper/drafts_ch3_6/` and `paper/literature/review_outputs/`.
