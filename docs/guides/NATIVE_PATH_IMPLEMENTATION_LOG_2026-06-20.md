# Native Path Implementation Log

Start date: 2026-06-20

## Objective

Complete the native-path experiment stack in this order:

1. finish a reproducible full UCPR LastFM run;
2. adapt CAFE to the canonical LastFM dataset and `xrecsys`;
3. extend the canonical dataset and model views to ML-1M;
4. run the supported models sequentially and collect recommendation and path-explainability results.

This file is the implementation source of truth. Every material code or experiment change must record:

- what changed;
- why it changed;
- how it was validated;
- where its output and logs are stored;
- whether the result is final, provisional, or blocked.

## Execution Policy

- Long jobs run in `tmux` or `nohup`; they must not depend on the SSH session.
- GPU jobs are launched sequentially on GPU 1 unless the log records a different choice.
- PGPR and CAFE receive `--gpu 1` because their parsers rewrite
  `CUDA_VISIBLE_DEVICES`; UCPR receives local `--gpu 0` under an outer
  `CUDA_VISIBLE_DEVICES=1` mapping because its model code constructs
  `cuda:0` directly.
- Model source repositories remain external dependencies. Reproducible builders, adapters, patches, runners, and records live in `eval_framework`.
- Native model defaults and cross-model robustness settings are reported separately.
- Only model-native recommendation paths are exported for `LIR`, `SEP`, and `ETD`.

## Baseline State Before This Task

### Canonical LastFM

Available at:

```text
runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1
```

Implemented:

- canonical interactions and labels;
- PGPR model view;
- UCPR model view;
- PGPR and UCPR adapters;
- PGPR/UCPR baseline and alpha-sweep evaluation;
- PGPR/UCPR tradeoff figures.

### Existing UCPR Run

The existing UCPR run used the full canonical LastFM interaction files and completed:

- 30 epochs of TransE training;
- 38 policy-training epochs;
- native path extraction;
- recommendation evaluation;
- `xrecsys` path evaluation.

However, it is not yet the final robustness run for two reasons:

1. path extraction used `topk=[25, 5, 1]`, producing at most about 125 paths per user;
2. UCPR's parser overwrites the command-line `--topk` value after parsing:

```python
args.topk = [25, 5, 1]
```

Therefore, passing `--topk 25 50 1` previously could not create a matched-beam result.

The existing result remains valid as the **native/default UCPR extraction setting**. It must not be silently replaced.

### Existing UCPR Validation Caveat

The added early-stop monitor used `avg_valid_reward`, but validation reward remained `0.0` at every recorded checkpoint. It therefore did not provide meaningful checkpoint selection.

For the current completion step:

- keep the completed epoch-30 checkpoint as the reproducible trained checkpoint;
- rerun native inference with a working configurable beam;
- label the wider-beam result as a robustness/matched-candidate experiment;
- do not claim that the zero-valued early-stop signal selected an optimal model.

## Phase 1: Full UCPR LastFM

### Planned Change

Add a tracked runtime patch that removes UCPR's post-parse hard-coded top-k override and preserves the user-provided `--topk` value.

Add a sequential runner that:

1. validates the checkpoint and canonical remap files;
2. runs UCPR path extraction with `25-50-1`;
3. exports canonical path CSVs under a distinct tag;
4. runs `xrecsys` baseline and `LIR/SEP/ETD` sweeps;
5. writes all logs to the task run directory.

### Reason

The native `25-5-1` result and PGPR's `25-50-1` result expose very different candidate-pool sizes. A matched-beam UCPR run is needed to distinguish:

- mechanism-driven sparsity;
- extraction-budget-driven sparsity.

This is a robustness check, not a replacement for UCPR's native default.

### Status

`IMPLEMENTED AND VALIDATED; FULL LASTFM RUN QUEUED AFTER UCPR`

## Phase 2: CAFE Canonical Adaptation

### Selected Source

Use:

```text
/usr1/home/s125mdg43_08/rep-path-reasoning-recsys/models/CAFE
```

instead of the separately modified `/usr1/home/s125mdg43_08/CAFE` experiment tree.

### Reason

The framework CAFE implementation already declares `lfm1m` and `ml1m`, and shares the same framework-level dataset conventions as the current UCPR implementation. This reduces hidden data-schema divergence.

### Required Code

- `scripts/data/canonical/build_cafe_view.py`
- `adapters/cafe_adapter.py`
- CAFE smoke/full runner scripts
- validation of canonical uid/pid round trips

### Status

`ML1M CANONICAL/PGPR/UCPR VIEWS VALIDATED; MODEL RUNS QUEUED`

## Phase 3: ML-1M Canonical Expansion

### Required Changes

- generate `ml1m_v1` from `xrecsys/datasets/ml1m`;
- generalize `build_pgpr_view.py` beyond LastFM;
- generalize `build_ucpr_view.py` beyond LastFM;
- reuse the new CAFE builder for ML-1M;
- validate split, id, entity, relation, and output round trips.

### Reason

The canonical contract should be reusable across datasets. The model view, not the canonical dataset, should contain model-specific relation filtering and internal remapping.

### Status

`IN PROGRESS`

## Change Log

### 2026-06-20: Task Initialized

Observed:

- all four RTX A5000 GPUs were nearly idle;
- GPU 1 was selected for sequential jobs;
- the existing UCPR parser hard-codes `topk=[25,5,1]`;
- the parser also clears `topk_string`, causing different beam outputs to share a filename;
- UCPR constructs `cuda:0` regardless of the displayed `--gpu` value, so the runner must set `CUDA_VISIBLE_DEVICES`;
- the existing UCPR training artifacts and epoch-30 policy checkpoint are present;
- framework CAFE supports both `lfm1m` and `ml1m` at the code-schema level.

Decision:

- finish UCPR by fixing configurable inference and producing a separate matched-beam result;
- then implement CAFE LastFM;
- then generalize all canonical/model-view builders to ML-1M.

### 2026-06-20: UCPR Runtime Patch and Runner Added

Changed:

- added `scripts/model_patches/patch_ucpr_cli_topk.py`;
- added `runs/debug_compare/2026-06-20_native_path_expansion/run_ucpr_lastfm_matched_beam.sh`;
- made beam-specific raw path filenames possible;
- made physical GPU selection explicit with `CUDA_VISIBLE_DEVICES=1`;
- preserved the native `25-5-1` artifacts before generating `25-50-1`.

Reason:

- command-line top-k previously had no effect;
- beam runs previously risked overwriting each other;
- `--gpu 1` did not identify the physical GPU used by UCPR;
- native-default and matched-beam results must remain separately auditable.

The UCPR runtime patch also:

- replaces removed `np.float` aliases;
- prevents division by zero when a projected relation has no observed edges.

The zero-edge fallback only initializes a valid negative-sampling distribution. It does not add KG edges or positive training examples.

Validation completed:

- runtime patch is idempotent;
- parsed beam equals `[25, 50, 1]`;
- `beam_batch_size=4` plus `torch.no_grad()` is stable;
- full path extraction is actively running.

Remaining:

- completion of path extraction, adapter export, xrecsys evaluation, and
  matched-beam figures.

### 2026-06-20: First UCPR Launch Failed Fast

Observed:

```text
ModuleNotFoundError: No module named 'models'
```

Cause:

- UCPR must run from `models/UCPR` because its data paths are relative to that directory;
- imports start at the runtime root (`models.UCPR...`);
- the old interactive environment had implicitly supplied that package root, but the clean background runner did not.

Change:

- the runner now explicitly exports the runtime root through `PYTHONPATH`.

Reason:

This preserves UCPR's required working directory while making module resolution reproducible and independent of an interactive shell.

### 2026-06-20: UCPR 25-50-1 Beam OOM

Observed:

```text
torch.OutOfMemoryError
23.06 GiB allocated on a 23.68 GiB GPU
```

Cause:

- UCPR hard-coded 16 users per beam-search batch;
- changing the second-hop beam from 5 to 50 increases the expanded state/path pool by roughly ten times;
- the wider candidate experiment therefore exceeded one RTX A5000.

Change:

- added runtime argument `--beam_batch_size`;
- an 8-user batch still exceeded 24 GB at the third hop;
- the matched `25-50-1` run now uses 4 users per batch;
- CUDA cache cleanup is performed between user batches.

Reason:

The beam remains unchanged, so the experiment still measures the same candidate budget. Only execution chunking changes, trading runtime for lower peak memory.

The second retry showed memory increasing across batches. The underlying cause was that UCPR used `model.eval()` without disabling autograd. The runtime patch now applies `@torch.no_grad()` to beam search. This removes inference computation graphs without changing model scores or path selection.

### 2026-06-20: CAFE Canonical Builder and Adapter Added

Changed:

- added `scripts/data/canonical/build_cafe_view.py`;
- added `adapters/cafe_adapter.py`.

Design:

- CAFE reuses the compact entity order from the canonical UCPR view;
- the CAFE builder creates its own global entity ids, forward/reverse triples, metapath rules, and labels;
- the UCPR TransE checkpoint is reused only as CAFE's KG embedding initialization;
- CAFE still trains its own neural-symbolic relation modules and generates native CAFE paths;
- CAFE outputs are mapped back to canonical uid/pid before `xrecsys`.

Reason:

CAFE and UCPR in the selected framework declare the same LastFM entity and relation names. Sharing the compact KG entity order avoids training/evaluating on silently different node spaces while preserving the distinct recommendation mechanisms.

Validation completed:

- LastFM CAFE view built;
- exact train/valid/test round trips verified;
- UCPR TransE entity/relation shapes verified against CAFE vocabularies;
- pretrained embedding copy smoke-tested;
- CAFE adapter relation, endpoint, filtering, score-normalization, and CSV
  output smokes passed.

Remaining:

- full CAFE preprocess, training, native inference, and xrecsys evaluation.

### 2026-06-20: CAFE LastFM View Built

Result:

- entities use the same compact local order as the canonical UCPR view;
- `5,720,900` triples were written including reverse edges;
- train, validation, and test labels all map back exactly to canonical labels;
- forward KG edge counts were recorded in `cafe_view_metadata.json`.

Added:

- `scripts/model_patches/patch_cafe_runtime.py`;
- `runs/debug_compare/2026-06-20_native_path_expansion/run_cafe_lastfm_canonical.sh`.

Runtime fixes and reasons:

- copy pretrained values into `embedding.weight`, rather than assigning an unused `embedding.data` attribute;
- replace removed NumPy aliases (`np.int`, `np.asfarray`);
- correctly merge train and validation exclusions during inference;
- fix `TREX_DATA_ROOT` environment lookup;
- remove unused `scipy` and `sklearn` imports so CAFE can use the existing `rep` environment;
- disable autograd during native path inference and neural-program execution;
- run validation only at the first epoch and every five epochs, always in `eval()` mode;
- keep all changes in the experiment runtime instead of modifying the external framework repository.

Execution policy:

- the CAFE runner is prepared but will not start until UCPR completes;
- it uses physical GPU 1 through `CUDA_VISIBLE_DEVICES=1`.

### 2026-06-20: ML-1M Canonical and Model Views Built

Canonical result:

| Split | Interactions | Users | Products |
|---|---:|---:|---:|
| Train | 744,603 | 6,040 | 3,168 |
| Validation | 6,040 | 6,040 | 1,718 |
| Test | 190,653 | 6,040 | 3,105 |

Properties:

- source ratings and timestamps are preserved;
- no mapped ML-1M interaction was dropped;
- canonical product ids use xrecsys movie kg ids.

PGPR view:

- ML-1M four-column interactions are preserved;
- user/movie identity mappings are used;
- no entity padding was required;
- train/test labels round-trip exactly.

PGPR runtime isolation:

- the first smoke copy included historical `tmp/ml1m` artifacts from `xrecsys/models/PGPR`;
- although preprocessing overwrote the main dataset/KG/label files, stale TransE and agent artifacts remained;
- the final runner now creates `pgpr_ml1m_runtime_clean` and copies source files only, explicitly excluding `tmp/`.

UCPR view:

- compact user/product ids were generated;
- nine xrecsys ML-1M KG relation files were mapped to UCPR names;
- `country` and `wikipage` are explicit empty schema projections because these relations are absent from the current xrecsys KG;
- no interactions were skipped.
- CAFE rules omit zero-edge `composer/country/wikipage` relations because CAFE cannot construct executable metapaths for relations absent from triples.

Preprocess validation:

- UCPR generated `dataset.pkl`, `kg.pkl`, and all three label files;
- UCPR compact train/valid/test labels map back exactly to canonical labels;
- clean PGPR preprocessing loaded 744,603 training interactions and all projected KG relations;
- clean PGPR train/test labels exactly equal canonical labels;
- no historical PGPR `tmp/` artifact is present in the final clean runtime.

Added sequential runners:

