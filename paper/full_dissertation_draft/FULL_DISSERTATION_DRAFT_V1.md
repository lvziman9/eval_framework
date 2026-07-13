# Chapter 1 Introduction

## 1.1 Background

Recommender systems reduce information overload by ranking items according to evidence about user preferences and item relevance. Conventional collaborative and content-based methods organise this evidence primarily through interactions and attributes. Knowledge graph recommender systems extend that setting by representing users, items, entities, and relations in a structured graph, allowing recommendation methods to exploit semantic context and higher-order connectivity [@guo2022kgsurvey]. This structure can improve the information available to a recommender, but the use of a knowledge graph does not by itself make the recommendation process inspectable.

Explainable recommendation addresses the need to communicate why an item was recommended, support model inspection, and distinguish recommendation quality from the quality of its accompanying evidence [@zhang2020explainableSurvey]. Explanations may be intrinsic to a model or reconstructed after prediction. In a knowledge graph setting, a native-path explanation is a path produced or retained within the recommendation or path-selection workflow. A post-hoc explanation is generated after the recommendation decision by a separate attribution, search, or explanatory procedure. The distinction matters because an intelligible path recovered after prediction need not represent the evidence used to produce the recommendation.

Path-reasoning recommenders make this distinction operational. Methods such as PGPR and CAFE traverse or construct graph paths as part of recommendation and can expose those paths as explanation candidates [@xian2019pgpr; @xian2020cafe]. A native path can connect a user and historical interaction to a recommended item through graph entities and relations, making endpoints, path types, and intermediate evidence available for validation. However, a visible path is not automatically faithful, useful, recent, serendipitous, or diverse. These properties require explicit definitions and separate checks.

Recommendation accuracy is therefore necessary but insufficient for evaluating native-path systems. HR@10, NDCG@10, Precision@10, and Recall@10 describe ranking outcomes, whereas path properties such as linked interaction recency (LIR), shared entity popularity or serendipity (SEP), and explanation type diversity (ETD) describe different aspects of the associated explanation evidence. The conceptual origin of these path properties is provided by XRecSys, while the exact formulas evaluated in this dissertation are repository-specific [@balloccu2022xrecsys]. A defensible evaluation must retain this separation rather than collapse ranking and explanation evidence into a single score.

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

The dissertation operationalises this family through LIR, SEP, and ETD. LIR concerns the recency of the historical interaction linked by a path. SEP concerns the rarity or serendipity associated with the bridge entity under the registered implementation. ETD concerns diversity among explanation path types across a recommendation list. These definitions are related to the XRecSys conceptual source, but their exact formulas and data assumptions remain repository-specific. They must therefore be traced both to the external conceptual publication and to the implementation and metric guide used by the dissertation.

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

The research gap is therefore evaluative and evidential. Heterogeneous native-path models cannot be compared reliably when identifiers, populations, paths, metrics, and validation criteria differ or remain implicit. Explanation quality cannot be reduced to the presence of a path, and ranking quality cannot be replaced by an explanation metric. A controlled analysis must retain the native evidence produced by each model while placing all reportable outputs under a common contract.

This dissertation addresses that gap through a canonical native-path evaluation and analysis framework. The framework separates canonical datasets from model-specific views, maps outputs back to shared identifiers, retains model-native recommendation paths, validates recommendation and explanation artifacts before scoring, and keeps strict accuracy, explanation-property sweeps, and ablation evidence in distinct roles. It evaluates LIR, SEP, and ETD as separate path properties and records blocked or not-applicable combinations as boundaries rather than model failures.

The resulting contribution is a method for auditable comparison and controlled trade-off analysis across heterogeneous native-path recommenders. The literature synthesis establishes five requirements for the next chapter: canonical dataset truth, model-specific execution views, native-path export semantics, validation before reporting, and explicit separation of ranking, explanation, and ablation evidence. Chapter 3 specifies and verifies that framework contract. Chapters 4 and 5 use the validated evidence to analyse ranking and explanation behaviour and to examine mechanism and coverage boundaries. Chapter 6 synthesises the supported conclusions and recommendations. This progression preserves the boundary established by the literature review: the dissertation contributes evaluation, validation, and analysis infrastructure, not a claim to a new recommender model or universal state-of-the-art performance.

# Chapter 3 Framework Implementation and Verification

## 3.1 Overview of the Implemented Framework

Chapter 2 showed that existing knowledge graph recommendation, path-reasoning, explainability, and benchmarking research supplies complementary methods and evaluation concepts without making heterogeneous native-path outputs automatically comparable. Fair comparison therefore requires more than applying the same ranking metrics to raw model outputs. The models can differ in graph schema, identifier space, search procedure, path format, and export behaviour, so an uncontrolled comparison can confound model performance with differences in data preparation and representation. This chapter addresses that comparability problem by describing the evaluation framework used in the later empirical chapters. The framework does not introduce a new recommender model; it provides a shared evaluation and verification contract for heterogeneous native-path recommenders.

