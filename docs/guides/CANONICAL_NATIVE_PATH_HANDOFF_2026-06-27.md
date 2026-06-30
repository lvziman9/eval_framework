# Canonical Native-Path Handoff

Date: `2026-06-27`; updated `2026-06-30` Asia/Singapore.

This is the short handoff for the current canonical native-path experiment
state. For full historical details, use
`docs/guides/NATIVE_PATH_IMPLEMENTATION_LOG_2026-06-20.md`.

## Quick status

| Area | State |
|---|---:|
| LastFM six-model native-path evaluation | Complete |
| ML-1M six-model native-path evaluation | Complete |
| LastFM / ML-1M alpha-sweep figures | Complete |
| Amazon-Book KGAT KGGLM formal baseline | Complete |
| Amazon-Book KGAT PEARLM formal baseline | Complete |
| Amazon-Book KGAT PGPR formal baseline | Complete; strict full-user export validation and accuracy PASS |
| Amazon UCPR | Data view, adapter aliases, runtime schema patch, preprocess smoke, and TransE forward smoke PASS; formal TransE PASS; batch-128, batch-32, and batch-16 policy attempts exceeded GPU memory at Adam optimizer step; paused for server safety, blocked pending a smaller protocol or dedicated high-memory run |
| Amazon CAFE | Blocked pending compatible Amazon UCPR runtime support and CAFE schema/metapaths |
| Amazon TPRec | Structural wiring complete; formal reporting blocked by timestamp semantics |

Current generated summary:

- `reports/tables/canonical_native_path_status_matrix.md`;
- `reports/tables/canonical_native_path_status_matrix.csv`;
- `reports/tables/amazon_classic_port_readiness.md`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_view_metadata.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_runtime_preprocess_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_forward_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_training_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_env_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_training_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_export_smoke_validation.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke_validation.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/preprocessed/ucpr_view_metadata.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_runtime_preprocess_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_transe_forward_smoke.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_preprocess_validation.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json`;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json`;
- `reports/tables/canonical_native_path_artifact_manifest.json`.

## One-command report refresh

Report-only refresh, including status table, export-validation manifest,
Amazon readiness audit, and artifact manifest:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