- `run_ucpr_ml1m_canonical.sh`
- `run_cafe_ml1m_canonical.sh`
- `run_pgpr_ml1m_canonical.sh`

Planned ML-1M order:

1. UCPR, including TransE checkpoint generation;
2. CAFE, reusing the aligned UCPR TransE initialization;
3. PGPR.

### 2026-06-20: Sequential Background Queue

Added:

- `run_sequential_queue.sh`
- `generate_native_path_figures.sh`

Order:

1. wait for successful UCPR LastFM matched-beam completion;
2. re-export LastFM PGPR with its native TransE item score;
3. CAFE LastFM;
4. UCPR ML-1M;
5. CAFE ML-1M;
6. PGPR ML-1M;
7. generate three-model `LIR/SEP/ETD` tradeoff figures for each completed dataset.

Failure policy:

- each stage has a separate log;
- `set -e` stops the queue on the first failed stage;
- later GPU jobs do not start after an upstream failure;
- completion marker files make resume state explicit.
- the queue now skips stages whose completion marker already exists, so a
  failed long run can be restarted without repeating successful training;
- figure generation has its own completion marker for each dataset.

### 2026-06-20: Adapter Package Import Repaired

Observed:

`adapters/__init__.py` imported `BaseAdapter`, but `base_adapter.py` only retained `_DeprecatedBaseAdapter`. Standalone adapter CLIs worked because they bypassed package import, while tests and reusable imports failed.

Change:

- restored `BaseAdapter` as a compatibility alias;
- exported the current shared adapter helpers.

Reason:

This keeps historical imports working without moving new adapters back to the deprecated class design.

### 2026-06-20: PGPR ML-1M Inference and Adapter Guardrails

Pre-execution review found three issues in the isolated PGPR runtime:

1. `--topk` used `type=list`, so CLI values such as `25 50 1` became character
   lists instead of integers.
2. `test_agent.py` imported xrecsys `myutils` unconditionally even though the
   canonical pipeline only needs native path export.
3. `pgpr_adapter.py` treated every beam endpoint as a product, while native
   PGPR explicitly discards paths ending at users or KG attributes.

Changes:

- added `patch_pgpr_runtime.py`;
- changed CLI top-k parsing to integers;
- added `beam_batch_size`, `torch.no_grad()`, and CUDA cache cleanup;
- disabled PGPR's model-specific legacy evaluation in the runner;
- retained native path generation and moved all evaluation to the shared
  adapter+xrecsys layer;
- filtered adapter candidates to `song` for LastFM and `movie` for ML-1M;
- added an explicit failure if no unseen product-ending path remains.

The ML-1M UCPR beam was also changed from `25-5-1` to `25-50-1`, with
`beam_batch_size=4`, so PGPR and UCPR use the same candidate beam width.

Reason:

Candidate-pool size and endpoint semantics affect both recommendation accuracy
and the available explanation paths. Leaving these mismatched would confound
the model comparison before xrecsys reranking even begins.

Further PGPR score review found that the old adapter used a sum of beam values
as item relevance. Native PGPR instead ranks candidate items with:

```python
score(uid, pid) = dot(user_embedding[uid] + interaction_embedding,
                      product_embedding[pid])
```

The policy probabilities determine which paths are found and which route is
selected as the explanation; they are not the native recommendation score.
The adapter now accepts `transe_embed.pkl`, computes the native item score,
normalizes it to `[0, 1]`, and chooses the best route per item by the product
of its three action probabilities.

The old PGPR beam code added `1` to valid action probabilities for top-k
selection and then exported those offset values. The runtime patch now uses
the offset only to select indices and gathers the original softmax
probabilities for output. The adapter auto-detects the `+1` offset in the
existing LastFM pickle for audit/backward-compatible conversion.

Consequence:

- `agent_topk=10-12-1-pgpr-canonical` remains a historical debug export;
- the pickle actually contains a `25-50-1` beam (13.8 million paths, which is
  impossible under a `10-12-1` maximum);
- the final LastFM PGPR export uses
  `agent_topk=25-50-1-pgpr-canonical-native-score`;
- previous PGPR figures must not be treated as final native-PGPR results.

The LastFM pickle is about 1.7 GB and contains 13.8 million paths. The adapter
was refactored to avoid constructing a second all-path grouping:

1. first pass computes the global native-score range and retains at most ten
   baseline candidates per user;
2. second pass streams rows directly to `pred_paths.csv`;
3. native item scores are cached once per observed `(uid, pid)`.

This preserves all candidate paths for xrecsys while bounding the additional
top-k state to ten products per user.

PGPR's `ActorCritic.forward()` also called functional dropout without
`training=self.training`, which keeps dropout active even after
`model.eval()`. The runtime patch adds the missing flag to both hidden layers.

The final LastFM PGPR stage therefore:

1. preserves the historical stochastic pickle as
   `policy_paths_epoch50.legacy_dropout.pkl`;
2. reruns only epoch-50 path inference with dropout disabled;
3. exports true policy probabilities and native TransE item scores;
4. does not retrain TransE or the RL policy.

This makes repeated inference deterministic for the fixed checkpoint and
seed, while keeping the historical artifact auditable.

### 2026-06-20: Shared Adapter Export Gate Added

Added `scripts/validation/validate_xrecsys_export.py` between each new adapter
run and xrecsys evaluation.

The validator streams the CSV files and checks:

- exactly three hops/four nodes per explanation path;
- canonical user and product endpoints;
- `song` endpoints for LastFM and `movie` endpoints for ML-1M;
- no training item leakage;
- unique top-k products with at most ten items;
- exact agreement between `uid_topk.csv` and
  `uid_pid_explanation.csv`;
- every selected explanation is present in `pred_paths.csv`;
- finite path scores and native path probabilities in `[0, 1]`.

Reason:

Model training success does not prove adapter correctness. This gate prevents
an invalid export from entering xrecsys and gives each run a compact JSON
validation artifact.

Canonical test-time exclusions now use `train + valid` whenever
`valid_label.pkl` exists. UCPR and CAFE already applied this policy inside
their native inference code; the shared adapter loader previously filtered
PGPR against train only. The change aligns candidate filtering across all
three mechanisms while preserving train-only behavior for legacy xrecsys
datasets without a validation split.

Smoke validation against the existing canonical UCPR LastFM export passed:

```text
pred_path_rows = 547,519
candidate_users = 14,081
topk_users = 14,620
explanations = 119,079
score_range = [0.0, 1.0]
```

### 2026-06-20: CAFE Native Path Scoring Corrected Before Full Run

Observed in the upstream CAFE executor:

```python
scores = F.log_softmax(scores[0], dim=0)
...
reduce(lambda x, y: x * y, r[1])
```

Each step value in `r[1]` is a log-probability. Multiplying those values does
not produce a path probability and can change the ranking according to path
length and sign. The same block also assigned directly into
`pred_paths[uid][pid]`, so a later route to the same product silently replaced
an earlier, better route.

Runtime-copy patch:

```python
path_log_score = float(np.sum(r[1]))
path_probability = float(np.exp(path_log_score))
if current is None or path_log_score > current[0][0]:
    pred_paths_instances[uid][pid] = [
        (path_log_score, path_probability, path)
    ]
```

Reason:

- summing log-probabilities is the mathematically correct native path score;
- all native CAFE routes are retained for xrecsys explanation reranking;
- item ranking still uses the highest native path log-score for each product;
- this remains intrinsic CAFE reasoning, not a post-hoc graph search;
- the adapter now rejects any path whose embedded user/product endpoints do
  not match the enclosing prediction keys.

CAFE stores inverse KG edges with a `rev_` prefix, while the xrecsys/PGPR
canonical path convention uses the same semantic relation name in both
directions:

```text
belong_to category ... belong_to song
```

The CAFE adapter therefore strips `rev_` before applying dataset relation
aliases. This prevents ETD from counting `rev_belong_to_genre` and
`belong_to` as different explanation types.

xrecsys single-metric alpha optimization directly mixes `path_score` with a
metric in `[0, 1]`. PGPR's adapter and UCPR's native export already min-max
normalize path scores globally. CAFE's summed log-probability is negative and
would otherwise dominate the mixture by scale rather than ranking quality.
The CAFE adapter now applies the same global `[0, 1]` min-max normalization
after filtering seen/unmapped paths; CAFE item ordering is unchanged because
the transform is monotonic.

### 2026-06-20: CAFE Path-Count Preprocessing Optimized Without Sampling Reduction

The upstream preprocessor calls `count_paths_with_target` for every training
interaction and every metapath. On canonical LastFM this means:

```text
2,773,892 train interactions x 5 metapaths = 13,869,460 calls
```

A full-graph microbenchmark measured about 102 calls/second, projecting about
37.8 hours for this preprocessing stage alone.

All current CAFE rules have the same three-hop shape:

```text
user -> product -> middle entity -> product
```

For this shape, the original forward/backward BFS count is exactly the number
of sampled user-history products that share a middle entity with the target.
The runtime patch computes that set intersection directly while preserving the
original maximum of 50 sampled history products:

```python
middle_relation = metapath[2][0]
target_middle_ids = set(self.get(PRODUCT, target_id, middle_relation))
count = sum(
    bool(target_middle_ids.intersection(
        self.get(PRODUCT, history_id, middle_relation)
    ))
    for history_id in set(history_ids)
)
```

Validation:

- 990 old/new comparisons matched exactly;
- 850 of those comparisons exercised histories longer than 50 items;
- the same random seed was restored before each old/new call;
- throughput increased to about 6,378 calls/second;
- projected full LastFM time fell from about 37.8 hours to about 0.6 hours.

Reason:

This changes only the implementation of the same approximate count. It does
not reduce the number of users, training interactions, metapaths, or the
native CAFE history-sampling limit.

### 2026-06-20: CAFE Top-100 Scoring Memory Bounded

The upstream CAFE preprocessor materializes the complete user-product score
matrix before selecting each user's top 100 products.

Canonical LastFM dimensions:

```text
users = 15,552
products = 47,981
full float32 score matrix = about 2.78 GiB
```

This matrix is allocated while the 5.72-million-edge KG is also resident.
The runtime patch computes the same exact per-user `argsort` in batches of 256
users:

```python
for start in range(0, len(user_embed), batch_size):
    scores = np.dot(
        user_embed[start:end] + purchase_embed,
        product_embed.T,
    )
    best100[start:end] = np.argsort(scores, axis=1)[:, -100:][:, ::-1]
```

At batch size 256, the temporary score matrix is about 46.9 MiB. This is an
exact batching transformation, not approximate retrieval, so each user's
top-100 ordering is unchanged.

Padding check:

```text
product real rows = 47,981
checkpoint rows = 47,983
remaining vocab-padding norm after CAFE's first trim = about 1.081
```

CAFE must retain one padding row in its product embedding table for shape
compatibility, but that row is not a KG product. The batched scorer therefore
uses `product_embed[:-1]` as its candidate matrix. All real-product scores and
their ordering are unchanged, while the invalid padding product cannot enter
the teacher top-100 list.

### 2026-06-20: CAFE Pseudo-Validation Disabled

Upstream CAFE creates both loaders with the same constructor:

```python
train_dataloader = OnlinePathLoader(...)
valid_dataloader = OnlinePathLoader(...)
```

`OnlinePathLoader` does not accept a split and does not read canonical
validation labels. The reported validation loss is therefore another random
sample from the same KG/top-100 training mechanism. It is not used for early
stopping or checkpoint selection; the runner loads the fixed epoch-20 model.

The runtime patch makes `--do_validation` use the existing boolean parser
correctly and honors it in the schedule. Canonical CAFE runners pass
`--do_validation false`.

Reason:

This removes repeated forward-only computation that is mislabeled as held-out
validation. It does not alter any training batch, optimizer step, epoch count,
or selected checkpoint.

### 2026-06-20: Live Execution Status

- UCPR LastFM matched-beam inference is actively progressing with
  `beam_batch_size=4` on physical GPU 1.
- The latest check observed user `1,164 / 14,544` (about 8%) at
  `2026-06-20 17:39 +08`; the log continued to update during review.
- Current throughput is about 2.6-2.8 seconds per user, implying roughly
  10-11 hours for all 14,544 users.
- The sequential queue waits for the UCPR completion marker before starting
  corrected PGPR LastFM inference/export, CAFE LastFM, UCPR ML-1M, CAFE
  ML-1M, and PGPR ML-1M.

### 2026-06-20: Clean Runtime Reconstruction Test

CAFE and PGPR source trees were copied fresh from their selected external
sources into `/tmp`. Each tracked runtime patch was then applied twice.

Result:

- first application patched all expected files;
- second application reported `already_patched`;
- all patched Python files compiled in their actual conda environments.

This confirms the runtime fixes are reproducible from clean source copies and
do not depend on the current experiment directory's manual history.

### 2026-06-21: CAFE Runtime Data Isolated from Canonical Views

