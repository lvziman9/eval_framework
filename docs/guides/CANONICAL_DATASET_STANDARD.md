# Canonical Dataset Standard

This document defines the project-level canonical dataset layer used for cross-model explainability evaluation.

The goal is to stop comparing models through historical, model-specific data artifacts that may use different user/item id spaces, split definitions, or filtering rules. Instead, each model may have its own training format, but all model outputs must map back to the same canonical ids and evaluation labels.

Current experiment planning is tracked in [NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md). That document narrows the main explainability evaluation to models with native recommendation paths and treats non-path KG recommenders as accuracy references only.

PGPR-specific canonical data flow and the embedding-table padding bug are documented in [PGPR_CANONICAL_DATA_FLOW_2026-06-12.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PGPR_CANONICAL_DATA_FLOW_2026-06-12.md).

The active UCPR/CAFE/ML-1M implementation and execution status is tracked in [NATIVE_PATH_IMPLEMENTATION_LOG_2026-06-20.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/NATIVE_PATH_IMPLEMENTATION_LOG_2026-06-20.md).

## Motivation

The recent `lastfm` debugging showed that assets with the same dataset name can still refer to different effective evaluation spaces:

- historical `PGPR tmp/lastfm` labels,
- precomputed `PGPR` path CSVs,
- raw `xrecsys/datasets/lastfm` train/test splits,
- converted `UCPR` inputs.

All of them are useful, but they should not be silently assumed to be one identical dataset. A canonical dataset makes the comparison contract explicit.

## Definition

A canonical dataset is the model-independent source of truth for:

1. user ids,
2. product ids,
3. train/valid/test interactions,
4. evaluation labels,
5. KG source assets,
6. model-output id mapping requirements.

A model may internally remap ids into compact indices, but any exported recommendations and explanation paths must be mapped back to canonical ids before `xrecsys` evaluation.

## Required Directory Layout

```text
canonical_datasets/{dataset_name}_v1/
  README.md
  metadata.json

  interactions/
    train.tsv.gz
    valid.tsv.gz
    test.tsv.gz

  labels/
    train_label.pkl
    valid_label.pkl
    test_label.pkl

  mappings/
    user_mapping.tsv
    product_mapping.tsv

  model_views/
    pgpr/
    ucpr/
    cafe/
    recbole/
```

For the first implementation we generate the required `interactions`, `labels`, `mappings`, and `metadata.json`. KG entity/relation assets are referenced through `metadata.json` first, rather than duplicated, to avoid moving large historical files prematurely.

## Interaction Format

All canonical interaction splits use four tab-separated columns:

```text
uid    pid    rating    timestamp
```

Existing generated `lastfm_v1` and `ml1m_v1` split files store rows without a
physical header line. Consumers must therefore accept both headerless
four-column files and future files that include the documented header.

Meaning:

- `uid`: canonical user id,
- `pid`: canonical product id,
- `rating`: explicit rating when available, otherwise implicit `1`,
- `timestamp`: original timestamp when available, otherwise `-1`.

## Label Format

The canonical labels are pickle files:

```python
{
  uid: [pid1, pid2, ...]
}
```

They are used by `xrecsys` through the low-coupling override:

```bash
python xrecsys/main.py \
  --dataset <dataset> \
  --agent_topk <path-set> \
  --labels_dir canonical_datasets/<dataset>_v1/labels \
  --eval_baseline True
```

The default historical `xrecsys` behavior remains unchanged unless `--labels_dir` is explicitly provided.

## ID Policy

Each dataset has its own canonical id space. Ids do not need to match across datasets.

For `lastfm_v1`:

- canonical user id: `xrecsys` internal user kgid from `user_mappings.txt`,
- canonical product id: selected by an explicit product-id policy,
- first trial policy: `xrecsys_kgid`, meaning the product column is retained only when it exists in the `kgid` column of `product_mappings.txt`.

For `ml1m_v1`:

- canonical user id: `xrecsys` internal user id,
- canonical product id: movie/product kgid,
- product entity: `movie`.

The first `ml1m_v1` implementation was generated on 2026-06-20 under:

```text
runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1
```

Its PGPR and UCPR views pass canonical label round-trip validation.

For `beauty_legacy_v1`:

- canonical user id: the shared historical PGPR/CAFE compact user index;
- canonical product id: the shared historical PGPR/CAFE compact product index;
- product entity: `product`;
- interaction relation: `purchase`;
- validation policy: intentionally empty to preserve the historical training
  graph exactly.

PGPR and CAFE contain the same per-user train/test pair sets for Beauty, even
though their label-list ordering differs. The raw Amazon review file provides
an exact one-to-one rating/timestamp record for every historical pair.

The empty validation split is a compatibility protocol, not a recommended
general split. Moving interactions from train to validation without rebuilding
CAFE's purchase and review-text KG edges would leak those held-out interactions
through the graph. A future temporal Beauty version must rebuild those edges
from its reduced training split.

## Larger Amazon Dataset with an Existing KG

`beauty_legacy_v1` is the correctness/reference dataset, not the project's
large-scale Amazon claim.

Only one additional large Amazon dataset is required. The selected benchmark
is KGAT/KGIN **Amazon-book**, which already distributes user-item
interactions, item-to-Freebase mappings, relation mappings, and KG triples.
This project will not construct a replacement graph from Amazon review
metadata and call it a native KG.

“Native KG” here means native to the published recommendation benchmark. The
KGAT authors followed KB4Rec to map Amazon-book items to Freebase entities via
title matching. It is not an Amazon-authored KG.

Published scale:

- 70,679 users;
- 24,915 items;
- 847,733 interactions;
- 88,572 KG entities;
- 39 relation types;
- 2,557,746 KG triples.

The canonical import preserves the source KG and mappings. Because the source
benchmark provides train/test but no validation split, one deterministic
interaction per eligible user will be held out from source train for
validation, and all models must be retrained.

The detailed source contract, model scope, and validation gates are tracked in
[AMAZON_BOOK_KG_EXPERIMENT_PLAN_2026-06-21.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/AMAZON_BOOK_KG_EXPERIMENT_PLAN_2026-06-21.md).

## Model Views

A model view is a model-specific training format generated from the canonical dataset.

Examples:

```text
canonical_datasets/lastfm_v1/model_views/pgpr/
canonical_datasets/lastfm_v1/model_views/ucpr/
```

Model views may compact or reorder ids internally. They must save remap tables such as:

```text
user_remap.tsv
product_remap.tsv
entity_remap.tsv
```

The rule is simple:

> Internal model ids may differ, but exported top-k and path CSVs must use canonical ids.

## Canonical KG vs Model-Specific KG View

The canonical dataset does not require every model to consume one identical internal KG.

What is unified at the canonical layer is mainly:

1. user ids,
2. product ids,
3. train/valid/test splits,
4. evaluation labels,
5. the upstream KG source assets and their provenance.

What is *not* required is that every model must ingest exactly the same final node and relation set.

This distinction matters because models such as `PGPR`, `UCPR`, `CAFE`, or future latent-GNN baselines may impose different structural assumptions on their usable KG:

- some relations may be unsupported by a model's action space,
- some entity types may be too sparse or too expensive for path search,
- some models may need compact remapping or relation pruning,
- some schemas may need relation merging or typed subgraph extraction.

Therefore, the intended workflow is:

```text
canonical KG source
-> model-specific KG projection / filtering / remapping
-> native model preprocessing
-> native model training and inference
-> export back to canonical uid/pid space
```

For example, a `PGPR` view may only keep the subset of entities and relations that can be converted into a `PGPR`-compatible environment, even if the canonical KG source is richer. This is acceptable as long as:

1. the canonical user/item truth space is preserved,
2. the projection rules are explicit and reproducible,
3. exported recommendations and explanation paths map back to canonical ids.

