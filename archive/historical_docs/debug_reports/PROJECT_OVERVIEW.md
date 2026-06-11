# Project Overview

This repository is the evaluation and experiment-tracking hub for explainability benchmarking of KG-aware recommender systems.

Its main job is not to train every model itself. Its main job is to:

1. prepare or standardize model outputs,
2. convert them into xrecsys-compatible path CSVs,
3. run recommendation-quality and explanation-quality evaluation,
4. keep experiment records, diagnostics, and reliability notes in one place.

## Core Repository Boundary

Current model boundary:
- Embedded model stack: `PGPR` remains inside `xrecsys/models/PGPR/` because xrecsys depends on it directly.
- External model stacks: models such as `VRKG4Rec`, `KGIN`, and future baselines are expected to live outside this repository.
- Adapter responsibility: convert model outputs or checkpoints into xrecsys-compatible path CSVs.
- Evaluation responsibility: run xrecsys metrics over those exported paths.

In practice, this repository is best thought of as:

`external or internal recommender -> adapter -> xrecsys path CSVs -> xrecsys metrics -> runs/reports/docs`

## Why Adapters Matter

xrecsys is not a generic "any path is fine" evaluator.
It expects explanation paths that can support all three explanation metrics:

- `LIR`: requires a clear interaction anchor item in the path,
- `SEP`: requires a clear bridge entity in the path,
- `ETD`: requires a stable explanation type, usually tied to the final relation.

So adapters do more than file conversion.
They define how a model's notion of recommendation or explanation is projected into xrecsys's path grammar.

This is especially important because different model families do not produce explanations in the same way.

## Three Model Families

The current project is most naturally organized around three explanation-source families.

### 1. RL-Based Reasoning Models

Example:
- `PGPR`

Typical behavior:
- the model already reasons over KG paths,
- recommendation and explanation are tightly coupled,
- the adapter mostly standardizes and filters native path outputs.

Adapter goal:
- preserve native reasoning paths as much as possible,
- choose the representative path per item,
- export into xrecsys format with minimal semantic distortion.

Main risk:
- even native path models may need path filtering or normalization before xrecsys can score them cleanly.

### 2. Latent GNN Models

Examples:
- `VRKG4Rec`
- `KGIN`

Typical behavior:
- the model mainly outputs latent embeddings or ranked items,
- it does not necessarily expose explicit reasoning paths,
- explanation must be reconstructed post hoc on the KG.

Adapter goal:
- retrieve short KG paths that are consistent with the model's latent user-item signal,
- not merely any graph-reachable path,
- export representative paths in a form xrecsys can score.

Main risk:
- recommendation semantics and explanation semantics can easily drift apart,
- candidate-pool design, ranking preservation, and path-scoring policy all matter.

### 3. Neural-Symbolic Models

Example:
- `CAFE`

Typical behavior:
- the model may provide symbolic structures, rules, programs, or partially explicit reasoning objects,
- these objects are often more structured than latent GNN outputs but not always identical to xrecsys path strings.

Adapter goal:
- preserve the symbolic explanation unit if possible,
- map it into xrecsys-compatible path form without losing the key semantics,
- document clearly what is preserved and what is projected.

Main risk:
- symbolic explanations may not align one-to-one with xrecsys path templates,
- projection choices may change what `LIR`, `SEP`, and `ETD` really mean.

## Current Practical Interpretation

In this repository, the three families currently imply three adapter strategies:

- `PGPR`: native path standardization
- `VRKG4Rec` / future latent GNNs: latent-consistent post-hoc path retrieval
- `CAFE` / future neural-symbolic models: symbolic explanation projection

This distinction is important because different errors happen at different layers:

- native path models are more vulnerable to path filtering or top-k policy issues,
- latent GNN models are more vulnerable to post-hoc retrieval and ranking mismatch,
- neural-symbolic models are more vulnerable to projection mismatch.

## Why xrecsys Constraints Feel Strong

`xrecsys` does not only ask whether a user-item pair is graph-reachable.
It asks whether the exported explanation path has a stable semantic structure that supports all three explanation metrics at once.

In practice, the framework assumes a short structured path in which it can reliably identify:

1. an interaction-anchor item for `LIR`,
2. a bridge entity for `SEP`,
3. a stable explanation type, usually tied to the final relation, for `ETD`.

This is why `xrecsys` feels stricter than a generic DFS/BFS path search:

- a graph-reachable path is not automatically an `xrecsys`-usable path,
- a long or weakly structured path may exist in the KG but still be unsuitable for stable `LIR / SEP / ETD` computation,
- the adapter must therefore do semantic standardization, not just graph traversal.

So the real constraint is not:
- `can the KG connect user and item at all?`

It is:
- `can we export a path whose semantic slots are stable enough for xrecsys metrics?`

## Same KG Does Not Mean Same Explanation Quality

Two models can operate on the same KG and still produce very different explanation-quality distributions.

Why:

- `xrecsys` evaluates the selected representative path, not abstract reachability,
- the same user-item pair can often be connected by multiple valid paths,
- different chosen paths can yield different `LIR`, `SEP`, and `ETD` values even if the target item is identical.

For the same target item, path differences can come from:

- a different historical anchor item,
- a different bridge entity,
- a different final relation type.

Those differences are exactly what xrecsys reads when computing:

- `LIR`: interaction anchor recency,
- `SEP`: bridge popularity,
- `ETD`: explanation type diversity across the top-k.