The initial runners symlinked `runtime/data/.../cafe` directly to the canonical
CAFE model view. CAFE writes `tmp/kg.pkl`, top-100 candidates, path counts, and
training metadata below that data directory, so a symlink would mutate the
static canonical projection and couple later runs through stale caches.

Both LastFM and ML-1M runners now copy the small model view into their runtime
data directories. Model inputs remain byte-identical, while generated caches
and preprocessing artifacts stay inside the experiment runtime. Existing
legacy symlinks are unlinked before the copy.

### 2026-06-21: PGPR Beam Batch Restored to 16

The temporary PGPR runners inherited UCPR's conservative inference batch of 4.
PGPR's existing full LastFM `25-50-1` artifact was successfully generated by
the upstream default batch of 16, and the new runtime additionally disables
autograd during beam search. Both PGPR LastFM and ML-1M runners therefore use
`beam_batch_size=16`. This changes execution chunking only, not the beam,
scores, selected paths, or evaluation protocol.

### 2026-06-21: Resumable Queue Reconciler Added

The original `native_path_queue` tmux session started before the later PGPR
score/inference corrections and per-stage figure markers were added. It was
left running to avoid interrupting UCPR or creating concurrent GPU stages.

A separate `native_path_reconcile` tmux session now waits for the original
queue to exit, then invokes the latest `run_sequential_queue.sh`. The latest
queue skips every stage with an existing `.complete` marker and executes only
missing work. This provides eventual convergence to the current experiment
plan without killing or duplicating the active pipeline.

Logs:

```text
runs/debug_compare/2026-06-20_native_path_expansion/queue_reconciler.log
runs/debug_compare/2026-06-20_native_path_expansion/sequential_queue_reconcile.log
```

### 2026-06-21: PGPR Environment Score Matrix Bounded

PGPR used a full user-product matrix only to compute one maximum relevance
value per user for reward scaling. On canonical LastFM this temporary matrix is
roughly 4+ GiB. The runtime patch now computes the same dot products and row maxima in
batches of 256 users. A float32 smoke test measured a maximum absolute
difference of about `1.9e-6` from the monolithic GEMM because BLAS accumulation
order changes with batch shape. This is numerically equivalent rather than
bitwise identical; only peak CPU memory is materially reduced.

The PGPR test entry point also now calls `set_random_seed(args.seed)`. Action
trimming is deterministic and inference dropout is disabled, but explicitly
seeding Python, NumPy, and Torch closes the remaining reproducibility gap.

### 2026-06-21: xrecsys ETD Top-K Overflow Fixed

`optimize_ETD()` called its fallback fill helper three times. The helper stopped
only when `len(best_candidates) == 10`; if it was called again with ten items,
the next append made the length eleven and the equality could never become true
again. ETD optimization could therefore replace a top-10 recommendation list
with most or all unique candidates, corrupting recommendation denominators and
explanation metrics.

The helper now returns immediately when already full and stops on
`len >= limit`. The duplicate calls were removed. A regression test with 20
unique candidates verifies that both the helper and `optimize_ETD()` retain
exactly ten unique products. This fix was applied before the new UCPR/PGPR/CAFE
ETD sweeps began.

### 2026-06-21: Expensive Model Stages Made Resumable

The pipeline previously used only one completion marker per full model run. A
failure during adapter conversion, xrecsys evaluation, or figure generation
could therefore repeat many hours of already-completed inference or training.

The runners now create substage markers after successful TransE training,
policy training, native inference, and CAFE preprocessing/training. On retry,
completed expensive substages are reused while adapters, validators, and
xrecsys outputs can be regenerated safely. The latest queue also retries UCPR
LastFM if its original tmux session ends without the final marker; a completed
and logged raw `policy_paths_epoch30_25-50-1.pkl` prevents repeating the long
inference.

### 2026-06-21: UCPR Native Path Probability Corrected

UCPR had the same beam-export defect previously found in PGPR. It added one to
valid softmax probabilities so masked actions could not enter `torch.topk`,
then persisted those offset values:

```python
selection_probability = action_probability + 1
path_prob = product(selection_probability)
```

This produced values above one, including `2.3299024` in the existing
canonical LastFM export. The value was not a probability, even though UCPR
used it to select the best route for each item.

The runtime patch now:

1. uses the offset tensor only for top-k index selection;
2. gathers the original softmax probabilities for saved paths;
3. computes path probability as the product of the three native action
   probabilities;
4. detects and subtracts the historical `+1` offset when re-extracting from an
   already-completed raw policy-path pickle.

UCPR runners now separate expensive beam inference from path extraction. If a
raw `policy_paths_epoch*.pkl` already exists, the corrected `pred_paths.pkl`
is regenerated without rerunning the model or beam search. The shared export
validator therefore keeps the stricter finite `[0, 1]` probability contract.

### 2026-06-21: Canonical RecBole Accuracy-Reference Track Started

The server already contains RecBole implementations of `KGIN`, `KGAT`, and
`LightGCN`, plus historical LastFM/ml-100k checkpoints. Those historical runs
do not use the canonical train/validation/test contract, so their metrics
cannot be inserted directly into the new comparison.

Added:

- `scripts/data/canonical/build_recbole_view.py`;
- `scripts/validation/evaluate_uid_topk.py`.

The RecBole view preserves canonical uid/pid values as external tokens, writes
the canonical splits as pre-split benchmark files, and projects the xrecsys KG
into RecBole `.link` and `.kg` files. KGIN and KGAT will consume the KG view;
LightGCN will consume the same interaction splits without claiming path
explanations.

The first build attempt exposed that existing canonical interaction files are
headerless even though the standard documents their four field names. The
builder now accepts both headerless four-column files and files with the
documented header. No model job was started from the failed partial build.

The first ML-1M RecBole smoke also found that RecBole assumes every entity in
`.link` appears in at least one `.kg` triple. Some canonical movies have no
edge in the current projected ML-1M KG. Those movies remain in `.item` and in
the recommendation candidate space, but the builder now links only products
with at least one real KG edge. It does not manufacture self-loop triples to
make the library accept an otherwise unlinked item.

Both canonical RecBole views now pass exact train/validation/test label
round-trip checks. Dataset/model initialization passes for KGIN and LightGCN
on canonical ML-1M. KGAT currently stops at model initialization because the
isolated RecBole environment has no `dgl` package; no compatible DGL wheel is
present in the server environments or local package caches.

A one-epoch KGIN ML-1M end-to-end smoke completed on physical GPU 2:

- training and best-checkpoint reload passed;
- all 6,040 canonical test users received ten unique unseen products;
- canonical top-k validation passed;
- xrecsys-compatible metrics were written separately from RecBole's metrics.

The NDCG values differ by definition: xrecsys normalizes DCG by the ideal
ordering of the hits found within the recommended list, while RecBole uses the
standard relevance-set denominator. Both are retained and must be labelled
with their evaluator.

Added a second, independent resumable queue on physical GPU 2:

```text
runs/debug_compare/2026-06-20_native_path_expansion/
  run_recbole_accuracy_queue.sh
```

Runnable order:

1. KGIN ML-1M;
2. LightGCN ML-1M;
3. KGIN LastFM;
4. LightGCN LastFM.

KGAT is attempted only when DGL imports successfully; otherwise the queue
writes `KGAT.blocked_missing_dgl` and continues without misreporting it as a
completed experiment.

Launch status:

- the queue script, canonical views, model initialization smokes, and KGIN
  one-epoch end-to-end smoke are complete;
- a new host `tmux` launch on physical GPU 2 was requested;
- the execution approval system rejected that host-level launch because the
  current approval/usage allowance was exhausted;
- no alternate or indirect launch was attempted;
- the existing GPU 1 native-path sessions continue independently.

The RecBole queue is therefore `READY_NOT_STARTED`, not running and not
complete.

### 2026-06-21: Amazon Beauty Legacy-Compatible Canonical Track

The untreated Amazon Beauty assets were audited before adding another model
queue. Historical PGPR and CAFE use the same compact user/product id space and
the same split:

- 22,363 users and 12,101 products;
- 149,844 training interactions;
- 48,658 test interactions;
- no duplicate pairs and no train/test pair overlap;
- PGPR and CAFE per-user pair sets are exactly equal in both splits;
- their only label difference is list ordering.

All 198,502 historical pairs map one-to-one to
`reviews_Beauty_5.json.gz`, so rating and timestamp fields can be restored
without inference or duplicate resolution.

Added:

- `scripts/data/canonical/build_amazon_beauty_legacy.py`;
- `runs/debug_compare/2026-06-20_native_path_expansion/beauty_legacy_v1`;
- Beauty support in the PGPR and CAFE canonical adapters;
- Beauty support in the shared path-export validator;
- `run_pgpr_beauty_legacy_export.sh`;
- `scripts/cafe/export_legacy_beauty_paths.py`;
- `run_cafe_beauty_legacy_export.sh`.

The dataset is deliberately named `beauty_legacy_v1`. Its validation files
exist but are empty. This preserves the original PGPR/CAFE training graph:
CAFE's source KG contains purchase and review-text edges derived from every
historical training review. Moving one item per user into validation without
rebuilding those edges would create graph-side validation leakage. A future
temporal Beauty protocol must rebuild the KG from the reduced training split
and cannot reuse the historical checkpoints as canonical results.

The existing PGPR Beauty epoch-20 path artifact was exported immediately on
CPU. The source contains 2,750,781 sampled paths. The adapter found the same
historical `+1` action-probability offset seen in other legacy beam outputs and
removed it before multiplying native probabilities.

Canonical PGPR Beauty export:

- 2,423,264 unseen product-ending candidate paths;
- 22,363 test users;
- exactly ten unique unseen recommendations per user;
- 223,630 selected uid-product explanations;
- normalized native TransE score range `[0, 1]`;
- shared structural/probability/export validation: `PASS`.

Accuracy under `scripts/validation/evaluate_uid_topk.py`:

- HR@10: `0.0257121138`;
- NDCG@10 (xrecsys-compatible hit-list normalization): `0.0158111764`;
- Precision@10: `0.0028037383`;
- Recall@10: `0.0110384314`.

The CAFE Beauty runner reuses the historical KG, epoch-10 symbolic checkpoint,
849 MB inferred-metapath artifact, and profile-guided executor. The original
CAFE code reports only aggregate metrics, so the new wrapper retains executed
paths with their summed log-probability and exponentiated probability for the
shared adapter.

A one-user CPU end-to-end smoke used the real Beauty KG, epoch-10 checkpoint,
849 MB inferred-metapath artifact, and path-count profile:

- model and historical pickle loading passed in `pgpr_env`;
- profile-guided execution produced 15 unique product-ending native paths;
- the CAFE adapter produced ten explanations;
- relation/entity aliases and identity uid/pid remaps passed;
- shared structural, score, and probability validation passed.

The full runner is prepared but has not been launched: it requires a new GPU
process, while the current execution-approval allowance is exhausted and the
existing physical-GPU-1 native queue must not be disturbed.

RecBole Beauty is not started from this legacy protocol. Its benchmark/early
stopping runner requires a non-empty validation split. Creating a RecBole-only
validation split would violate the canonical split contract; using test as
validation would leak evaluation labels. RecBole Beauty therefore waits for
the future KG-rebuilt temporal protocol rather than silently changing the
experiment.

The physical-GPU-2 work is grouped in
`run_gpu2_expansion_queue.sh`. It runs CAFE Beauty first because it is a native
path model in the main explainability scope, then runs the independent
RecBole KGIN/LightGCN accuracy-reference queue. Each stage is resumable and
records its own failure marker; the queue itself has not been launched because
the current host-execution approval window is still unavailable.

### 2026-06-21: Larger Amazon Benchmark Corrected to Amazon-Book KG

Beauty is explicitly scoped as the correctness and historical cross-model
proof. Only one additional large Amazon dataset is required.

An intermediate proposal selected Amazon Cellphones 2018 and later
Electronics. That proposal was withdrawn before either dataset was downloaded:
their official review releases contain rich metadata, but the intended graph
would have been constructed by this project from brand/category/co-view
fields. It would not satisfy the stricter requirement for a dataset with an
existing benchmark KG.

The selected dataset is now the Amazon-book benchmark distributed with KGAT
and reused by KGIN:

- 70,679 users;
- 24,915 items;
- 847,733 interactions;
- 88,572 KG entities;
- 39 relations;
- 2,557,746 KG triples.

The KGAT pipeline follows KB4Rec and maps items into Freebase entities through
title matching where available. Documentation will therefore call it a
benchmark-provided Freebase KG, not an Amazon-authored KG and not a KG created
by this repository.

Added:

- `docs/guides/AMAZON_BOOK_KG_EXPERIMENT_PLAN_2026-06-21.md`.

Removed before use:

- the Cellphones/Electronics scale-plan document;
- the Cellphones 2018 download script.

No Cellphones/Electronics raw download or model run was started.