Full report refresh, additionally regenerating LastFM and ML-1M alpha-sweep
figures/CSVs:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh
```

These commands do not launch training or path extraction.

## What is reportable now

The authoritative status table has `18` rows:

- `15` complete rows:
  - LastFM: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM;
  - ML-1M: PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM;
  - Amazon-Book KGAT: KGGLM, PEARLM, PGPR.
- `3` blocked rows:
  - Amazon-Book KGAT: UCPR, CAFE, TPRec.

Amazon formal comparison:

| Model | Users | HR@10 | NDCG@10 | Export validation |
|---|---:|---:|---:|---:|
| KGGLM | 70,591 | 0.012665 | 0.003022 | PASS |
| PEARLM | 70,591 | 0.029338 | 0.010716 | PASS |
| PGPR | 70,591 | 0.054851 | 0.015723 | PASS |

Amazon alpha-sweep explanation tradeoffs are not reportable yet because no
approved timestamp/SEP/ETD denominator exists for Amazon-Book KGAT.

Paused / blocked but not reportable yet:

| Job | State | Evidence |
|---|---:|---|
| Amazon-Book KGAT UCPR | Failed at policy `optimizer.step()` even after `foreach=False` and batch size 16; pause further Amazon UCPR attempts for server safety | status JSON `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`; formal TransE status `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_transe_formal_status.json`; formal preprocess validation `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_preprocess_validation.json`; readiness audit `reports/tables/amazon_classic_port_readiness.json` |
| Amazon-Book KGAT TPRec | Blocked before formal launch | timestamp audit `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json` |

## Validation evidence

Core evidence files:

- `reports/tables/canonical_export_validation/manifest.json`
  - `status=PASS`;
  - `exports=15`.
- `reports/tables/amazon_classic_port_readiness.json`
  - `status=BLOCKED`;
  - blocked models: PGPR, UCPR, CAFE, TPRec.
- `reports/tables/amazon_classic_port_readiness.md`
  - human-readable model-by-model readiness table;
  - failed gates and required next actions for PGPR, UCPR, CAFE, TPRec.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_view_metadata.json`
  - PGPR Amazon data-view smoke artifact;
  - train/valid/test canonical label round-trip is exact;
  - this is not a PGPR Amazon training/export result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_runtime_preprocess_smoke.json`
  - isolated PGPR runtime preprocess smoke summary;
  - generated PGPR `dataset.pkl`, `kg.pkl`, train/test labels;
  - train/test labels exactly match canonical labels;
  - this is still not a PGPR Amazon training/export result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_forward_smoke.json`
  - one-batch PGPR TransE forward/backward smoke;
  - verifies the Amazon book/entity relation schema enters the TransE loss;
  - this is still not a trained PGPR Amazon checkpoint.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_training_smoke.json`
  - 1-epoch small-dimension PGPR TransE training smoke;
  - checkpoint and `transe_embed.pkl` exist and have expected Amazon
    book/entity/relation shapes;
  - this is still not a formal PGPR Amazon result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_env_smoke.json`
  - PGPR policy environment and beam-search smoke;
  - validates one real `user -> book -> entity -> book` native path and a
    random ActorCritic beam pass;
  - this is still not a trained PGPR Amazon policy result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_training_smoke.json`
  - 1-epoch small-policy PGPR training smoke;
  - checkpoint exists with expected `state_dim=64` and `act_dim=251` shapes;
  - this is still not a formal PGPR Amazon policy run.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke.json`
  - beam inference smoke from the policy-training smoke checkpoint;
  - `8` users generated `191` paths, including `170` book-ending paths;
  - this is still not a formal PGPR Amazon export or accuracy result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_export_smoke_validation.json`
  - adapter/export smoke from the 8-user PGPR policy-inference pkl;
  - validates Amazon `book` path serialization into xrecsys CSVs;
  - `166` pred-path rows, `8` candidate users, `80` top-k explanations;
  - `require_all_test_users=false`, so this is intentionally not formal.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke.json`
  - 8-user streaming exporter smoke using the formal epoch-50 policy checkpoint
    and formal TransE embeddings;
  - validates the memory-safe path used for full Amazon inference/export;
  - `677` raw candidate rows, `8` candidate users, slot coverage `1.0`.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke_validation.json`
  - xrecsys CSV validator for the streaming smoke;
  - `status=PASS`, `677` pred-path rows, `80` explanations, normalized score
    range `[0.0, 1.0]`;
  - `require_all_test_users=false`, so this is intentionally still a smoke.
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`
  - formal-v1 PGPR Amazon pipeline launched through tmux;
  - current stage at updated handoff: `inference_export`;
  - `streaming_export_enabled=1`;
  - configuration: TransE `30` epochs, dim `300`, batch `2048`,
    negatives `5`; policy `50` epochs, hidden `512 256`, batch `8192`,
    max actions `250`; export beam `10 12 1`;
  - this is a running job marker, not a reportable result.
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_streaming_export_formal.json`
  - live formal streaming export progress marker;
  - starts as `status=RUNNING`, `stage=beam_stream` and is expected to become
    `PASS` only after all `70,591` canonical test users are exported.
- `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_preprocess_validation.json`
  - formal runtime preprocess validation;
  - train/test label round-trip is exact against canonical labels.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/preprocessed/ucpr_view_metadata.json`
  - Amazon UCPR data-view artifact;
  - train/valid/test canonical label round-trip is exact;
  - users: `70,679`; products: `24,915`; relation files: `9`;
  - skipped users/products: `0` in all splits;
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_runtime_preprocess_smoke.json`
  - isolated Amazon UCPR runtime preprocess smoke;
  - runtime schema checks pass for `INTERACTION`, `KG_RELATION`,
    `PATH_PATTERN`, and `MAIN_PRODUCT_INTERACTION`;
  - generated UCPR `dataset.pkl`, `kg.pkl`, and train/valid/test label
    pickles;
  - train/valid/test label round-trip remains exact against canonical labels;
  - this is still not a UCPR Amazon training/export result.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_transe_forward_smoke.json`
  - one-batch Amazon UCPR TransE forward/backward smoke;
  - batch shape `[64, 11]`, loss `24.95353126525879`, and `21` finite
    gradient tensors;
  - all expected Amazon relation parameters are present;
  - this is still not a trained UCPR Amazon checkpoint.
- `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`
  - formal UCPR Amazon training queue launched through tmux;
  - current stage at updated handoff: `policy`;
  - `run_inference=0`, intentionally deferring full-user UCPR path export until
    a memory-safe export path is available.
- `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_transe_formal_status.json`
  - formal UCPR Amazon TransE status;
  - `status=PASS`;
  - confirms `transe_best_model.ckpt` and `transe_embed.pkl` exist.
- `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_preprocess_validation.json`
  - formal runtime preprocess validation;
  - train/valid/test label round-trip is exact against canonical labels.
- `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json`
  - Amazon TPRec structural support audit;
  - Hopwise view preserves interactions/KG and all configured relation-token
    path constraints are present;
  - train/valid/test timestamps are all sentinel `-1`;
  - `formal_temporal_reward_approved=false`, so formal TPRec reporting remains
    blocked unless real timestamps are restored or a non-temporal ablation is
    explicitly approved.
- `reports/tables/canonical_native_path_artifact_manifest.json`
  - status matrix: `18` rows, `14` complete, `4` blocked;
  - LastFM figure bundle: `12` PNG + `12` CSV;
  - ML-1M figure bundle: `12` PNG + `12` CSV.

Sanity check command:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

Expected terminal tail:

```text
amazon classic readiness audit present
artifact manifest present
canonical native-path report validation PASS
Canonical native-path reports regenerated.
```

## Main changed code paths

- `scripts/validation/evaluate_uid_topk.py`
  - adds explicit `--allow-user-subset` for smoke-only subset evaluation;
  - formal evaluations remain strict unless that flag is passed.
- `scripts/hopwise/run_canonical_pearlm_pipeline.sh`
  - robust nested HuggingFace checkpoint discovery.
