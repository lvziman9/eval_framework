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

### 2026-06-25: PEARLM ML-1M Completed and Queues Resumed

The 2026-06-25 server audit found no active canonical native-path experiment
processes. GPU 3 was free; GPUs 0--2 each had a small unrelated process. The
worktree was clean before new runs were started.

The first PEARLM ML-1M resume attempt used a plain background `nohup` command
and exited after printing the selected checkpoint without writing paths. A
32-user foreground diagnostic with the same checkpoint, GPU, and export
configuration passed:

- requested/processed users: 32/32;
- raw validated paths: 234;
- output:
  `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_ml1m_v1/diagnostic_pearlm_paths_32.pkl`.

This showed the exporter and checkpoint were valid. The failure mode was
therefore treated as background process detachment, not a PEARLM model or data
bug. Formal long-running commands are now hosted in `tmux` sessions instead of
plain `nohup`.

PEARLM ML-1M was resumed in:

```bash
tmux new-session -d -s pearl_ml1m_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  '/bin/bash scripts/hopwise/run_canonical_pearlm_pipeline.sh canonical_ml1m_v1 3 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/pearlm_ml1m_resume_20260625_2127.log 2>&1'
```

The pipeline skipped the completed training stage, exported native paths, ran
the adapter, strict export validation, standalone accuracy, and
canonical-all-users xrecsys protocol. It completed with `pipeline.complete`
present.

PEARLM ML-1M final evidence:

- train marker: `train.complete`;
- path marker: `paths.complete`;
- pipeline marker: `pipeline.complete`;
- requested/processed users: 6,040/6,040;
- raw edge-validated paths: 45,071;
- unseen paths: 44,986;
- users with recommendations: 5,833;
- selected explanations: 38,798;
- path shards: 189;
- strict export validation: `PASS`;
- xrecsys sweep validation: `PASS`;
- standard HR@10: `0.2147350993`;
- standard NDCG@10: `0.03530345750`;
- standard Precision@10: `0.02711920530`;
- standard Recall@10: `0.01103966777`;
- empty users: 207;
- mean native recommendations: `6.4235`;
- slot coverage: `64.2351%`.

TPRec LastFM was then resumed on GPU 3 in:

```bash
tmux new-session -d -s tprec_lastfm_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  '/bin/bash scripts/hopwise/run_canonical_tprec_pipeline.sh canonical_lastfm_v1 3 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/tprec_lastfm_resume_20260625_2128.log 2>&1'
```

The runner reused completed TransE, embedding export, preflight, temporal
pretraining, and policy stages. It also reused the 6,352 existing per-user
path shards and began generating new shards after that point. At the latest
documented snapshot, TPRec LastFM had reached 6,396/14,620 requested users and
7,387,871 raw paths. This is active/resumable and not yet a final result.

To avoid mixing legacy exact-ten and canonical-all-users recommendation
protocols in refreshed figures, a separate ML-1M canonical-all-users xrecsys
refresh queue was started for the four older completed models:

```bash
tmux new-session -d -s xrec_ml1m_canon_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  'LABELS=/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-06-20_native_path_expansion/ml1m_v1/labels; /bin/bash scripts/hopwise/run_canonical_xrecsys_protocol.sh ml1m 25-50-1-pgpr-canonical-ml1m "$LABELS" 25-50-1-pgpr-canonical-ml1m-canonical-all-users && /bin/bash scripts/hopwise/run_canonical_xrecsys_protocol.sh ml1m 25-50-1-ucpr-canonical-ml1m "$LABELS" 25-50-1-ucpr-canonical-ml1m-canonical-all-users && /bin/bash scripts/hopwise/run_canonical_xrecsys_protocol.sh ml1m cafe-canonical-ml1m "$LABELS" cafe-canonical-ml1m-canonical-all-users && /bin/bash scripts/hopwise/run_canonical_xrecsys_protocol.sh ml1m tprec-canonical-e50-25-50-1 "$LABELS" tprec-canonical-e50-25-50-1-canonical-all-users > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/ml1m_canonical_xrecsys_refresh_20260625.log 2>&1'
```

The first queue item, PGPR ML-1M canonical-all-users, had written its baseline
and LIR files by the latest snapshot. The queue remains active until PGPR,
UCPR, CAFE, and TPRec each have validated 21-point LIR/SEP/ETD sweeps under
their `*-canonical-all-users` result tags.

A follow-up GPU queue was also registered for KGGLM LastFM:

```bash
tmux new-session -d -s kgglm_lastfm_after_tprec_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  'while [ ! -f runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_lastfm_v1/paths.complete ]; do sleep 300; done; /bin/bash scripts/hopwise/run_canonical_kgglm_pipeline.sh canonical_lastfm_v1 3 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/kgglm_lastfm_after_tprec_20260625.log 2>&1'
```

This queue intentionally waits for TPRec LastFM path extraction to finish
before using GPU 3. KGGLM LastFM already has a completed pretraining marker, so
the follow-up runner should skip pretraining and continue from finetuning when
the wait condition is satisfied.

The server later showed GPUs 0--2 idle while TPRec used GPU 3, so the waiting
KGGLM queue was stopped to avoid a duplicate future launch and KGGLM LastFM was
started immediately on GPU 0:

```bash
tmux kill-session -t kgglm_lastfm_after_tprec_20260625

tmux new-session -d -s kgglm_lastfm_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  '/bin/bash scripts/hopwise/run_canonical_kgglm_pipeline.sh canonical_lastfm_v1 0 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/kgglm_lastfm_resume_20260625_2137.log 2>&1'
```

KGGLM LastFM reused the completed 3-epoch generic-path pretraining checkpoint,
then completed its 2-epoch recommendation-path finetuning:

- best validation checkpoint: epoch 2;
- validation NDCG@10: `0.0044`;
- validation Recall/Hit@10: `0.0084`;
- validation Precision@10: `0.0008`;
- validation Fidelity@10: `0.6376`;
- marker: `finetune.complete`.

The same session then completed native path extraction and the canonical
adapter/standard-accuracy gates:

- requested users: 14,620;
- processed users: 14,544;
- skipped cold-start users: 76;
- raw edge-validated paths: 191,294;
- unseen paths: 191,102;
- users with recommendations: 14,537;
- selected explanations: 128,496;
- path shards: 457;
- strict export validation: `PASS`;
- standard HR@10: `0.1258549932`;
- standard NDCG@10: `0.02131871191`;
- standard Precision@10: `0.01640902873`;
- standard Recall@10: `0.01419057838`;
- empty users: 83;
- slot coverage: `87.8906%`;
- marker: `paths.complete`.

Canonical-all-users xrecsys was active for KGGLM LastFM under
`kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users` at the latest
snapshot. The result is not yet complete until `canonical_protocol.complete`
and `xrecsys_sweeps_validation.json` are present.

The Amazon-book PEARLM compact checkpoint was also used to start the missing
100-user native-path export gate before any full 70k-user formal run:

```bash
tmux new-session -d -s pearlm_amazon_100_20260625 -c /usr1/home/s125mdg43_08/eval_framework \
  'ROOT=/usr1/home/s125mdg43_08/eval_framework; RUN_ROOT=$ROOT/runs/debug_compare/2026-06-20_native_path_expansion; PY=/usr1/home/s125mdg43_08/miniconda3/envs/hopwise/bin/python; EVAL_PY=/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python; OUT=$RUN_ROOT/hopwise_amazon_smoke/pearlm_100user_export; mkdir -p "$OUT/path_shards" "$OUT/export_checkpoints" "$RUN_ROOT/job_logs"; export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/usr1/home/s125mdg43_08/hopwise:$ROOT HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1; $PY scripts/hopwise/export_native_paths.py --model PEARLM --dataset canonical_amazon_book_kgat_v1 --data-root $RUN_ROOT/hopwise_data --checkpoint $RUN_ROOT/hopwise_amazon_smoke/pearlm_compact/checkpoints/huggingface-distilgpt2-PEARLM-Jun-23-2026_02-25-08.pth --checkpoint-dir "$OUT/export_checkpoints" --output "$OUT/pearlm_paths_100.pkl" --shard-dir "$OUT/path_shards" --gpu-id 1 --embedding-size 128 --num-heads 4 --num-layers 2 --paths-per-user 25 --num-beams 25 --batch-size 16 --max-users 100 && $EVAL_PY adapters/hopwise_adapter.py --raw-path "$OUT/pearlm_paths_100.pkl" --xrecsys-dir $ROOT/xrecsys --labels-dir $RUN_ROOT/amazon_book_kgat_v1/labels --topk 10 --agent-topk-tag pearlm-amazon-compact-e1-h128-l2-b25-100user --summary-json "$OUT/adapter.json" && $EVAL_PY scripts/validation/validate_xrecsys_export.py --paths-dir $ROOT/xrecsys/paths/amazon_book_kgat_v1/agent_topk=pearlm-amazon-compact-e1-h128-l2-b25-100user --labels-dir $RUN_ROOT/amazon_book_kgat_v1/labels --dataset amazon_book_kgat_v1 --topk 10 --summary-json "$OUT/export_validation.json" && $EVAL_PY scripts/validation/evaluate_uid_topk.py --uid-topk $ROOT/xrecsys/paths/amazon_book_kgat_v1/agent_topk=pearlm-amazon-compact-e1-h128-l2-b25-100user/uid_topk.csv --labels-dir $RUN_ROOT/amazon_book_kgat_v1/labels --topk 10 --allow-short --summary-json "$OUT/accuracy.json" && touch "$OUT/pearlm_amazon_100.complete"'
```

This Amazon-book smoke is intentionally scoped as a gate, not a final formal
baseline. Hopwise still performs full split-level KG path sampling before the
`--max-users` export limit is applied; at launch it was sampling 70,679 users
at roughly 14 users/second.

### 2026-06-26: Completion Audit, Figure Refresh, and Amazon Smoke Fix

The 2026-06-26 host audit found no active `tmux` experiment sessions and no
active experiment Python processes. `nvidia-smi` showed all four GPUs idle
with about 9 MiB used on each device. This means the previous queue has
finished or exited; the current state is a verification/documentation and next
Amazon-formal-run decision point, not an active-training point.

Current standard accuracy gates:

| Dataset | Model | Status | Users | HR@10 | NDCG@10 | Precision@10 | Recall@10 | Slot coverage | Empty users |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LastFM | PGPR | PASS | 14,620 | 0.186389 | 0.030905 | 0.025356 | 0.017731 | 0.994460 | 76 |
| LastFM | UCPR | PASS | 14,620 | 0.216416 | 0.037377 | 0.031129 | 0.023155 | 0.959767 | 118 |
| LastFM | CAFE | PASS | 14,620 | 0.180233 | 0.030214 | 0.025718 | 0.018639 | 0.994802 | 76 |
| LastFM | TPRec | PASS | 14,620 | 0.188919 | 0.038981 | 0.032736 | 0.022307 | 0.944371 | 189 |
| LastFM | KGGLM | PASS | 14,620 | 0.125855 | 0.021319 | 0.016409 | 0.014191 | 0.878906 | 83 |
| LastFM | PEARLM | PASS | 14,620 | 0.099590 | 0.015960 | 0.012736 | 0.009047 | 0.862825 | 280 |
| ML-1M | PGPR | PASS | 6,040 | 0.511258 | 0.101896 | 0.092914 | 0.042342 | 1.000000 | 0 |
| ML-1M | UCPR | PASS | 6,040 | 0.441887 | 0.086215 | 0.066391 | 0.037913 | 0.828179 | 52 |
| ML-1M | CAFE | PASS | 6,040 | 0.554305 | 0.116655 | 0.107119 | 0.052024 | 1.000000 | 0 |
| ML-1M | TPRec | PASS | 6,040 | 0.474503 | 0.094220 | 0.089702 | 0.043772 | 0.999983 | 0 |
| ML-1M | KGGLM | PASS | 6,040 | 0.168874 | 0.033649 | 0.019305 | 0.010506 | 0.310613 | 645 |
| ML-1M | PEARLM | PASS | 6,040 | 0.214735 | 0.035303 | 0.027119 | 0.011040 | 0.642351 | 207 |

Current xrecsys sweep evidence:

| Dataset | Model | Result tag | Sweep validation | Canonical protocol marker | Notes |
|---|---|---|---|---|---|
| ML-1M | PGPR | `25-50-1-pgpr-canonical-ml1m-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| ML-1M | UCPR | `25-50-1-ucpr-canonical-ml1m-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| ML-1M | CAFE | `cafe-canonical-ml1m-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| ML-1M | TPRec | `tprec-canonical-e50-25-50-1-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| ML-1M | KGGLM | `kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| ML-1M | PEARLM | `pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 4,557 avg rows per objective |
| LastFM | PGPR | `10-12-1-pgpr-canonical` | PASS | no | Existing canonical export sweep validated after the audit; no canonical-all-users marker |
| LastFM | UCPR | `10-12-1-ucpr-canonical` | PASS | no | Existing canonical export sweep validated after the audit; no canonical-all-users marker |
| LastFM | CAFE | `cafe-canonical-lastfm` | PASS | no | Existing canonical export sweep validated after the audit; no canonical-all-users marker |
| LastFM | TPRec | `tprec-canonical-e50-25-50-1` | PASS | no | TPRec pipeline used `--include-all-test-users`/`--require-all-test-users`, but wrote validation into the model root rather than a result-dir marker |
| LastFM | KGGLM | `kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 1,470 avg rows per objective |
| LastFM | PEARLM | `pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users` | PASS | yes | 21 alphas for LIR/SEP/ETD, 1,470 avg rows per objective |

The following light validation commands were used to make the LastFM result
directories self-verifying without rerunning the expensive sweeps:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/validate_xrecsys_sweeps.py \
  --results-dir xrecsys/results/lastfm/agent_topk=<tag> \
  --summary-json xrecsys/results/lastfm/agent_topk=<tag>/sweeps_validation.json
```

This was run for:

- `10-12-1-pgpr-canonical`;
- `10-12-1-ucpr-canonical`;
- `cafe-canonical-lastfm`;
- `tprec-canonical-e50-25-50-1`.

Figure refresh:

- generated `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`;
- generated `reports/figures/tradeoff/canonical_lastfm_native_paths_v3/`;
- each directory now contains 12 PNGs and 12 CSVs;
- ML-1M v2 includes six models under the same canonical-all-users protocol:
  PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM;
- LastFM v3 intentionally includes only the three completed native-path models
  with current comparable path-native evidence: TPRec, KGGLM, PEARLM. The
  legacy LastFM PGPR/UCPR/CAFE sweeps are validated, but their result dirs do
  not carry the canonical protocol marker, so they should be plotted separately
  unless rerun under the same tagged protocol.

The plotting commands used `scripts/analysis/tradeoff_analyzer.py` with the
`eval_frame` Python environment and `--exp-metric` set separately to `LIR`,
`SEP`, and `ETD`.

Amazon-book PEARLM 100-user smoke:

- adapter: `PASS`;
- strict export validation: `PASS`;
- processed/output users: 112;
- canonical test users: 70,591;
- path shards: 7;
- explanations: 729;
- accuracy gate after smoke-subset fix: `PASS`;
- subset HR/NDCG/Precision/Recall: all `0.0`;
- evaluated-user slot coverage: `0.650893`;
- marker: `pearlm_amazon_100.complete`.

The Amazon smoke failure was caused by an evaluator interface mismatch, not by
the adapter/export itself. `scripts/validation/evaluate_uid_topk.py` previously
allowed short top-k rows but always required prediction users to exactly match
the full test split. That is correct for formal runs but blocks partial smoke
gates. A new explicit `--allow-user-subset` flag was added. Default behavior is
unchanged: formal evaluations still require all test users unless this flag is
provided.

The fixed smoke command was:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/evaluate_uid_topk.py \
  --uid-topk xrecsys/paths/amazon_book_kgat_v1/agent_topk=pearlm-amazon-compact-e1-h128-l2-b25-100user/uid_topk.csv \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --topk 10 \
  --allow-short \
  --allow-user-subset \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/hopwise_amazon_smoke/pearlm_100user_export/accuracy.json
```

Next decisions:

1. Treat ML-1M as the current complete same-protocol six-model showcase.
2. Treat LastFM as complete for native-path TPRec/KGGLM/PEARLM, with legacy
   PGPR/UCPR/CAFE available as validated but not same-marker sweeps.
3. Do not report Amazon-book PEARLM 100-user smoke as a formal baseline; use it
   only as proof that the larger native-KG Amazon view can be exported and
   evaluated end-to-end on a small gate.
4. Before launching a full Amazon-book run, decide whether to start with KGGLM,
   PEARLM, or TPRec, because PEARLM currently performs full KG path sampling
   before applying `--max-users`, which makes even small gates expensive.

KGGLM was selected as the first larger Amazon-book formal run because the
pipeline explicitly supports `canonical_amazon_book_kgat_v1` and disables
xrecsys explanation sweeps for Amazon until a canonical SEP/ETD denominator is
approved.

Launched:

```bash
tmux new-session -d -s kgglm_amazon_formal_20260626 -c /usr1/home/s125mdg43_08/eval_framework \
  '/bin/bash scripts/hopwise/run_canonical_kgglm_pipeline.sh canonical_amazon_book_kgat_v1 0 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/kgglm_amazon_formal_20260626.log 2>&1'
```

Startup evidence after launch:

- tmux session: `kgglm_amazon_formal_20260626`;
- active process: `scripts/hopwise/run_canonical_native_path.py --model KGGLM --train-stage pretrain --dataset canonical_amazon_book_kgat_v1`;
- process PID at audit: `3030516`;
- CPU use at audit: about `94%`;
- GPU status at audit: GPU 0 was still near idle, consistent with CPU-side
  graph/path preparation before training;
- log: `runs/debug_compare/2026-06-20_native_path_expansion/job_logs/kgglm_amazon_formal_20260626.log`;
- log reached Amazon data/KG loading and collaborative KG construction:
  70,680 users, 24,916 items, 846,434 interactions, 113,488 entities,
  41 relations, 2,557,746 triples, collaborative KG vertices 184,168 and
  edges 3,139,581.

Current status: running; no `pretrain.complete` marker yet.

Follow-up monitor:

- tmux session was still present: `kgglm_amazon_formal_20260626`;
- active pretrain process was still running as PID `3030516`;
- CPU use was about `96%`, which indicates the process had not silently died;
- GPU memory/use remained near idle, consistent with the current CPU-heavy
  KG/path sampling or data preparation stage before model training;
- the latest log line was still collaborative KG ready, with no Python
  traceback and no failure marker;
- no `pretrain.complete` marker or checkpoint artifact had been written yet.

Next monitor should check whether the job has advanced past pretraining data
preparation into checkpoint writing. If the log and output directory remain
unchanged for a long period while CPU drops to idle, inspect the tmux pane
before taking any recovery action.

Second follow-up monitor:

- tmux session remained active;
- PID `3030516` was still running with about `99%` CPU;
- GPU memory was about 328 MiB on GPUs 0--2 and 12 MiB on GPU 3, with low
  utilization, which is still consistent with CPU-bound path sampling;
- the log advanced from KG construction into KGGLM pretrain path sampling;
- latest visible progress: `50,000/113,486` sampled nodes and `50,000` unique
  paths after `2,832.0s`;
- approximate sampling rate from the log: about `17.7` nodes/second;
- rough remaining sampling time from 50k nodes: about one hour, before the
  actual GPU training/checkpoint stage begins.

This confirms the Amazon KGGLM formal job is progressing rather than stalled.

Third follow-up monitor:

- after another wait window, the same tmux session and PID were still active;
- PID `3030516` was using about `99.5%` CPU;
- latest visible progress advanced to `60,000/113,486` sampled nodes and
  `60,000` unique paths after `3,402.2s`;
- the sampling rate remained stable at roughly `17.6` nodes/second;
- no checkpoint or `pretrain.complete` marker had been written yet, which is
  still expected because the job is still in the pretraining path sampling
  phase.

Fourth follow-up monitor:

- after a longer wait window, the tmux session was still active;
- PID `3030516` remained the active pretrain process, using about `99.6%` CPU;
- latest visible progress advanced to `70,000/113,486` sampled nodes and
  `70,000` unique paths after `3,972.1s`;
- GPU utilization remained low and no checkpoint/marker had been written yet;
- based on the same roughly `17.6` nodes/second sampling rate, the remaining
  pretraining sampling time was roughly forty minutes before the job can enter
  model training/checkpoint writing.

Fifth follow-up monitor:

- the job remained active under the same tmux session and PID;
- latest visible progress advanced to `80,000/113,486` sampled nodes and
  `80,000` unique paths after `4,542.4s`;
- GPU 0 showed only modest utilization, while CPU stayed near fully occupied;
- no checkpoint/marker was present yet, so the run is still in sampling rather
  than training/checkpoint writing.

Sixth follow-up monitor:

- the job advanced to `90,000/113,486` sampled nodes and `90,000` unique paths
  after `5,112.7s`;
- PID `3030516` was still the active process at roughly `99.6%` CPU;
- no checkpoint or `pretrain.complete` marker was present yet;
- at the observed rate, remaining sampling time was roughly twenty to
  twenty-five minutes.

Seventh follow-up monitor:

- the job advanced to `100,000/113,486` sampled nodes and `100,000` unique
  paths after `5,683.1s`;
- the same PID remained active at roughly `99.6%` CPU;
- GPU utilization remained low, so the job still had not entered the main
  training/checkpoint writing stage;
- no checkpoint or `pretrain.complete` marker was present yet.

Eighth follow-up monitor:

- pretrain sampling completed: `113,486/113,486` sampled nodes and `113,486`
  unique paths after `6,452.3s`;
- sparse relation annotation completed and the pretrain path dataset was ready
  after `6,458.3s`;
- the training stage started at `2026-06-26 14:46`;
- epoch 1 completed in `186.30s` with train loss `4.1574`;
- checkpoint artifacts were written under
  `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1/pretrain_checkpoints/huggingface-distilgpt2-KGGLM-canonical_amazon_book_kgat_v1-pretrained-1.pth/checkpoint-444/`;
- observed checkpoint files included `model.safetensors`, `config.json`,
  `tokenizer.json`, `trainer_state.json`, `optimizer.pt`, `scheduler.pt`, and
  `rng_state.pth`;
- at this monitor point the tmux session and Python process were still active,
  so the pipeline had not yet written `pretrain.complete` or advanced to the
  finetune command.

Ninth follow-up monitor:

- `pretrain.complete` was present;
- `pretrain.json` status was `PASS`;
- the wrapper JSON reports `epochs=1`, while the formal KGGLM pretraining
  configuration is recorded as `pretrain_epochs=3`; the log confirms three
  pretraining epochs were run;
- epoch losses were: epoch 1 `4.1574`, epoch 2 `4.1275`, epoch 3 `3.9647`;
- latest pretrain checkpoint selected by the pipeline:
  `pretrain_checkpoints/huggingface-distilgpt2-KGGLM-canonical_amazon_book_kgat_v1-pretrained-3.pth/checkpoint-1332`;
- the pipeline then advanced automatically into recommendation-path
  finetuning;
- active finetune process at the monitor point: PID `3114882`;
- finetune command uses `--train-stage finetune`, `--epochs 2`,
  `--validation-paths-per-user 10`, `--validation-num-beams 10`, and
  `--select-best-validation`;
- no finetune checkpoint had been written yet at this monitor point.

Tenth follow-up monitor:

- `finetune.complete` was present;
- `finetune.json` status was `PASS`;
- epoch 1 finetune training completed in `101.11s` with train loss `5.0337`;
- epoch 1 validation completed in `1630.74s` with valid-score/NDCG@10
  `0.002300`, recall@10 `0.0038`, hit@10 `0.0038`, precision@10 `0.0004`,
  and Fidelity@10 `0.5553`;
- epoch 2 finetune training completed in `108.13s` with train loss `4.8722`;
- epoch 2 validation completed in `1633.91s` with valid-score/NDCG@10
  `0.001600`, recall@10 `0.0025`, hit@10 `0.0025`, precision@10 `0.0002`,
  and Fidelity@10 `0.4214`;
- because epoch 1 had the better validation score, the selected finetune
  checkpoint remained
  `finetune_checkpoints/huggingface-distilgpt2-KGGLM-Jun-26-2026_16-07-27.pth`;
- the log emitted `There were missing keys in the checkpoint model loaded:
  ['lm_head.weight']` at checkpoint reload time; this was non-fatal because the
  pipeline advanced into path export, but it should remain on the risk list
  until adapter/export validation and accuracy evaluation pass.

Eleventh follow-up monitor:

- tmux session `kgglm_amazon_formal_20260626` was still active;
- active process was PID `3178065`, running
  `scripts/hopwise/export_native_paths.py --model KGGLM --dataset
  canonical_amazon_book_kgat_v1`;
- process runtime at audit was about `1:34:02`, CPU about `103%`, memory about
  `1.8%`;
- GPU 0 showed about `4739` MiB memory use and `34%` utilization, confirming
  the export process was active rather than idle;
- `path_shards/` contained `1013` shard files, latest observed shard
  `batch_001012.pkl`;
- latest export progress line:
  `requested_users=16208 processed_users=16208 skipped_cold_start_users=0 raw_paths=287964`;
- no final `kgglm_paths.pkl`, `path_export.json`, `adapter.json`,
  `export_validation.json`, `accuracy.json`, `paths.complete`, or
  `pipeline.complete` artifact existed yet.

Current interpretation: Amazon-book KGGLM formal is past pretrain and finetune
and is actively exporting native paths. It is not yet a reportable formal
Amazon result because final path merge, adapter conversion, export validation,
and accuracy evaluation have not completed.

Twelfth follow-up monitor and next Amazon launch:

- after a further wait, KGGLM export continued to advance; latest observed
  progress was
  `requested_users=27456 processed_users=27456 skipped_cold_start_users=0 raw_paths=499554`;
- `path_shards/` for KGGLM contained `1716` shard files at this audit point;
- because the machine has `48` CPU cores, load average was about `6.6`, and
  GPU 3 was idle, a second formal native-path Amazon job was launched without
  sharing KGGLM's GPU 0;
- launched PEARLM Amazon-book formal:

```bash
tmux new-session -d -s pearlm_amazon_formal_20260626 -c /usr1/home/s125mdg43_08/eval_framework \
  '/bin/bash scripts/hopwise/run_canonical_pearlm_pipeline.sh canonical_amazon_book_kgat_v1 3 > runs/debug_compare/2026-06-20_native_path_expansion/job_logs/pearlm_amazon_formal_20260626.log 2>&1'