The KGAT Amazon-book source was then imported from fixed commit
`c03737be46ac26a0b5431efe149828e982ffbbfb`. All pinned SHA-256 checks pass.
The canonical build audited every KG triple and found:

- 846,434 actual source interaction pairs;
- 113,487 total entity ids, consisting of 24,915 item entities plus the
  published 88,572 non-item KG entities;
- 39 relation ids;
- 2,557,746 unique triples and no duplicates;
- all item-to-Freebase mappings aligned with the first 24,915 entity ids.

The source interaction count is 1,299 lower than the published table. Both are
recorded, but the fixed official files are authoritative for canonical runs.

Canonical split:

- train: 581,835 interactions;
- validation: 70,679 deterministic source-train holdouts;
- test: 193,920 source-test interactions over 70,591 non-empty test users.

The source has 88 empty test-user rows; they are retained in source audit
statistics but omitted from evaluation labels to avoid undefined relevance
metrics.

The RecBole view preserves all 2,557,746 KG triples and links all 24,915
products. Train/validation/test exact round-trip validation passes. KGIN and
LightGCN data/model initialization both pass on CPU:

- KGIN: 70,679 users, 24,915 items, 113,488 internal entities including
  padding, 41 internal relations including framework-added ids;
- LightGCN: 70,679 users and 24,915 items.

The full Amazon-book KGIN/LightGCN queue is scheduled after the active GPU2
Beauty/LastFM/ML-1M expansion queue. KGAT remains explicitly blocked by the
missing DGL dependency.

### 2026-06-21: UCPR LastFM Raw-Path Recovery

The first UCPR LastFM matched-beam run completed native inference and metrics
but the launch copy of the shell script ended on an unmatched quote before it
could write the completion marker. The reconciler therefore started a second
11-hour beam run.

The original raw artifact was audited before intervention:

- 14,032,980 paths;
- 14,032,980 probability rows;
- all rows have three action values;
- 14,544 model-eligible test users;
- 76 canonical test users are correctly absent because UCPR native inference
  excludes users without train history;
- raw step-value range `[1, 2]`, confirming the known historical `+1` offset.

After this evidence passed, the duplicate retry was terminated normally and
GPU resources were released. Added
`scripts/validation/validate_ucpr_raw_paths.py`; the runner now trusts an
existing raw file only when its validation summary is `PASS`.

The main queue was resumed from native-probability extraction, adapter export,
and xrecsys evaluation. It did not rerun beam inference.

### 2026-06-21: Native-Path Baseline Priority and Modern Model Audit

The experiment priority was corrected after review. KGIN, KGAT, and LightGCN
do not produce native recommendation paths and are now accuracy-only appendix
references. The active KGIN GPU2 run and the waiting Amazon-book RecBole queue
were stopped before further training.

The strict candidate audit is recorded in
`docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md`.

Immediate additions:

- KGGLM (RecSys 2024);
- PEARLM (2023);
- TPRec (TOIS 2022) on timestamped datasets only.

PR4SR and the 2024 counterfactual path framework remain watch-list items
because no verified runnable official implementation was found and their
protocols do not directly match the current user-item canonical task.
PLM-Rec is excluded from the strict table because unconstrained decoding can
produce paths absent from the KG. KGLRR is excluded because its final
explanation is not a predicted KG path.

The local Hopwise environment is usable:

- Python 3.11.14;
- Torch 2.5.1+cu121;
- Hopwise 0.9.1.post1.

Added canonical Hopwise view, smoke, and compact-run scripts. Completed:

- PEARLM canonical ML1M fixed-split load: `PASS`;
- KGGLM canonical ML1M fixed-split load: `PASS`;
- PEARLM canonical LastFM fixed-split load: `PASS`;
- KGGLM canonical Amazon-book fixed-split and 2,557,746-triple KG load:
  `PASS`;
- PEARLM full canonical ML1M training-path sampling: 6,040 paths, `PASS`;
- PEARLM KG-constrained model initialization: 54,147,840 parameters, `PASS`.
- KGGLM canonical ML1M generic pretraining paths: 9,056 paths, `PASS`;
- KGGLM model initialization: 54,147,840 parameters, `PASS`.

Two Hopwise compatibility issues were fixed in the repository-owned runner:

1. model views filter inactive `.link` catalog rows while preserving every
   interaction and KG triple;
2. the upstream dense `|V| x |V|` relation map is replaced at runtime by an
   `O(|E|)` sparse edge lookup.

KGGLM also required a sampler correction. Its parallel branch returned a lazy
`joblib` generator without consuming it, while its serial branch omitted the
worker arguments. The canonical runner installs a correct serial sampler and
asserts that non-empty paths were produced.

A compact one-epoch PEARLM canonical ML1M training/test integration run
completed on physical GPU 2. It trained 48 batches in 3.39 seconds and
evaluated all 6,040 test users in 12 seconds. Smoke metrics were Recall@10
`0.0068`, NDCG@10 `0.0243`, Hit@10 `0.1781`, Precision@10 `0.0203`, and
Fidelity@10 `0.1`. These numbers prove the integration chain only; they are
not the final baseline configuration.

### 2026-06-21: CAFE Beauty Completion and Evaluator Correction

Full CAFE Beauty native inference completed:

- 319,644 path rows;
- 22,363 users;
- 223,553 selected uid-item explanations;
- shared path export validation: `PASS`.

Forty-four users have fewer than ten unique unseen product-ending paths. The
minimum list length is five and slot coverage is 99.9656%. The evaluator now
allows explicit short native-path lists without filling them with non-path
items.

The same audit found that the previous NDCG helper constructed its ideal DCG
from the number of observed hits rather than the number of relevant items.
This overestimated NDCG. The evaluator now uses the standard
`min(K, |relevant|)` ideal ranking and always divides Precision@K by K.

Corrected Beauty metrics:

- CAFE: HR@10 `0.1015516702`, NDCG@10 `0.0365739320`,
  Precision@10 `0.0120109109`, Recall@10 `0.0557564255`;
- PGPR: HR@10 `0.0257121138`, NDCG@10 `0.0077758109`,
  Precision@10 `0.0028037383`, Recall@10 `0.0110384314`.

### 2026-06-21: LastFM Matched-Beam UCPR and Corrected PGPR Completion

The latest UCPR LastFM result is the completed matched large-candidate run,
not the earlier small-beam artifact:

- policy checkpoint: epoch 30;
- beam: `25-50-1`;
- `max_acts=50`;
- beam batch size: 4;
- tag: `25-50-1-ucpr-canonical-matched`;
- 14,032,980 raw paths and probability rows;
- 13,932,404 product-ending paths;
- 5,294,784 unseen canonical `pred_paths.csv` rows after history filtering;
- 14,620 canonical output users;
- 140,318 selected explanations;
- shared export validation: `PASS`.

The term “large candidate pool” refers to the wider native beam
`25 x 50 x 1`; it is not an exhaustive score over all 47,981 catalog
products.

UCPR xrecsys baseline (`alpha=0`, Overall):

- NDCG: `0.1255989053`;
- HR: `0.2196728592`;
- Recall: `0.01495103539`;
- Precision: `0.03157427281`;
- LIR: `0.00477369650`;
- SEP: `0.5169831079`;
- ETD: `0.1211734306`.

PGPR LastFM was then re-inferred and re-exported with native TransE item
relevance instead of the old policy-probability surrogate:

- policy checkpoint: epoch 50;
- beam: `25-50-1`;
- tag: `25-50-1-pgpr-canonical-native-score`;
- 11,695,015 unseen exported path rows;
- 14,544 users with recommendations;
- 145,390 selected explanations;
- shared export validation: `PASS`.

PGPR xrecsys baseline (`alpha=0`, Overall):

- NDCG: `0.1129505543`;
- HR: `0.1875172034`;
- Recall: `0.01096689487`;
- Precision: `0.02550922103`;
- LIR: `0.00751366738`;
- SEP: `0.5688205016`;
- ETD: `0.1609216477`.

All LIR/SEP/ETD optimization runs completed for both models. The final
LastFM comparison figures remain pending until CAFE finishes. Figures under
the older June 12 output directory must not be presented as results from
these corrected exports.

### 2026-06-21: PEARLM Canonical Export and LastFM Runtime Fixes

The one-epoch PEARLM ML-1M integration checkpoint was extended from the
framework's internal smoke metric to a validated canonical path export:

- all 6,040 canonical test users were requested;
- 29,929 KG-validated generated paths;
- 29,845 unseen exported path rows;
- 29,756 selected explanations;
- 5,933 users with at least one recommendation;
- 107 empty users;
- mean recommendation-list length `4.92649`;
- slot coverage `49.2649%`;
- shared export validation: `PASS`.

Canonical top-k accuracy for this smoke:

- HR@10: `0.1970198675`;
- NDCG@10: `0.0343417780`;
- Precision@10: `0.0234437086`;
- Recall@10: `0.0117411815`.

This remains a one-epoch integration result, not a final tuned PEARLM
baseline.

The first export audit found an upstream cumulative-score alignment defect.
Hopwise sliced the prompt tail and omitted the generated terminal item when
matching generation probabilities to tokens. KG-constrained masked prompt
tokens therefore collapsed every path score to zero. The repository runner
now aligns each generation step with the token generated at that step. The
corrected ML-1M native score range is `[0.3369653, 0.4310509]`.

PEARLM LastFM was then launched on physical GPU 2 with:

```bash
bash runs/debug_compare/2026-06-20_native_path_expansion/run_pearlm_lastfm_full_smoke.sh
```

The one-epoch train stage completed and saved:

- checkpoint:
  `huggingface-distilgpt2-PEARLM-Jun-21-2026_21-35-09.pth`;
- 121 training batches;
- 6.87 seconds model training time;
- training marker and JSON: `PASS`.

The LastFM Hopwise view contains 9,592 active linked items, not the full
47,981-item catalog. This is not interaction loss:

- every train interaction is covered;
- every validation interaction is covered;
- all 697,133 test interactions are covered;
- 38,389 removed `.link` rows are catalog items absent from all three
  canonical interaction splits;
- interaction and KG files are preserved.

The initial final-test generation failed on `U15477`. Canonical LastFM has 76
test users without train history, so those users are absent from the
train-derived collaborative KG. UCPR naturally excludes the same 76 users.
The fix does not invent fallback explanations:

- the training runner can skip Hopwise's unconditional internal final-test
  generation after saving the checkpoint;
- the canonical exporter filters only users absent from the train CKG;
- skipped canonical user ids are recorded in the raw artifact;
- the adapter still writes all test users, with empty recommendation rows for
  native-path-ineligible users.

LastFM also exposed an upstream scale issue in constrained decoding. Hopwise
cached one full-vocabulary boolean mask for every graph state. With a
106,260-token vocabulary this grows toward tens of GB. The repository-owned
runtime patch now:

- caches the vocabulary size once per logits processor;
- uses the original cache for vocabularies up to 50,000 tokens;
- uses a 4,096-entry LRU for larger vocabularies;
- bounds LastFM mask storage to roughly 0.44 GB plus Python overhead.

The export is resumable from the completed training marker. At
2026-06-21 21:54 +08, native path extraction was still running and no final
CSV/accuracy claim had been made. The active process began before the final
vocabulary-size micro-optimization was loaded; the next controlled restart
must use the current source if throughput remains poor.

### 2026-06-21: KGGLM LastFM Model-Level Smoke and Active Queue Snapshot

Added and launched:

```bash
bash runs/debug_compare/2026-06-20_native_path_expansion/run_kgglm_lastfm_model_smoke.sh
```

The smoke checks the fixed canonical split, full LastFM KG, KGGLM generic
pretraining-path sampler, and KG-constrained model initialization. It does
not claim trained recommendation performance. At 2026-06-21 21:54 +08 it was
still actively building/sampling the large collaborative graph; no completion
marker or result JSON existed yet.

Concurrent authoritative runtime state at that time:

- CAFE LastFM preprocessing: complete;
- CAFE LastFM training: epoch 7 of 20 complete;
- PEARLM LastFM one-epoch training: complete;
- PEARLM LastFM path extraction: active;
- KGGLM LastFM model-level smoke: active;
- UCPR/PGPR LastFM: complete through CSV, validation, baseline, and all three
  explanation optimizations;
- canonical ML-1M UCPR/CAFE/PGPR formal queue: waiting behind CAFE LastFM and
  the LastFM figure stage.

The sequential queue remains:

1. finish CAFE LastFM inference, adapter, validation, and xrecsys;
2. generate corrected LastFM PGPR/UCPR/CAFE figures;
3. run UCPR ML-1M;
4. run CAFE ML-1M;
5. run PGPR ML-1M;
6. generate ML-1M figures.

Host process-control approval was exhausted while attempting to reload the
last PEARLM performance patch. Existing jobs were left running. A future
continuation must inspect markers and logs before restarting anything; it
must not assume that the active process loaded the latest source.

