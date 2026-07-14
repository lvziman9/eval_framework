# Chapter 3 Framework Implementation and Verification

## 3.1 Overview of the Implemented Framework

Chapter 2 showed that existing knowledge graph recommendation, path-reasoning, explainability, and benchmarking research supplies complementary methods and evaluation concepts without making heterogeneous native-path outputs automatically comparable. Fair comparison therefore requires more than applying the same ranking metrics to raw model outputs. The models can differ in graph schema, identifier space, search procedure, path format, and export behaviour, so an uncontrolled comparison can confound model performance with differences in data preparation and representation. This chapter addresses that comparability problem by describing the evaluation framework used in the later empirical chapters. The framework does not introduce a new recommender model; it provides a shared evaluation and verification contract for heterogeneous native-path recommenders.

The implemented architecture separates five concerns: canonical dataset truth, model-specific views, native-path export, validation gates, and metric reporting. Each concern resolves a distinct source of ambiguity. The canonical layer defines the shared evaluation population and labels. Model-specific views preserve the internal representations required by individual recommenders. Native exports retain the paths produced within the recommendation process. Validation determines whether those exports meet the common contract, and metric reporting keeps ranking and explanation evidence in their proper roles.

Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit. The Batch 1C framework dataflow specification expands that workflow from canonical dataset truth through native-path exports and validation to the separate Chapter 4 and Chapter 5 evidence roles; it describes an evaluation process rather than a new recommender architecture.

The workflow therefore begins from a canonical dataset layer containing shared user identifiers, item identifiers, interaction splits, labels, and knowledge-graph provenance. Individual models build the training views they require from this layer, but their outputs must return to canonical `uid` and `pid` space before evaluation. The validation layer then checks whether the recommendations and explanation paths are complete and internally consistent. Only rows that pass these checks are admitted as reportable experimental evidence.

This validation-first design makes evidence eligibility explicit. A model-dataset row can be complete, blocked, or not applicable. A blocked row is not evidence of poor recommendation performance; it means that the current repository does not support faithful scoring for that row. The framework thus defines both how supported results can be compared and where comparison must stop.

The notation used to formalise this evaluation contract is summarised below.

| Symbol | Meaning |
| --- | --- |
| \(\mathcal{D}\) | Set of datasets considered in the framework |
| \(d\) | Dataset index |
| \(\mathcal{U}_d\) | Canonical user set for dataset \(d\) |
| \(\mathcal{I}_d\) | Canonical item set for dataset \(d\) |
| \(\mathcal{G}_d\) | Knowledge graph associated with dataset \(d\) |
| \(\mathcal{M}\) | Set of native-path models evaluated in the main experiments |
| \(m\) | Model index |
| \(\hat{R}_{u}^{K,m,d}\) | Top-\(K\) recommendation list for user \(u\), model \(m\), dataset \(d\) |
| \(p_{u,i}^{m,d}\) | Native path associated with recommendation item \(i\) for user \(u\) |
| \(V_{m,d}\) | Validation eligibility indicator for model-dataset row \((m,d)\) |
| \(q\) | Explanation objective, one of LIR, SEP, or ETD |
| \(\alpha\) | Trade-off control parameter |

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

## 3.3 Native-Path Export Contract and Implementation

Comparable identifiers are necessary but insufficient when the explanation itself is part of the model evidence. The export contract therefore defines the minimum artifacts required for a complete native-path row:

- `uid_topk.csv`, containing ranked recommendation lists for canonical users;
- `pred_paths.csv`, containing candidate or selected recommendation paths;
- `uid_pid_explanation.csv`, containing the path used to explain each user-item recommendation.

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

The Batch 1C single-example trace illustrates this alignment with abstract placeholders for a canonical user, seed item, bridge entity, and recommended item. It is a schematic dataflow aid rather than an experimental row, and it assigns no identifier, score, validation status, or performance value.

The contract is implemented through export and validation scripts rather than through a new model architecture. The registered validation evidence shows that LastFM and ML-1M satisfy the required export checks for all six native-path models: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. These exports provide the model-faithful evidence on which Chapters 4 and 5 depend.