```

- tmux sessions after launch:
  `kgglm_amazon_formal_20260626` and `pearlm_amazon_formal_20260626`;
- PEARLM launch log:
  `runs/debug_compare/2026-06-20_native_path_expansion/job_logs/pearlm_amazon_formal_20260626.log`;
- PEARLM formal output root:
  `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1`;
- active PEARLM train process at audit: PID `3254163`, running
  `scripts/hopwise/run_canonical_native_path.py --model PEARLM --dataset
  canonical_amazon_book_kgat_v1 --gpu-id 3 --epochs 50 ...`;
- PEARLM successfully reached Amazon data/KG loading:
  70,680 users, 24,916 items, 846,434 interactions, 113,488 entities,
  41 relations, 2,557,746 triples, and 24,915 linked items;
- no PEARLM `train.complete` marker or JSON result existed yet, which is
  expected at launch time.

Current Amazon queue:

1. KGGLM formal: actively exporting paths on GPU 0; not yet final.
2. PEARLM formal: newly running on GPU 3; not yet trained.

TPRec is not launched for Amazon in this pass because
`scripts/hopwise/run_canonical_tprec_pipeline.sh` currently only supports
`canonical_ml1m_v1` and `canonical_lastfm_v1`; Amazon TPRec requires a
separate canonical runtime/config extension before it is an honest compatible
baseline.

Thirteenth follow-up monitor:

- KGGLM export continued to progress after PEARLM launch, reaching
  `requested_users=30352 processed_users=30352 skipped_cold_start_users=0 raw_paths=554365`;
- KGGLM `path_shards/` contained `1897` shard files at this audit point;
- PEARLM log had not advanced beyond initial Amazon data/KG loading, but the
  PEARLM Python process remained active rather than failed;
- active PEARLM process at audit: PID `3254163`, runtime about `04:53`, CPU
  about `95.9%`, memory about `0.6%`;
- GPU 3 still showed only idle memory, so PEARLM was still in a CPU-bound
  preparation/sampling phase before GPU training/checkpointing;
- no PEARLM `train.complete` marker, JSON result, checkpoint, or path shard had
  been created yet.

Next monitor should watch for either PEARLM training/checkpoint log lines or a
stalled CPU drop with no log/checkpoint change. No recovery action is needed
while PID `3254163` remains CPU-active.

LastFM six-model figure bundle update:

The earlier `canonical_lastfm_native_paths_v3` figure bundle intentionally used
only TPRec/KGGLM/PEARLM because those result directories had the newer
canonical-all-users marker convention. A follow-up audit confirmed that the
classic LastFM baselines also have complete and validated xrecsys alpha sweeps:

- PGPR latest large-candidate result:
  `xrecsys/results/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score`;
- UCPR latest matched large-candidate result:
  `xrecsys/results/lastfm/agent_topk=25-50-1-ucpr-canonical-matched`;
- CAFE result:
  `xrecsys/results/lastfm/agent_topk=cafe-canonical-lastfm`;
- TPRec result:
  `xrecsys/results/lastfm/agent_topk=tprec-canonical-e50-25-50-1`;
- KGGLM result:
  `xrecsys/results/lastfm/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users`;
- PEARLM result:
  `xrecsys/results/lastfm/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users`.

Important correction: an initial v4 generation attempt used the older
`10-12-1` PGPR/UCPR tags. It was immediately overwritten after checking the
formal accuracy and sweep-validation summaries, which point to the `25-50-1`
large-candidate tags above.

The corrected six-model figure command was:

```bash
mkdir -p .cache/matplotlib
export MPLCONFIGDIR=/usr1/home/s125mdg43_08/eval_framework/.cache/matplotlib
for METRIC in LIR SEP ETD; do
  /usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python scripts/analysis/tradeoff_analyzer.py \
    --dataset lastfm \
    --models \
      PGPR=xrecsys/results/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score \
      UCPR=xrecsys/results/lastfm/agent_topk=25-50-1-ucpr-canonical-matched \
      CAFE=xrecsys/results/lastfm/agent_topk=cafe-canonical-lastfm \
      TPRec=xrecsys/results/lastfm/agent_topk=tprec-canonical-e50-25-50-1 \
      KGGLM=xrecsys/results/lastfm/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users \
      PEARLM=xrecsys/results/lastfm/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users \
    --exp-metric "$METRIC" \
    --out reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model
done
```

Generated and validated:

- output directory:
  `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model`;
- 24 files total: 12 PNGs and 12 CSVs;
- each CSV has 126 rows: 6 models times 21 alpha values;
- all CSVs contain exactly these models:
  `CAFE`, `KGGLM`, `PEARLM`, `PGPR`, `TPRec`, `UCPR`;
- all CSVs cover alpha `0.0` through `1.0` in the expected 21-point grid;
- visual smoke check passed on
  `tradeoff_lastfm_SEP_ndcg_models.png`.

This v4 bundle is now the presentation-ready LastFM six-model tradeoff bundle.
The v3 bundle remains useful only as the stricter marker-convention subset for
TPRec/KGGLM/PEARLM.

Reproducibility fix:

- added the tracked helper
  `scripts/analysis/generate_native_path_figures.sh` as the canonical
  figure-regeneration entrypoint for current six-model LastFM and ML-1M
  bundles;
- also updated the ignored run-local helper
  `runs/debug_compare/2026-06-20_native_path_expansion/generate_native_path_figures.sh`
  for convenience in this experiment sandbox;
- `lastfm` now regenerates the v4 six-model bundle with the latest PGPR and
  UCPR `25-50-1` large-candidate result tags;
- `ml1m` now regenerates
  `reports/figures/tradeoff/canonical_ml1m_native_paths_v2` with all six
  canonical-all-users result tags;
- reran `bash scripts/analysis/generate_native_path_figures.sh lastfm` and
  `bash scripts/analysis/generate_native_path_figures.sh ml1m`; both completed
  successfully and wrote the expected figure/table bundles.

Fourteenth Amazon monitor:

- KGGLM export was still active under PID `3178065`;
- KGGLM progress reached
  `requested_users=38432 processed_users=38432 skipped_cold_start_users=0 raw_paths=707084`;
- KGGLM `path_shards/` contained `2402` shard files;
- no KGGLM final `kgglm_paths.pkl`, adapter summary, export-validation
  summary, accuracy summary, or pipeline marker existed yet;
- PEARLM remained active under PID `3254163`, runtime about `13:15`, CPU about
  `98.5%`, memory about `0.6%`;
- PEARLM still had no new log lines after initial Amazon KG loading, no
  checkpoint, no JSON, and no marker; this remains consistent with CPU-bound
  path/data preparation as long as CPU stays active.

Amazon classic-model compatibility audit:

While KGGLM/PEARLM formal jobs were running, the classic native-path adapters
were checked for Amazon-book compatibility.

Findings:

- `scripts/data/canonical/build_pgpr_view.py` only exposes
  `--model-dataset {lastfm,ml1m}` and hard-codes LastFM/ML-1M relation files
  plus product entity names (`song`/`movie`);
- `scripts/data/canonical/build_ucpr_view.py` only defines `DATASET_CONFIG`
  entries for `lastfm` and `ml1m`;
- `scripts/data/canonical/build_cafe_view.py` likewise only defines CAFE
  schema configs for `lastfm` and `ml1m`, and CAFE depends on a compatible
  UCPR view plus UCPR TransE checkpoint;
- the UCPR runtime contains historical Amazon constants such as
  `AZ_BOOK_CORE = 'book'` and shell scripts mentioning `amazon-book_20core`,
  but the active canonical runtime utilities still define `DATASET_DIR`,
  `TMP_DIR`, `KG_RELATION`, `MAIN_PRODUCT_INTERACTION`, metric paths, and
  path-pattern tables only for the integrated ML-1M/LastFM schemas in the
  canonical queue;
- UCPR training also has an explicit branch where `AZ_BOOK_CORE` is commented
  out of the ML-1M/LastFM parameter-freezing path:
  `elif args.dataset in [LFM1M,ML1M]:#MOVIE_CORE, AZ_BOOK_CORE]`.

Decision:

- Do not launch PGPR/UCPR/CAFE on `canonical_amazon_book_kgat_v1` yet. They
  are not currently honest drop-in compatible with the native KGAT Amazon-book
  view.
- Treat KGGLM and PEARLM as the current formal Amazon native-path baselines
  because their Hopwise pipeline explicitly supports
  `canonical_amazon_book_kgat_v1` and keeps the native KG path semantics.
- Treat TPRec as not launched for Amazon until its canonical path constraints
  and runtime support are extended beyond ML-1M/LastFM.

If Amazon classic baselines are required later, the correct next task is a
separate schema-porting task: define an Amazon product/entity/relation
projection, build and validate PGPR/UCPR/CAFE model views, add runtime
constants/path patterns, run smoke gates, then run formal jobs. Starting them
now would mix unapproved schema assumptions into the comparison.

Fifteenth Amazon monitor:

- KGGLM export remained active as PID `3178065`, runtime about `1:56:47`, CPU
  about `105%`;
- KGGLM progress reached
  `requested_users=42064 processed_users=42064 skipped_cold_start_users=0 raw_paths=774842`;
- KGGLM `path_shards/` contained `2629` shard files;
- GPU 0 showed about `4735` MiB memory and `25%` utilization;
- PEARLM remained active as PID `3254163`, runtime about `19:57`, CPU about
  `99%`;
- PEARLM still had no checkpoint, JSON, marker, or post-KG-loading log update,
  so it remains in the CPU-bound preparation/sampling watch state.

Sixteenth Amazon monitor: KGGLM formal completed

KGGLM Amazon-book formal pipeline completed at `2026-06-26 19:27:07`.

Final KGGLM artifacts:

- run root:
  `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1`;
- markers present: `pretrain.complete`, `finetune.complete`,
  `paths.complete`, `pipeline.complete`;
- summary JSONs present: `pretrain.json`, `finetune.json`, `adapter.json`,
  `export_validation.json`, `accuracy.json`;
- raw manifest: `kgglm_paths.pkl`;
- path shards: `4412`;
- raw manifest metadata:
  `requested_users=70591`, `processed_users=70591`,
  `raw_paths=1327552`, `row_shards=4412`, `paths_per_user=25`,
  `num_beams=25`;
- xrecsys sweeps were intentionally not run for Amazon; marker note present in
  `xrecsys_not_applicable.txt`.

Independent re-validation was run after pipeline completion without overwriting
the formal summaries:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/validate_xrecsys_export.py \
  --paths-dir xrecsys/paths/amazon_book_kgat_v1/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25 \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --require-all-test-users \
  --summary-json /tmp/kgglm_amazon_export_validation_recheck.json
```

Recheck result: `PASS`.

- canonical test users: `70591`;
- top-k users: `70591`;
- candidate users: `70586`;
- pred-path rows: `1326486`;
- explanation rows: `655285`;
- score range: `[0.0, 1.0]`.

Accuracy was independently rechecked with strict full-user coverage and only
`--allow-short` for short recommendation lists:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/evaluate_uid_topk.py \
  --uid-topk xrecsys/paths/amazon_book_kgat_v1/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25/uid_topk.csv \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --topk 10 \
  --allow-short \
  --summary-json /tmp/kgglm_amazon_accuracy_recheck.json
```

Recheck result: `PASS`.

Amazon-book KGGLM formal accuracy:

- users: `70591`;
- user coverage: `1.0`;
- missing test users: `0`;
- extra prediction users: `0`;
- HR@10: `0.01266450397`;
- NDCG@10: `0.00302209521`;
- Precision@10: `0.00138261251`;
- Recall@10: `0.00474723572`;
- slot coverage: `0.92828405887`;
- empty users: `5`;
- exact-k users: `55267`;
- short users: `15324`.

Interpretation: KGGLM is now the first completed formal native-path baseline
on the larger native-KG Amazon-book dataset. It is reportable for
recommendation accuracy and native path export quality. It is not reportable
for SEP/ETD/LIR alpha-sweep explanation tradeoffs because Amazon has no
approved canonical timestamp/SEP/ETD denominator yet, so xrecsys sweeps are
intentionally disabled.

