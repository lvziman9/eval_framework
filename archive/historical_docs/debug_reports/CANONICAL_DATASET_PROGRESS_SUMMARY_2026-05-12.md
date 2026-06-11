# Canonical Dataset Progress Summary

Date: 2026-05-12

This note summarizes the work completed from the introduction of the canonical dataset layer to the current `PGPR` and `UCPR` runs on `lastfm_v1`. It is intended for group meeting reporting.

## 1. Goal

The main goal of this stage was not only to run `PGPR` or `UCPR`, but to first build a reliable, reusable dataset layer for cross-model comparison.

The problem we wanted to solve was:

- models with the same dataset name may still use different effective user/item spaces,
- historical artifacts may use different split definitions,
- explainability metrics and recommendation metrics can become incomparable if outputs are not mapped back to one shared label space.

To address this, we introduced a canonical dataset protocol and made `PGPR` and `UCPR` consume model-specific views derived from the same canonical source.

## 2. Canonical Dataset Layer

We defined a project-level canonical dataset standard in:

- [CANONICAL_DATASET_STANDARD.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/CANONICAL_DATASET_STANDARD.md)

We also implemented the builders:

- [build_canonical_dataset.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_canonical_dataset.py)
- [build_pgpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_pgpr_view.py)
- [build_ucpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_ucpr_view.py)

The workflow is now:

```text
raw dataset
-> canonical dataset
-> model-specific view
-> native model training
-> export back to canonical ids
-> unified evaluation
```

## 3. First Canonical Dataset: `lastfm_v1`

We built the first canonical dataset instance here:

- [lastfm_v1](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1)

This canonical dataset already contains:

- interaction splits:
  - [train.tsv.gz](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/interactions/train.tsv.gz)
  - [valid.tsv.gz](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/interactions/valid.tsv.gz)
  - [test.tsv.gz](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/interactions/test.tsv.gz)
- evaluation labels:
  - [train_label.pkl](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/labels/train_label.pkl)
  - [valid_label.pkl](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/labels/valid_label.pkl)
  - [test_label.pkl](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/labels/test_label.pkl)
- canonical mappings:
  - [user_mapping.tsv](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/mappings/user_mapping.tsv)
  - [product_mapping.tsv](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/mappings/product_mapping.tsv)

At this stage, `lastfm_v1` becomes the shared source of truth for model comparison.

## 4. Model Views for `PGPR` and `UCPR`

Instead of directly rewriting model code, we generated model-specific views from the same canonical dataset.

This gives us two benefits:

- low coupling: each model can keep its native input format,
- high comparability: all exported results must map back to canonical `uid/pid`.

We completed:

- a `PGPR` view generated from `lastfm_v1`,
- a `UCPR` view generated from `lastfm_v1`.

## 5. Smoke Validation Before Full Training

Before running full training, we verified whether both model views could pass native preprocessing and still stay aligned with canonical labels.

This step was important because it checked not just file existence, but whether:

- the model could really consume the generated data,
- the effective train/test label space still matched the canonical truth space.

Result:

- `PGPR` preprocess smoke test passed,
- `UCPR` preprocess smoke test passed,
- label alignment checks passed after remapping.

This was the first strong evidence that the canonical layer was functioning correctly.

## 6. Main Debug Finding: `PGPR` Identity View Was Not Internally Safe

The most important bug we found was in the `PGPR` canonical view.

Although the canonical labels were aligned correctly, `PGPR` still failed during training because its embedding table size was determined by the number of rows in `entities/user.txt.gz`, not by the maximum user id in the mapping table.

That created the following mismatch:

- canonical user ids extended to a larger maximum value,
- the `PGPR` user entity table was shorter,
- training therefore hit embedding index overflow.

This was a critical finding because it showed:

```text
label-space alignment
!=
model-internal embedding safety
```

We fixed this in the builder, not in core `PGPR` training code:

- [build_pgpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_pgpr_view.py)

