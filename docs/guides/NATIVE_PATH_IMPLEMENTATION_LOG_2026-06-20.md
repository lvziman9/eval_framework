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