The implemented architecture separates five concerns: canonical dataset truth, model-specific views, native-path export, validation gates, and metric reporting. Each concern resolves a distinct source of ambiguity. The canonical layer defines the shared evaluation population and labels. Model-specific views preserve the internal representations required by individual recommenders. Native exports retain the paths produced within the recommendation process. Validation determines whether those exports meet the common contract, and metric reporting keeps ranking and explanation evidence in their proper roles.

Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit.

The workflow therefore begins from a canonical dataset layer containing shared user identifiers, item identifiers, interaction splits, labels, and knowledge-graph provenance. Individual models build the training views they require from this layer, but their outputs must return to canonical `uid` and `pid` space before evaluation. The validation layer then checks whether the recommendations and explanation paths are complete and internally consistent. Only rows that pass these checks are admitted as reportable experimental evidence.

This validation-first design makes evidence eligibility explicit. A model-dataset row can be complete, blocked, or not applicable. A blocked row is not evidence of poor recommendation performance; it means that the current repository does not support faithful scoring for that row. The framework thus defines both how supported results can be compared and where comparison must stop.

## 3.2 Canonical Dataset and Model View Construction

The first requirement for controlled comparison is a model-independent evaluation space. For each dataset, the canonical layer specifies users, products, train/validation/test interactions, evaluation labels, upstream knowledge-graph assets, and mapping requirements. This design is documented in `docs/guides/CANONICAL_DATASET_STANDARD.md` and provides the shared truth against which model exports are evaluated.

Canonicalisation does not require every recommender to consume an identical internal graph. Such a requirement would be incompatible with native-path models that depend on different relation vocabularies, entity-pruning strategies, compact identifiers, or path-search constraints. The framework instead standardises the comparison contract while allowing model-specific execution.

Model views are generated from the canonical layer for PGPR, UCPR, CAFE, hopwise, and RecBole-oriented workflows. External model papers establish the architectural context for PGPR, UCPR, CAFE, TPRec, and KGGLM, while PEARLM is cited through its verified arXiv record because final venue and DOI metadata remain unresolved [@xian2019pgpr; @tai2021ucpr; @xian2020cafe; @zhao2022tprec; @balloccu2024kgglm; @balloccu2023pearlm]. These views may remap identifiers internally, but the reported artifacts must return to canonical identifiers. In particular, exported `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` files must use canonical `uid` and `pid` values even when the training and inference code uses a different internal namespace. This rule separates legitimate implementation variation from variation that would make outputs incomparable.

The resulting dataset scope is also explicit. LastFM and ML-1M form the complete six-model native-path comparisons used for the main dissertation results. Amazon-Book KGAT remains a partial stress test and boundary case: KGGLM, PEARLM, and PGPR have complete rows, whereas UCPR, CAFE, and TPRec are blocked under the current evidence. Canonical construction therefore supports both the main comparison and the later analysis of incomplete coverage.

## 3.3 Native-Path Export Contract and Implementation

Comparable identifiers are necessary but insufficient when the explanation itself is part of the model evidence. The export contract therefore defines the minimum artifacts required for a complete native-path row:

- `uid_topk.csv`, containing ranked recommendation lists for canonical users;
- `pred_paths.csv`, containing candidate or selected recommendation paths;
- `uid_pid_explanation.csv`, containing the path used to explain each user-item recommendation.

For non-path recommenders or accuracy-reference models, `uid_topk.csv` is sufficient for accuracy evaluation, but explanation metrics are not assigned. This boundary protects explanation fidelity. A post-hoc path recovered after recommendation is not treated as equivalent to a path produced by the model's recommendation mechanism, because the recovered path need not represent how the recommendation was generated.

The evaluation layer represents each path as a sequence of relation/entity-type/entity-id triples. In LastFM and ML-1M, the standard path starts from a user, traverses a seed interaction in that user's training history, passes through a knowledge-graph bridge entity, and ends at the recommended item. LIR, SEP, and ETD operate on properties of this structure, so preserving the native path and its canonical endpoints is essential to the meaning of the later metrics.

The contract is implemented through export and validation scripts rather than through a new model architecture. The registered validation evidence shows that LastFM and ML-1M satisfy the required export checks for all six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. These exports provide the model-faithful evidence on which Chapters 4 and 5 depend.

## 3.4 Evaluation and Validation Pipeline

The pipeline must determine not only how evidence is scored, but whether it is admissible. It therefore computes strict accuracy and explanation metrics from separate evidence sources and applies validation before either stream is interpreted.

