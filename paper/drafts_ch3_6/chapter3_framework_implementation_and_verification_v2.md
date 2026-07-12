# Chapter 3 Framework Implementation and Verification

## 3.1 Overview of the Implemented Framework

This chapter describes the implemented evaluation framework used in the later empirical chapters. The framework is designed for knowledge graph recommender systems whose explanations are native to the recommendation process. It does not introduce a new recommender model. Its contribution is an evaluation and verification framework that makes heterogeneous native-path recommenders comparable under a shared contract.

The framework separates five concerns: canonical dataset truth, model-specific views, native-path export, validation gates, and metric reporting. This separation is necessary because path-based recommenders often use different internal graph schemas, identifier spaces, search procedures, and path formats. A direct comparison of their raw outputs would therefore mix model performance with data-format and mapping differences.

The implemented workflow begins with a canonical dataset layer. Each dataset defines shared user identifiers, item identifiers, interaction splits, labels, and KG provenance. Individual models may then build their own training views from this layer. After inference, model outputs must be exported back into canonical `uid` and `pid` space before evaluation. The validation layer checks whether exported recommendations and explanation paths satisfy the framework contract. Only rows that pass this validation are treated as reportable experimental evidence.

The framework is therefore validation-first. A model/dataset row can be complete, blocked, or not applicable. A blocked row is not interpreted as poor recommendation performance; it means that the current repository evidence does not support faithful scoring for that row.

## 3.2 Canonical Dataset and Model View Construction

The canonical dataset layer defines the model-independent evaluation space. For each dataset, it specifies canonical users, canonical products, train/validation/test interactions, evaluation labels, upstream KG assets, and mapping requirements. This design is documented in `docs/guides/CANONICAL_DATASET_STANDARD.md`.

The canonical layer does not require every recommender to ingest the same internal graph. This is a deliberate design choice. Native-path models may require different relation vocabularies, entity pruning strategies, compact identifiers, or path-search constraints. The framework therefore standardises the comparison contract rather than forcing a single internal representation.

Model-specific views are generated from the canonical layer. Examples include PGPR, UCPR, CAFE, hopwise, and RecBole-oriented views. These views may remap identifiers internally, but their exports must return to canonical identifiers. The key rule is that internal model identifiers may differ, while exported `uid_topk.csv`, `pred_paths.csv`, and `uid_pid_explanation.csv` must use canonical `uid` and `pid` values.

The main complete datasets for the dissertation are LastFM and ML-1M. The final handoff and dataset audit identify both as complete six-model native-path comparisons. Amazon-Book KGAT is retained as a partial stress test and boundary case. It has complete rows for KGGLM, PEARLM, and PGPR, while UCPR, CAFE, and TPRec are blocked under current evidence.

## 3.3 Native-Path Export Contract and Implementation

The export contract defines the minimum files required for a model to be evaluated as a native-path recommender. A complete native-path row must provide:

- `uid_topk.csv`, containing ranked recommendation lists for canonical users;
- `pred_paths.csv`, containing candidate or selected recommendation paths;
- `uid_pid_explanation.csv`, containing the path used to explain each user-item recommendation.

For non-path recommenders or accuracy-reference models, `uid_topk.csv` is sufficient for accuracy evaluation, but explanation metrics are not assigned. This distinction is central to the dissertation. Post-hoc path recovery is not treated as equivalent to native-path explanation because it does not necessarily represent the model's actual recommendation mechanism.

The path format used by the evaluation layer is a sequence of relation/entity-type/entity-id triples. For LastFM and ML-1M, the standard path begins at a user, moves through a seed interaction from the user's training history, passes through a KG bridge entity, and ends at the recommended item. This structure is used by the LIR, SEP, and ETD metrics.

The contract is implemented through export scripts and validation scripts rather than through a new model architecture. The validation evidence shows that LastFM and ML-1M pass the required export checks for six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM.

## 3.4 Evaluation and Validation Pipeline

The evaluation pipeline computes strict accuracy metrics and explanation metrics from different evidence sources. Strict accuracy is computed from the recommendation export and canonical labels. The reported strict accuracy metrics are HR@10, NDCG@10, Precision@10, and Recall@10.

Explanation metrics are computed from native paths. LIR measures whether the path is anchored in recent linked user interactions. SEP measures the serendipity of the bridge entity in the path. ETD measures the diversity of explanation path types across a user's recommendations. These metrics are implemented through the xrecsys path-metric stack and documented in `docs/guides/PATH_METRICS_GUIDE.md`.

The validation pipeline checks whether exported files can be safely evaluated. The checks include canonical test-user coverage, top-k coverage, duplicate recommendation checks, seen-item leakage checks, path endpoint consistency, top-k/explanation alignment, candidate-path consistency, and score-range validity. The current validation status table records 15 passing export-validation rows and 3 blocked Amazon-Book KGAT rows.

The pipeline distinguishes strict accuracy from alpha-sweep trade-off evidence. Strict accuracy values come from accuracy JSON files and the final accuracy summary table. Alpha-sweep values come from trade-off CSVs, where the recommendation objective is varied by an alpha parameter. The alpha-sweep results are used to study trade-off behaviour, not to replace strict accuracy results.

## 3.5 Framework Verification Results

The framework verification results show that the implemented contract is complete for the two main datasets. LastFM has passing validation for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. ML-1M also has passing validation for the same six models. These rows provide the experimental basis for the main accuracy and trade-off results in Chapter 4.

The validation results also show why Amazon-Book KGAT is treated differently. KGGLM, PEARLM, and PGPR pass validation on Amazon-Book KGAT, but UCPR, CAFE, and TPRec are blocked or not applicable under current evidence. The blocked rows reflect implementation and data-contract limitations rather than measured recommendation quality.

The strict accuracy snapshot confirms that LastFM and ML-1M have complete accuracy values for all six native-path models. Amazon-Book KGAT has strict accuracy values only for the three complete rows. It has no valid explanation alpha sweeps in the current evidence pack, so it must not be presented as a complete trade-off experiment.

Representative alpha-sweep endpoint examples confirm that explanation metrics can be computed for LastFM and ML-1M. For example, LastFM PGPR shows LIR moving from 0.0062 at alpha=0 to 0.0219 at alpha=1, while ML-1M PGPR shows LIR moving from 0.4655 to 0.9627. These endpoint examples verify the operation of the trade-off pipeline. Their interpretation as model behaviour is deferred to Chapters 4 and 5.

## 3.6 Trade-off and Ablation Experiment Setup

The trade-off experiments use alpha sweeps to vary the optimisation emphasis between recommendation quality and explanation-oriented objectives. The main datasets for this analysis are LastFM and ML-1M. The main models are the six native-path models with passing validation on those datasets.

The trade-off analysis is organised by explanation metric: LIR-oriented, SEP-oriented, and ETD-oriented sweeps. This organisation is necessary because the metrics measure different path properties. LIR concerns interaction recency, SEP concerns bridge-entity rarity, and ETD concerns explanation type diversity. They should not be treated as interchangeable measures of a single generic explanation score.

The ablation experiments are separate from the main six-model trade-off analysis. The PGPR/UCPR path-module ablation evidence is stored under `reports/tables/ablation/pgpr_ucpr_path_module/` and `reports/figures/ablation/pgpr_ucpr_path_module/`. These files are used in Chapter 5 to analyse controllability and mechanism-level effects.

Chapter 4 uses the verified strict accuracy, explanation endpoint, and trade-off evidence as the main result set. Chapter 5 uses ablation, mechanism, and boundary-case evidence. Chapter 6 summarises these findings and introduces no new experimental results.