PEARLM Amazon status at the same audit:

- PEARLM completed KG path sampling for `70679/70679` users after about
  `1:10:01`;
- PEARLM entered GPU training on physical GPU 3;
- epoch 1 train loss: `5.1043`;
- epoch 2 train loss: `4.9762`;
- epoch 3 train loss: `4.7239`;
- epoch 4 train loss: `4.6830`;
- active PID remained `3254163`, GPU 3 memory about `5606` MiB and utilization
  about `73%`;
- no PEARLM checkpoint/`train.complete` marker existed yet, because the formal
  50-epoch run is still training.

Seventeenth Amazon monitor:

- `tmux list-sessions` showed only `pearlm_amazon_formal_20260626`; the KGGLM
  tmux session had naturally exited after writing `pipeline.complete`;
- KGGLM formal artifacts remained complete and unchanged:
  `pipeline.complete`, `paths.complete`, `adapter.json`, `export_validation.json`,
  and `accuracy.json` were present and `PASS`;
- PEARLM remained the only active Amazon formal job;
- active PEARLM process: PID `3254163`, runtime about `1:24:52`, CPU about
  `99.8%`, memory about `1.0%`;
- GPU 3 showed about `5606` MiB memory and `69%` utilization;
- PEARLM log had reached epoch 4:
  - epoch 1 train loss `5.1043`;
  - epoch 2 train loss `4.9762`;
  - epoch 3 train loss `4.7239`;
  - epoch 4 train loss `4.6830`;
- no PEARLM `train.complete`, `pearlm_paths.pkl`, adapter, export-validation,
  accuracy, or pipeline marker existed yet.

Next monitor should wait for PEARLM validation/checkpoint events around the
configured `eval_step=5`, then continue through export, adapter validation, and
strict full-user accuracy validation.

Eighteenth Amazon monitor:

Checked again at `2026-06-26 20:12:02 +08`.

KGGLM Amazon-book formal remains complete:

- run root:
  `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1`;
- markers present: `pretrain.complete`, `finetune.complete`,
  `paths.complete`, `pipeline.complete`;
- summaries present: `pretrain.json`, `finetune.json`, `adapter.json`,
  `export_validation.json`, `accuracy.json`;
- final validation state remains `PASS` for export and `PASS` for strict
  full-user accuracy.

PEARLM Amazon-book formal remains active, not complete:

- tmux session: `pearlm_amazon_formal_20260626`;
- active process: PID `3254163`;
- runtime: about `1:29:40`;
- process state: `Rl+`, CPU about `102%`, memory about `1.4%`;
- physical GPU 3 active with about `6284` MiB memory and about `24%`
  utilization;
- log reached epoch 5 training:
  - epoch 1 train loss `5.1043`;
  - epoch 2 train loss `4.9762`;
  - epoch 3 train loss `4.7239`;
  - epoch 4 train loss `4.6830`;
  - epoch 5 train loss `4.1698`;
- latest log modification time: `2026-06-26 20:07:29`;
- current checkpoint directory contains one initial HuggingFace checkpoint
  directory, `huggingface-distilgpt2-PEARLM-Jun-26-2026_19-53-31.pth`;
- no `train.complete`, `train.json`, `paths.complete`, `pearlm_paths.pkl`,
  `adapter.json`, `export_validation.json`, `accuracy.json`, or
  `pipeline.complete` exists yet.

Interpretation: PEARLM is still inside the train/validation phase after the
first configured validation boundary (`eval_step=5`). It has not failed, but
there is still no reportable Amazon PEARLM result. Next monitor should look for
either a best-checkpoint/epoch-6 log update or a `train.complete` marker. If the
training step completes, immediately continue with path export, adapter
validation, export validation, and strict full-user accuracy recheck.

Short follow-up poll:

- checked workspace artifacts again at `2026-06-26 20:16:09 +08`;
- PEARLM log still had `188` lines and latest modification time
  `2026-06-26 20:07:29`;
- the last logged training event was still epoch 5 with train loss `4.1698`;
- no PEARLM completion markers or summary JSONs had appeared yet.

Interpretation: this remains a waiting state inside the PEARLM train/validation
stage. Because the formal run is still the only route to a reportable Amazon
PEARLM baseline, no restart or parameter change was made.

Nineteenth Amazon monitor and checkpoint-discovery fix:

Checked Amazon PEARLM artifacts again at `2026-06-26 23:36:37 +08`.

PEARLM had progressed substantially:

- still no `train.complete`, `train.json`, `paths.complete`,
  `pearlm_paths.pkl`, `adapter.json`, `export_validation.json`,
  `accuracy.json`, or `pipeline.complete`;
- checkpoint root now contained both the Hopwise checkpoint file and a
  HuggingFace checkpoint directory;
- the best HuggingFace checkpoint was written under the nested path
  `checkpoints/huggingface-distilgpt2-PEARLM-Jun-26-2026_19-53-31.pth/checkpoint-5525`;
- this nested checkpoint contains `model.safetensors` and `config.json`;
- epoch 5 validation completed after `1512.96s` with
  `valid_score=0.012000`;
- epoch 5 validation metrics:
  `recall@10=0.017`, `ndcg@10=0.012`, `hit@10=0.017`,
  `precision@10=0.0017`, `Fidelity@10=0.5333`;
- PEARLM saved the epoch 5 checkpoint as the current best;
- later validation did not improve the best score:
  - epoch 10: `valid_score=0.008900`;
  - epoch 15: `valid_score=0.008100`;
  - epoch 20: `valid_score=0.008600`;
  - epoch 25: `valid_score=0.008500`;
- training had reached epoch 30 with train loss `1.4015`; epoch-30 validation
  was expected next.

Bug found before export:

- `scripts/hopwise/run_canonical_pearlm_pipeline.sh` looked only one directory
  deep for a directory containing `model.safetensors`;
- PEARLM's saved HuggingFace checkpoint is nested one level deeper under
  `checkpoint-5525`;
- if left unchanged, the shell pipeline could finish training and then fail at
  checkpoint discovery before path export.

Fix applied:

- changed PEARLM checkpoint discovery to search up to four levels for
  `model.safetensors`, then pass the containing directory to
  `export_native_paths.py`;
- applied the same more robust lookup to KGGLM finetune checkpoint discovery
  for future reruns.

Validation after the fix:

```bash
bash -n scripts/hopwise/run_canonical_pearlm_pipeline.sh
bash -n scripts/hopwise/run_canonical_kgglm_pipeline.sh
git diff --check
```

All checks passed. A direct filesystem check found exactly one current PEARLM
`model.safetensors`, under the nested `checkpoint-5525` directory, and confirmed
the sibling `config.json` exists.

Twentieth Amazon monitor:

Checked PEARLM again at `2026-06-26 23:46:06 +08`.

- still no PEARLM `train.complete`, `train.json`, `paths.complete`,
  `adapter.json`, `export_validation.json`, `accuracy.json`, or
  `pipeline.complete`;
- epoch 30 validation completed after `1445.87s`;
- epoch 30 validation score was `0.007600`, so it did not improve over the
  epoch 5 best checkpoint;
- epoch 30 validation metrics:
  `recall@10=0.0122`, `ndcg@10=0.0076`, `hit@10=0.0122`,
  `precision@10=0.0012`, `Fidelity@10=0.7012`;
- training continued through epoch 31 with train loss `1.4153`;
- training continued through epoch 32 with train loss `1.4042`;
- latest log modification time was `2026-06-26 23:44:46`.

Interpretation: PEARLM remains healthy but not complete. Since the best
validation score is still from epoch 5 and there have now been five later
non-improving validation checkpoints, the next expected decision point is
around the epoch 35 validation/early-stop boundary.

Twenty-first Amazon monitor: PEARLM training completed

PEARLM training completed at local log time `2026-06-27 00:17`.

Training artifacts:

- marker present: `train.complete`;
- summary present:
  `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1/train.json`;
- `train.json` status: `PASS`;
- requested max epochs: `50`;
- selected best validation checkpoint: epoch 5;
- best validation score: `0.012`;
- best validation metrics:
  `recall@10=0.017`, `ndcg@10=0.012`, `hit@10=0.017`,
  `precision@10=0.0017`, `Fidelity@10=0.5333`;
- final observed validation before early stop:
  epoch 35, `valid_score=0.007800`;
- epoch 35 validation metrics:
  `recall@10=0.0125`, `ndcg@10=0.0078`, `hit@10=0.0125`,
  `precision@10=0.0013`, `Fidelity@10=0.7028`;
- Hopwise built-in test evaluation was intentionally skipped:
  `SKIPPED_FOR_CANONICAL_COLD_START_USERS`;
- formal canonical accuracy will be computed from the exported `uid_topk.csv`
  after the adapter includes all canonical test users.

Checkpoint/export transition:

- after training, the best HuggingFace checkpoint was also materialized at
  `checkpoints/huggingface-distilgpt2-PEARLM-Jun-26-2026_19-53-31.pth/model.safetensors`;
- the running pipeline selected
  `checkpoints/huggingface-distilgpt2-PEARLM-Jun-26-2026_19-53-31.pth`
  as the export checkpoint;
- `export_native_paths.py` started after checkpoint selection;
- at `2026-06-27 00:31:50 +08`, there were still no
  `pearlm_paths.pkl`, path shards, `paths.complete`, `adapter.json`,
  `export_validation.json`, `accuracy.json`, or `pipeline.complete`.

Interpretation: PEARLM has moved from training into the path-export phase.
There is still no reportable Amazon PEARLM recommendation result until export,
adapter validation, export validation, and strict full-user accuracy evaluation
finish.

Twenty-second Amazon monitor: PEARLM export live check

Checked the live PEARLM export process at `2026-06-27 00:32:46 +08`.

- parent tmux shell remained alive under session
  `pearlm_amazon_formal_20260626`;
- active export process:
  `scripts/hopwise/export_native_paths.py`;
- export PID: `3456663`;
- export runtime: about `15:26`;
- process state: `Rl+`;
- CPU usage: about `98.7%`;
- memory usage: about `0.6%`;
- command confirmed formal export settings:
  `--model PEARLM`, `--dataset canonical_amazon_book_kgat_v1`,
  `--paths-per-user 25`, `--num-beams 25`, `--batch-size 16`,
  `--gpu-id 3`;
- no path shards or `pearlm_paths.pkl` existed yet at the artifact check just
  before this process check;
- GPU usage for this process was not yet visible, which is consistent with the
  export still being in CPU-heavy dataset/model/path-sampling preparation.

Interpretation: export is active and CPU-bound, not failed. The next useful
artifact-level evidence is the first shard under `path_shards/`, followed by
`pearlm_paths.pkl` and `paths.complete`.

Twenty-third Amazon monitor: PEARLM export still in CPU preparation

Checked at `2026-06-27 00:53:29 +08`.

- PEARLM export process was still alive:
  PID `3456663`, runtime about `36:08`;
- process state remained `Rl+`;
- CPU usage remained about `99.4%`;
- memory remained about `0.6%`;
- no GPU allocation by the PEARLM export process was visible yet;
- artifact state was unchanged:
  `train.complete` and `train.json` present, but no `path_shards/` files,
  no `pearlm_paths.pkl`, no `paths.complete`, no adapter/export/accuracy
  summaries, and no `pipeline.complete`;
- PEARLM export log still had no new line after the export-start warnings.

Interpretation: the export step is still active and CPU-bound. This is
consistent with the export process rebuilding Hopwise dataset/path-sampling
state before the first generation batch; the earlier training-side KG path
sampling took about `1:10:01`, so the absence of shards at `36` minutes is not
yet evidence of failure.

Twenty-fourth Amazon monitor: PEARLM export writing shards

Checked at `2026-06-27 01:34:02 +08`.

- `train.complete` and `train.json` remained present;
- PEARLM export had started writing per-batch shards;
- path shard count: `402`;
- first shard:
  `path_shards/batch_000000.pkl`, mtime `2026-06-27 01:28:38`;
- latest observed shard:
  `path_shards/batch_000401.pkl`, mtime `2026-06-27 01:34:02`;
- latest shard summary:
  `requested_users=16`, `processed_users=16`, skipped users `0`,
  rows `214`;
- latest log counters reached:
  `requested_users=6432`, `processed_users=6432`,
  `skipped_cold_start_users=0`, `raw_paths=87235`;
- no `pearlm_paths.pkl`, `paths.complete`, adapter/export/accuracy summaries,
  or `pipeline.complete` yet.

Interpretation: PEARLM export is now past the long dataset/path-sampling
preparation phase and is actively generating/writing path shards. Amazon-book
has `70591` canonical test users, so with `batch-size=16` the expected full
export is about `4412` shard batches before the manifest and downstream
adapter/validation steps appear.

Twenty-fifth Amazon monitor: PEARLM formal completed

PEARLM Amazon-book formal pipeline completed at `2026-06-27 02:27:39 +08`.

Final PEARLM artifacts:

- run root:
  `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1`;
- markers present: `train.complete`, `paths.complete`, `pipeline.complete`;
- summary JSONs present: `train.json`, `adapter.json`,
  `export_validation.json`, `accuracy.json`;
- raw manifest: `pearlm_paths.pkl`;
- path shards: `4412`;
- first shard: `path_shards/batch_000000.pkl`;
- last shard: `path_shards/batch_004411.pkl`;
- manifest metadata:
  `source_dataset=canonical_amazon_book_kgat_v1`,
  `canonical_dataset=amazon_book_kgat_v1`, `paths_per_user=25`,
  `num_beams=25`, `requested_users=70591`, `processed_users=70591`,
  `raw_paths=887376`, `row_shards=4412`;
- skipped cold-start users during path export: `0`;
- xrecsys alpha sweeps were intentionally not run for Amazon; marker note
  present in `xrecsys_not_applicable.txt`.

Adapter summary:

- status: `PASS`;
- dataset: `amazon_book_kgat_v1`;
- requested users: `70591`;
- processed users: `70591`;
- output users: `70591`;
- users with recommendations: `70216`;
- raw users: `70290`;
- raw paths: `887376`;
- unseen paths: `885270`;
- explanations: `578518`;
- native score range:
  `[8.445615094387904e-06, 0.9891902804374695]`;
- path shards: `4412`.

Export validation:

- status: `PASS`;
- canonical test users: `70591`;
- top-k users: `70591`;
- candidate users: `70216`;
- pred-path rows: `885270`;
- explanation rows: `578518`;
- score range: `[0.0, 1.0]`;
- strict full-test-user requirement: enabled.

Accuracy:

- status: `PASS`;
- users: `70591`;
- user coverage: `1.0`;
- missing test users: `0`;
- extra prediction users: `0`;
- HR@10: `0.02933801759`;
- NDCG@10: `0.01071598226`;
- Precision@10: `0.00309954527`;
- Recall@10: `0.01540367157`;
- empty users: `375`;
- exact-k users: `41791`;
- short users: `28800`;
- mean recommendation items: `8.19535068210`;
- slot coverage: `0.81953506821`.

Independent PEARLM re-validation was run after pipeline completion without
overwriting the formal summaries:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/validate_xrecsys_export.py \
  --paths-dir xrecsys/paths/amazon_book_kgat_v1/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25 \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --require-all-test-users \
  --summary-json /tmp/pearlm_amazon_export_validation_recheck.json
```

Recheck result: `PASS`.

Accuracy was independently rechecked with strict full-user coverage and only
`--allow-short` for naturally short recommendation lists:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/evaluate_uid_topk.py \
  --uid-topk xrecsys/paths/amazon_book_kgat_v1/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25/uid_topk.csv \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --topk 10 \
  --allow-short \
  --summary-json /tmp/pearlm_amazon_accuracy_recheck.json
```

Recheck result: `PASS`.

Interpretation: Amazon-book now has two completed formal native-path baselines
on the larger native-KG dataset: KGGLM and PEARLM. PEARLM has higher formal
recommendation accuracy than KGGLM on this dataset in the current run
(`HR@10=0.029338` vs. KGGLM `HR@10=0.012665`; `NDCG@10=0.010716` vs. KGGLM
`NDCG@10=0.003022`). Both are reportable for recommendation accuracy and
native path export quality. Neither is reportable for Amazon SEP/ETD/LIR
alpha-sweep explanation tradeoffs until an approved timestamp/SEP/ETD
denominator is defined for Amazon-book.

Current status matrix:

Created a concise reporting matrix at
`reports/tables/canonical_native_path_status_matrix.md`.

The matrix records:

- LastFM and ML-1M six-model completion state and HR/NDCG values;
- Amazon-book KGGLM/PEARLM formal completion state and comparison metrics;
- Amazon PGPR/UCPR/CAFE/TPRec blocked state and the required schema/runtime
  porting reason;
- figure-bundle status for LastFM and ML-1M;
- Amazon alpha-sweep status as `N/A` until a canonical timestamp/SEP/ETD
  denominator is approved.

Follow-up reporting artifact:

- added machine-readable companion CSV:
  `reports/tables/canonical_native_path_status_matrix.csv`;
- added Amazon classic-port acceptance criteria to the Markdown matrix:
  shared canonical projection/remap/export/accuracy gates plus model-specific
  PGPR, UCPR, CAFE, and TPRec prerequisites.

Reproducibility follow-up:

- added `scripts/analysis/generate_canonical_status_matrix.py`;
- the script reads current accuracy/export JSON artifacts, validates that
  completed rows are `PASS`, counts LastFM/ML-1M figure bundle files, and
  regenerates both:
  - `reports/tables/canonical_native_path_status_matrix.csv`;
  - `reports/tables/canonical_native_path_status_matrix.md`;
- verified regeneration with:

```bash
python scripts/analysis/generate_canonical_status_matrix.py
python -m py_compile scripts/analysis/generate_canonical_status_matrix.py
```

The generated Markdown now shows Amazon blocker reasons directly in the main
status table, while the CSV keeps the same reasons in `blocker_or_note`.

Report regeneration wrapper:

- added `scripts/analysis/regenerate_canonical_native_path_reports.sh`;
- default behavior:
  - regenerate LastFM six-model alpha-sweep figures/CSVs;
  - regenerate ML-1M six-model alpha-sweep figures/CSVs;
  - regenerate the canonical native-path status CSV/Markdown;
  - validate that each figure bundle has `12` PNG and `12` CSV files;
  - validate that the status CSV has `18` rows and that the Markdown contains
    the Amazon porting criteria;
- quick mode:
  `bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only`;
- full mode:
  `bash scripts/analysis/regenerate_canonical_native_path_reports.sh`.

Both modes were executed successfully. The full mode completed as report-only
analysis, not training or path extraction, and ended with:

```text
canonical native-path report validation PASS
Canonical native-path reports regenerated.
```

Stronger export-validation evidence:

- added `scripts/analysis/validate_canonical_export_evidence.py`;
- the validator enumerates the `14` complete model/dataset rows
  (LastFM six models, ML-1M six models, Amazon KGGLM/PEARLM), runs
  `validate_xrecsys_export.validate(..., require_all_test_users=True)`, and
  writes per-row summaries under
  `reports/tables/canonical_export_validation/`;
- full revalidation summaries now exist for all `14` complete rows, and
  `reports/tables/canonical_export_validation/manifest.json` records
  `status=PASS`, `exports=14`;
- because classic PGPR/UCPR exports contain multi-million-row `pred_paths.csv`
  files (for example LastFM PGPR has about `11.7M` rows), the validator also
  supports targeted runs:

```bash
python scripts/analysis/validate_canonical_export_evidence.py --list
python scripts/analysis/validate_canonical_export_evidence.py \
  --only amazon_book_kgat_v1:KGGLM \
  --only amazon_book_kgat_v1:PEARLM
python scripts/analysis/validate_canonical_export_evidence.py --manifest-only
```

- `scripts/analysis/generate_canonical_status_matrix.py` now requires these
  export-validation summaries for complete rows and records each summary path
  in the CSV `export_evidence` column;
- `scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only`
  now rebuilds the export-validation manifest before regenerating the status
  matrix.

Completion audit artifact:

- added `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`;
- the audit maps the active objective to evidence by requirement area:
  LastFM, ML-1M, Amazon, export validation, accuracy validation, report
  reproducibility, bug fixes, documentation, and remaining blockers;
- verified referenced paths exist:
  - status CSV/Markdown;
  - export-validation manifest;
  - LastFM and ML-1M figure bundles;
  - report regeneration wrapper.

Audit conclusion: all reportable LastFM and ML-1M canonical native-path
baselines are complete, and Amazon KGGLM/PEARLM formal baselines are complete.
The broader goal remains active rather than globally closed because Amazon
PGPR/UCPR/CAFE/TPRec are documented schema/runtime porting blockers, not
implemented experiments.

Amazon classic readiness audit:

- added `scripts/analysis/audit_amazon_classic_port_readiness.py`;
- generated `reports/tables/amazon_classic_port_readiness.json`;
- current readiness status: `BLOCKED`;
- blocked models: `PGPR`, `UCPR`, `CAFE`, `TPRec`;
- checks include:
  - PGPR `RELATION_FILES`/`PRODUCT_ENTITIES` and CLI model-dataset support;
  - UCPR `DATASET_CONFIG` and CLI model-dataset support;
  - CAFE `DATASET_CONFIG` and CLI model-dataset support;
  - TPRec path-constraint and pipeline case support;
- `scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only`
  now regenerates this readiness audit as part of report validation.

Artifact manifest:

- added `scripts/analysis/generate_canonical_artifact_manifest.py`;
- generated `reports/tables/canonical_native_path_artifact_manifest.json`;
- the manifest records:
  - status matrix row counts (`18` rows, `14` complete, `4` blocked);
  - export-validation manifest status (`PASS`, `14` exports);
  - Amazon classic readiness status (`BLOCKED`);
  - figure-bundle counts for LastFM and ML-1M (`12` PNG + `12` CSV each);
  - core report files and scripts with file size, mtime, and SHA-256 hashes
    for small files;
  - the `14` per-row export-validation summaries;
- `scripts/analysis/regenerate_canonical_native_path_reports.sh` now creates
  this manifest and asserts it exists before reporting success.

Amazon classic readiness Markdown companion:

- extended `scripts/analysis/audit_amazon_classic_port_readiness.py` so the
  Amazon PGPR/UCPR/CAFE/TPRec readiness gate writes both:
  - machine-readable JSON:
    `reports/tables/amazon_classic_port_readiness.json`;
  - human-readable Markdown:
    `reports/tables/amazon_classic_port_readiness.md`;
- the Markdown table records model-by-model readiness, passed-check counts,
  failed gates, concrete next actions, and per-check evidence;
- `scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only`
  now asserts that both readiness artifacts exist;
- `scripts/analysis/generate_canonical_artifact_manifest.py` now includes the
  readiness Markdown and the short handoff document in its core-file manifest;
- `docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md` now points to the
  human-readable readiness table as the fastest way to inspect the remaining
  Amazon classic blockers.

Amazon PGPR data-view smoke:

- extended `scripts/data/canonical/build_pgpr_view.py` with an
  `amazon_book_kgat_v1` model-dataset option;
- the builder now creates a generic Amazon book/entity PGPR view from the
  KGAT Amazon-book source:
  - `entities/user.txt.gz`: `70,679` users;
  - `entities/book.txt.gz`: `24,915` book/product entities;
  - `entities/entity.txt.gz`: `113,487` KG entities;
  - nine default semantic book relations:
    author, genre, original language, subject, next/previous series,
    part-of-series, character, interior illustration;
- generated the smoke view with:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/data/canonical/build_pgpr_view.py \
  --canonical-root runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1 \
  --source-xrecsys-dataset-dir data_sources/kgat_amazon_book \
  --out-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/amazon_book_kgat_v1 \
  --dataset amazon_book_kgat_v1 \
  --model-dataset amazon_book_kgat_v1
```

- metadata:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_view_metadata.json`;
- round-trip validation is exact for train, valid, and test labels:
  - train users: `70,679`;
  - valid users: `70,679`;
  - test users: `70,591`;
- this is a preparation artifact only. PGPR Amazon remains blocked until an
  isolated PGPR runtime patch defines the Amazon book/entity schema, relation
  constants, path patterns, loader smoke, training, path export, strict export
  validation, and strict accuracy validation.

Amazon PGPR isolated preprocess smoke:

- added `scripts/model_patches/patch_pgpr_amazon_runtime.py`;
  - patches an isolated PGPR runtime copy, not the source `xrecsys` tree;
  - adds `amazon_book_kgat_v1` dataset constants;
  - adds generic `book`/`entity` schema support;
  - wires the nine default Amazon semantic book relations into PGPR
    `utils.py`, `data_utils.py`, and `knowledge_graph.py`;
- added `scripts/validation/validate_pgpr_preprocess_smoke.py`;
  - validates PGPR-generated train/test labels against canonical labels;
  - confirms core PGPR preprocess pickles exist;