Strict accuracy is computed from canonical labels and the recommendation export. The reported metrics are HR@10, NDCG@10, Precision@10, and Recall@10. Explanation metrics are computed from native paths through the xrecsys path-metric stack documented in `docs/guides/PATH_METRICS_GUIDE.md`. The dissertation cites XRecSys for the conceptual origin of recency, shared-entity popularity or serendipity, and explanation-type diversity, while the exact evaluated LIR, SEP, and ETD formulas remain repository-specific [@balloccu2022xrecsys]. LIR measures whether the path is anchored in recent linked user interactions, SEP measures the serendipity of the bridge entity, and ETD measures the diversity of explanation path types across a user's recommendations. These dimensions remain separate because they describe different path properties rather than one generic explanation score.

Before reporting, the validation pipeline checks canonical test-user coverage, top-k coverage, duplicate recommendations, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate-path consistency, and score ranges. The current validation status table contains 15 passing export-validation rows and 3 blocked Amazon-Book KGAT rows. Passing status establishes conformity with the registered contract; blocked status prevents unsupported rows from entering the comparison.

The pipeline also separates strict accuracy from alpha-sweep trade-off evidence. The strict values used in this draft are currently traceable to `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`. The twelve expected row-level primary accuracy JSON files are not accessible in the current worktree and must not be described as directly inspected. Alpha-sweep values come from trade-off CSVs in which an alpha parameter varies the recommendation objective. The former describe validated ranking outputs, while the latter describe response trajectories under an explanation-oriented control. Alpha-sweep values are therefore not substitutes for strict accuracy results.

Figure 3.2 summarises this design by showing how the alpha sweep generates metric-specific trade-off evidence after the baseline and evaluation contract have been established. The separation of sources ensures that later chapters can state exactly whether a claim concerns strict performance, sweep behaviour, or ablation.

## 3.5 Framework Verification Results

Verification tests whether the implemented contract can support the intended comparison and identify cases in which it cannot. For the two main datasets, the result is complete: LastFM passes validation for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM, and ML-1M passes for the same six models. These rows establish the empirical basis for the strict accuracy and trade-off analysis in Chapter 4.

Amazon-Book KGAT demonstrates the other function of verification. KGGLM, PEARLM, and PGPR pass validation, whereas UCPR, CAFE, and TPRec are blocked or not applicable under the current evidence. The blocked rows record implementation and data-contract limitations, not measured recommendation quality. By distinguishing these statuses before comparison, the framework prevents absent or unsupported results from being interpreted as model outcomes.

The strict accuracy snapshot follows the same boundary. LastFM and ML-1M contain complete strict accuracy values for all six native-path models. Amazon-Book KGAT contains strict values only for the three complete rows and has no valid explanation alpha sweeps in the current evidence pack. It can therefore support a partial boundary analysis, but not a complete six-model trade-off experiment.

Representative endpoints additionally verify that the trade-off pipeline operates on the two complete datasets. LastFM PGPR LIR moves from 0.0062 at alpha=0 to 0.0219 at alpha=1, while ML-1M PGPR LIR moves from 0.4655 to 0.9627. At this stage, these values confirm computation and export continuity. Their interpretation as model behaviour belongs to Chapters 4 and 5.

## 3.6 Trade-off and Ablation Experiment Setup

With the evidence contract verified, the next question is whether supported models exhibit common or heterogeneous relationships between ranking utility and explanation properties. The trade-off experiments address this question through alpha sweeps on LastFM and ML-1M using the six native-path models that pass validation on both datasets.

The analysis is organised into LIR-, SEP-, and ETD-oriented sweeps. This metric-specific organisation is necessary because LIR concerns interaction recency, SEP concerns bridge-entity rarity, and ETD concerns explanation-type diversity. A movement in one dimension cannot be interpreted as an equivalent movement in another, and none of the three is treated as a complete explanation-quality score.

The ablation experiments form a separate evidence stream. The PGPR/UCPR path-module evidence is stored under `reports/tables/ablation/pgpr_ucpr_path_module/` and `reports/figures/ablation/pgpr_ucpr_path_module/`. Chapter 5 uses these files to examine controllability and mechanism-level effects; they do not replace the six-model trade-off comparison.

Chapter 4 therefore uses the verified strict accuracy, explanation endpoint, and alpha-sweep evidence to test whether a universal performance or explanation profile emerges. Chapter 5 then asks which observed effects can be supported by ablation, which mechanism interpretations remain descriptive, and where dataset coverage reaches a boundary. Chapter 6 synthesises those findings without introducing new experimental results.

# Chapter 4 Accuracy–Explainability Trade-off Results

## 4.1 Experimental Scope and Result Organisation

Chapter 3 established which native-path outputs satisfy the common export and validation contract. This chapter uses that admissible evidence to test whether validated native-path recommenders exhibit a universal accuracy leader or a common explanation response. The evidence covers the two complete main datasets, LastFM and ML-1M, and the six implementations that pass the Chapter 3 validation gates on both datasets: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. The chapter reports empirical results rather than revisiting framework design.