The fix pads the `PGPR` user entity file so that the embedding table fully covers the maximum canonical user id.

This preserved:

- canonical identity-style ids,
- original training hyperparameters,
- low coupling to upstream model code.

## 7. Training Progress on Canonical Views

### `PGPR`

Canonical workspace:

- [pgpr_smoke_padded_155745](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/pgpr_smoke_padded_155745)

What has already completed:

- `TransE` training completed,
- policy training completed up to epoch 50,
- trained embeddings and checkpoints were saved.

Important artifacts:

- [transe_embed.pkl](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/pgpr_smoke_padded_155745/models/PGPR/tmp/lastfm/transe_embed.pkl)
- [policy_model_epoch_50.ckpt](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/pgpr_smoke_padded_155745/models/PGPR/tmp/lastfm/train_agent_canonical/policy_model_epoch_50.ckpt)

This means `PGPR` has already finished the main training stage on the canonical view.

### `UCPR`

Canonical workspace:

- [ucpr_smoke_153538](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538)

What has already completed:

- `TransE` training completed,
- policy training has started,
- policy checkpoints have begun to appear.

Important artifacts:

- [transe_embed.pkl](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538/data/lfm1m/preprocessed/ucpr/tmp/transe_embed.pkl)
- [transe_best_model.ckpt](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538/data/lfm1m/preprocessed/ucpr/tmp/train_transe_model_canonical/transe_best_model.ckpt)
- [policy_model_best.ckpt](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538/data/lfm1m/preprocessed/ucpr/tmp/policy_model_best.ckpt)

This means `UCPR` has moved beyond preprocessing and embedding pretraining and is now in the policy-learning stage.

## 8. Additional Runtime Fixes

After the main training stages, we encountered two more issues during resume and evaluation.

### `PGPR` resume fix

Two issues were handled:

- missing `PYTHONPATH` for `myutils`,
- invalid `--topk 25 50 1` argument parsing during `test_agent.py`.

We fixed these through the resume script:

- [run_pgpr_resume_test_only.sh](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/nohup_jobs/run_pgpr_resume_test_only.sh)

### `UCPR` resume fix

`UCPR` policy training originally failed because `models/utils.py` was missing in the smoke workspace.

We fixed this by patching the resume launcher so that it copies the required utility file before restarting policy training:

- [run_ucpr_resume_policy.sh](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/nohup_jobs/run_ucpr_resume_policy.sh)

## 9. What Has Been Achieved So Far

Up to now, the following milestones have been achieved:

1. a canonical dataset protocol has been defined,
2. `lastfm_v1` has been built as the first canonical dataset,
3. `PGPR` and `UCPR` model views have been generated from the same canonical source,
4. both model views passed preprocessing smoke validation,
5. a key `PGPR` canonical-view bug was identified and fixed,
6. both models have been pushed into real training on canonical data,
7. intermediate trained artifacts now exist for both models.

## 10. What Is Still Missing

The framework layer and the major training stages are largely in place, but the final comparison outputs are not fully ready yet.

What we still need:

- stable completion of `test / path extraction / export`,
- canonical-format result files such as:
  - `uid_topk.csv`
  - `pred_paths.csv`
  - `uid_pid_explanation.csv`
- unified `xrecsys` evaluation using canonical labels,
- final tradeoff figures for cross-model comparison.

So the current status is:

```text
canonical dataset layer: built
model-specific canonical views: built
preprocess validation: passed
training artifacts: available
final comparable export/eval: still in progress
```

## 11. Why This Matters

This work is useful beyond the current `PGPR` and `UCPR` runs.

The canonical dataset framework is intended to become a reusable base for future models and datasets, including:

- `PGPR`
- `UCPR`
- `VRKG4Rec`
- `KGIN`
- `CAFE`
- future `RecBole` baselines
- future datasets such as `ml1m_v1` and `amazon_v1`

The key value is that future model comparisons can be made on a shared and explicit evaluation space, instead of relying on historical artifacts that only appear to use the same dataset name.