- added `scripts/validation/run_pgpr_amazon_preprocess_smoke.sh`;
  - copies PGPR into
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke/`;
  - copies the generated Amazon PGPR view;
  - applies the existing general PGPR patch plus the new Amazon preprocess
    patch;
  - runs `preprocess.py --dataset amazon_book_kgat_v1`;
  - writes
    `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_runtime_preprocess_smoke.json`;
- executed:

```bash
bash scripts/validation/run_pgpr_amazon_preprocess_smoke.sh
```

- smoke result: `PASS`;
- generated core runtime artifacts:
  - `dataset.pkl`: `35,947,655` bytes;
  - `kg.pkl`: `16,042,181` bytes;
  - `train_label.pkl`: `2,521,951` bytes;
  - `test_label.pkl`: `1,345,587` bytes;
- label validation:
  - train users/interactions: `70,679` / `581,835`, exact match;
  - test users/interactions: `70,591` / `193,920`, exact match;
- `scripts/analysis/audit_amazon_classic_port_readiness.py` now records PGPR
  preprocess smoke as a passed gate, while keeping PGPR Amazon blocked until
  formal export and accuracy validation exist.

Amazon PGPR TransE one-batch smoke:

- extended `scripts/model_patches/patch_pgpr_amazon_runtime.py` to patch the
  isolated PGPR `transe_model.py` for `amazon_book_kgat_v1`;
  - adds Amazon `user`/`book`/`entity` embeddings;
  - adds `purchased` plus the nine semantic book relations;
  - routes the Amazon batch columns through the PGPR negative-sampling loss;
  - replaces deprecated `np.float` with `float` in the patched runtime copy;
- added `scripts/validation/run_pgpr_transe_forward_smoke.py`;
- executed:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python \
  scripts/validation/run_pgpr_transe_forward_smoke.py \
  --runtime-root runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke \
  --dataset amazon_book_kgat_v1 \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_forward_smoke.json \
  --batch-size 64 \
  --embed-size 16 \
  --num-neg-samples 2
```

- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_forward_smoke.json`;
- batch shape: `64 x 11`
  (`user`, `book`, and nine semantic book-relation columns);
- finite loss: `18.71475601196289`;
- gradient tensors: `21`;
- this proves the Amazon PGPR schema can enter TransE loss computation, but it
  is not yet a trained checkpoint, policy run, path export, or formal
  accuracy result.

Amazon PGPR TransE training smoke:

- extended `scripts/model_patches/patch_pgpr_amazon_runtime.py` so the
  isolated `train_transe_model.py` can export Amazon `transe_embed.pkl`;
- added `scripts/validation/validate_pgpr_transe_training_smoke.py`;
- added `scripts/validation/run_pgpr_amazon_transe_training_smoke.sh`;
- executed a small, non-formal training smoke:

```bash
bash scripts/validation/run_pgpr_amazon_transe_training_smoke.sh
```

- smoke configuration:
  - epochs: `1`;
  - embedding dimension: `16`;
  - batch size: `2048`;
  - negative samples: `2`;
  - device: CPU;
- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_training_smoke.json`;
- generated checkpoint:
  `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke/models/PGPR/tmp/amazon_book_kgat_v1/train_transe_model_amazon_smoke_e1_d16/transe_model_sd_epoch_1.ckpt`;
- generated embedding pickle:
  `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl`;
- validation details:
  - checkpoint exists: `true`;
  - embedding pickle exists: `true`;
  - missing embedding keys: none;
  - expected embedding dimension: `16`;
  - train log contains `Epoch: 01`;
- this advances PGPR Amazon from data/runtime smoke into training smoke, but
  PGPR Amazon remains blocked until policy training/inference, path export,
  strict export validation, and strict accuracy validation pass.

Amazon PGPR policy environment / beam smoke:

- extended `scripts/model_patches/patch_pgpr_amazon_runtime.py` to patch the
  isolated PGPR `kg_env.py` and `test_agent.py`;
  - replaces ml1m/lastfm-only product/relation/path-pattern branches with the
    generic helper functions added for Amazon;
  - patches `batch_step` to use the Amazon KG relation map;
  - patches beam search to use `get_kg_relation(env.dataset_name)`;
- added `scripts/validation/run_pgpr_policy_env_smoke.py`;
- first smoke attempt caught a real bug:
  - `_get_actions` had been patched to use `self.KG_RELATION`;
  - `batch_step` still used the old ml1m/lastfm conditional map because the
    patch helper skipped an identical replacement string already present in a
    different function;
  - fixed with a context-specific replacement around the `# Execute batch
    actions` block;
- executed:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python \
  scripts/validation/run_pgpr_policy_env_smoke.py \
  --runtime-root runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke \
  --dataset amazon_book_kgat_v1 \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_env_smoke.json \
  --max-acts 10000
```

- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_env_smoke.json`;
- verified manual native path:
  `user(0) -> purchased -> book(0) -> book_author -> entity(81640) -> book_author -> book(11)`;
- manual path checks:
  - environment done: `true`;
  - path pattern accepted: `true`;
  - final node is book: `true`;
  - reward finite: `true`;
- random ActorCritic beam smoke:
  - beam paths: `4`;
  - book-ending paths: `4`;
- this proves the Amazon PGPR policy environment and beam relation mapping can
  execute native paths, but PGPR Amazon is still blocked until policy training,
  path export/adaptation, strict export validation, and strict accuracy
  validation are complete.

Amazon PGPR policy training and inference smokes:

- added `scripts/validation/validate_pgpr_policy_training_smoke.py`;
- added `scripts/validation/run_pgpr_amazon_policy_training_smoke.sh`;
- added `scripts/validation/run_pgpr_policy_inference_smoke.py`;
- updated `scripts/validation/run_pgpr_amazon_policy_training_smoke.sh` to apply
  both the general PGPR runtime patch and the Amazon-specific PGPR runtime
  patch before training;
- fixed `scripts/model_patches/patch_pgpr_runtime.py` idempotency:
  - a runtime that had already been Amazon-patched contained the newer generic
    `self.review_interaction` / `self.main_product` user-product scaling block;
  - the general patch previously recognized only its own ml1m/lastfm batched
    scaling block and aborted;
  - the patch now treats the Amazon-aware scaling block as already patched;
- first policy-inference smoke attempt executed beam search but failed while
  serializing the summary because the probability examples contained
  `numpy.float32`;
- fixed `scripts/validation/run_pgpr_policy_inference_smoke.py` with a small
  `to_jsonable` converter for numpy/torch scalar containers;
- executed policy training smoke:

```bash
bash scripts/validation/run_pgpr_amazon_policy_training_smoke.sh
```

- smoke configuration:
  - epochs: `1`;
  - policy hidden sizes: `32 16`;
  - batch size: `8192`;
  - max actions: `250`;
  - device: CPU;
- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_training_smoke.json`;
- generated policy checkpoint:
  `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke/models/PGPR/tmp/amazon_book_kgat_v1/train_agent_amazon_smoke_e1_a250_h32-16/policy_model_epoch_1.ckpt`;
- validation details:
  - checkpoint exists: `true`;
  - train log contains the checkpoint save marker: `true`;
  - `state_dim`: `64`;
  - `act_dim`: `251`;
  - expected actor/critic/layer shapes passed;
- executed policy inference smoke:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python \
  scripts/validation/run_pgpr_policy_inference_smoke.py \
  --runtime-root runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_smoke \
  --dataset amazon_book_kgat_v1 \
  --run-name train_agent_amazon_smoke_e1_a250_h32-16 \
  --epoch 1 \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke.json \
  --max-acts 250 \
  --num-users 8 \
  --topk 5 5 1
```

- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke.json`;
- inference details:
  - users: `8`;
  - generated paths: `191`;
  - probability rows: `191`;
  - finite probability rows: `191`;
  - book-ending paths: `170`;
- `scripts/analysis/audit_amazon_classic_port_readiness.py` now records the
  policy training and policy inference smokes as passed gates. PGPR Amazon
  remains blocked because there is still no formal policy run, native path
  export/adaptation, strict export validation, or strict accuracy result.

Amazon PGPR adapter/export smoke:

- updated `adapters/pgpr_adapter.py` to support
  `amazon_book_kgat_v1` with product type `book` and interaction relation
  `purchased`;
- updated `scripts/validation/run_pgpr_policy_inference_smoke.py` with an
  optional `--paths-pkl` output so the already-validated beam smoke can feed
  the existing PGPR adapter interface;
- added `scripts/validation/run_pgpr_amazon_export_smoke.sh`;
- executed:

```bash
bash scripts/validation/run_pgpr_amazon_export_smoke.sh
```

- smoke result: `PASS`;
- inference pkl:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke_paths.pkl`;
- xrecsys export directory:
  `xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-smoke-e1_a250_8users`;
- validation summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_export_smoke_validation.json`;
- export validation details:
  - status: `PASS`;
  - pred-path rows: `166`;
  - candidate users: `8`;
  - canonical test users listed in `uid_topk.csv`: `70,591`;
  - top-k explanations: `80`;
  - `require_all_test_users`: `false`;
- interpretation:
  - the Amazon PGPR path serializer and adapter can emit xrecsys-compatible
    `pred_paths.csv`, `uid_topk.csv`, and `uid_pid_explanation.csv`;
  - this is deliberately still a smoke export, not a formal PGPR Amazon
    baseline, because it uses an 8-user policy-inference pkl and does not
    require full-user candidate coverage.

Amazon PGPR formal-v1 pipeline launch:

- generalized `scripts/validation/validate_pgpr_policy_training_smoke.py`:
  - added `--expected-hidden`;
  - formal PGPR policy checkpoints can now be validated with hidden sizes
    other than the smoke-only `32 16`;
- generalized `scripts/validation/run_pgpr_policy_inference_smoke.py`:
  - added `--hidden`;
  - added `--beam-batch-size`;
  - `--num-users 0` now means all canonical test users;
- added `scripts/validation/run_pgpr_amazon_formal_pipeline.sh`;
- added `scripts/validation/launch_pgpr_amazon_formal_pipeline.sh`;
- rationale:
  - the formal pipeline must not reuse the smoke `dim=16` TransE or
    `hidden=32 16` policy checkpoint;
  - the first formal-v1 Amazon PGPR run uses full canonical test-user coverage
    with a CPU-feasible beam `10 12 1`;
  - the larger historical PGPR `25 50 1` beam is supported through
    `PGPR_FORMAL_TOPK` but is expected to create a much larger path pool on
    Amazon-Book KGAT and should be treated as a separate expensive run if
    needed;
- launched through persistent tmux:

```bash
bash scripts/validation/launch_pgpr_amazon_formal_pipeline.sh
```

- launch result:
  - tmux session: `pgpr_amazon_formal`;
  - pane pid recorded in:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline.pid`;
  - log:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline.log`;
  - status:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`;
- formal-v1 configuration:
  - device: CPU;
  - TransE: `30` epochs, dim `300`, batch `2048`, negative samples `5`;
  - policy: `50` epochs, hidden `512 256`, batch `8192`,
    max actions `250`;
  - full-user inference/export beam: `10 12 1`;
  - strict export summary target:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json`;
  - strict accuracy summary target:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json`;
- current observed state:
  - formal runtime preprocess validation PASS;
  - status stage: `transe`;
  - PGPR Amazon remains not reportable until the formal pipeline writes strict
    full-user export validation and strict accuracy summaries with
    `status=PASS`.

Amazon TPRec structural wiring and timestamp semantics audit:

- added Amazon relation-token path constraints to
  `scripts/hopwise/tprec_runtime.py`;
- added `canonical_amazon_book_kgat_v1` to:
  - `scripts/hopwise/run_canonical_tprec.py`;
  - `scripts/hopwise/export_tprec_paths.py`;
  - `scripts/hopwise/run_canonical_tprec_pipeline.sh`;
- the Amazon TPRec product endpoint is exported as canonical `book`, and the
  interaction relation is `purchased`;
- added `scripts/validation/audit_tprec_amazon_timestamp_semantics.py`;
- ran:

```bash
python scripts/validation/audit_tprec_amazon_timestamp_semantics.py
```

- audit output:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json`;
- structural checks:
  - Hopwise Amazon view status: `PASS`;
  - kept link rows: `24,915`;
  - dropped link rows: `0`;
  - required TPRec relation-token constraints are all present in the Hopwise
    KG: `relation:5`, `relation:10`, `relation:11`, `relation:13`,
    `relation:15`, `relation:18`, `relation:19`, `relation:20`,
    `relation:36`;
- timestamp findings:
  - canonical metadata `timestamp_policy`: `-1`;
  - train sentinel fraction: `1.0`;
  - valid sentinel fraction: `1.0`;
  - test sentinel fraction: `1.0`;
  - `formal_temporal_reward_approved`: `false`;
- verified the Amazon TPRec formal pipeline default entrypoint stops safely at
  the timestamp gate:

```bash
bash scripts/hopwise/run_canonical_tprec_pipeline.sh canonical_amazon_book_kgat_v1
```

- expected result:
  - exit code: `3`;
  - message: Amazon TPRec formal run blocked because all canonical timestamps
    are sentinel `-1`;
- updated `scripts/analysis/audit_amazon_classic_port_readiness.py`;
- updated `scripts/analysis/generate_canonical_status_matrix.py`;
- regenerated report tables:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

- readiness result:
  - TPRec checks passed: `5/6`;
  - only failed TPRec gate:
    `Amazon timestamps support formal TPRec temporal rewards`;
- interpretation:
  - Amazon TPRec is no longer blocked by missing path constraints or missing
    pipeline entrypoints;
  - it remains blocked for formal reporting because TPRec is a temporal model
    and the canonical Amazon-book KGAT interactions contain no real timestamps;
  - running it anyway would need to be labeled as a non-temporal ablation, not
    a formal TPRec baseline.

Amazon UCPR data-view projection:

- extended `scripts/data/canonical/build_ucpr_view.py` with an
  `amazon_book_kgat_v1` KGAT-source projection;
- the projection exposes Amazon book items as UCPR `product`, generic KG tail
  nodes as `entity`, and nine native book relations:
  `book_author_entity`, `book_genre_entity`,
  `book_original_language_entity`, `book_subject_entity`,
  `book_next_in_series_entity`, `book_previous_in_series_entity`,
  `book_part_of_series_entity`, `book_character_entity`, and
  `book_interior_illustration_entity`;
- generated the UCPR view with:

```bash
python scripts/data/canonical/build_ucpr_view.py \
  --canonical-root runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1 \
  --source-xrecsys-dataset-dir data_sources/kgat_amazon_book \
  --out-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/preprocessed/ucpr \
  --dataset amazon_book_kgat_v1 \
  --model-dataset amazon_book_kgat_v1