Two evidence streams remain separate throughout the analysis. Strict accuracy results come from the accessible canonical status matrix and the exactly matching final accuracy summary presented in Table 4.1; the twelve expected row-level primary JSON files remain unavailable. Alpha-sweep results come from the canonical trade-off CSVs and describe changes in LIR, SEP, ETD, and their paired sweep ranking metrics as alpha varies. Alpha-sweep ranking values are not used as substitutes for strict accuracy. All explanation results concern paths produced natively within the recommendation workflow; the main comparison contains no post-hoc explanations.

Amazon-Book KGAT is excluded because the current evidence does not contain a complete six-model alpha-sweep result set. Chapter 5 treats it only as a partial boundary case. The present chapter first establishes the strict accuracy pattern, then examines explanation endpoints and metric-specific trade-offs, and finally compares the resulting profiles across datasets. Ablation and mechanism-level interpretation remain separate and are deferred to Chapter 5.

## 4.2 Strict Accuracy Results

The strict results do not identify a universal winner across datasets and metrics. Table 4.1 reports HR@10, NDCG@10, Precision@10, and Recall@10, while Figures 4.1 and 4.2 visualise HR@10 and NDCG@10 for LastFM and ML-1M. This section uses no alpha-sweep evidence.

LastFM divides leadership between two models. UCPR records the highest HR@10 at 0.216416 and the highest Recall@10 at 0.023155. TPRec records the highest NDCG@10 at 0.038981 and the highest Precision@10 at 0.032736. PGPR, CAFE, KGGLM, and PEARLM are lower than these metric-specific leaders on all four measures. The result is therefore a metric-dependent ordering rather than a single LastFM leader.

ML-1M produces a different pattern. CAFE leads all four strict metrics, with HR@10 of 0.554305, NDCG@10 of 0.116655, Precision@10 of 0.107119, and Recall@10 of 0.052024. PGPR is second on HR@10 and NDCG@10, while TPRec is second on Precision@10 and Recall@10. The leading identity thus changes from the split UCPR and TPRec result on LastFM to CAFE on ML-1M. Any assessment of model performance must consequently remain conditional on dataset and metric.

## 4.3 Explanation Metric Endpoint Results

The next question is whether explanation behaviour can be reduced to a single dimension or common response pattern. Table 4.2 and Figure 4.3 report alpha=0 and alpha=1 endpoints from the NDCG alpha-sweep summaries for three distinct properties. LIR measures the recency of the linked historical interaction used by a path, SEP measures the serendipity associated with its bridge entity, and ETD measures diversity among explanation path types. Movement in one dimension does not establish overall explanation superiority.

On LastFM, PGPR shows the largest LIR endpoint movement, from 0.0062 to 0.0219. SEP increases for all six models, reaching alpha=1 values from 0.6106 for PEARLM to 0.9890 for CAFE. ETD responses are more varied: TPRec has the largest movement, while PGPR and CAFE also move visibly and KGGLM and PEARLM change only slightly. Table 4.2 retains the complete endpoint set.

ML-1M yields both larger movements and a different ordering in several cases. PGPR and TPRec show large LIR responses, and PGPR, CAFE, and TPRec all approach the upper end of the SEP scale at alpha=1. CAFE records the largest ETD movement, from 0.2902 to 0.8542, followed by visible TPRec and PGPR changes. KGGLM has identical alpha=0 and alpha=1 values for all three metrics, and PEARLM changes only slightly. Explanation-objective controllability is therefore conditional on metric, model, and dataset rather than captured by one endpoint ranking.

## 4.4 LIR-oriented Trade-off Results

The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.4 plots LIR against the NDCG sweep metric for both datasets. These NDCG values belong to the alpha-sweep evidence stream and are distinct from the strict NDCG@10 results in Section 4.2.

LastFM separates a costly LIR response from more strongly preserved or limited responses. PGPR increases LIR from 0.0062 to 0.0219 while sweep NDCG changes from 0.1130 to 0.0680. UCPR increases LIR from 0.0050 to 0.0118 with a much smaller NDCG change, from 0.1256 to 0.1231. CAFE and TPRec also increase LIR, whereas KGGLM and PEARLM show only small movement and essentially unchanged sweep NDCG endpoints. Figure 4.4 retains the complete trajectories.

The ML-1M profiles differ in both scale and ranking cost. PGPR moves from 0.4655 to 0.9627 in LIR while NDCG changes from 0.1019 to 0.0619. UCPR again preserves more of the paired ranking metric, moving from 0.4568 to 0.7342 in LIR and from 0.0862 to 0.0829 in NDCG. TPRec and CAFE show substantial LIR movement with larger paired ranking changes than UCPR, while KGGLM is unchanged and PEARLM moves only slightly. The curves establish distinct LIR trade-off profiles without selecting a universal operating point.