- `scripts/hopwise/run_canonical_kgglm_pipeline.sh`
  - same robust checkpoint discovery for KGGLM finetune reruns.
- `scripts/analysis/*.py` and `scripts/analysis/*.sh`
  - report generation, export evidence validation, Amazon readiness audit,
    artifact manifest.
- `scripts/validation/run_pgpr_amazon_formal_pipeline.sh`
  - launches the full PGPR Amazon formal-v1 sequence:
    preprocess validation, TransE, policy training, full-user beam inference,
    adapter export, strict export validation, and strict `uid_topk` accuracy.
- `scripts/validation/launch_pgpr_amazon_formal_pipeline.sh`
  - starts the formal pipeline in a persistent `tmux` session and records
    `pid`, log, and status paths.
- `scripts/validation/run_pgpr_policy_inference_smoke.py`
  - now accepts `--hidden` and `--beam-batch-size`, so the same inference
    checker can load both smoke and formal policy checkpoints.
- `scripts/validation/export_pgpr_streaming.py`
  - memory-safe PGPR full-user exporter for Amazon-size candidate pools;
  - streams candidate rows to CSV and keeps only per-user top-k state in
    memory, avoiding the giant intermediate `PATHS_PKL`.
- `scripts/validation/validate_pgpr_policy_training_smoke.py`
  - now accepts `--expected-hidden`, allowing formal-size policy checkpoints
    to be validated without hard-coded smoke dimensions.
- `scripts/hopwise/tprec_runtime.py`,
  `scripts/hopwise/run_canonical_tprec.py`,
  `scripts/hopwise/export_tprec_paths.py`,
  `scripts/hopwise/run_canonical_tprec_pipeline.sh`
  - Amazon TPRec structural wiring is present;
  - the default Amazon TPRec pipeline runs the timestamp audit and exits before
    formal training unless an explicit ablation override is set.
- `scripts/validation/audit_tprec_amazon_timestamp_semantics.py`
  - records why Amazon TPRec is blocked for formal temporal reporting.
- `scripts/data/canonical/build_ucpr_view.py`
  - now supports the `amazon_book_kgat_v1` KGAT source projection and records
    exact train/valid/test label round-trip metadata for the UCPR view.
- `adapters/ucpr_adapter.py`
  - now includes Amazon UCPR `product -> book` and `book_*_entity -> book_*`
    alias scaffolding; this remains unvalidated until an Amazon UCPR runtime
    emits native paths.
- `scripts/model_patches/patch_ucpr_amazon_runtime.py`
  - injects Amazon UCPR runtime constants/path patterns into an experiment
    runtime copy.
- `scripts/validation/run_ucpr_amazon_preprocess_smoke.sh`,
  `scripts/validation/validate_ucpr_preprocess_smoke.py`
  - run and validate the isolated Amazon UCPR preprocess gate.
- `scripts/validation/run_ucpr_transe_forward_smoke.py`
  - validates that the patched Amazon UCPR runtime can execute one TransE
    forward/backward step through all Amazon relation parameters.
- `scripts/validation/run_ucpr_amazon_formal_pipeline.sh`
  - launches UCPR Amazon formal training stages; by default it stops after
    policy training with `UCPR_RUN_INFERENCE=0`; when inference is enabled it
    defaults to the streaming exporter instead of native giant-pickle export.
- `scripts/validation/launch_ucpr_amazon_formal_pipeline.sh`
  - starts the UCPR Amazon formal pipeline in persistent `tmux`.
- `scripts/validation/export_ucpr_streaming.py`
  - memory-safe UCPR exporter for Amazon-size candidate pools;
  - streams candidate rows directly to xrecsys CSVs and keeps only per-user
    top-k state in memory.

## Do not do this accidentally

- Do not report Amazon PGPR/UCPR/CAFE/TPRec as failed accuracy baselines; they
  have not been honestly ported to the KGAT Amazon-book schema.
- Do not run Amazon alpha-sweep SEP/ETD/LIR figures until a canonical
  denominator is approved.
- Do not use user-subset accuracy for formal reporting.
- Do not treat historical Beauty as the larger Amazon-book KGAT result.

## Remaining work if the project continues

If Amazon classic baselines are required, start a separate porting task:

1. let the running PGPR Amazon formal-v1 streaming export job finish, then
   inspect strict export validation and accuracy summaries;
2. if formal-v1 passes, refresh readiness/status reports and decide whether a
   larger `25-50-1` PGPR beam is required for a second, more expensive run;
3. let the running UCPR Amazon `foreach=False`/batch-16 policy training
   finish, run a small streaming-export smoke from the resulting checkpoint,
   then enable full-user streaming export and strict export/accuracy gates;
4. add CAFE Amazon schema/metapaths after compatible UCPR runtime support;
5. for TPRec, either rebuild Amazon-book KGAT with real timestamps or approve a
   clearly labeled non-temporal ablation before running training/export;
6. run smoke exports with full-user inclusion;
7. run strict export validation and strict accuracy validation;
8. only then add formal rows to the status matrix.