So shared KG structure does not force shared explanation-quality behavior.
What matters is which path a model or adapter ultimately chooses to represent each recommendation.

## Native Path Models vs Post-Hoc Path Models

This project currently sits across both sides of that divide.

### PGPR

`PGPR` is closer to a native path model:

- it already reasons over paths,
- recommendation and explanation are more tightly coupled,
- the adapter mostly standardizes and filters path outputs that are already path-like.

That does not mean:

- PGPR is automatically more accurate,
- every PGPR top-k item always has a perfect path,
- every PGPR internal path is already in ideal xrecsys form.

It means:

- PGPR is easier to standardize into xrecsys path grammar,
- its explanations are more naturally connected to the model's own decision process.

### VRKG4Rec

`VRKG4Rec` is different:

- the model primarily provides latent recommendation signals,
- it does not natively expose xrecsys-style reasoning paths,
- the current adapter reconstructs representative paths after recommendation.

So current VRKG4Rec explanations should be interpreted as:

- post-hoc exported representative paths,
- analyzable by xrecsys,
- but not automatically faithful internal reasoning traces.

This is a meaningful distinction:

- `PGPR` is closer to native path explainability,
- `VRKG4Rec` is currently closer to post-hoc path explainability.

## Current VRKG4Rec Decision Points

The current `VRKG4Rec -> adapter -> xrecsys` integration is not only a coding problem.
It also contains three design decisions that materially change the meaning of the final evaluation.

### 1. Ranking Semantics

Question:
- should exported `uid_topk` strictly preserve the model's original item ranking,
- or may the adapter re-rank items using path-derived scores?

Why it matters:

- if ranking is changed inside the adapter, `NDCG / HR / Recall / Precision` are no longer purely the original model's recommendation metrics,
- recommendation quality becomes a mixed property of model ranking plus adapter explanation policy.

### 2. Final Top-k Alignment

Question:
- should recommendation and explanation metrics be computed on the same final explainable top-k,
- or should recommendation metrics still include items without explanations?

For tradeoff analysis, the stronger interpretation is:

- recommendation quality and explanation quality should be computed on the same final exported top-k,
- otherwise the tradeoff is not being measured on one coherent system output.

### 3. Candidate-Selection Policy

Question:
- should the final explainable top-k be chosen only from raw top-10 items,
- or from a larger candidate window such as top-50?

Why it matters:

- this choice does not change xrecsys metric formulas,
- but it does change the mechanism used to construct the final explainable recommendation list,
- and therefore changes both baseline and tradeoff behavior.

The `cand50` experiment should therefore be interpreted as:

- a mechanism variant,
- not merely a cosmetic repair of the old output.

## Current High-Risk Points in the VRKG4Rec Integration

At the moment, the biggest risks are not in the abstract theory of the model family, but in the actual documented integration path used in this repository.

The current highest-risk issues are:

1. `uid_topk` may not preserve original VRKG4Rec ranking semantics.
2. Items without explanations may still enter the exported top-k.
3. The candidate pool can be too narrow, producing incomplete explainable top-k lists before xrecsys even starts evaluating.

These risks are documented in detail in:
- `docs/guides/VRKG4REC_INTEGRATION_RISKS.md`

They are also linked to concrete validation results in:
- `docs/guides/PIPELINE_RELIABILITY_LOG.md`

## Candidate-Window Variants

Candidate-window variants such as `cand50` are important enough to name explicitly.

Interpret them as:

- keeping the same xrecsys metric definitions,
- while changing the policy used to generate the final explainable top-k.

This means:

- they are useful for mechanism comparison,
- they can improve explainable coverage substantially,
- but they should not be confused with the raw original mechanism.

For latent GNN models, this kind of mechanism study is especially relevant because the explanation layer is already post-hoc and policy-sensitive.

## Current VRKG4Rec Status

The current `VRKG4Rec -> lastfm -> xrecsys` integration is usable for exploratory analysis, but it is still under reliability review.

What is already clear:
- the current adapter produces post-hoc explanations rather than native reasoning traces,
- the current adapter can change ranking semantics before xrecsys evaluates them,
- the current candidate-pool policy strongly affects explainable coverage,
- explanation-quality analysis is meaningful, but it must be interpreted as analysis of the exported representative paths, not automatic proof of model-internal reasoning.

Important related documents:
- `docs/guides/VRKG4REC_INTEGRATION_RISKS.md`
- `docs/guides/PIPELINE_RELIABILITY_LOG.md`
- `docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md`

## Directory Roles

- `adapters/`: model-specific conversion and data-prep logic.
- `xrecsys/`: evaluation engine, datasets, path files, logs, and results.
- `runs/`: mirrored experiment records for both internal and external models.
- `reports/`: curated figures, tables, and summaries.
- `docs/guides/`: durable project documentation.
- `docs/plans/`: planning and roadmap documents that may not match current implementation.
- `docs/handoffs/`: historical snapshots and exported handoff packages.
- `archive/`: deprecated or temporary artifacts not needed for the main workflow.

## Key Review Documents

- `docs/guides/DATA_PROVENANCE.md`: where datasets, KG files, labels, and path exports come from.
- `docs/guides/PIPELINE_RELIABILITY_LOG.md`: running review log for reliability risks, fixes, and validation results.
- `docs/guides/VRKG4REC_INTEGRATION_RISKS.md`: focused review of the highest-risk parts of the current VRKG4Rec integration.
- `docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md`: reusable post-hoc path-retrieval template for latent GNN recommenders.