## 4.5 SEP-oriented Trade-off Results

SEP asks a different question: how does ranking change when paths with rarer bridge entities are favoured? It measures serendipity through the normalised rarity of the bridge entity rather than through interaction recency. The canonical SEP-NDCG views listed as optional Figure 4.5 remain optional or appendix candidates rather than part of the four-figure core.

On LastFM, PGPR increases SEP from 0.5688 to 0.9877 while sweep NDCG changes from 0.1130 to 0.0676. UCPR reaches SEP 0.9336 from 0.5170 while NDCG changes only from 0.1256 to 0.1238. CAFE and TPRec also reach high SEP endpoints, whereas KGGLM and PEARLM show smaller movement. The contrast shows that similar directional SEP gains can carry different paired ranking costs.

On ML-1M, PGPR, CAFE, and TPRec again reach high alpha=1 SEP values but incur different NDCG changes. UCPR increases SEP from 0.4935 to 0.7406 while NDCG changes only from 0.0862 to 0.0825. KGGLM remains unchanged on both measures, and PEARLM records a small SEP increase with nearly unchanged NDCG. The optional Figure 4.5 views retain the complete trajectories. These profiles show that popularity exposure can be redirected to different degrees and at different paired ranking costs; they do not make SEP a complete explanation-quality measure.

## 4.6 ETD-oriented Trade-off Results

ETD adds a third perspective by measuring the diversity of explanation path types within a user's recommendation list. Its sweep tests whether this diversity can increase while the paired ranking metric is preserved. Optional Figure 4.6 identifies the existing dataset-specific ETD-NDCG views supporting the section.

On LastFM, TPRec has the largest ETD endpoint increase, from 0.1766 to 0.3983, while its sweep NDCG changes from 0.1178 to 0.1138. PGPR and CAFE also increase ETD with comparatively limited paired NDCG changes. UCPR has a smaller increase, and KGGLM and PEARLM show minimal endpoint movement. The profile differs from both LIR and SEP, confirming that path-type diversity adds separate information.

ML-1M again changes the scale and ordering. CAFE records the largest ETD movement, from 0.2902 to 0.8542, while its sweep NDCG changes from 0.1115 to 0.0862. TPRec and PGPR also move substantially. UCPR increases ETD from 0.2088 to 0.2555 with a smaller NDCG change from 0.1008 to 0.0992, while KGGLM remains unchanged and PEARLM changes only slightly. The optional Figure 4.6 views retain the complete trajectories. These results establish differences in ETD controllability; they do not by themselves establish the mechanism causing those differences.

## 4.7 Cross-Dataset Comparison

Across the two evidence streams, the central empirical result is heterogeneity rather than universal dominance. Strict accuracy leadership changes by dataset and metric: UCPR and TPRec lead different measures on LastFM, while CAFE leads all four measures on ML-1M. Explanation endpoints likewise do not yield one model ordering across LIR, SEP, and ETD, and the paired NDCG response differs across models.

The datasets also change the scale and pattern of movement. PGPR, UCPR, CAFE, and TPRec generally show larger absolute LIR changes on ML-1M than on LastFM. CAFE, TPRec, and PGPR have substantial ETD movement on ML-1M, but their ordering and magnitude differ on LastFM. KGGLM and PEARLM provide contrasting cases with limited movement in several sweeps. A model's trade-off profile is thus conditional on both the dataset and the explanation property being controlled.

No single model dominates all strict accuracy measures, explanation dimensions, and datasets. The common native-path contract instead reveals multiple trade-off profiles whose evidence roles must remain distinct. Comparative curves alone, however, cannot establish why those profiles differ. Chapter 5 therefore examines the registered PGPR and UCPR ablation, uses model mechanisms only as cautious interpretive context, and treats Amazon-Book KGAT separately as a coverage boundary.

# Chapter 5 Ablation, Mechanism Analysis, and Boundary Cases

## 5.1 Ablation Analysis of Framework Controllability

Chapter 4 established heterogeneous trade-off profiles, but comparative curves alone cannot show whether an explanation-oriented control begins from the registered baseline or can satisfy an explicit ranking-utility condition. The ablation addresses that narrower question. It tests framework controllability for PGPR and UCPR; it is not designed to show that either model becomes a stronger recommender after modification. Its evidence remains separate from the strict six-model accuracy results and the main alpha sweeps in Chapter 4.

The experiment uses a strict baseline-preserving canonical alpha sweep over the frozen original top-k item set. PGPR is the main ablation model and UCPR is an auxiliary replication. On both LastFM and ML-1M, the alpha=0 checks pass for LIR, SEP, and ETD. The exported top-k rankings and explanation pairs are preserved exactly, with a maximum metric difference of 0.0 from the original result. The control mechanism therefore begins from the registered baseline rather than a separately reconstructed ranking.