### 2026-06-21: TPRec Added as a Native-Path Baseline

TPRec was selected for canonical integration because its recommendation is
produced by an actor-critic traversal over the collaborative KG and it returns
the traversed path. Historical Hopwise logs prove that the implementation can
complete TransE initialization, temporal pretraining, policy learning, and
path-aware evaluation on ML-100K. It is therefore a native-path model rather
than a score-only model with a post-hoc explainer.

Repository-owned integration files:

- `scripts/hopwise/tprec_runtime.py`;
- `scripts/hopwise/run_canonical_tprec.py`;
- `scripts/hopwise/export_transe_embeddings.py`;
- `scripts/hopwise/export_tprec_paths.py`.

The external Hopwise tree remains read-only. All corrections are installed at
runtime by the canonical entry points.

The audit found and corrected the following upstream defects before accepting
any TPRec result:

1. functional dropout was active during evaluation because
   `training=self.training` was omitted;
2. beam search added `1` to every valid action probability, so exported values
   were not native probabilities;
3. the temporal interaction embedding was not reset between users, causing
   cross-user accumulation;
4. the temporal matrix assumed evaluation user ids were contiguous from one
   to the number of observed users; this fails on canonical LastFM subsets;
5. result tensor rows followed the insertion order of users with paths rather
   than the requested evaluation-user order;
6. the full user-by-item normalization matrix was materialized at once;
7. TransE embeddings described as fine-tuned were frozen by
   `nn.Embedding.from_pretrained`'s default;
8. configured UI relations were expanded into synthetic relation names such
   as `UI_0`, but graph traversal emits only the real UI relation id. Every
   path therefore failed `_has_pattern()` and policy rewards were zero;
9. the original reward implementation assumed a tensor user id and failed for
   integer ids used by beam inference;
10. Hopwise's knowledge trainer references an uninitialized validation
    summary when `eval_step=0`;
11. validation dictionaries use enum keys that are not directly JSON
    serializable.

Canonical fixes now:

- disable dropout in `eval()` mode;
- retain native `[0,1]` action probabilities;
- construct a full user-indexed temporal matrix with zero vectors for absent
  users;
- calculate path scores only for the requested batch;
- preserve exact evaluation-user row order and native-path-only outputs;
- calculate normalization maxima in bounded user batches;
- fine-tune user, entity, and relation embeddings during temporal pretraining;
- match graph paths against unexpanded relation patterns while retaining
  temporal cluster embeddings in reward scoring;
- evaluate TransE once at the end instead of disabling validation;
- normalize enum-keyed summaries before writing JSON.

The first atomic-feature attempt exposed an additional canonical ID hazard.
ML-1M has 30 active items without KG links. Hopwise's embedding aliases merge
the already-final item/entity vocabulary a second time and duplicate those 30
numeric item tokens:

- TransE entity vocabulary: 9,059;
- aliased TPRec entity vocabulary: 9,089.

No interaction or item was removed. Canonical TPRec now injects the TransE
checkpoint directly during model construction. Shape checks require exact
agreement for the user, entity, and relation axes. The corrected TPRec view is
again 6,041 users, 9,059 entities, and 10 relations. Atomic embedding files are
still exportable for audit but are not used to remap TPRec.

### 2026-06-21: TPRec Canonical ML-1M End-to-End Smoke

One-epoch CPU stages were run without occupying the active experiment GPUs:

```bash
PYTHONPATH=/usr1/home/s125mdg43_08/hopwise:. \
python scripts/hopwise/run_canonical_tprec.py \
  --stage transe --dataset canonical_ml1m_v1 \
  --data-root runs/debug_compare/2026-06-20_native_path_expansion/hopwise_data \
  --checkpoint-dir runs/debug_compare/2026-06-20_native_path_expansion/tprec_ml1m_smoke/checkpoints \
  --output runs/debug_compare/2026-06-20_native_path_expansion/tprec_ml1m_smoke/transe.json \
  --epochs 1 --embedding-size 100 --train-batch-size 2048
```

TransE:

- 364 training batches in 4.73 seconds;
- validation NDCG@10 `0.0193`, HR@10 `0.0404`;
- checkpoint:
  `TransE-Jun-21-2026_22-22-12.pth`;
- stage JSON: `PASS`.

Temporal TPRec pretraining:

- 728 training batches in 28.50 seconds;
- checkpoint:
  `TPRec-canonical_ml1m_v1-1.pth`;
- all three TransE embedding tables verified trainable;
- stage JSON: `PASS`.

The first policy smoke completed with loss `0.1605`, but it was rejected after
the zero-reward pattern defect was discovered. After the correction, the
one-epoch policy stage completed six user batches in 18.12 seconds with loss
`96.3937` and saved:

`TPRec-Jun-21-2026_22-30-16.pth`.

An eight-user `25-50-1` native-path export then produced:

- 9,145 structurally valid item-ending paths;
- 8,828 paths with positive temporal reward;
- native score range `[-10.3548870, 18.3111591]`;
- native path-probability range
  `[1.327857e-07, 1.436610e-04]`;
- exact repeated-beam determinism in `eval()` mode;
- no missing graph edge or invalid configured metapath.

The shared adapter retained 6,814 unseen paths, wrote ten explanations for
each of the eight smoke users, preserved empty rows for the other canonical
test users, and passed the shared xrecsys validator. The resulting accuracy
numbers are deliberately not a baseline claim because only eight users were
exported and all stages used one epoch.

Authoritative smoke artifacts are under:

`runs/debug_compare/2026-06-20_native_path_expansion/tprec_ml1m_smoke/`.

### 2026-06-21: TPRec Canonical LastFM End-to-End Smoke

The same corrected pipeline was then exercised on canonical LastFM.

TransE one-epoch smoke:

- 678 training batches in 39.88 seconds;
- validation NDCG@10 `0.0647`;
- validation HR@10 `0.0997`;
- validation Precision@10 `0.0100`;
- checkpoint:
  `TransE-Jun-21-2026_22-34-56.pth`;
- stage JSON: `PASS`.

The TPRec temporal dataset and model preflight covered:

- 15,476 train users;
- 15,303 validation users;
- 14,620 test users;
- 15,553 internal users including padding;
- 9,593 internal items including padding;
- 90,690 entities;
- 10 relations.

All user/entity/relation checkpoint shapes matched exactly and all three
embedding tables were trainable. One temporal-pretrain epoch completed 678
batches in 76.50 seconds and saved:

`TPRec-canonical_lastfm_v1-1.pth`.

One corrected policy epoch completed four user batches in 129.44 seconds with
loss `106.1452` and saved:

`TPRec-Jun-21-2026_22-41-42.pth`.

A two-user deterministic `25-50-1` path smoke produced:

- 1,734 structurally valid item-ending native paths;
- 1,534 paths with positive temporal reward;
- native score range `[-8.2225122, 18.8327465]`;
- native probability range
  `[1.561291e-07, 8.269389e-05]`;
- exact repeated-beam determinism;
- shared graph-edge and metapath validation: `PASS`.

After canonical train-history filtering, the adapter retained 365 unseen path
rows, generated 20 explanations, preserved all 14,620 test users in
`uid_topk.csv`, and passed the common export validator. Accuracy from this
two-user export is intentionally not reported as model performance.

Authoritative artifacts are under:

`runs/debug_compare/2026-06-20_native_path_expansion/tprec_lastfm_smoke/`.

TPRec is now ready for formal multi-epoch ML-1M and LastFM queues. Full
training and full-user path export remain pending; the one-epoch checkpoints
must retain the `smoke` label and must not be shown as final baselines.

### 2026-06-21: Formal TPRec ML-1M Queue Launched

Added the resumable full-pipeline runner:

`scripts/hopwise/run_canonical_tprec_pipeline.sh`.

It writes independent completion markers for:

1. TransE;
2. TransE atomic embedding audit;
3. TPRec model/data preflight;
4. temporal pretraining;
5. policy training;
6. full-user native path extraction;
7. adapter, structural validation, accuracy, baseline, and LIR/SEP/ETD
   optimization.

The formal ML-1M queue was launched on CPU at 2026-06-21 22:48 +08 so it
would not contend with active CAFE and PEARLM GPU jobs:

```bash
bash scripts/hopwise/run_canonical_tprec_pipeline.sh canonical_ml1m_v1 \
  > runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal_ml1m.log 2>&1
```

Formal settings:

- TransE: 50 epochs;
- temporal pretraining: 5 epochs;
- policy: 50 epochs;
- beam: `25-50-1`;
- full canonical test-user export;
- output tag: `tprec-canonical-e50-25-50-1`.

At launch verification, TransE epochs 0 and 1 completed normally. The queue
remains active and no formal TPRec result is claimed until the final
`pipeline.complete` marker and shared validator summaries exist.

At 2026-06-21 22:55 +08, the formal queue had advanced through:

- TransE 50/50 epochs;
- final TransE validation NDCG@10 `0.0418`, HR@10 `0.0856`;
- atomic embedding export audit: complete;
- corrected TPRec preflight: complete;
- temporal pretraining 5/5 epochs;
- policy-stage initialization: active.

The queue remains incomplete until full policy training, full-user paths, CSV,
validation, and xrecsys optimization finish.

### 2026-06-21: KGGLM LastFM Model Smoke Completed

The long-running KGGLM LastFM model-level smoke completed at
2026-06-21 22:54:46 +08:

- fixed canonical split loading: `PASS`;
- 2,773,892 train rows;
- 15,303 validation rows;
- 697,133 test rows;
- 15,553 users including padding;
- 9,593 items including padding;
- 90,690 entities;
- 10 relations;
- 348,972 KG triples;
- 9,592 linked real items;
- tokenizer vocabulary: 106,263;
- generic KGGLM pretraining paths sampled: 90,688;
- path sampling: `PASS`;
- KG-constrained model instantiation: `PASS`;
- model parameters: 124,145,664.

This proves LastFM data, KG, tokenizer, generic pretraining-path sampler, and
model construction compatibility. It does not yet prove KGGLM training,
recommendation quality, full path export, or xrecsys integration.

### 2026-06-21 22:56 +08: Concurrent Runtime Snapshot

- CAFE LastFM preprocessing: complete;
- CAFE LastFM training: epoch 12 of 20 complete;
- PEARLM LastFM training: complete;
- PEARLM LastFM path extraction: 4,480 of 14,620 requested users processed,
  55,796 raw paths;
- KGGLM LastFM fixed-split/path-sampling/model smoke: complete and `PASS`;
- TPRec formal ML-1M TransE: 50/50 complete;
- TPRec formal ML-1M temporal pretraining: 5/5 complete;
- TPRec formal ML-1M policy: epoch 2 of 50 complete;
- UCPR and PGPR LastFM: complete through CSV, validation, baseline, and
  LIR/SEP/ETD optimization.

### 2026-06-22: PEARLM LastFM Full-User Integration Completed

The one-epoch PEARLM LastFM integration run completed through native
KG-constrained generation, canonical CSV conversion, shared structural
validation, and top-k accuracy:

- requested canonical test users: 14,620;
- processed native-path-eligible users: 14,544;
- train-graph cold-start users preserved as empty outputs: 76;
- KG-validated raw paths: 179,793;
- unseen exported paths: 179,647;
- users with recommendations: 14,544;
- selected explanations: 134,723;
- native score range: `[0.2048038542, 0.6944137812]`;
- shared export validation: `PASS`.

Canonical accuracy:

- HR@10: `0.1121751026`;
- NDCG@10: `0.01696863959`;
- Precision@10: `0.01320109439`;
- Recall@10: `0.01112636437`;
- mean native-path recommendation-list length: `9.21498`;
- slot coverage: `92.1498%`.

This remains a one-epoch integration smoke and must not be relabeled as a
tuned PEARLM baseline.

### 2026-06-22: CAFE LastFM Cold-Start Execution Failure and Fix

CAFE LastFM completed preprocessing and all 20 training epochs. Native program
inference also produced the complete
`canonical_neural_symbolic/infer_path_data.pkl`, but program execution failed
at internal user 126:

```text
KeyError: 126
program = create_heuristic_program(
    kg.metapaths, raw_paths[uid], path_counts[uid], args.sample_size
)
```

An exact set audit found 76 canonical test users absent from all three
train-derived CAFE inputs:

- `raw_paths`;
- `path_count.pkl`;
- merged train/validation history.

They are exactly the same 76 LastFM train-graph cold-start users excluded by
UCPR and recorded by PEARLM. The reusable
`scripts/model_patches/patch_cafe_runtime.py` now:

- initializes an empty native recommendation row for every test user;
- skips only users absent from `raw_paths` or `path_counts`;
- never inserts a popularity or score-only fallback;
- uses an empty prior-history list defensively;
- logs the number of native-path-ineligible users;
- remains idempotent when the runner applies the patch repeatedly.