## 3.4 Evaluation and Validation Pipeline

The pipeline must determine not only how evidence is scored, but whether it is admissible. It therefore computes strict accuracy and explanation metrics from separate evidence sources and applies validation before either stream is interpreted.

Strict accuracy is computed from canonical labels and the recommendation export. The reported metrics are HR@10, NDCG@10, Precision@10, and Recall@10. Explanation metrics are computed from native paths through the xrecsys path-metric stack documented in `docs/guides/PATH_METRICS_GUIDE.md`. The dissertation cites XRecSys for the conceptual origin of recency, shared-entity scoring, and explanation-type diversity, while the exact evaluated LIR, SEP, and ETD formulas remain repository-specific [@balloccu2022xrecsys]. LIR measures whether the path is anchored in recent linked user interactions, and ETD measures the diversity of explanation path types across a user's recommendations. SEP is a repository-specific bridge-entity score. SEP follows the XRecSys-style explanation-metric setting but is interpreted here through the implemented repository metric pipeline. These dimensions remain separate because they describe different path properties rather than one generic explanation score.

Before reporting, the validation pipeline checks canonical test-user coverage, top-k coverage, duplicate recommendations, seen-item leakage, path endpoint consistency, top-k/explanation alignment, candidate-path consistency, and score ranges. The current validation status table contains 15 passing export-validation rows and 3 blocked Amazon-Book KGAT rows. Passing status establishes conformity with the registered contract; blocked status prevents unsupported rows from entering the comparison.

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

The Batch 1C validation-gate flowchart expands these checks as a reportability decision sequence. Its PASS and BLOCKED or PARTIAL terminals describe evidence eligibility and do not represent recommendation-performance levels.

Let \(R_u^+\) denote the relevant canonical test items for user \(u\). The strict ranking metrics are

\[
\mathrm{HR@K}
=
\frac{1}{|\mathcal{U}_{test}|}
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
\frac{1}{|\mathcal{U}_{test}|}
\sum_{u \in \mathcal{U}_{test}}
\frac{
|\hat{R}_{u}^{K,m,d} \cap R_u^+|
}{K},
\]

\[
\mathrm{Recall@K}
=
\frac{1}{|\mathcal{U}_{test}|}
\sum_{u \in \mathcal{U}_{test}}
\frac{
|\hat{R}_{u}^{K,m,d} \cap R_u^+|
}{
|R_u^+|
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
\frac{1}{|\mathcal{U}_{test}|}
\sum_{u \in \mathcal{U}_{test}}
\frac{
\mathrm{DCG@K}(u)
}{
\mathrm{IDCG@K}(u)
}.
\]

Here, \(\mathrm{IDCG@K}(u)\) uses \(\min(K,|R_u^+|)\) relevant gains, as required by the canonical evaluator. Short native-path lists preserve missing positions as non-hits rather than introducing non-path padding. These are strict accuracy metrics. They are reported separately from alpha-sweep paired ranking metrics.

For explanation scoring, the repository-specific path anchors are

\[
a(p_{u,i}) = e_1,
\quad
b(p_{u,i}) = e_{L-1},
\quad
\tau(p_{u,i}) = r_L.
\]

The function \(a(p_{u,i})\) denotes the linked historical seed item, \(b(p_{u,i})\) denotes the bridge entity, and \(\tau(p_{u,i})\) denotes the path type used for diversity. The Batch 1C metric-anchor schematic maps these three path positions to LIR, SEP, and ETD. It is a definition aid and preserves the repository-specific boundary of each metric. The corresponding path-level definitions are

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
\left|
\left\{
\tau(p_{u,i}) : i \in \hat{R}_{u}^{K,m,d}
\right\}
\right|
}{
|\mathcal{T}_d|
},
\]

where \(\mathcal{T}_d\) denotes the legal path-type set for dataset \(d\). ETD is user-level path-type diversity over the top-\(K\) explanation set.