The second test selects the maximum explanation gain subject to NDCG retention greater than or equal to 95%. All twelve dataset-model-objective combinations in Table 5.1 have an operating point satisfying this rule. The selected alpha varies with the objective: some settings choose alpha=1.0; PGPR SEP chooses 0.75 on LastFM and 0.95 on ML-1M; and intermediate settings also occur for ML-1M PGPR LIR and ML-1M UCPR SEP. This variation is the relevant controllability result because the operating point follows the joint response of the explanation objective and NDCG rather than a fixed endpoint.

The scale of movement is also objective-dependent. The selected LastFM PGPR LIR setting records a 502.1737281916887% explanation gain with 99.94241852350147% NDCG retention, whereas the selected ETD setting records a 3.470375996962718% gain with 98.85509635280121% retention. These percentages are not directly comparable because LIR and ETD use different scales and represent different path properties. They demonstrate that the same retention rule can expose different response ranges across objectives.

UCPR supplies an auxiliary protocol check rather than a second main ablation claim. Its alpha=0 preservation passes on both datasets, and each selected point satisfies the 95% NDCG-retention rule. Agreement in protocol behaviour across PGPR and UCPR supports a framework-level statement about auditable control. It does not establish improvement of the underlying recommender, because the experiment controls path or explanation selection over a frozen original item set.

Figure 5.1 presents the registered PGPR/UCPR trade-off curves for LastFM and ML-1M. Together with Table 5.1, the evidence supports a bounded conclusion: the framework provides an auditable control variable, exactly preserves the registered ranking at alpha=0, and identifies explanation-oriented operating points under an explicit NDCG-retention constraint.

## 5.2 Mechanism-Level Comparison of Native-Path Models

The ablation establishes controllability only within its registered scope. Interpreting the broader Chapter 4 patterns requires a different evidential level. The six models differ in candidate-path generation, constraints, and selection, and the repository architecture and candidate audit support the mechanism groupings below. These differences provide plausible context, but they do not independently demonstrate causality. External model papers support architectural context only; repository evidence determines the behaviour evaluated in this dissertation. Table 5.2 summarises the mechanism groupings, evidence grades, and current citation status.

PGPR and UCPR form the reinforcement-learning path-search family, with UCPR additionally treated in the repository as a user-centric variant [@xian2019pgpr; @tai2021ucpr]. Their registered ablation directly shows that the path-selection layer can be redirected towards LIR, SEP, or ETD while preserving the alpha=0 baseline. It does not show that reinforcement learning or user-centric modelling causes every difference between the two models. That stronger interpretation would require targeted evidence; the verified primary papers establish model context, not the cause of repository-specific curve differences.

CAFE represents the coarse-to-fine neural-symbolic reasoning family in the repository audit [@xian2020cafe]. Chapter 4 shows substantial movement for CAFE in some ML-1M explanation dimensions while CAFE also leads the strict ML-1M accuracy metrics. This evidence establishes that high strict accuracy and visible explanation movement can coexist. It does not establish coarse-to-fine reasoning as the cause of the curve shape, because the evidence pack contains no CAFE-specific module ablation. The verified primary paper supports the family description; the interpretation of the observed curve remains descriptive.

TPRec represents time-aware path reasoning [@zhao2022tprec]. Because LIR depends on valid interaction timestamps, temporal data availability becomes part of the evaluation contract. TPRec participates in the complete LastFM and ML-1M comparisons, but its Amazon row is blocked: the canonical Amazon timestamps are sentinel -1, and no formal temporal reward is approved. This contrast shows that a model requirement can determine whether an experiment is reportable. The external citation supports model context, while the Amazon status is established by internal validation evidence.

KGGLM and PEARLM form the language-model-style path generation or scoring group [@balloccu2024kgglm; @balloccu2023pearlm]. The candidate audit records constrained decoding for PEARLM and path-language-model infrastructure for both models. Their limited endpoint movement in several Chapter 4 sweeps is consistent with a more restricted set of available or selected paths. Candidate-path flexibility was not independently measured, however, so constrained generation cannot be claimed as the demonstrated cause of smaller movement. KGGLM publication metadata is verified. PEARLM is cited through its verified arXiv record, while its final venue and publisher DOI still require manual verification.

The mechanism comparison therefore supports two different levels of statement. The experiments directly establish that observed controllability varies across models and datasets. Repository architecture supplies plausible context through path-generation and path-selection constraints. Model-specific causal explanations remain hypotheses until they are supported by targeted ablations and verified primary sources.

## 5.3 Accuracy–Explainability Interaction Patterns

Taken together, the Chapter 4 results and the registered ablation reject a one-dimensional view of the trade-off. Strict accuracy leaders change with dataset and metric, while the largest movements in explanation properties occur in different model-objective combinations. Leading a strict ranking measure does not imply having the largest controllable response in LIR, SEP, or ETD.