The LastFM runner also reuses a non-empty inferred-program artifact on an
execution-only retry instead of rebuilding it. CAFE was resumed from the
completed epoch-20 checkpoint; no training was repeated.

### 2026-06-22: TPRec Formal ML-1M Extraction Made Resumable

The formal TPRec ML-1M stages completed:

- TransE: 50/50 epochs;
- temporal pretraining: 5/5 epochs;
- corrected policy training: 50/50 epochs.

The original full-user exporter then stopped without a traceback at 4,193 of
6,040 users after accumulating 4,987,682 nested path dictionaries in one
Python list. No `paths.complete` marker or final pickle existed. The process
was no longer present. Because the old exporter wrote only after all users
finished, none of that partial extraction was resumable.

The exporter and adapter were changed without reducing the formal candidate
budget:

- beam remains `25-50-1`;
- every valid native item-ending path remains exportable;
- each evaluation batch is written as an atomic pickle shard;
- existing shards are validated against dataset, policy checkpoint, beam,
  user order, and optional user limit before reuse;
- the small final manifest references the shards instead of embedding all
  rows;
- the adapter performs a validation/min-max pass followed by a streaming CSV
  pass;
- only one shard's candidate paths and per-item maxima are resident during
  CSV generation;
- exact-path de-duplication remains equivalent to the previous adapter.

Regression command:

```bash
PYTHONPATH=/usr1/home/s125mdg43_08/hopwise:. \
python scripts/hopwise/export_tprec_paths.py \
  --dataset canonical_ml1m_v1 \
  --data-root runs/debug_compare/2026-06-20_native_path_expansion/hopwise_data \
  --checkpoint-dir runs/debug_compare/2026-06-20_native_path_expansion/tprec_ml1m_smoke/checkpoints \
  --policy-checkpoint runs/debug_compare/2026-06-20_native_path_expansion/tprec_ml1m_smoke/checkpoints/TPRec-Jun-21-2026_22-30-16.pth \
  --output /tmp/tprec_sharded_regression.pkl \
  --shard-dir /tmp/tprec_sharded_regression_parts \
  --batch-size 8 --beam-search-hop 25 50 1 --max-users 8 \
  --verify-determinism
```

The eight-user regression reproduced the prior smoke exactly:

- raw paths: 9,145;
- positive-reward paths: 8,828;
- unseen paths: 6,814;
- explanations: 80;
- native-score and path-probability ranges: exact match;
- sorted `pred_paths.csv` content: exact match;
- `uid_topk.csv`: byte-identical;
- `uid_pid_explanation.csv`: byte-identical;
- a second extractor invocation reused all eight shards;
- shared export validation: `PASS`.

The formal pipeline now passes
`--shard-dir <formal-output>/path_shards`. Formal extraction and evaluation
remain incomplete until the resumed queue writes `pipeline.complete`.

### 2026-06-22 04:02 +08: CAFE LastFM Export Passed and Formal Queues Resumed

The corrected CAFE execution completed all 14,620 canonical test users:

- native-path-ineligible users: 76, emitted as empty rows;
- model `pred_paths.pkl`: approximately 180 MB;
- unseen canonical `pred_paths.csv`: 2,056,564 rows;
- users with native recommendations: 14,544;
- selected explanations: 145,440;
- raw log-score range: `[-306.476837, -0.195225]`;
- normalized score range: `[0, 1]`;
- shared export validation: `PASS`.

The canonical top-k evaluator, which uses standard IDCG and divides
Precision@10 by ten, reported:

- HR@10: `0.1802325581`;
- NDCG@10: `0.03005525217`;
- Precision@10: `0.02571819425`;
- Recall@10: `0.01863885183`;
- empty users: 76;
- slot coverage: `99.4802%`.

The xrecsys baseline table uses its historical comparison protocol and
reported:

- NDCG: `0.1018903099`;
- HR: `0.1811743674`;
- Recall: `0.01147136444`;
- Precision: `0.02585258526`;
- LIR: `0.001205329855`;
- SEP: `0.7307516265`;
- ETD: `0.2275345797`.

These two metric blocks are intentionally labeled separately; the standard
top-k JSON must not be silently substituted for the historical xrecsys
trade-off table. CAFE LIR/SEP/ETD optimization was still active at this
snapshot.

TPRec ML-1M formal extraction was resumed from the completed epoch-50 policy.
The first restart exposed a server-device selection issue: Hopwise/RecBole
rewrites `CUDA_VISIBLE_DEVICES` from its `gpu_id`, so passing post-mask ordinal
zero overrides an outer physical-card mask. The TPRec runner now:

- sets `CUDA_DEVICE_ORDER=PCI_BUS_ID`;
- exports the requested physical mask;
- passes the same physical id to Hopwise configuration.

Host `nvidia-smi` process UUID verification confirms TPRec is on physical GPU
2. Existing shards were reused before new users were generated.

The same audit found that UCPR's TransE entry point independently rewrites
`CUDA_VISIBLE_DEVICES` from `--gpu`. The ML-1M UCPR runner now accepts a
physical GPU argument, sets PCI bus ordering, and passes that physical id to
TransE while retaining visible-device ordinal zero for policy/test code that
does not rewrite the environment. Host UUID verification confirms the
resumed UCPR TransE process is on physical GPU 3.

### 2026-06-22: PGPR LastFM Canonical User Denominator Corrected

Running the standalone canonical `uid_topk` evaluator across completed LastFM
exports exposed a user-set inconsistency:

- UCPR writes all 14,620 canonical test users, including empty rows;
- CAFE writes all 14,620 canonical test users, including the 76 train-graph
  cold-start users as empty rows;
- PEARLM follows the same policy;
- PGPR wrote only its 14,544 native-path-eligible users.

The shared path validator previously accepted this because all written users
were valid test users, but it did not require exact test-user coverage. The
standalone accuracy evaluator correctly rejected PGPR with 76 missing users.

`adapters/pgpr_adapter.py` now loads canonical `test_label.pkl` whenever
`--labels-dir` is supplied and:

- rejects sampled paths for users outside the canonical test set;
- initializes `uid_topk.csv` and `uid_pid_explanation.csv` for every canonical
  test user;
- preserves empty rows for the 76 PGPR-ineligible users;
- does not create fallback recommendations or explanations.

The 13.8-million-path beam artifact and native TransE scores are reused; only
CSV conversion and evaluation are repeated. Existing PGPR LastFM xrecsys
tables were calculated with the 14,544-user file and are therefore historical,
not final canonical-denominator results, until baseline and LIR/SEP/ETD are
regenerated from the corrected 14,620-user CSV.

### 2026-06-22: CAFE LastFM Formal Pipeline Completed

CAFE LastFM completed all xrecsys stages:

- baseline: complete;
- LIR alpha sweep: 21/21 alpha values;
- SEP alpha sweep: 21/21 alpha values;
- ETD alpha sweep: 21/21 alpha values.

The process reached the end of ETD at 2026-06-22 04:18:37 +08. A shell syntax
error was then reported because the runner file had been edited while the
already-running Bash process was reading later lines. The current file passes
`bash -n`; model output and all result CSVs were unaffected. The completion
marker was written only after:

- strict exact test-user validation passed;
- all three non-empty optimization files existed;
- every optimization contained the expected 21 Overall alpha values.

CAFE LastFM is therefore complete through preparation, epoch-20 training,
native inference, CSV, standard accuracy, xrecsys baseline, and all three
trade-off sweeps. Comparison figures still wait for corrected PGPR
full-user-denominator results.

### 2026-06-22: TPRec Formal ML-1M Completed

The resumable TPRec ML-1M formal pipeline completed at
2026-06-22 08:34:31 +08:

- TransE: 50 epochs;
- temporal pretraining: 5 epochs;
- policy: 50 epochs;
- beam: `25-50-1`;
- requested/processed users: 6,040/6,040;
- atomic path shards: 6,040;
- raw native paths: 7,188,427;
- positive-temporal-reward paths: 7,061,369;
- unseen exported paths: 4,218,974;
- users with recommendations: 6,040;
- selected explanations: 60,399;
- deterministic repeated-beam check: `PASS`;
- strict shared export validation: `PASS`;
- final `pipeline.complete`: present.

Standard canonical top-k metrics:

- HR@10: `0.4745033113`;
- NDCG@10: `0.09426046977`;
- Precision@10: `0.08970198675`;
- Recall@10: `0.04377185572`;
- one user has nine native recommendations; all others have ten;
- slot coverage: `99.9983%`.

xrecsys historical-comparison baseline:

- NDCG: `0.2630800120`;
- HR: `0.4744162941`;
- Recall: `0.04377711365`;
- Precision: `0.08963404537`;
- LIR: `0.4530435210`;
- SEP: `0.4948293327`;
- ETD: `0.2910927152`.

LIR, SEP, and ETD sweeps each contain all 21 alpha values. This is the first
newer-model formal native-path result completed on canonical ML-1M.

### 2026-06-22: UCPR Formal ML-1M Completed

The UCPR ML-1M formal queue completed at 2026-06-22 11:30:20 +08:

- TransE: 30 epochs, completed 04:44:59;
- policy: 40 epochs, completed 05:43:54;
- native `25-50-1` beam inference: all 6,040 users, completed after
  5 hours 23 minutes;
- native-probability extraction: complete;
- unseen exported paths: 2,543,087;
- users in canonical `uid_topk.csv`: 6,040;
- users with candidate paths: 5,988;
- selected explanations: 50,022;
- strict exact test-user validation: `PASS`;
- LIR/SEP/ETD sweeps: 21/21 alpha values each;
- final completion marker: present.

Standard canonical top-k metrics:

- HR@10: `0.4418874172`;
- NDCG@10: `0.08714204382`;
- Precision@10: `0.06639072848`;
- Recall@10: `0.03791315430`;
- empty users: 52;
- slot coverage: `82.8179%`.

xrecsys historical-comparison baseline:

- NDCG: `0.2519919206`;
- HR: `0.4157594609`;
- Recall: `0.04886036583`;
- Precision: `0.06174183515`;
- LIR: `0.4524662542`;
- SEP: `0.4935368585`;
- ETD: `0.2177980132`.

### 2026-06-22: Exact Canonical Test-User Validation Gate Added

`scripts/validation/validate_xrecsys_export.py` now supports
`--require-all-test-users`. Formal canonical runners enable it so that
`uid_topk.csv` must contain exactly the canonical test-user set, including
explicit empty rows. Partial-user smoke exports can omit the flag.

Strict revalidation passed for:

- UCPR LastFM;
- CAFE LastFM;
- PEARLM LastFM;
- corrected PGPR LastFM;
- UCPR ML-1M;
- TPRec ML-1M.

The corrected PGPR LastFM CSV now contains all 14,620 canonical test users:

- 14,544 users with native recommendations;
- 76 explicit empty users;
- 11,695,015 unseen path rows;
- 145,390 selected explanations;
- strict export validation: `PASS`.

Standard PGPR LastFM metrics after the denominator correction:

- HR@10: `0.1863885089`;
- NDCG@10: `0.03135817541`;
- Precision@10: `0.02535567715`;
- Recall@10: `0.01773135800`;
- slot coverage: `99.4460%`.

The corrected PGPR xrecsys baseline and LIR/SEP/ETD regeneration is active;
the LastFM comparison figures remain gated on its completion.

### 2026-06-22: Corrected LastFM Comparison Figures Completed

PGPR LastFM full-user CSV re-evaluation completed after the exact canonical
test-user fix:

- baseline regenerated: complete;
- LIR: 21/21 alpha values;
- SEP: 21/21 alpha values;
- ETD: 21/21 alpha values;
- re-evaluation completion marker: present.

The xrecsys recommendation metrics remain numerically unchanged because its
historical path loader evaluates users with candidate paths, while the
standalone canonical accuracy JSON includes all 14,620 test users. The
regenerated explanation baselines are:

- LIR: `0.007495017010`;
- SEP: `0.5688205016`;
- ETD: `0.1600851193`.

After verifying all three models had complete 21-point sweeps, the corrected
LastFM figures were generated under:

`reports/figures/tradeoff/canonical_lastfm_native_paths_v2/`

Artifacts:

- 12 PNG comparison plots: four recommendation metrics for each of
  LIR/SEP/ETD;
- 12 corresponding CSV tables;
- `figures_lastfm.complete`: present.

A visual inspection of `tradeoff_lastfm_SEP_ndcg_models.png` confirmed that
the PGPR, UCPR-matched, and CAFE curves, alpha endpoints, axes, and legend are
rendered and not clipped. Older June-12 figures remain historical and must not
be substituted for this directory.

### 2026-06-22: xrecsys Moving-Alpha Sweeps Made Resumable

The corrected PGPR LastFM re-evaluation was interrupted by an execution
session refresh during SEP at alpha `0.65`. The default xrecsys behavior opens
the moving-alpha output files with truncation, so a blind retry would discard
all completed alpha values.

`xrecsys/main.py` now supports:

```bash
python main.py ... --opt SEPopt --resume-moving-alpha
```

Resume behavior:

- scans both average and distribution CSVs;
- counts rows independently for every alpha;
- treats an alpha as complete only when both files contain the full expected
  row count;
- removes partial rows for an interrupted alpha;
- appends only missing alpha values;
- flushes both output streams after every completed alpha;
- rejects combining `--resume-moving-alpha` with a single explicit
  `--alpha`.

For the interrupted PGPR SEP files, the audit found:

- alpha `0.00` through `0.60`: 70/70 average rows and complete distributions;
- alpha `0.65`: only 35/70 average rows;
- resumable completed set: 13 alpha values.

The retry therefore preserved the first 13 values and resumed at `0.65`
instead of restarting from zero. The same mechanism can recover future LIR,
SEP, or ETD sweeps after scheduler or session interruption.

### 2026-06-22: Sweep Completion Gate and Corrected LastFM Figures

Added `scripts/validation/validate_xrecsys_sweeps.py`. A formal xrecsys result
now passes only when:

- `baseline_avg.csv` is present and non-empty;
- LIR, SEP, and ETD average files each contain exactly 21 expected alphas;
- all average alphas have the same row count;
- all distribution alphas have the same row count;
- no unexpected alpha is present.

Formal runners invoke this gate before writing their final marker. Existing
completed artifacts passed:

- UCPR LastFM;
- CAFE LastFM;
- UCPR ML-1M;
- TPRec ML-1M.

The corrected PGPR LastFM rerun then completed:

- baseline regenerated from the 14,620-user CSV;
- LIR: 21/21;
- SEP: resumed from 13 complete alphas and finished 21/21;
- ETD: regenerated from zero and finished 21/21;
- sweep validation: `PASS`;
- full-user re-evaluation marker: present.

Corrected PGPR xrecsys baseline:

- NDCG: `0.1129505543`;
- HR: `0.1875172034`;
- Recall: `0.01096689487`;
- Precision: `0.02550922103`;
- LIR: `0.007495017010`;
- SEP: `0.5688205016`;
- ETD: `0.1600851193`.

The recommendation metrics remain numerically equal to the prior xrecsys
table because that evaluator skips empty recommendation rows internally. LIR
and ETD changed after exact-user CSV regeneration, so the old explanation
metric files were not reused.

Final corrected LastFM comparison figures were generated under:

`reports/figures/tradeoff/canonical_lastfm_native_paths_v2/`

Artifacts:

- three explanation objectives: LIR, SEP, ETD;
- four recommendation metrics per objective: NDCG, HR, Precision, Recall;
- 12 PNG figures;
- 12 matching source CSV tables;
- all inputs validated at 21 alpha values;
- visual inspection confirmed PGPR, UCPR-matched, and CAFE curves, legends,
  and alpha endpoints are rendered.

The older June 12 figure directory remains historical and must not be used for
the corrected result.

### 2026-06-22 19:03 +08: CAFE Formal ML-1M Pipeline Started

The canonical CAFE ML-1M view was rebuilt from the completed UCPR ML-1M
TransE checkpoint before starting the formal model queue:

- canonical users: 6,040;
- canonical products: 3,265;
- enabled native metapath rules: 9;
- forward interaction/KG edges: 856,748;
- triples including reverse edges: 1,713,496;
- train/validation/test user sets map back exactly to the canonical labels;
- embedding dimension: 100;
- source UCPR checkpoint: epoch 30 formal ML-1M TransE.

The first interactive preprocessing attempt was interrupted while estimating
per-user path counts. It had created only `embed.pkl`, `kg.pkl`, and
`user_products_pos.npy`; no preprocessing completion marker was written.
These partial files were therefore not treated as a completed stage.

All four physical RTX A5000 GPUs were idle at launch. The formal CAFE ML-1M
pipeline was started on physical GPU 3 with:

```bash
/bin/bash -x \
  runs/debug_compare/2026-06-20_native_path_expansion/run_cafe_ml1m_canonical.sh \
  3
```

The runner:

1. rebuilds and validates the aligned CAFE model view;
2. completes path-count preprocessing for all 6,040 users;
3. trains the neural-symbolic model for 20 epochs;
4. infers and executes native programs;
5. exports canonical path CSVs with an exact-test-user gate;
6. computes standard top-k accuracy and xrecsys baseline;
7. completes resumable 21-point LIR, SEP, and ETD sweeps;
8. writes `cafe_ml1m.complete` only after sweep validation passes.

At this timestamp the process is in step 2, path-count preprocessing. CAFE
ML-1M must not yet be reported as trained or as having a formal result.
PGPR ML-1M remains prepared but unstarted so the two formal model jobs do not
compete for host CPU during CAFE preprocessing.

The ML-1M CAFE and PGPR runners were also hardened for view refresh and
resume:

- rebuilding a canonical model view now refreshes the corresponding runtime
  source files even when the runtime directory already exists;
- CAFE keeps generated `tmp/` artifacts, so a refreshed view does not destroy
  resumable preprocessing or model outputs;
- PGPR preprocessing now has its own
  `pgpr_ml1m_preprocess.complete` marker and is skipped on a valid resume.

CAFE preprocessing finished at 2026-06-22 19:15:18 +08:

- path-count users: 6,040/6,040;
- `path_count.pkl`: present and non-empty;
- `cafe_ml1m_preprocess.complete`: present.

Editing the live runner while Bash was reading later lines caused the same
line-offset failure mode previously observed after CAFE LastFM: after writing
the valid preprocessing marker, the old shell interpreted a continuation
argument as a command. No model training had started and no artifact was
invalidated. The current runner passes `bash -n`; it was restarted from the
preprocessing marker without repeating path counting. CAFE ML-1M formal
epoch-20 training then started on physical GPU 3 at 2026-06-22 19:23:12 +08.
The process exposed the selected physical card as local `cuda:0`, as expected.

### 2026-06-22 20:05 +08: PGPR Formal ML-1M Pipeline Started

With physical GPUs 0, 1, and 2 still idle, PGPR ML-1M was started in parallel
on physical GPU 2:

```bash
/bin/bash \
  runs/debug_compare/2026-06-20_native_path_expansion/run_pgpr_ml1m_canonical.sh \
  2
```

The clean PGPR runtime loaded:

- 6,040 users;
- 3,265 movies;
- 744,603 training reviews;
- 15,112 total graph nodes;
- 1,489,206 bidirectional review edges;
- the same nine non-empty ML-1M KG relation families used by the aligned
  UCPR/CAFE views.

Canonical PGPR preprocessing completed and the formal TransE epoch-30 stage
started successfully. GPU inspection confirmed independent placement:

- PGPR ML-1M: physical GPU 2;
- CAFE ML-1M: physical GPU 3;
- physical GPUs 0 and 1 remained idle.

The PGPR pipeline will continue through policy epoch 50, native
`25-50-1` extraction, exact-user CSV validation, standard accuracy, and the
three validated 21-point explanation sweeps. It is not yet a completed
ML-1M result.

### 2026-06-22 20:29 +08: TPRec Formal LastFM Pipeline Started

The completed two-user LastFM smoke was not reused as a formal result. A new
formal output directory was created and the full TPRec LastFM pipeline was
started on physical GPU 1:

```bash
/bin/bash scripts/hopwise/run_canonical_tprec_pipeline.sh \
  canonical_lastfm_v1 1
```

Formal configuration:

- TransE: 50 epochs, embedding size 100;
- temporal pretraining: 5 epochs;
- corrected policy training: 50 epochs;
- beam: `25-50-1`;
- training batch size: 4,096;
- extraction batch size: 4;
- resumable per-user path shards;
- deterministic repeated-beam verification;
- exact 14,620-user export validation;
- standard accuracy plus validated 21-point LIR/SEP/ETD sweeps.

The TransE model loaded 15,553 users, 90,690 entities, 10 relation types, and
10,625,300 trainable parameters. GPU inspection after launch showed:

- TPRec LastFM on physical GPU 1;
- PGPR ML-1M on physical GPU 2;
- CAFE ML-1M on physical GPU 3;
- physical GPU 0 idle.

This stage is active and must not yet be reported as a completed TPRec
LastFM baseline.

### 2026-06-22 21:20 +08: CAFE Formal ML-1M Completed

CAFE ML-1M completed its full formal pipeline:

- preprocessing: 6,040/6,040 users;
- training: 20/20 epochs;
- native program inference and execution: complete;
- unseen canonical path CSV rows: 2,349,585;
- canonical test users: 6,040/6,040;
- users with recommendations: 6,040;
- explanations: 60,400;
- recommendation length: exactly 10 for every user;
- strict export validation: `PASS`;
- LIR, SEP, and ETD sweeps: 21/21 alpha values each;
- sweep validation: `PASS`;
- `cafe_ml1m.complete`: present.

Standard canonical accuracy:

- HR@10: `0.5543046358`;
- NDCG@10: `0.1165709173`;
- Precision@10: `0.1071192053`;
- Recall@10: `0.05202378906`.

xrecsys historical-comparison baseline:

- NDCG: `0.3228955112`;
- HR: `0.5543046358`;
- Recall: `0.05202378906`;
- Precision: `0.1071192053`;
- LIR: `0.3949423764`;
- SEP: `0.4619402987`;
- ETD: `0.2697350993`.

CAFE is now a completed, displayable canonical ML-1M result. At completion,
its standard HR/NDCG/Precision/Recall are all higher than the completed UCPR
and TPRec ML-1M runs.

### 2026-06-22: Formal PEARLM Runner and Resumable Export Added

The one-epoch, two-layer PEARLM smoke is intentionally retained as an
integration result and is not relabeled as a baseline. Added
`scripts/hopwise/run_canonical_pearlm_pipeline.sh` for formal canonical runs.
Its default architecture and training schedule follow the repository's
PEARLM experiment configuration:

- 50 epochs;
- embedding/hidden size 768;
- 12 attention heads;
- 6 transformer layers;
- training batch size 64;
- 250 warmup steps;
- deterministic 25-beam native KG-constrained generation.

The canonical adaptation keeps the established three-hop constrained native
path semantics and exact canonical split rather than reverting to a random
framework split.

`scripts/hopwise/export_native_paths.py` now optionally writes atomic
per-batch shards. Each shard records and validates:

- model and canonical dataset;
- checkpoint path, file size, and modification timestamp;
- beam/path counts and batch size;
- exact canonical users assigned to the batch;
- processed and cold-start user accounting;
- generated native path rows.

A 64-user LastFM regression used the existing compact checkpoint with two
32-user shards. The second export reported `resumed_batch=0` and
`resumed_batch=1`, generated no replacement shards, and produced a final
payload semantically identical to the first export:

- requested users: 64;
- processed users: 64;
- raw validated paths: 764;
- semantic payload equality: `True`.

The two pickle byte hashes differ because pickle memoizes shared object
references differently when rows are reloaded from independent shards; all
decoded fields and rows compare exactly equal.

The formal PEARLM LastFM pipeline was then started on the released physical
GPU 3 at 2026-06-22 21:55:52 +08:

```bash
/bin/bash scripts/hopwise/run_canonical_pearlm_pipeline.sh \
  canonical_lastfm_v1 3
```

The instantiated model has 124,145,664 trainable parameters and a 106,263
token canonical LastFM vocabulary. Training batch size 64 fits on one RTX
A5000 without OOM; the first four epochs completed in about 27 seconds per
epoch. This is the first formal PEARLM LastFM run and is separate from the
one-epoch compact smoke.

### 2026-06-22: PEARLM Validation-Selection Bug Found

The first 50-epoch, six-layer PEARLM run completed structurally:

- training: 50/50 epochs;
- all 14,620 canonical users accounted for;
- native paths: 191,133;
- unseen exported paths: 191,016;
- strict export validation: `PASS`;
- all three 21-point xrecsys sweeps: `PASS`.

However, standard accuracy was unexpectedly below the one-epoch compact
integration smoke:

- HR@10: `0.07749658003`;
- NDCG@10: `0.01291121710`;
- Precision@10: `0.01068399453`;
- Recall@10: `0.007280602971`.

This exposed a training-selection bug in the canonical integration runner.
`build_pearlm_config()` had forced `eval_step=0`, and `run_train_only()` called
the Hopwise trainer with `saved=False`. Hopwise's `HopwiseCallback` explicitly
skips validation when `eval_step <= 0` and only saves best checkpoints when
`saved=True`. Consequently:

- `best_valid_score` and `best_valid_result` were null;
- no validation-selected checkpoint existed;
- export used the final epoch after the loss had largely saturated;
- the result is valid as a **final-epoch diagnostic**, not as a tuned formal
  baseline.

The result JSON was relabeled accordingly; its artifacts are retained for
auditing and overfitting analysis.

The formal runner now uses:

- validation every 5 epochs;
- early-stopping patience of 5 validation checks;
- `saved=True` through `--select-best-validation`;
- a separate output root and agent tag containing `bestval`;
- the same fixed canonical validation split.

The corrected best-validation run started on physical GPU 3 at
2026-06-22 23:18:12 +08. Epoch-5 validation executed successfully and wrote a
best checkpoint, proving that validation/checkpoint selection is active.

The first corrected attempt still used the integration runner's hard-coded
single validation beam. That selection objective does not match PEARLM's
official ten-beam validation configuration or the formal 25-beam export.
The run was stopped before completion and is not a result artifact.

The runner now exposes validation path/beam counts separately from final
export and uses:

- validation paths per user: 10;
- validation beams: 10;
- final export paths/beams: 25/25.

A clean `bestval10` run started at 2026-06-22 23:48:53 +08. Epoch-5
validation completed in 159 seconds with Fidelity@10 `0.6405` and NDCG@10
`0.0037`, and wrote a validation-selected checkpoint. This run remains
active.

### 2026-06-22 23:10 +08: PGPR Formal ML-1M Completed

PGPR ML-1M completed its full formal pipeline:

- preprocessing: complete;
- TransE: 30/30 epochs;
- policy: 50/50 epochs;
- native beam: `25-50-1`;
- raw beam artifact: approximately 847 MB;
- unseen canonical path rows: 5,457,838;
- canonical test users: 6,040/6,040;
- users with exactly ten recommendations: 6,040;
- explanations: 60,400;
- strict export validation: `PASS`;
- LIR, SEP, and ETD sweeps: 21/21 each;
- sweep validation: `PASS`;
- `pgpr_ml1m.complete`: present.

Standard canonical accuracy:

- HR@10: `0.5112582781`;
- NDCG@10: `0.1013894733`;
- Precision@10: `0.09291390728`;
- Recall@10: `0.04234239176`.

xrecsys historical-comparison baseline:

- NDCG: `0.2967702239`;
- HR: `0.5112582781`;
- Recall: `0.04234239176`;
- Precision: `0.09291390728`;
- LIR: `0.4620944067`;
- SEP: `0.4797962841`;
- ETD: `0.1626324503`.

PGPR is now a completed, displayable canonical ML-1M result. Together with
UCPR, CAFE, and TPRec, the existing-model ML-1M comparison set is complete;
the final multi-model figures still wait for active TPRec LastFM extraction
only if the figure set is expanded to include cross-dataset new models.

### 2026-06-22: Four-Model ML-1M Comparison Figures Completed

The completed PGPR, UCPR, CAFE, and TPRec ML-1M sweeps were rendered under:

`reports/figures/tradeoff/canonical_ml1m_native_paths/`

Artifacts:

- LIR, SEP, and ETD objectives;
- NDCG, HR, Precision, and Recall recommendation metrics;
- 12 PNG figures;
- 12 matching source CSV tables;
- `figures_ml1m.complete`: present.

Visual inspection of the SEP–NDCG and ETD–HR plots confirmed:

- all four model curves are present;
- alpha-0 and alpha-1 endpoint markers are rendered;
- axes and legends are not clipped;
- the large CAFE/PGPR/TPRec/UCPR differences are represented without
  accidental curve truncation.

### 2026-06-23: KGGLM Two-Stage Formal Pipeline Added

KGGLM is now integrated as a true two-stage native-path baseline rather than
only a model-construction smoke:

1. generic KG-only path pretraining;
2. recommendation-path finetuning from the generic checkpoint;
3. validation-selected finetuning checkpoint export;
4. deterministic KG-constrained native path generation;
5. canonical CSV conversion, strict validation, accuracy, xrecsys baseline,
   and 21-point LIR/SEP/ETD sweeps.

The formal defaults follow the authors' official recommendation table:

- generic pretraining: 3 epochs;
- recommendation-specific finetuning: 2 epochs;
- hidden size: 768;
- attention heads: 12;
- transformer layers: 6;
- batch size: 256;
- learning rate: `2e-4`.

The canonical finetuning view retains the same fixed split and constrained
three-hop recommendation-path semantics used by PEARLM. The generic
pretraining stage installs the existing corrected serial sampler because
upstream KGGLM has both a missing-arguments serial call and an unconsumed lazy
parallel generator.

Implemented:

- `build_kgglm_config()` in `scripts/hopwise/canonical_config.py`;
- KGGLM pretrain/finetune support in
  `scripts/hopwise/run_canonical_native_path.py`;
- KGGLM checkpoint loading and export support in
  `scripts/hopwise/export_native_paths.py`;
- `scripts/hopwise/run_canonical_kgglm_pipeline.sh`.

The first compact canonical ML-1M regression exposed a Hopwise configuration
compatibility bug. Explicitly passing the historical string
`pretrain_hop_length="(3,3)"` through `config_dict` caused the configurator to
convert it to a tuple before `KGGLMDataset` attempted to parse it as a string.
The canonical builder now leaves that property to KGGLM's model YAML and only
overrides the sampler parameters that differ.

After the fix, the two-stage ML-1M smoke passed:

- generic KG paths: 9,057;
- compact pretraining: 1 epoch, `PASS`;
- pretrained checkpoint: safetensors load, `PASS`;
- compact recommendation finetuning: 1 epoch, `PASS`;
- validation NDCG@10: `0.0026`;
- 16 requested export users, 16 processed;
- 30 edge-validated native paths;
- two atomic path shards;
- sharded manifest and canonical CSV validation: `PASS`.

The PEARLM/KGGLM exporter now writes a small `row_shards` manifest when
`--shard-dir` is enabled instead of re-embedding all rows in the final pickle.
The adapter already supports two-pass streaming over this format. A regression
rebuilt the completed 191,133-path PEARLM LastFM diagnostic from its 457
existing shards:

- raw paths: 191,133;
- unseen paths: 191,016;
- output users: 14,620;
- `uid_topk.csv`: byte-identical to the prior direct-pickle conversion;
- `uid_pid_explanation.csv`: byte-identical;
- regression status: `PASS`.

Formal KGGLM ML-1M was started on physical GPU 2 at
2026-06-23 00:34:54 +08:

```bash
/bin/bash scripts/hopwise/run_canonical_kgglm_pipeline.sh \
  canonical_ml1m_v1 2
```

This remains active and is not yet a reportable formal result.

At the same snapshot:

- TPRec LastFM has completed TransE, temporal pretraining, and policy
  training; resumable full-user extraction reached 2,502/14,620 shards
  (`17.11%`);
- PEARLM LastFM `bestval10` reached epoch 35. Epoch 10 remains the best
  validation checkpoint with NDCG@10 `0.0049`;
- Hopwise continued training after five later non-improving validation checks,
  so configured patience does not currently guarantee an early stop. The run
  still preserves and exports the validation-selected best checkpoint.

### 2026-06-23: PEARLM Best-Validation LastFM Completed

The corrected PEARLM LastFM `bestval10` pipeline completed at
2026-06-23 00:54:59 +08:

- training stopped after epoch 40;
- validation executed every five epochs with 10 paths and 10 beams;
- best checkpoint: epoch 10;
- best validation NDCG@10: `0.0049`;
- final export: 25 paths and 25 beams per eligible user;
- requested users: 14,620;
- processed train-graph-eligible users: 14,544;
- preserved cold-start empty users: 76;
- raw edge-validated paths: 183,676;
- unseen canonical paths: 183,538;
- users with recommendations: 14,340;
- selected explanations: 126,145;
- atomic path shards: 457;
- strict exact test-user validation: `PASS`;
- legacy xrecsys LIR/SEP/ETD sweeps: 21/21 each;
- finite-Overall sweep validation: `PASS`;
- `pipeline.complete`: present.

Corrected standard canonical metrics after the NDCG discount audit:

- HR@10: `0.09958960328`;
- NDCG@10: `0.01595967406`;
- Precision@10: `0.01273597811`;
- Recall@10: `0.009046671640`;
- empty users: 280;
- slot coverage: `86.2825%`.

The legacy exact-ten xrecsys baseline remains separately labeled:

- NDCG: `0.05707241003`;
- HR: `0.09894485367`;
- Recall: `0.006234530771`;
- Precision: `0.01262193908`;
- LIR: `0.001144790065`;
- SEP: `0.5263316048`;
- ETD: `0.1109667123`.

This is the first validation-selected formal PEARLM result. The earlier
50-epoch final-checkpoint diagnostic and one-epoch compact integration run
remain audit artifacts and must not replace it.

### 2026-06-23: TPRec Full-Sort Batch Semantics Fixed

TPRec's exporter accepted `--batch-size 4`, but Hopwise's
`FullSortRecEvalDataLoader` interprets `eval_batch_size` as
`users × item_count`. Passing four therefore produced one user per dataloader
batch and made LastFM extraction unnecessarily slow.

The exporter now:

- takes the fixed test-user order directly from `test_data.uid_list`;
- groups missing users into real four-user beam calls;
- continues writing one shard per user, preserving the existing shard schema;
- validates and reuses every old one-user shard unchanged;
- splits generated paths back to their origin user before atomic writes.

An eight-user formal ML-1M regression compared the new four-user beam calls
against the prior one-user formal shards:

- native path keys and order: exact;
- native item scores: exact;
- positive-reward counts: exact;
- path-probability difference: at most approximately `7e-11`, caused by
  batched floating-point evaluation;
- final `uid_topk.csv`: byte-identical;
- final `uid_pid_explanation.csv`: byte-identical.

The old LastFM exporter was stopped with `SIGINT` after 2,765 safely written
shards. The formal runner restarted at 2026-06-23 00:48:19 +08 and reused
those shards before generating new users in groups of four. No TransE,
temporal pretraining, or policy training was repeated.

### 2026-06-23: Canonical Recommendation-Evaluation Protocol Added

The KGGLM ML-1M run exposed that legacy xrecsys skips every recommendation
list shorter than ten. KGGLM produced no exact-ten lists, so the old protocol
wrote `NaN` for all Overall recommendation metrics even though the canonical
CSV and standalone evaluator were valid.

The legacy behavior is retained for historical comparison, but xrecsys now
also supports:

```text
--rec_eval_protocol canonical-all-users
--result_tag <separate-result-tag>
```

The canonical protocol:

- evaluates every canonical test user, including empty rows;
- keeps genuine native-path short lists without score-only filling;
- divides Precision@10 by ten;
- uses standard DCG discounts `1/log2(rank+1)`;
- builds IDCG from `min(10, |relevant|)`;
- writes into a separate result directory so legacy artifacts are not
  overwritten.

Added `scripts/hopwise/run_canonical_xrecsys_protocol.sh` to run the baseline,
all three 21-point sweeps, and validation under this protocol.

The same audit found that `scripts/validation/evaluate_uid_topk.py` gave ranks
one and two equal weight. It now uses the standard discount. HR, Recall, and
Precision are unchanged; corrected standard NDCG values supersede earlier
standard-NDCG numbers in this log:

- LastFM UCPR: `0.03737679270`;
- LastFM PGPR: `0.03090466256`;
- LastFM CAFE: `0.03021389957`;
- LastFM PEARLM bestval10: `0.01595967406`;
- ML-1M UCPR: `0.08621536338`;
- ML-1M PGPR: `0.1018963310`;
- ML-1M CAFE: `0.1166553352`;
- ML-1M TPRec: `0.09421957761`;
- ML-1M KGGLM: `0.03364933434`.

The sweep validator now rejects non-finite Overall NDCG/HR/Recall/Precision
or explanation metrics at any alpha. Existing PGPR ML-1M results pass this
stronger gate; KGGLM's legacy exact-ten result is correctly rejected.

### 2026-06-23: KGGLM Formal ML-1M Completed

KGGLM ML-1M completed its two-stage formal pipeline at
2026-06-23 00:42:29 +08:

- generic KG paths: 9,057;
- generic pretraining: 3/3 epochs;
- recommendation finetuning: 2/2 epochs;
- best validation NDCG@10: `0.0068` at epoch 2;
- raw edge-validated native paths: 18,819;
- unseen paths: 18,761;
- requested/processed users: 6,040/6,040;
- users with recommendations: 5,395;
- explanations: 18,761;
- strict export validation: `PASS`;
- standard HR@10: `0.1688741722`;
- standard NDCG@10: `0.03364933434`;
- standard Precision@10: `0.01930463576`;
- standard Recall@10: `0.01050622572`;
- empty users: 645;
- mean native recommendations: `3.1061`;
- slot coverage: `31.0613%`.

The low coverage is a native model result and is not filled with non-path
items. Canonical-all-users xrecsys evaluation is active under the separate
result tag:

`kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users`

Its finite baseline is:

- NDCG: `0.03364933434`;
- HR: `0.1688741722`;
- Recall: `0.01050622572`;
- Precision: `0.01930463576`;
- LIR: `0.3161425276`;
- SEP: `0.4790553972`;
- ETD: `0.09503311258`.