For \(q \in \{\mathrm{LIR},\mathrm{SEP}\}\), user- and dataset-level aggregation are

\[
Q_{u,m,d}^{q}
=
\frac{1}{|\hat{R}_{u}^{K,m,d}|}
\sum_{i \in \hat{R}_{u}^{K,m,d}}
q(p_{u,i}^{m,d})
\]

and

\[
Q_{m,d}^{q}
=
\frac{1}{|\mathcal{U}_{test}|}
\sum_{u \in \mathcal{U}_{test}}
Q_{u,m,d}^{q}.
\]

For ETD, the user-level quantity is the diversity ratio defined above rather than a simple average of path-level scores. These definitions follow the validated path alignment contract; the exact missing-anchor and normalisation behaviour remains governed by the repository implementation.

The pipeline also separates strict accuracy from alpha-sweep trade-off evidence. The strict values used in this draft are currently traceable to `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`. The twelve expected row-level primary accuracy JSON files are not accessible in the current worktree and must not be described as directly inspected. Alpha-sweep values come from trade-off CSVs in which an alpha parameter varies the recommendation objective. The former describe validated ranking outputs, while the latter describe response trajectories under an explanation-oriented control. Alpha-sweep values are therefore not substitutes for strict accuracy results.

Figure 3.2 summarises this design by showing how the alpha sweep generates metric-specific trade-off evidence after the baseline and evaluation contract have been established. The separation of sources ensures that later chapters can state exactly whether a claim concerns strict performance, sweep behaviour, or ablation.

## 3.5 Framework Verification Results

Verification tests whether the implemented contract can support the intended comparison and identify cases in which it cannot. For the two main datasets, the result is complete: LastFM passes validation for PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM, and ML-1M passes for the same six models. These rows establish the empirical basis for the strict accuracy and trade-off analysis in Chapter 4.

Amazon-Book KGAT demonstrates the other function of verification. KGGLM, PEARLM, and PGPR pass validation, whereas UCPR, CAFE, and TPRec are blocked or not applicable under the current evidence. The blocked rows record implementation and data-contract limitations, not measured recommendation quality. By distinguishing these statuses before comparison, the framework prevents absent or unsupported results from being interpreted as model outcomes.

The strict accuracy snapshot follows the same boundary. LastFM and ML-1M contain complete strict accuracy values for all six native-path models. Amazon-Book KGAT contains strict values only for the three complete rows and has no valid explanation alpha sweeps in the current evidence pack. It can therefore support a partial boundary analysis, but not a complete six-model trade-off experiment.

Representative endpoints additionally verify that the trade-off pipeline operates on the two complete datasets. LastFM PGPR LIR moves from 0.0062 at alpha=0 to 0.0219 at alpha=1, while ML-1M PGPR LIR moves from 0.4655 to 0.9627. At this stage, these values confirm computation and export continuity. Their interpretation as model behaviour belongs to Chapters 4 and 5.

## 3.6 Trade-off and Ablation Experiment Setup

With the evidence contract verified, the next question is whether supported models exhibit common or heterogeneous relationships between ranking utility and explanation properties. The trade-off experiments address this question on LastFM and ML-1M using the six native-path models that pass validation on both datasets. Recommendation exports are evaluated at top-k 10, and strict ranking is reported through HR@10, NDCG@10, Precision@10, and Recall@10. The same canonical user, item, label, export, and validation contract is applied across models, while model-native training and inference remain heterogeneous.

The framework standardises the evaluation contract, exported artifacts, validation gates, and metric computation. It does not claim that heterogeneous models share identical internal hyperparameter spaces. PGPR, UCPR, and CAFE are represented by registered canonical exports and implementation-log provenance, whereas the accessible TPRec, KGGLM, and PEARLM pipeline scripts declare more of their stage, architecture, and inference configuration directly. The generated historical run tree and checkpoint files are not present in the current evidence package, so exact checkpoint identities and several model-native optimiser settings cannot be re-inspected. Detailed model-native hyperparameters are retained in their respective configuration or execution sources where available; parameters not accessible in the current evidence package are not reconstructed or inferred.

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