In other words, the canonical layer standardizes the comparison contract, not the internal graph implementation of every model.

## Evaluation Contract

For a model result to be comparable under the canonical protocol, it must provide:

```text
pred_paths.csv
uid_topk.csv
uid_pid_explanation.csv
```

with canonical `uid` and `pid` values.

Then `xrecsys` should evaluate with the matching canonical labels:

```bash
--labels_dir canonical_datasets/{dataset_name}_v1/labels
```

Native-path models are allowed to return fewer than `K` recommendations when
the graph search produces fewer than `K` unique unseen item-ending paths.
They must not insert non-path recommendations solely to fill the list.

In that case evaluation must:

1. preserve the short list;
2. count missing slots as non-hits;
3. divide Precision@K by `K`, not by the returned list length;
4. report exact-K users, short users, empty users, and slot coverage;
5. compute NDCG against the ideal ranking with
   `min(K, number_of_relevant_items)` gains.

This exception applies to candidate exhaustion, not duplicate items or seen
item leakage; both remain validation errors.

## First Implementation Plan

We will start with `lastfm_v1` because it is where the current mismatch was found.

Execution order:

1. build `lastfm_v1` canonical interactions and labels,
2. validate split statistics and id coverage,
3. generate a UCPR model view from `lastfm_v1`,
4. generate a PGPR model view from `lastfm_v1`,
5. train/evaluate both models,
6. export both models back to canonical `xrecsys` CSVs,
7. draw single-model and multi-model tradeoff figures.

The same framework is now reused for `ml1m_v1`. Amazon should be added later after its KG and product entity schema are fixed.

## First Smoke-Run Result: `lastfm_v1`

Date: 2026-04-14

Canonical root:

```text
runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1
```

Both generated model views can pass their native preprocess stage in isolated workspaces.

### PGPR View

Smoke workspace:

```text
runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/pgpr_smoke_clean_153822
```

Command shape:

```bash
cd <pgpr_smoke>/models/PGPR
python preprocess.py --dataset lastfm
```

Generated native PGPR artifacts:

```text
dataset.pkl
kg.pkl
train_label.pkl
test_label.pkl
```

Validation after native PGPR preprocessing:

```text
train:
  canonical_users: 15476
  pgpr_users: 15476
  canonical_items: 2773892
  pgpr_items: 2773892
  exact_match: true

test:
  canonical_users: 14620
  pgpr_users: 14620
  canonical_items: 697133
  pgpr_items: 697133
  exact_match: true
```

This confirms that the PGPR identity-mapping view preserves canonical labels through PGPR's original preprocessing logic.

### UCPR View

Smoke workspace:

```text
runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538
```

Command shape:

```bash
cd <ucpr_smoke>/models/UCPR
PYTHONPATH=<ucpr_smoke> python preprocess.py --dataset lfm1m
```

Generated native UCPR artifacts:

```text
dataset.pkl
kg.pkl
train_label.pkl
valid_label.pkl
test_label.pkl
```

Validation after mapping UCPR compact ids back to canonical ids:

```text
train:
  canonical_users: 15476
  converted_users: 15476
  canonical_items: 2773892
  converted_items: 2773892
  exact_match: true

valid:
  canonical_users: 15303
  converted_users: 15303
  canonical_items: 15303
  converted_items: 15303
  exact_match: true

test:
  canonical_users: 14620
  converted_users: 14620
  canonical_items: 697133
  converted_items: 697133
  exact_match: true
```

This confirms that UCPR may use compact internal ids while still remaining comparable after remapping outputs back to canonical uid/pid.

## Current Boundary

This standard solves the cross-model evaluation-space problem. It does not by itself solve:

- how a latent GNN should retrieve post-hoc paths,
- whether a model's explanation is native or post-hoc,
- PGPR/UCPR training cost,
- whether `SEP` is semantically stable for collaborative-user bridge paths.

Those remain model-adapter responsibilities.