The explanation dimensions also remain non-interchangeable. LIR concerns the recency of the historical interaction anchoring a path; SEP uses the degree-derived serendipity of its bridge entity; and ETD concerns the diversity of path types within a user's recommendation list. The markedly different response ranges for the same model and dataset in the ablation reinforce that each metric describes a separate property. A large percentage change in one cannot be interpreted as an equivalent improvement in another.

Controllability is model-dependent. Chapter 4 shows substantial sweep movement for some models and only limited movement for others. Within the common ablation protocol, the alpha selected by the 95% NDCG-retention rule also changes by model and objective. A single global alpha therefore cannot be assumed to represent an equivalent trade-off across model mechanisms.

The response is dataset-dependent as well. PGPR and UCPR select different operating points and produce different explanation gains on LastFM and ML-1M. The datasets differ in available interactions, timestamps, graph structure, bridge-entity degrees, path types, and candidate paths. The evidence establishes dataset-dependent outcomes, but it does not isolate the causal contribution of each property.

These findings depend on the separation of evidence streams. Strict HR@10, NDCG@10, Precision@10, and Recall@10 describe validated baseline recommendation outputs. The main alpha sweeps describe six-model trade-off trajectories. The PGPR/UCPR ablation applies a frozen-item-set, baseline-preserving protocol to test control of the explanation or path module. Neither sweep NDCG nor ablation NDCG can replace the strict final-accuracy table.

This separation is the practical value of the canonical framework. It makes clear whether an observed difference is a validated baseline result, an explanation-objective trajectory, an ablation outcome, or an experiment that current evidence cannot support. Without common identifiers, validation gates, metric definitions, path-fidelity rules, and evidence roles, those categories could be incorrectly combined.

## 5.4 Amazon-Book KGAT as a Boundary Case

Amazon-Book KGAT tests where the framework can support comparison and where it must stop. It is a partial stress test, not a complete main experiment. The validation register contains PASS rows for KGGLM, PEARLM, and PGPR. Each covers 70,591 canonical test users, although the models produce different numbers of path and explanation records. The result establishes that several native-path exports can be validated in the larger Amazon setting.

The remaining UCPR, CAFE, and TPRec rows are BLOCKED / N/A for different contract reasons. UCPR has completed several port and smoke checks but lacks the required formal full-user export and strict-accuracy outputs. CAFE requires an Amazon-compatible schema and data-builder path, including a compatible UCPR view and checkpoint. TPRec has structural support, but the canonical interaction timestamps are sentinel -1 and do not support an approved formal temporal reward. None of these statuses is evidence of poor recommender performance.

Amazon explanation alpha sweeps are N/A because the current evidence contains no approved timestamp, SEP, and ETD denominator protocol for the dataset. The three passing rows therefore cannot be expanded into a six-model explanation comparison, and the blocked models cannot be ranked. Table 5.3 records the available and unavailable evidence for each row.

Figure 5.2 visualises the experiment-status matrix. The figure captures a methodological result: validation is itself part of the empirical outcome. Recording PASS and BLOCKED / N/A before comparative reporting prevents partial ports, unsupported temporal assumptions, and absent explanation denominators from being presented as comparable model evidence.

## 5.5 Limitations of the Current Framework and Experiments

The framework's conclusions are first bounded by coverage. Only LastFM and ML-1M provide complete six-model native-path comparisons. Amazon-Book KGAT has three PASS and three BLOCKED / N/A rows, and its explanation alpha sweeps are not reportable. Main comparative conclusions must therefore remain tied to the two complete datasets, with Amazon used only to demonstrate a boundary.

The explanation metrics add operational limitations. LIR requires valid timestamps and a recoverable interaction anchor. SEP treats bridge-entity degree as a proxy for popularity or unexpectedness. ETD depends on a declared taxonomy and denominator for legal path types. These definitions are auditable but do not exhaust explanation quality and cannot be collapsed into one latent construct. Their conceptual source is verified through XRecSys, while the exact formulas and data assumptions evaluated here remain repository-specific [@balloccu2022xrecsys].

Native-path fidelity also affects strict accuracy. When a model cannot produce ten unique unseen path-ending items, the evaluator preserves the short or empty list, counts missing slots as non-hits, and reports slot coverage instead of padding with non-path recommendations. This policy protects the native-path contract, but strict accuracy can consequently reflect both recommendation quality and native-path candidate availability.

The current package contains no user study and therefore supports claims about computational path properties, not perceived usefulness, understanding, persuasiveness, or trust. No statistical-significance test artifact has been identified, and its final status requires manual checking. Numerical differences in Chapters 4 and 5 must remain observed experimental differences rather than inferential population claims.

Evidence quality also depends on model ports, canonical ID recovery, export completeness, and path validation. A blocked row may result from an incomplete data contract or unsupported mechanism requirement rather than weak model performance. Conversely, a PASS row establishes conformity with the registered evaluation contract, not universal correctness outside it.

