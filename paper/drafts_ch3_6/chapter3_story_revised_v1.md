# Chapter 3 Framework Implementation and Verification

## 3.1 Overview of the Implemented Framework

Fair comparison among native-path knowledge graph recommenders requires more than applying the same ranking metrics to their raw outputs. The models can differ in graph schema, identifier space, search procedure, path format, and export behaviour, so an uncontrolled comparison can confound model performance with differences in data preparation and representation. This chapter addresses that comparability problem by describing the evaluation framework used in the later empirical chapters. The framework does not introduce a new recommender model; it provides a shared evaluation and verification contract for heterogeneous native-path recommenders.

The implemented architecture separates five concerns: canonical dataset truth, model-specific views, native-path export, validation gates, and metric reporting. Each concern resolves a distinct source of ambiguity. The canonical layer defines the shared evaluation population and labels. Model-specific views preserve the internal representations required by individual recommenders. Native exports retain the paths produced within the recommendation process. Validation determines whether those exports meet the common contract, and metric reporting keeps ranking and explanation evidence in their proper roles.

Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit.

The workflow therefore begins from a canonical dataset layer containing shared user identifiers, item identifiers, interaction splits, labels, and knowledge-graph provenance. Individual models build the training views they require from this layer, but their outputs must return to canonical `uid` and `pid` space before evaluation. The validation layer then checks whether the recommendations and explanation paths are complete and internally consistent. Only rows that pass these checks are admitted as reportable experimental evidence.

This validation-first design makes evidence eligibility explicit. A model-dataset row can be complete, blocked, or not applicable. A blocked row is not evidence of poor recommendation performance; it means that the current repository does not support faithful scoring for that row. The framework thus defines both how supported results can be compared and where comparison must stop.

## 3.2 Canonical Dataset and Model View Construction

The first requirement for controlled comparison is a model-independent evaluation space. For each dataset, the canonical layer specifies users, products, train/validation/test interactions, evaluation labels, upstream knowledge-graph assets, and mapping requirements. This design is documented in `docs/guides/CANONICAL_DATASET_STANDARD.md` and provides the shared truth against which model exports are evaluated.

Canonicalisation does not require every recommender to consume an identical internal graph. Such a requirement would be incompatible with native-path models that depend on different relation vocabularies, entity-pruning strategies, compact identifiers, or path-search constraints. The framework instead standardises the comparison contract while allowing model-specific execution.

Model views are generated from the canonical layer for PGPR, UCPR, CAFE, hopwise, and RecBole-oriented workflows. These views may remap identifiers internally, but the reported artifacts must return to canonical identifiers. In particular, exported `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` files must use canonical `uid` and `pid` values even when the training and inference code uses a different internal namespace. This rule separates legitimate implementation variation from variation that would make outputs incomparable.

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

Strict accuracy is computed from canonical labels and the recommendation export. The reported metrics are HR@10, NDCG@10, Precision@10, and Recall@10. Explanation metrics are computed from native paths through the xrecsys path-metric stack documented in `docs/guides/PATH_METRICS_GUIDE.md`. LIR measures whether the path is anchored in recent linked user interactions, SEP measures the serendipity of the bridge entity, and ETD measures the diversity of explanation path types across a user's recommendations. These dimensions remain separate because they describe different path properties rather than one generic explanation score.

Before reporting, the validation pipeline checks canonical test-user coverage, top-k coverage, duplicate recommendations, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate-path consistency, and score ranges. The current validation status table contains 15 passing export-validation rows and 3 blocked Amazon-Book KGAT rows. Passing status establishes conformity with the registered contract; blocked status prevents unsupported rows from entering the comparison.

The pipeline also separates strict accuracy from alpha-sweep trade-off evidence. Strict values come from the accuracy JSON files and final accuracy summary table. Alpha-sweep values come from trade-off CSVs in which an alpha parameter varies the recommendation objective. The former describe validated ranking outputs, while the latter describe response trajectories under an explanation-oriented control. Alpha-sweep values are therefore not substitutes for strict accuracy results.

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