| Quantity | Evidence source | Used for | Not used for |
| --- | --- | --- | --- |
| Strict HR@10 / NDCG@10 / Precision@10 / Recall@10 | Canonical status matrix and final accuracy summary | Strict ranking comparison | Explanation trade-off trajectory |
| Sweep NDCG | Alpha-sweep outputs | Paired ranking response under an explanation objective | Strict accuracy ranking |
| LIR / SEP / ETD endpoints | Explanation metric outputs | Explanation-property response | User-perceived explanation quality |
| Ablation retention | PGPR / UCPR ablation artifacts | Controllability under the ablation setting | Six-model model superiority |
| Boundary validation state | Validation status matrix | Reportability and boundary detection | Performance comparison |

The Batch 1C evidence-stream separation diagram visualises these five roles. It is intentionally separate from the alpha-sweep process diagram so that strict accuracy, explanation endpoints, main sweeps, PGPR/UCPR ablation, and boundary validation cannot be read as interchangeable measurements.

The configuration and provenance boundary is summarised below. The detailed model-by-dataset audit is retained in `EXPERIMENT_CONFIGURATION_PROVENANCE.md` for later appendix use.

| Configuration item | Setting / provenance | Evidence source | Interpretation boundary |
| --- | --- | --- | --- |
| Main datasets and models | LastFM and ML-1M; six validated native-path models on each dataset | Export validation manifest and canonical status matrix | Amazon-Book KGAT is a partial boundary case, not a third complete main experiment. |
| Model-native training and inference | Heterogeneous model-specific pipelines; directly available settings are recorded in the Batch 1 provenance audit | Model pipeline scripts, implementation log, and export registry | The framework does not impose or imply one shared hyperparameter space. |
| Canonical recommendation cut-off | Top-k 10 | `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py` | Short native-path lists may remain short; non-path recommendations are not used for padding. |
| Strict ranking evaluation | HR@10, NDCG@10, Precision@10, and Recall@10 | Canonical status matrix and final accuracy summary | The twelve expected primary row-level accuracy JSON files are unavailable. |
| Explanation objectives | Separate LIR-, SEP-, and ETD-oriented sweeps | `scripts/hopwise/run_canonical_xrecsys_protocol.sh` | The exact metric implementation and data assumptions remain repository-specific. |
| Alpha grid | 0.00 to 1.00 inclusive at 0.05 intervals, yielding 21 points | `scripts/validation/validate_xrecsys_sweeps.py` | Paired sweep ranking metrics are not substitutes for strict accuracy. |
| Validation gate | Exact canonical test-user coverage, unique top-k items, leakage checks, endpoint checks, candidate consistency, and explanation alignment | Export validator and per-row validation summaries | PASS establishes conformity with the registered contract rather than universal correctness. |
| Random seeds and exact checkpoint identities | Not available in the current evidence package for the complete six-model set | Batch 1 provenance audit | Missing values are not inferred from framework or library defaults. |
| PGPR/UCPR ablation | Frozen original top-k item set with exact alpha=0 preservation and a declared NDCG-retention analysis | `reports/tables/ablation/pgpr_ucpr_path_module/` | Separate from both the six-model sweep and strict final accuracy. |

The ablation experiments therefore form a separate evidence stream. The PGPR/UCPR path-module evidence is stored under `reports/tables/ablation/pgpr_ucpr_path_module/` and `reports/figures/ablation/pgpr_ucpr_path_module/`. Chapter 5 uses these files to examine bounded controllability and mechanism-level effects; they do not replace the six-model trade-off comparison or supply mechanism evidence for CAFE, TPRec, KGGLM, or PEARLM.

Chapter 4 uses the verified strict accuracy, explanation endpoint, and alpha-sweep evidence to report empirical patterns and result-level findings. Chapter 5 then asks which observations can be strengthened by the registered ablation, which mechanism interpretations remain descriptive, and where dataset coverage reaches a boundary. Chapter 6 synthesises those findings without introducing new experimental results.