Finally, the external citation layer is closed at draft level but not frozen for final submission. Primary sources for PGPR, UCPR, CAFE, TPRec, KGGLM, and XRecSys/LIR/SEP/ETD are verified. PEARLM remains safe as an arXiv citation, but its final venue and publisher DOI require manual checking. The same final-publication caveat applies to the “Measuring Why” survey if it is introduced later. These metadata gaps do not change the internal evidence, and external papers continue to support model or metric context rather than repository experimental values.

Table 5.4 consolidates these limitations, their implications, and possible mitigations. They define the valid scope of the current results and motivate the evidence-coverage, robustness, human-evaluation, and reproducibility recommendations in Chapter 6.

# Chapter 6 Conclusion and Recommendations

## 6.1 Conclusion

Building on the evidence boundaries established in Chapter 5, this dissertation addressed a comparison problem in knowledge graph recommendation. Native-path recommenders can differ in data representation, identifier space, path format, and inference procedure, making raw outputs unsuitable for direct comparison. The work therefore developed and evaluated a canonical native-path evaluation and analysis framework. It did not introduce a new recommender model.

The framework's first contribution is comparability. A canonical dataset layer defines shared users, items, interaction splits, labels, knowledge-graph provenance, and mapping requirements, while model-specific views preserve the flexibility required by individual implementations. Recommendations and native paths must return to canonical user and item identifiers through a shared export contract. Validation gates then determine whether each model-dataset row is complete and internally consistent enough to support reporting.

Chapter 3 established that this validation-first design can support the intended empirical programme. It specified recommendation and path exports, separated native explanation from post-hoc path recovery, and registered distinct evidence streams for strict accuracy, alpha-sweep trade-offs, and ablation. LastFM and ML-1M provide complete six-model native-path experiment sets. Blocked and not-applicable rows are reported as incomplete evaluation contracts rather than interpreted as poor model performance.

The second contribution is multidimensional measurement. Chapter 4 compared PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM on the two complete datasets. Strict accuracy leadership changes with dataset and metric, and the model leading a strict measure is not necessarily the model with the largest explanation-metric movement. The evidence therefore supports model-, dataset-, and metric-specific trade-off profiles rather than a universal ordering.

LIR, SEP, and ETD make different parts of those profiles visible. LIR concerns the recency of the historical interaction linked by a path, SEP uses degree-derived serendipity of the bridge entity, and ETD represents diversity among path types. Their endpoint movements differ across models and datasets. No movement in one metric can be treated as an equivalent movement in another or as a complete measure of explanation quality.

The third contribution is bounded interpretation. Chapter 5 tested whether explanation-oriented objectives could be controlled under an explicit ranking-utility condition. The PGPR/UCPR ablation preserves the registered alpha=0 baseline and identifies operating points under the declared NDCG-retention rule. This demonstrates framework controllability over the registered path or explanation selection protocol. It does not establish improvement in the underlying recommender and does not replace the six-model main results.

The mechanism synthesis further distinguishes observation from explanation. Trade-off behaviour varies with model, dataset, and explanation metric, and path-generation or path-selection mechanisms provide useful interpretive context. Beyond the registered ablation, however, the current evidence does not support causal attribution. This graded claim structure prevents architectural descriptions or plausible hypotheses from being reported as demonstrated mechanisms.

Amazon-Book KGAT makes the same principle visible at the dataset boundary. KGGLM, PEARLM, and PGPR have reportable rows, while UCPR, CAFE, and TPRec are blocked or not applicable under the current evidence. No approved Amazon explanation alpha sweeps are available. Amazon-Book is therefore a partial stress test rather than a complete main experiment. Its contribution is to show that validation can expose incomplete model ports, unsupported timestamp semantics, and missing metric contracts before they enter a comparison.

Taken together, the framework makes the accuracy–explainability trade-off of native-path knowledge graph recommenders measurable, comparable, and auditable under a shared contract. Explicit ranking and path metrics provide measurability. Canonical identifiers, common validation gates, and separated evidence roles provide comparability. Export checks, provenance records, figure and table sources, and explicit unsupported-row statuses provide auditability. The resulting contribution is a reproducible basis for evaluation without a claim of a new recommendation algorithm or universal model superiority.

The conclusion remains bounded by the registered evidence. The twelve expected LastFM and ML-1M row-level strict-accuracy JSON artifacts are not accessible; the draft values are currently traceable to the canonical status matrix and the exactly matching final accuracy summary. No statistical-significance artifact or user-study artifact is registered, so numerical comparisons remain descriptive and the computational path metrics do not establish user-perceived explanation quality.

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

[To be generated from verified BibTeX in a later formatting goal.]

# Appendix

[Appendix tables, extended figures, and traceability materials to be selected in a later integration goal.]