```

- output metadata:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/preprocessed/ucpr_view_metadata.json`;
- validation result:
  - users: `70,679`;
  - products: `24,915`;
  - relation files: `9`;
  - train interactions: `581,835`, exact canonical label round-trip;
  - valid interactions: `70,679`, exact canonical label round-trip;
  - test interactions: `193,920`, exact canonical label round-trip;
  - skipped users/products: `0` in all splits;
- updated `scripts/analysis/audit_amazon_classic_port_readiness.py` so UCPR
  reports generated view evidence separately from runtime support;
- added Amazon book aliases to `adapters/ucpr_adapter.py`:
  - UCPR `product` paths map to canonical `book`;
  - Amazon relation names with `_entity` suffixes map to canonical
    `book_*` relation names;
- interpretation:
  - Amazon UCPR is no longer blocked at the data-view/remap layer;
  - it is also no longer blocked by the adapter alias scaffold;
  - it remains blocked for formal training/export because the active UCPR
    runtime constants, `KG_RELATION`, main interaction relation, and
    path-pattern tables still need an Amazon-specific patch.

2026-06-27 14:59 +08 progress checkpoint:

- refreshed status-only reports after the Amazon UCPR data-view and adapter
  alias updates:

```bash
python -m py_compile \
  adapters/ucpr_adapter.py \
  scripts/data/canonical/build_ucpr_view.py \
  scripts/analysis/audit_amazon_classic_port_readiness.py \
  scripts/analysis/generate_canonical_status_matrix.py \
  scripts/analysis/generate_canonical_artifact_manifest.py

bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

- validation result:
  - `canonical native-path report validation PASS`;
  - status matrix remains `18` rows: `14` complete, `4` blocked;
  - UCPR Amazon readiness is now `4/5`;
  - the only failed UCPR gate is active runtime Amazon path semantics;
- PGPR Amazon formal-v1 monitor:
  - tmux session `pgpr_amazon_formal` is still alive;
  - status JSON still reports `status=RUNNING`, `stage=transe`;
  - TransE checkpoints through epoch `7` are present;
  - log has advanced into epoch `8`;
  - strict formal export validation and strict accuracy JSONs are still absent,
    so PGPR Amazon remains not reportable.

Amazon UCPR runtime schema patch and preprocess smoke:

- added `scripts/model_patches/patch_ucpr_amazon_runtime.py`;
- the patch injects `amazon_book_kgat_v1` into the runtime copy's UCPR
  dictionaries:
  - `DATASET_DIR`, `TMP_DIR`, metric/config/log path maps;
  - `INTERACTION`;
  - `KG_RELATION`;
  - `PATH_PATTERN`;
  - `MAIN_PRODUCT_INTERACTION`;
  - KG-based preprocess branch for Amazon;
- added `scripts/validation/validate_ucpr_preprocess_smoke.py`;
- added `scripts/validation/run_ucpr_amazon_preprocess_smoke.sh`;
- executed:

```bash
bash scripts/validation/run_ucpr_amazon_preprocess_smoke.sh
```

- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_runtime_preprocess_smoke.json`;
- runtime:
  `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_runtime_smoke`;
- generated UCPR runtime core files:
  - `dataset.pkl`: `30,628,454` bytes;
  - `kg.pkl`: `55,436,208` bytes;
  - train/valid/test label pickles all present;
- validation details:
  - runtime schema checks all true;
  - dataset entities: `entity`, `product`, `user`;
  - UCPR Amazon relations: `9`;
  - train labels: `581,835` interactions, exact canonical round-trip;
  - valid labels: `70,679` interactions, exact canonical round-trip;
  - test labels: `193,920` interactions, exact canonical round-trip;
  - KG `purchased` user edges: `581,835`;
  - all nine Amazon relation edge sets are non-empty;
- interpretation:
  - Amazon UCPR is now past the data-view, adapter-alias, runtime-schema, and
    preprocess-label gates;
  - it is still not a formal Amazon UCPR baseline because TransE training,
    policy training, native-path export, strict export validation, and strict
    accuracy validation have not run.

Amazon UCPR TransE forward/backward smoke:

- added `scripts/validation/run_ucpr_transe_forward_smoke.py`;
- executed:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/rep/bin/python \
  scripts/validation/run_ucpr_transe_forward_smoke.py \
  --runtime-root runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_runtime_smoke \
  --dataset amazon_book_kgat_v1 \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_transe_forward_smoke.json \
  --batch-size 64 \
  --embed-size 32 \
  --num-neg-samples 3
```

- smoke result: `PASS`;
- summary:
  `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_transe_forward_smoke.json`;
- details:
  - batch shape: `[64, 11]`;
  - loss: `24.95353126525879`;
  - finite gradient tensors: `21`;
  - all expected Amazon relation parameters are present, including
    `purchased` and the nine `book_*_entity` relations;
- interpretation:
  - the patched UCPR Amazon runtime can instantiate its TransE model and run
    loss/backprop through the Amazon schema;
  - formal UCPR Amazon TransE training is still pending.

2026-06-27 15:14 +08 progress checkpoint:

- refreshed status-only reports after the UCPR Amazon TransE smoke:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

- validation result:
  - `canonical native-path report validation PASS`;
  - UCPR Amazon readiness is now `7/8`;
  - the only failed UCPR gate is formal Amazon UCPR export and accuracy
    validation;
- PGPR Amazon formal-v1 monitor:
  - tmux session `pgpr_amazon_formal` is still alive;
  - status JSON still reports `status=RUNNING`, `stage=transe`;
  - TransE checkpoints through epoch `11` are present;
  - log has advanced into epoch `12`;
  - strict formal export validation and strict accuracy JSONs are still absent.

2026-06-29 11:10 +08 PGPR Amazon formal inference/export resume:

- observed that the earlier PGPR Amazon formal-v1 status file still reported
  `status=RUNNING`, `stage=inference_export`, but there was no live tmux
  session or matching Python process;
- current artifacts showed that the expensive training stages had completed:
  - TransE formal checkpoint:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_formal/models/PGPR/tmp/amazon_book_kgat_v1/train_transe_model_amazon_formal_e30_d300_b2048_n5/transe_model_sd_epoch_30.ckpt`;
  - policy formal checkpoint:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_formal/models/PGPR/tmp/amazon_book_kgat_v1/train_agent_amazon_formal_e50_a250_h512-256/policy_model_epoch_50.ckpt`;
  - strict final files were still absent:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json`;
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json`;
- diagnosis:
  - the old full-user inference path accumulated all beam-search paths in one
    Python object before writing `PATHS_PKL`;
  - for Amazon, `70,591` canonical test users with beam `10-12-1` can create
    millions of Python path/probability objects;
  - this likely explains the stale `RUNNING` status with no output pickle and
    no final CSVs;
- fix:
  - added `scripts/validation/export_pgpr_streaming.py`;
  - the new exporter keeps native PGPR beam search and native TransE item
    scoring, but streams candidate paths through a raw temporary CSV and keeps
    only per-user top-10 state in memory;
  - updated `scripts/validation/run_pgpr_amazon_formal_pipeline.sh` so
    `PGPR_USE_STREAMING_EXPORT=1` is the default for the Amazon formal
    inference/export stage;
  - the legacy pickle route remains available by setting
    `PGPR_USE_STREAMING_EXPORT=0`;
- smoke validation:

```bash
/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python \
  scripts/validation/export_pgpr_streaming.py \
  --runtime-root runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_formal \
  --dataset amazon_book_kgat_v1 \
  --run-name train_agent_amazon_formal_e50_a250_h512-256 \
  --epoch 50 \
  --embedding-pkl runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_runtime_formal/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --paths-dir xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-streaming-smoke-8users \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke.json \
  --max-acts 250 \
  --beam-batch-size 4 \
  --hidden 512 256 \
  --topk 10 12 1 \
  --recommendation-topk 10 \
  --num-users 8

/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python \
  scripts/validation/validate_xrecsys_export.py \
  --paths-dir xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-streaming-smoke-8users \
  --labels-dir runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/labels \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --summary-json runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke_validation.json
```

- smoke result:
  - streaming export summary:
    `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke.json`;
  - status: `PASS`;
  - processed users: `8`;
  - raw candidate rows: `677`;
  - candidate users: `8`;
  - slot coverage: `1.0`;
  - native score range before normalization:
    `[-2.5623128414154053, 6.311394214630127]`;
  - validator summary:
    `runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_streaming_export_smoke_validation.json`;
  - validator status: `PASS`;
  - validator saw `677` pred-path rows, `80` explanations, and normalized
    score range `[0.0, 1.0]`;
- formal resume command:

```bash
PGPR_USE_STREAMING_EXPORT=1 PGPR_INFERENCE_BATCH_SIZE=256 \
  bash scripts/validation/launch_pgpr_amazon_formal_pipeline.sh
```

- launch result:
  - tmux session: `pgpr_amazon_formal`;
  - tmux pane pid: `97901`;
  - active Python child observed: `99221`;
  - status:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status now records `streaming_export_enabled=1` and
    `stage=inference_export`;
  - streaming progress summary:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_streaming_export_formal.json`;
  - live output directory:
    `xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-formal-e50_a250_beam10-12-1`;
  - at the first monitor checkpoint, `pred_paths.raw.tmp.csv` had reached
    `107,592` lines and the Python child was using about `1.7GB` RSS;
- interpretation:
  - PGPR Amazon is materially past training and is actively running formal
    full-user native-path export again;
  - it remains not reportable until the pipeline writes:
    - `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json`;
    - `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json`;
  - after those appear, regenerate the status matrix and Amazon readiness
    report before promoting PGPR Amazon from blocked to a formal result row.

2026-06-29 11:23 +08 UCPR Amazon formal training queue launch:

- GPU/resource check before launch:
  - all four RTX A5000 GPUs were effectively idle;
  - PGPR Amazon streaming export was CPU-bound, so a UCPR GPU training queue
    could run concurrently;
- added `scripts/validation/run_ucpr_amazon_formal_pipeline.sh`;
- added `scripts/validation/launch_ucpr_amazon_formal_pipeline.sh`;
- formal-v1 training configuration:
  - dataset: `amazon_book_kgat_v1`;
  - runtime:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_runtime_formal`;
  - TransE: `30` epochs, embed size `100`, batch `512`, negative samples `5`;
  - policy: `40` epochs, batch `128`;
  - native beam tag: `25-5-1-ucpr-amazon-formal-e40`;
  - `UCPR_RUN_INFERENCE=0` by default;
- reason for deferring UCPR full-user inference/export:
  - UCPR's native test path, like the old PGPR path, writes a full
    `policy_paths` pickle before adapter export;
  - Amazon `70,591` test users with beam `25-5-1` can still produce
    multi-million path objects;
  - after the PGPR stale-run diagnosis, it is safer to complete UCPR formal
    training first and add/approve a memory-safe export path before enabling
    full-user inference/export;
- initial launch command:

```bash
UCPR_RUN_INFERENCE=0 UCPR_GPU=0 \
  bash scripts/validation/launch_ucpr_amazon_formal_pipeline.sh 0
```

- first run exposed an environment bug:
  - preprocessing succeeded, but the formal script called
    `validate_ucpr_preprocess_smoke.py` with `eval_frame` Python;
  - the UCPR pickle had been produced by the `rep` environment and failed to
    unpickle in `eval_frame` with `ModuleNotFoundError: No module named
    'numpy._core'`;
  - fix: run the UCPR preprocess validator with `REP_PY`, matching the
    environment that created the UCPR pickle;
- relaunched with the same command after the fix;
- current evidence:
  - tmux session: `ucpr_amazon_formal`;
  - status:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`;
  - log:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline.log`;
  - formal preprocess validation:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_preprocess_validation.json`;
  - formal preprocess status: `PASS`;
  - exact train/valid/test label round-trip remains true;
  - formal TransE training has started on GPU 0 and reached epoch `1`
    logging;
- current interpretation:
  - UCPR Amazon has moved from smoke-only readiness into an active formal
    training queue;
  - it remains not reportable because policy training, memory-safe full-user
    path export, strict export validation, and strict accuracy validation are
    not complete.

2026-06-29 11:31 +08 UCPR Amazon streaming exporter and policy-stage update:

- UCPR formal TransE training completed:
  - status summary:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_transe_formal_status.json`;
  - status: `PASS`;
  - best checkpoint:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_runtime_formal/data/amazon_book_kgat_v1/preprocessed/ucpr/tmp/train_transe_model_amazon_formal_e30_d100_b512_n5/transe_best_model.ckpt`;
  - embedding file:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_runtime_formal/data/amazon_book_kgat_v1/preprocessed/ucpr/tmp/transe_embed.pkl`;
- UCPR formal pipeline status advanced to:
  - `status=RUNNING`;
  - `stage=policy`;
  - policy run name: `train_agent_amazon_formal_e40_b128_d100`;
- added `scripts/validation/export_ucpr_streaming.py`;
- exporter design:
  - reuses UCPR's native `BatchKGEnvironment`, `UCPR` policy model, action
    probabilities, and TransE item score;
  - avoids the native full-user `policy_paths.pkl` and `pred_paths.pkl`
    accumulation;
  - streams raw candidate rows to a temporary CSV, normalizes native scores in
    a second pass, and keeps only per-user top-10 state in memory;
  - maps UCPR-local `product` paths back to canonical Amazon `book` paths via
    `user_remap.tsv` and `product_remap.tsv`;
- updated `scripts/validation/run_ucpr_amazon_formal_pipeline.sh`:
  - `UCPR_RUN_INFERENCE=1` now defaults to
    `UCPR_USE_STREAMING_EXPORT=1`;
  - legacy UCPR pickle inference/export remains available only by setting
    `UCPR_USE_STREAMING_EXPORT=0`;
- updated `scripts/validation/launch_ucpr_amazon_formal_pipeline.sh` to carry
  `UCPR_USE_STREAMING_EXPORT` into tmux;
- status/report refresh:

```bash
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

- validation result:
  - `canonical native-path report validation PASS`;
  - status matrix now records UCPR Amazon as
    `formal training pipeline status=RUNNING, stage=policy, beam=25-5-1,
    run_inference=0`;
- manifest note:
  - `export_ucpr_streaming.py` is now included in the artifact manifest;
  - the future formal streaming summary JSON is not listed as a required
    manifest input until it exists, because no full-user UCPR export has run
    yet;
- current interpretation:
  - UCPR Amazon is no longer blocked at TransE training;
  - it remains not reportable until policy training completes and the
    streaming full-user export plus strict validation/accuracy pass.

2026-06-29 11:40 +08 Amazon PGPR/UCPR live monitor and UCPR batch-size mitigation:

- live process check:
  - `tmux list-sessions` shows both `pgpr_amazon_formal` and
    `ucpr_amazon_formal`;
  - PGPR active child:
    `/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python
    scripts/validation/export_pgpr_streaming.py`;
  - UCPR active child:
    `/usr1/home/s125mdg43_08/miniconda3/envs/rep/bin/python train.py
    --dataset amazon_book_kgat_v1 --name train_agent_amazon_formal_e40_b32_d100
    --gpu 0 --epochs 40 --batch_size 32 ...`;
  - `nvidia-smi --query-compute-apps=pid,process_name,used_memory` reports the
    UCPR process using about `6150 MiB` on GPU 0;
- PGPR streaming export progress:
  - status file:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status remains `RUNNING`, `stage=inference_export`;
  - latest log progress observed:
    `processed_users=25600 raw_rows=1647159 candidate_users=25600`;
  - temporary raw stream:
    `xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-formal-e50_a250_beam10-12-1/pred_paths.raw.tmp.csv`;
  - observed line count: `1,647,156`;
  - strict final outputs are still absent:
    `pgpr_amazon_book_kgat_export_validation.json` and
    `pgpr_amazon_book_kgat_accuracy.json`;
- UCPR policy-stage mitigation:
  - the first policy attempt used the original formal default
    `train_agent_amazon_formal_e40_b128_d100`;
  - that attempt was observed to hit CUDA OOM during the policy optimizer
    step before the queue was relaunched;
  - `scripts/validation/run_ucpr_amazon_formal_pipeline.sh` was then changed
    to default `UCPR_POLICY_BATCH_SIZE` to `32` and export
    `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`;
  - relaunch command:

```bash
UCPR_RUN_INFERENCE=0 UCPR_POLICY_BATCH_SIZE=32 UCPR_GPU=0 \
  bash scripts/validation/launch_ucpr_amazon_formal_pipeline.sh 0
```

  - current UCPR status:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status was `RUNNING`, `stage=policy`, policy run
    `train_agent_amazon_formal_e40_b32_d100` at this checkpoint;
  - `ucpr_amazon_book_kgat_policy_formal_status.json`,
    `ucpr_amazon_book_kgat_streaming_export_formal.json`,
    `ucpr_amazon_book_kgat_export_validation.json`, and
    `ucpr_amazon_book_kgat_accuracy.json` are still absent;
- interpretation:
  - PGPR is actively producing the full-user candidate stream and is not
    stalled;
  - UCPR is past formal TransE and is actively training policy with a smaller
    memory envelope;
  - neither row is reportable yet, because neither has completed strict
    full-user export validation plus strict accuracy.

2026-06-29 11:46 +08 UCPR policy OOM root cause and second mitigation:

- the batch-32 UCPR policy attempt failed at the same policy training stage:
  - status:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status became `FAILED`, `stage=line_193`;
  - failing command was `train.py --dataset amazon_book_kgat_v1 --name
    train_agent_amazon_formal_e40_b32_d100 --gpu 0 --epochs 40 --batch_size
    32 ...`;
  - traceback showed the failure at `optimizer.step()` inside PyTorch Adam;
  - concrete error:
    `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 5.27 GiB`;
  - GPU 0 had about `2.05 GiB` free while the process held about `21.62 GiB`;
- diagnosis:
  - batch size contributed to the memory footprint, but the direct failure
    point was Adam's multi-tensor/`foreach` implementation materializing a
    large temporary tensor across UCPR's Amazon-scale parameter set;
  - therefore simply reducing from `128` to `32` was insufficient;
- code fix:
  - extended `scripts/model_patches/patch_ucpr_amazon_runtime.py` so the
    isolated Amazon UCPR runtime patches policy training from
    `optim.Adam(model.parameters(), lr=args.lr)` to
    `optim.Adam(model.parameters(), lr=args.lr, foreach=False)`;
  - this keeps Adam semantics but avoids the large multi-tensor temporary
    allocation in the first optimizer step;
  - changed `scripts/validation/run_ucpr_amazon_formal_pipeline.sh` default
    `UCPR_POLICY_BATCH_SIZE` from `32` to `16`;
- relaunch command:

```bash
UCPR_RUN_INFERENCE=0 UCPR_POLICY_BATCH_SIZE=16 UCPR_GPU=0 \
  bash scripts/validation/launch_ucpr_amazon_formal_pipeline.sh 0
```

- relaunch status:
  - tmux session: `ucpr_amazon_formal`;
  - pipeline pid: `232640`;
  - active Python child observed: `233217`;
  - run name: `train_agent_amazon_formal_e40_b16_d100`;
  - status: `RUNNING`, `stage=policy`;
  - GPU process memory observed around `5790 MiB`, far below the failed
    batch-32 process footprint;
- concurrent PGPR monitor:
  - PGPR streaming export remained active in tmux session
    `pgpr_amazon_formal`;
  - latest observed progress:
    `processed_users=30720 raw_rows=1959503 candidate_users=30720`;
- interpretation:
  - UCPR's current blocker is not data/schema/TransE; it is policy-training
    GPU memory on the larger Amazon KG;
  - the current b16 + scalar Adam run is the active attempt and has not yet
    produced a reportable policy checkpoint;
  - PGPR remains in full-user streaming export and still lacks final strict
    export/accuracy summaries.

2026-06-29 11:50 +08 post-mitigation monitor:

- UCPR:
  - `ucpr_amazon_formal` remains alive more than five minutes after the
    `foreach=False`/batch-16 relaunch;
  - active policy process:
    `train.py --dataset amazon_book_kgat_v1 --name
    train_agent_amazon_formal_e40_b16_d100 --gpu 0 --epochs 40 --batch_size
    16 ...`;
  - GPU memory observed around `5980 MiB`;
  - no new `torch.OutOfMemoryError` was present in the current tail of
    `results/amazon_book_kgat_v1/ucpr/eval/UCPR/train_log.txt`;
  - policy checkpoint summary is still absent, so UCPR remains not reportable;
- PGPR:
  - `pgpr_amazon_formal` remains alive;
  - latest streaming-export progress observed:
    `processed_users=33280 raw_rows=2113294 candidate_users=33280`;
  - final strict export validation and accuracy summaries are still absent.

2026-06-30 Amazon Book safety decision and current state:

- PGPR Amazon completed after the 2026-06-29 monitor:
  - pipeline status:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status: `PASS`, `stage=complete`;
  - strict export validation:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json`;
  - export validation status: `PASS`;
  - canonical test users / top-k users: `70,591` / `70,591`;
  - pred-path rows: `4,109,983`;
  - explanations: `705,846`;
  - strict accuracy:
    `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json`;
  - HR@10: `0.054851`;
  - NDCG@10: `0.015723`;
- UCPR Amazon batch-16 also failed:
  - status:
    `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_formal_pipeline_status.json`;
  - status: `FAILED`, `stage=line_193`;
  - failing command:
    `train.py --dataset amazon_book_kgat_v1 --name
    train_agent_amazon_formal_e40_b16_d100 --gpu 0 --epochs 40 --batch_size
    16 ...`;
  - failure remains at Adam `optimizer.step()`;
  - even with `foreach=False`, PyTorch single-tensor Adam attempted another
    `5.27 GiB` allocation while the process held about `21.56 GiB`;
- safety decision:
  - do not launch more Amazon Book classic-model training/export attempts by
    default;
  - keep the reportable Amazon Book evidence to the completed formal rows:
    KGGLM, PEARLM, and PGPR;
  - leave UCPR, CAFE, and TPRec as blocked until there is either a much smaller
    approved protocol or a dedicated high-memory server allocation;
- report refresh:

```bash
python3 scripts/analysis/validate_canonical_export_evidence.py --only amazon_book_kgat_v1:PGPR
bash scripts/analysis/regenerate_canonical_native_path_reports.sh --status-only
```

- refreshed report state:
  - status rows: `18`;
  - complete rows: `15`;
  - blocked rows: `3`;
  - export-validation manifest: `status=PASS`, `exports=15`;
  - Amazon formal comparison now includes KGGLM, PEARLM, and PGPR.

2026-07-01 strict PGPR/UCPR path-module ablation correction:

- corrected the PGPR/UCPR ablation protocol so `alpha=0` is strictly
  baseline-preserving:
  - the module now operates only on the frozen original top-k item set;
  - `alpha=0` exactly preserves both original top-k ranking and original
    explanation paths;
  - candidate-pool replacement items are excluded from the main ablation;
- switched the main ablation from legacy xrecsys alpha-sweep CSVs to a
  regenerated strict canonical sweep from frozen `uid_topk.csv`,
  `uid_pid_explanation.csv`, `pred_paths.csv`, export validation JSON, and
  strict accuracy JSON;
- added explicit validation artifact:
  `reports/tables/ablation/pgpr_ucpr_path_module/alpha0_baseline_preservation.csv`;
- validation result:
  - all `12/12` dataset-model-target alpha=0 checks are `PASS`;
  - exact top-k preservation is `100%`;
  - exact explanation-path preservation is `100%`;
  - max metric delta vs Original at alpha=0 is `0.0`;
- strict baseline accuracy now matches the validated accuracy JSON exactly:
  - LastFM PGPR NDCG@10: `0.03090466256434531`;
  - LastFM UCPR NDCG@10: `0.037376792696135475`;
  - ML-1M PGPR NDCG@10: `0.10189633102321971`;
  - ML-1M UCPR NDCG@10: `0.08621536338059343`;
- regenerated ablation outputs:
  - `reports/summaries/pgpr_ucpr_path_module_ablation.md`;
  - `reports/tables/ablation/pgpr_ucpr_path_module/main_ablation_table_95pct_ndcg.csv`;
  - `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_summary_95pct_ndcg.csv`;
  - `reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv`;
  - `reports/tables/ablation/pgpr_ucpr_path_module/endpoint_comparison.csv`;
  - `reports/tables/ablation/pgpr_ucpr_path_module/provenance_validation.csv`;
  - `reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg`;
  - `reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg`;
  - `reports/cases/ablation/pgpr_ucpr_path_module_cases.md`;
  - `reports/cases/ablation/pgpr_ucpr_path_module_cases.json`;
- Amazon-Book remains excluded from this ablation and is documented only as
  auxiliary large-dataset evidence from the main experiment.
