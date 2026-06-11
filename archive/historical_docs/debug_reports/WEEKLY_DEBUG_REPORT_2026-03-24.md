# Weekly Debug Report (2026-03-24)

## Scope

This week's work focused on debugging the explainability evaluation pipeline rather than adding a finished new model result.

The main question was:

- Why do the tradeoff figures change so dramatically?
- How much of that change comes from the model itself, and how much comes from the evaluation / integration pipeline?

The current answer is:

1. Some large figure changes are real metric tradeoffs.
2. Some large figure changes were caused by implementation issues in `xrecsys`.
3. Some large figure changes were caused by how `VRKG4Rec` was integrated into `xrecsys`.
4. `PGPR` is much more native to the `xrecsys` evaluation setting than `VRKG4Rec`, so its tradeoff plots are methodologically cleaner.


## What Was Fully Confirmed

The following points have already been verified with code review and/or rerun comparisons.

1. `xrecsys` really runs one optimization per `alpha` during alpha sweep.
2. The plotting script does not rerun optimization; it only reads the saved CSV.
3. Old `ETD-family` optimization code had a top-k collapse bug.
4. That `ETD-family` bug materially changed both `VRKG4Rec` and `PGPR` results.
5. `VRKG4Rec` baseline coverage was already incomplete before tradeoff optimization.
6. The main `VRKG4Rec` baseline coverage issue came from a too-narrow candidate pool in the adapter.
7. `PGPR` is much more naturally aligned with `xrecsys` than `VRKG4Rec`.


## End-to-End Pipeline

The current tradeoff pipeline is:

1. Generate `pred_paths.csv`, `uid_topk.csv`, `uid_pid_explanation.csv`.
2. Run `xrecsys/main.py` with `alpha=-1`.
3. `xrecsys/main.py` loops over all alpha values and writes `*_moving_alpha_avg.csv`.
4. `scripts/analysis/tradeoff_analyzer.py` reads the saved CSV and draws the figure.

This means:

- The figure itself is a static visualization.
- The points inside the figure come from a real alpha sweep that was already executed earlier.


## How Tradeoff CSVs Are Actually Generated

The key logic is in [main.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/main.py).

When `alpha == -1`, `xrecsys` explicitly expands the sweep:

```python
if args.alpha == -1:
    alphas = [0, 0.05, 0.1, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
              0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90,
              0.95, 1.0]
```

Then it loops over each alpha and reruns optimization:

```python
for alpha in alphas:
    path_data = build_path_data(args)
    run_alpha_optimization(path_data, chosen_optimization, alpha)

    rec_metrics_after = measure_rec_quality(path_data)
    exp_metrics_after, distributions_exp_metrics_after = compute_exp_metrics(path_data)
```

Finally, it writes one row per metric per alpha into `*_moving_alpha_avg.csv`:

```python
writer.writerow([alpha, metric_name, group_name, safe_mean(value), chosen_optimization])
```

So the correct interpretation is:

- `main.py` really ran the optimization for each alpha.
- The saved CSV is the output of those runs.
- The figure is a later visualization of those saved outputs.


## How Figures Are Actually Drawn

The plotting script is [tradeoff_analyzer.py](/usr1/home/s125mdg43_08/eval_framework/scripts/analysis/tradeoff_analyzer.py).

It chooses the relevant CSV file by explanation metric:

```python
OPT_FILE = {
    'LIR': 'LIRopt_moving_alpha_avg.csv',
    'SEP': 'SEPopt_moving_alpha_avg.csv',
    'ETD': 'ETDopt_moving_alpha_avg.csv',
}
```

Then it simply reads the CSV:

```python
csv_path = result_dir / OPT_FILE[exp_metric]
df = pd.read_csv(csv_path)
overall = df[df['group'] == 'Overall'].copy()
pivot = overall.pivot_table(index='alpha', columns='metric', values='data', aggfunc='first')
```

And draws curves directly from the dataframe:

```python
ax_abs.plot(df[exp_col], df[rec_metric], color=color, linewidth=2.5, label=METRIC_DISPLAY[rec_metric])
```

The relative-change panel is also computed only from CSV values:

```python
rec0 = df[rec_metric].iloc[0]
rec_delta = (df[rec_metric] - rec0) / (abs(rec0) + 1e-9) * 100
ax_rel.plot(df['alpha'], rec_delta, color=color, linewidth=2.5, label=METRIC_DISPLAY[rec_metric])
```

So the plotting script does not perform reranking or metric recomputation.


## Why the Old ETD-Family Results Were Unreliable

The key issue was in [optimizations.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/optimizations.py).

The old `ETD-family` logic prioritized type diversity first, but it could stop early before refilling the list back to top-k.

The problematic structure was effectively:

```python
while len(best_candidates) < 10:
    ...
    if best_type is None:
        break
```

This means:

- if no new type bucket could provide a fresh item,
- optimization stopped,
- even if there were still remaining valid candidates.

That caused:

1. many users to fall below top-10,
2. many users to be dropped from rec metrics,
3. tradeoff curves to reflect a changed evaluation population.

This was not just a theoretical concern. It was validated by reruns:

- `VRKG4Rec` changed materially after the refill fix,
- `PGPR` also changed materially after the refill fix.

So the old `ETD-family` figures should be treated cautiously.


## Why VRKG4Rec Was More Fragile

`VRKG4Rec` is not a native path-reasoning model in this setup. Its explanations are post-hoc, and the adapter has to construct a representative path after recommendation has already happened.

The effective logic in [vrkg4rec_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/vrkg4rec_adapter.py) is:

1. compute user-item scores from latent embeddings,
2. keep only raw top-k items,
3. search short 2-hop / 3-hop paths for those items,
4. convert valid paths to `xrecsys` format,
5. keep one best path per item,
6. export `uid_topk.csv` and `uid_pid_explanation.csv`.

This is qualitatively different from `PGPR`, where the path is much closer to the model's own reasoning process.

A key snippet is the adapter's retrieval stage:

```python
u_emb = user_gcn_emb[vrkg_uid].unsqueeze(0)
item_scores = _torch.matmul(u_emb, all_item_emb.t()).squeeze(0)
for ti in train_items_set:
    if ti < n_items:
        item_scores[ti] = float('-inf')
top_item_ids = item_scores.topk(args.topk).indices.tolist()

for target_entity_id in top_item_ids:
    paths = find_paths_for_item(...)
```

So the adapter first chooses items from latent scores, and only afterward tries to recover explanation paths.


## VRKG4Rec Integration Risk 1: Candidate Pool Too Narrow

The most important baseline coverage issue came from the fact that the adapter only searched for explanations inside raw top-k items.

The relevant snippet is:

```python
top_item_ids = item_scores.topk(args.topk).indices.tolist()

for target_entity_id in top_item_ids:
    paths = find_paths_for_item(
        vrkg_uid, target_entity_id, rev_adj,
        train_items_set, entity_gcn_emb,
        item_etype, lookups, args.topk_paths)
```

That means the old policy was effectively:

- raw top-10 item window
- then explanation search only inside that window
- no backfilling from item 11, 12, 13, ... if explanation search failed

This is exactly why a user could have:

- a valid recommender top-10 from the latent model,
- but fewer than 10 explainable exported items in `xrecsys`.

This was then validated experimentally:

- original `VRKG4Rec` baseline full top-10 users: `13143`
- sandbox `cand50` full top-10 users: `14559`

So the large baseline coverage gap was not just a vague hypothesis; it was directly tied to the adapter's candidate-selection policy.


## VRKG4Rec Integration Risk 2: Path Construction Is Heuristic

The adapter does not recover a native reasoning path from the model. Instead, it enumerates short reverse-KG paths and scores them heuristically.

The path search itself is here:

```python
for (b_entity, b_etype, b_lid) in rev_adj.get(target_entity_id, []):
    ...
    if b_etype == item_etype and b_entity in train_items_set:
        score = cosine(seed, target)
        paths.append(([vrkg_uid, b_entity, target_entity_id], score))
    ...
    for (s_entity, s_etype, s_lid) in rev_adj.get(b_entity, []):
        if s_etype == item_etype and s_entity in train_items_set:
            score = (cosine(seed, bridge) + cosine(bridge, target)) / 2.0
            paths.append(([vrkg_uid, s_entity, b_entity, target_entity_id], score))
```

This means the explanation path is not selected because the original VRKG model explicitly traversed that path. It is selected because:

- the item was first recommended by the latent model,
- then a short path was found in the KG,
- then that short path received a good heuristic similarity score.

So the explanation remains analyzable, but it should be interpreted as post-hoc explanation quality rather than native path-reasoning fidelity.


## VRKG4Rec Integration Risk 3: Ranking Semantics May Drift

Another risk is that the final exported `uid_topk` can drift away from the recommender's original ranking semantics.

After path conversion, the adapter groups by item and keeps only the best-scoring path per item:

```python
pid_best = {}
for (pid, score, path_nodes) in user_raw:
    path_str = convert_path(...)
    if path_str:
        if pid not in pid_best or score > pid_best[pid][0]:
            pid_best[pid] = (score, path_str)
    else:
        if pid not in pid_best or score > pid_best[pid][0]:
            pid_best[pid] = (score, None)

items_scored = sorted(pid_best.items(), key=lambda kv: kv[1][0], reverse=True)
top_items = items_scored[:args.topk]
uid_topk[xuid] = [p for p, _ in top_items]
uid_pid_best[xuid] = {p: ps for p, (_, ps) in top_items if ps is not None}
```

So the final exported ranking is no longer just “the original latent model's item ranking”. It becomes:

- latent model ranking to define a narrow candidate set,
- then path-level heuristic scoring to decide best path per item,
- then item export based on that path score grouping.

This matters because recommendation metrics such as:

- `NDCG`
- `HR`
- `Recall`
- `Precision`

are only fully clean when the exported top-k still clearly corresponds to the intended recommendation ranking semantics.


## What We Previously Did, and Why It Became a Risk

The original VRKG integration was a reasonable first bridge into `xrecsys`: use the latent model to recommend items, then recover short KG paths so that `LIR`, `SEP`, and `ETD` can be computed.

However, once the figures started changing sharply, the code review showed that this bridge had three important assumptions built into it:

1. raw top-k is a sufficient search window,
2. short reverse-KG path search is a good enough explanation proxy,
3. exporting one best path per item does not significantly alter ranking semantics.

The debugging work this week showed that those assumptions are not harmless. They are exactly where the current `VRKG4Rec` evaluation becomes fragile.


## VRKG4Rec Integration Risk 4: Not Every Found Graph Path Becomes a Valid xrecsys Path

A second hidden source of fragility is that even when the adapter finds a graph path, that path must still satisfy `xrecsys` format constraints before it can be used.

The key conversion logic is in [vrkg4rec_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/vrkg4rec_adapter.py):

```python
def convert_path(path_nodes, vrkg_uid, xrecsys_uid, dataset, lookups, kg_G):
    n = len(path_nodes)
    if n < 3 or n > 4:
        return None
    ...
    if n == 4:
        ...
        if e1_etype != item_etype:
            return None
        rel2 = find_relation(...)
        rel3 = find_relation(...)
        if rel2 is None or rel3 is None:
            return None
    else:  # n == 3
        ...
        if e1_etype != item_etype:
            return None
        rel2 = find_relation(...)
        if rel2 is None:
            return None
```

So even if the reverse-KG search finds a path in graph space, that path is discarded unless it also satisfies the `xrecsys` structural template.

This matters because the user-facing symptom can look like:

- “the graph has a path”
- but the exported explanation is still missing

In practice, this means `VRKG4Rec` explainability here is constrained not just by graph reachability, but also by path-template compatibility.


## Why This Directly Affects the Figures

The effect on final tradeoff plots is amplified by the recommendation-metric filtering logic in [metrics.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/metrics.py):

```python
def measure_rec_quality(path_data):
    ...
    topk_matches = path_data.uid_topk
    test_labels = path_data.test_labels
    ...
    for uid in test_user_idxs:
        if uid not in topk_matches: continue
        if len(topk_matches[uid]) < 10:
            invalid_users.append(uid)
            continue
```

So once the exported top-k becomes shorter than 10, that user is removed from rec-metric aggregation entirely.

This is the key bridge between adapter behavior and figure instability:

1. narrow candidate pool or failed path conversion shortens exported top-k,
2. short exported top-k removes the user from rec metrics,
3. the evaluation population changes,
4. the resulting tradeoff curve can shift for implementation reasons rather than pure model reasons.

This is why the `VRKG4Rec` debug work had to inspect both:

- adapter-side path generation, and
- metric-side user filtering.


## Why PGPR Is a Better Baseline for xrecsys

`PGPR` is much more naturally aligned with `xrecsys`.

Reason:

- `PGPR` is already a path-reasoning model,
- `xrecsys` explanation metrics are designed for path-structured explanations,
- `PGPR` does not require a strong post-hoc path construction step to enter the evaluation framework.

So for `PGPR`, the tradeoff design is methodologically much more reasonable.

That does not mean the implementation was perfect everywhere. It means the baseline semantics are much cleaner than for `VRKG4Rec`.


## PGPR Adapter Review: What Was Checked

Although `PGPR` is already a native `xrecsys` baseline, [pgpr_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/pgpr_adapter.py) was still reviewed to check whether it faithfully matches the original internal export logic.

### Difference 1: path score definition

Current adapter uses:

```python
score = sum(prob_list)
```

Whereas original internal PGPR logic in [test_agent.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/test_agent.py) uses:

```python
path_score = scores[uid][pid]
```

This means:

- current adapter is closer to a policy-probability scoring view,
- original PGPR export is closer to a user-item recommendation score view.

### Difference 2: final top-k tie-breaking

Current adapter sorts by a single best-path score:

```python
items_scores.sort(key=lambda x: x[1], reverse=True)
```

Original PGPR internal logic uses a richer sort criterion:

```python
best_pred_paths[uid].sort(key=lambda x: (x[0], x[1]), reverse=True)
```

So the current adapter is not a 100% strict clone of the original internal export logic.

### Overall review conclusion

No major structural baseline failure was found for `PGPR`, unlike `VRKG4Rec`.

The correct summary is:

- `PGPR` remains a trustworthy baseline for `xrecsys`.
- `pgpr_adapter.py` is not completely identical to the original internal PGPR export path.


## Why the Figures Look Different Across Metrics

### SEP

`SEP` is a local path-level property. It mainly depends on the bridge entity's popularity / rarity.

So in the current setting:

- optimization signal is smoother,
- curves are easier to interpret,
- plots tend to look more stable.

This is why the `SEP` plots are the cleanest.

### LIR

`LIR` often changes the explanation anchor more than it changes the hit set.

So:

- explanation quality can move,
- while recommendation ranking quality moves less.

This makes `LIR-NDCG` style plots look flatter.

### ETD

`ETD` is a set-level metric, not a local path-level metric.

To improve it, the optimization often has to alter the type composition of the whole top-k list.

That makes it:

- inherently more sensitive,
- more dependent on stable top-k construction,
- more vulnerable to implementation bugs such as early stopping / no refill.

That is why `ETD` plots are the easiest to distort.


## Answer 1: Why Did ETD Suddenly Change by ~200%?

This question refers to the relative-change panel, not just the absolute tradeoff panel.

The reason is mainly:

- baseline `ETD` was small,
- so a moderate absolute increase becomes a very large percentage increase.

Example from PGPR ETD data:

- baseline `ETD` was about `0.120`
- high-alpha `ETD` rose to about `0.359`

Absolute increase:

- about `+0.239`

Relative increase:

- about `0.239 / 0.120 ≈ 198%`

So the correct interpretation is:

- the absolute change is real,
- the `200%` appearance is amplified by a small baseline.

This is a property of percentage visualization, not necessarily a sign of numerical explosion.


## Answer 2: Why Did LIR Suddenly Drop?

More precisely, what suddenly dropped was usually the recommendation metric, not `LIR` itself.

The mechanism is:

1. For moderate alpha, ranking still retains some original recommendation score.
2. At `alpha=1`, the optimization may become pure explanation-priority ranking.
3. Once the recommendation score no longer stabilizes the list, top-k composition can shift abruptly.

So the typical pattern is:

- `LIR` improves steadily,
- recommendation metrics change slowly for a while,
- then recommendation metrics drop sharply near pure explanation-only ranking.

This is best understood as a mechanism change at extreme alpha, not as a plotting artifact.


## Are the Pareto / Tradeoff Plots Poor Because of Too Few Points?

Mostly no.

The current alpha sweep already uses:

- `0, 0.05, ..., 1.0`

That gives 21 points, which is already enough to show trend shape.

So when a plot looks strange, the main reason is usually not:

- too few sample points

but rather:

- unstable evaluation population,
- unstable top-k construction,
- metric-specific sensitivity,
- or implementation problems.

For `PGPR`, the design is more reasonable.
For `VRKG4Rec`, the same plot type is more fragile because the explanation object is post-hoc and the candidate-selection mechanism is weaker.


## Current Figure Generation Setup

The refined plotting setup now prioritizes:

- single model,
- multiple recommendation metrics,
- one explanation metric at a time.

This was chosen because it is easier to interpret than mixing model differences and metric differences in the same figure.

Current formal outputs:

- [tradeoff_lastfm_PGPR_SEP.png](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_SEP.png)
- [tradeoff_lastfm_PGPR_LIR.png](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_LIR.png)
- [tradeoff_lastfm_PGPR_ETD.png](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_ETD.png)

The corresponding tables are:

- [tradeoff_lastfm_PGPR_SEP.csv](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_SEP.csv)
- [tradeoff_lastfm_PGPR_LIR.csv](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_LIR.csv)
- [tradeoff_lastfm_PGPR_ETD.csv](/usr1/home/s125mdg43_08/eval_framework/reports/figures/tradeoff/tradeoff_lastfm_PGPR_ETD.csv)


## Why We Are Not Treating VRKG4Rec and PGPR in the Same Way

This is an important reporting point.

`PGPR`:

- is already a path-based baseline within `xrecsys`,
- explanation paths are much closer to original model reasoning.

`VRKG4Rec`:

- is a latent GNN model,
- current explanation path is post-hoc,
- explanation quality is therefore analysis of a constructed path, not direct analysis of native reasoning.

So even if both are evaluated by `xrecsys`, they are not equally natural citizens of the framework.


## Latent GNN Handling Direction

For latent GNN models such as:

- `VRKG4Rec`
- `KGIN`

the current conclusion is that explanation should not rely on arbitrary post-hoc path picking.

The better direction is:

- latent-consistent path retrieval

That means:

1. use the user-item latent signal from the model,
2. enumerate short KG candidate paths,
3. retrieve the path most consistent with that latent signal,
4. convert it into `xrecsys` path format for evaluation.

This idea has already been recorded in:

- [LATENT_PATH_RETRIEVAL_PSEUDOCODE.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md)


## New Model Progress: UCPR

This week did not end with a finished new-model result, but the pipeline was pushed much further.

`UCPR` progress currently is:

1. external repo located and prepared,
2. our own `lastfm` converted into UCPR-compatible format,
3. UCPR preprocess finished,
4. TransE pretraining finished,
5. UCPR main training has been completed,
6. native UCPR recommendation evaluation has been repaired and run successfully,
7. a first `UCPR -> xrecsys` adapter has been written,
8. explainability-style baseline export into `xrecsys` has been made runnable.

This matters because it shows we are no longer only debugging old results; we are also building the next path-reasoning baseline on our own dataset.

This part is still ongoing, so it should be presented as progress, not as a fully aligned final result.


## UCPR: What Is Already Working

The following parts are now confirmed to run:

1. `UCPR` training on our converted `lastfm`,
2. native recommendation evaluation from `test.py`,
3. path export files such as `policy_paths_epoch30_.pkl`,
4. `pred_paths.pkl` extraction,
5. a first adapter export into `xrecsys` CSV format.

The native recommendation metrics obtained from the repaired `UCPR test.py` path are:

- `NDCG = 0.0903`
- `HR = 0.1684`
- `Precision = 0.0229`
- `Recall = 0.0090`

This is important because it shows the model itself is not failing silently; it can be trained and evaluated on our converted dataset.


## UCPR: What Was Repaired in Native Evaluation

The native `UCPR` evaluation did not run cleanly at first. It had to be repaired in a few small but real places:

1. a boolean was accidentally called like a function,
2. `test-only` users caused `KeyError` during evaluation,
3. `np.asfarray(...)` was incompatible with the current NumPy version,
4. traceback visibility was too weak to see the real error source.

The repaired examples in [test.py](/usr1/home/s125mdg43_08/rep-path-reasoning-recsys/models/UCPR/test.py) include:

```python
if args.save_paths or args.run_eval:
```

and:

```python
train_pids = set(train_labels.get(uid, []))
```

These changes are best interpreted as runtime / compatibility fixes, not as method changes.


## UCPR Adapter Review: What Was Confirmed

The first `UCPR` adapter was written to export:

- `pred_paths.csv`
- `uid_topk.csv`
- `uid_pid_explanation.csv`

into the standard `xrecsys` path folder layout.

The most important review result is that the adapter does **not** appear to distort native `UCPR` ranking semantics.

Native `UCPR` ranking logic was reconstructed from `pred_paths.pkl` as:

- for each `(uid, pid)`, keep the path with highest `path_prob`,
- rank items by `(path_score, path_prob)` descending.

The adapter export was checked against this reconstruction, and the result was:

- `checked users = 14620`
- `mismatches = 0`

So the current conclusion is:

- the adapter is already faithful to native top-k ordering,
- the major remaining issue is not top-k sorting drift.


## Why Three CSVs Are Necessary but Not Sufficient

This is a key design point for the next phase.

The three exported CSVs:

- `pred_paths.csv`
- `uid_topk.csv`
- `uid_pid_explanation.csv`

solve the **model-output interface** problem. They tell `xrecsys`:

- which items were recommended,
- which paths explain those items,
- and which explanation is selected per `(uid, pid)`.

However, recommendation metrics such as:

- `NDCG`
- `HR`
- `Recall`
- `Precision`

also require a **truth space**:

- which users belong to the evaluation set,
- which test items are ground truth for each user,
- which train items should be filtered out.

So the correct separation is:

1. the three CSVs unify **prediction outputs**,
2. the label files unify **evaluation targets**.

This is why “just exporting the three CSVs” is enough to plug a model into the framework, but not always enough to guarantee cross-model comparability.


## Why UCPR xrecsys Rec Metrics Are Still Too Low

The current `UCPR -> xrecsys` baseline run produced recommendation metrics that are much lower than native `UCPR` metrics.

This initially looked like an adapter failure, but the ranking review above showed that the adapter is already faithful to native top-k ordering.

The stronger current explanation is:

- there is a **label / user-space mismatch** between the current `UCPR` export and the label space that `xrecsys` is using for metric computation.

Observed facts:

- adapter-exported users: `14620`
- `PGPR tmp/lastfm/test_label.pkl` users: `14642`
- intersection: only `9394`

So the remaining problem is not simply:

- “adapter generated the wrong top-k”

but rather:

- “different models are not yet being judged against exactly the same answer sheet.”


## Why Canonical Labels Are the Next Step

The purpose of canonical labels is **not** to replace the three CSV interface.

Instead, canonical labels create a shared evaluation layer:

- one agreed train-label space,
- one agreed test-label space,
- one agreed filtering policy,
- one agreed user/item truth set.

So the clean conceptual split becomes:

1. adapters standardize what models **predict**,
2. canonical labels standardize how those predictions are **judged**.

This is actually lower coupling than letting each model silently depend on a different historical label source.


## Why We Plan to Start Canonical Labels with PGPR and UCPR

We do **not** need to force all models into canonical labels at once.

The current best next step is:

1. generate canonical labels for `lastfm`,
2. use them first for `PGPR` and `UCPR`,
3. test whether those two path-reasoning models become directly comparable in recommendation metrics.

This is a good middle ground because:

- `PGPR` and `UCPR` are more similar model families,
- both naturally produce path-based recommendation outputs,
- the engineering cost is much lower than trying to align `VRKG4Rec` at the same time.

If this works well, the same canonical evaluation layer may later be reused for `VRKG4Rec` recommendation metrics, even if its explanation-generation policy still needs separate handling.


## Current Recommendation for the Next Phase

The current best next step is:

1. record the current `UCPR` pipeline state,
2. generate `PGPR + UCPR` canonical labels from the same raw `lastfm` split,
3. make `xrecsys` label loading configurable rather than hardcoded to the `PGPR tmp` directory,
4. rerun baseline recommendation metrics for both models under the same canonical truth space,
5. only then decide whether the resulting figures are ready for direct model comparison.


## Canonical Labels: Corrected Implementation Result

The low-coupling canonical-label implementation has now been added and corrected once after a field-semantics review.

### What was implemented

1. a generator script:
   - [generate_canonical_labels.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/generate_canonical_labels.py)
2. a label-override entry point in `xrecsys`:
   - [main.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/main.py) now accepts `--labels_dir`
   - [myutils.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/myutils.py) now resolves `train_label.pkl` / `test_label.pkl` from that override directory
   - [path_data_loader.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/path_data_loader.py) now passes the override into label loading

This is low-coupling because:

- existing default behavior is unchanged,
- historical runs still use the old hardcoded `PGPR tmp` labels,
- only runs that explicitly pass `--labels_dir` switch to the canonical truth space.

### What canonical labels were generated from

The corrected canonical labels are generated directly from:

- `xrecsys/datasets/lastfm/train.txt.gz`
- `xrecsys/datasets/lastfm/test.txt.gz`
- `user_mappings.txt`
- `product_mappings.txt`

with the following corrected rule:

1. map raw user ids into the xrecsys internal user space,
2. keep the product column as xrecsys internal `kgid` (because `train/test.txt.gz` already store product ids in that space),
3. only filter out products that are not valid xrecsys products.

The corrected generated summary was:

- `train_users = 15472`
- `train_kept_interactions = 3238575`
- `train_skipped_product_interactions = 14312611`
- `test_users = 14642`
- `test_kept_interactions = 713959`
- `test_skipped_product_interactions = 3681687`

So the canonical test set matches the previously observed filtered raw `lastfm` test scale.

This correction was important because an earlier draft mistakenly treated the product column in `train/test.txt.gz` as a raw external product id. After fixing that assumption, the canonical labels aligned exactly with the `UCPR` converted `test.txt.gz` once both were mapped into the same compact UCPR space.


## Canonical Labels: Corrected Baseline Comparison

Using copied path folders with `-canonical` suffix and `--labels_dir`, a corrected same-truth-space baseline comparison was run for both `PGPR` and `UCPR`.

### PGPR baseline

Historical baseline:

- `NDCG = 0.08596`
- `HR = 0.18183`
- `Recall = 0.01042`
- `Precision = 0.02694`

Corrected canonical-label baseline:

- `NDCG = 0.00234`
- `HR = 0.00439`
- `Recall = 0.000086`
- `Precision = 0.000439`

Interpretation:

- `PGPR` collapses under the corrected canonical labels,
- this means the currently stored `PGPR` artifacts are not aligned with the same raw `lastfm` truth space as the corrected canonical labels,
- in other words, the historical `PGPR tmp` label space is not the same as the raw-split truth space we want for direct cross-model comparison.

### UCPR baseline

Previous xrecsys baseline:

- `NDCG = 0.00070`
- `HR = 0.00100`
- `Recall = 0.000052`
- `Precision = 0.000100`

Corrected canonical-label baseline:

- `NDCG = 0.09905`
- `HR = 0.16891`
- `Recall = 0.00860`
- `Precision = 0.02270`

Interpretation:

- corrected canonical labels restore `UCPR` to roughly the same scale as native `UCPR` evaluation,
- this means the earlier near-zero xrecsys rec metrics for `UCPR` really were caused by label-space mismatch,
- the `UCPR` adapter and export path now look much more trustworthy than before.


## Updated Reading of the Canonical-Label Situation

After the corrected canonical-label rerun, the current best summary is:

1. `UCPR` native evaluation works and gives reasonable recommendation metrics,
2. the first `UCPR` adapter preserves native top-k ordering,
3. corrected canonical labels repair the `UCPR` rec-metric collapse inside `xrecsys`,
4. `UCPR` now aligns much more closely with its native evaluation scale,
5. the current comparability problem has shifted to `PGPR`, whose historical artifact space does not match the corrected canonical truth space.

So the problem has become narrower:

- it is no longer “UCPR adapter may be wrong,”
- it is no longer “UCPR still cannot be judged in xrecsys,”
- it is now a more specific cross-model issue:
- `UCPR` can now be evaluated on the corrected canonical raw-split truth space,
- but the currently stored `PGPR` outputs appear to belong to a different label/split space,
- so direct `PGPR` vs `UCPR` figure comparison still requires one more alignment step.


## Root Cause: The Raw lastfm Split Does Not Behave Like One Clean Product-ID Space

The strongest current evidence is that `xrecsys/datasets/lastfm/train.txt.gz` and `test.txt.gz` do **not** behave like a single clean product-id space that both model pipelines interpret in the same way.

Two different historical assumptions were effectively used:

1. `PGPR preprocess.py` assumes the product column is a raw dataset product id and converts it through:

```python
id2kgid = get_product_id_kgid_mapping(dataset)
product_idx = int(arr[1])
if product_idx not in id2kgid:
    continue
user_products[user_idx].append(id2kgid[product_idx])
```

2. the first `UCPR` conversion path effectively treated the product column as already close to xrecsys internal product ids, and then only kept rows whose product existed in the contiguous song-id space used by the converter.

Once we measured the raw split directly against `product_mappings.txt`, the conflict became clear:

- train interactions total: `17,551,186`
- train items matching `kgid` interpretation: `2,789,195` (`15.89%`)
- train items matching raw-product-id interpretation: `3,238,575` (`18.45%`)
- train items matching both interpretations: `990,320` (`5.64%`)

- test interactions total: `4,395,646`
- test items matching `kgid` interpretation: `697,133` (`15.86%`)
- test items matching raw-product-id interpretation: `713,959` (`16.24%`)
- test items matching both interpretations: `215,571` (`4.90%`)

So the main issue is not simply:

- “UCPR adapter was wrong”

and not simply:

- “PGPR baseline was badly evaluated by xrecsys”

The deeper issue is:

- the current raw `lastfm` split files are being filtered through **different valid-subset interpretations** by different model pipelines.

That is why both of the following can be true at the same time:

1. `UCPR` now aligns perfectly with the corrected canonical labels built under its own valid-subset interpretation,
2. `PGPR` collapses under that same corrected canonical truth space.

This is not a contradiction; it is exactly what we would expect once two model families have historically been attached to different surviving subsets of the same raw split files.


## What the xrecsys Source Chain Actually Suggests

The `xrecsys` README itself already suggests that `lastfm` is not carried around as one single monolithic artifact. It asks users to download three separate bundles:

```md
You can download the preprocessed dataset directly from there: [preprocessed-datasets]
...
Precomputed Paths ... [LAST-FM]
...
Precomputed TransE embeddings, agent-policy and agent ckpt ... [LAST-FM]
```

So the intended reproduction setup is:

1. one preprocessed `datasets/lastfm` package,
2. one precomputed `paths/lastfm` package,
3. one `models/PGPR/tmp/lastfm` package.

This matters because the current local mismatch does **not** automatically mean the original author assets were wrong. A more careful reading is:

- the original Drive assets may have been self-consistent inside their own expected bundle,
- but our current local `datasets/lastfm`, `paths/lastfm`, and `tmp/lastfm` are no longer guaranteed to still share one unambiguous item-id interpretation.

There is also a local record pointing in the same direction. In [docs/plans/log.md](/usr1/home/s125mdg43_08/eval_framework/docs/plans/log.md), the note explicitly says:

```md
原作者预计算的 kg.pkl ... 与我们用 preprocess.py 重新生成的 ... 有差异，
路径 CSV 中的实体 ID 与原作者 kg.pkl 对应，因此使用原作者版本。
```

This is another sign that the repository already depended on multiple historical assets that had to be kept aligned carefully.


## One Hard Piece of Evidence: `tmp/lastfm` Uses `kgid`, While Raw Split Filtering Splits Into Two User Sets

After tracing the source chain, I checked the current local artifacts directly.

First, the historical `PGPR tmp/lastfm` item space is not arbitrary. The items stored in:

- [train_label.pkl](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/tmp/lastfm/train_label.pkl)
- [test_label.pkl](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/tmp/lastfm/test_label.pkl)

are a pure subset of the `kgid` column in:

- [product_mappings.txt](/usr1/home/s125mdg43_08/eval_framework/xrecsys/datasets/lastfm/mappings/product_mappings.txt)

and **not** a subset of the raw `lastfmid` column.

That means the current `tmp/lastfm` label pkls are definitely living in xrecsys internal product space.

Second, when I filtered the raw split by the two competing product-column interpretations, the surviving test-user counts matched the two model families we have been seeing:

- test users surviving `kgid` interpretation: `14620`
- test users surviving raw-product-id interpretation: `14642`

These two numbers are exactly the ones that kept reappearing in later debugging:

- `UCPR` export users: `14620`
- historical `PGPR tmp/lastfm/test_label.pkl` users: `14642`

So the current local evidence is now quite specific:

1. `tmp/lastfm` uses internal `kgid` item labels,
2. the raw split still admits two different valid filtering interpretations,
3. those two interpretations produce the two user-set sizes that later show up in `UCPR` and historical `PGPR` evaluation.

This is why I now treat the current problem as a **local asset-alignment issue**, not as proof that the original Google Drive PGPR bundle itself was invalid.


## Why Canonical-Compatible PGPR Is Not a One-Line Re-evaluation

I also checked whether the current local repository still has the intermediate PGPR artifacts needed to cheaply regenerate a new `lastfm` baseline under the corrected canonical truth space.

What is available locally:

- [xrecsys/models/PGPR/tmp/lastfm/train_label.pkl](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/tmp/lastfm/train_label.pkl)
- [xrecsys/models/PGPR/tmp/lastfm/test_label.pkl](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/tmp/lastfm/test_label.pkl)
- [xrecsys/models/PGPR/tmp/lastfm/transe_embed.pkl](/usr1/home/s125mdg43_08/eval_framework/xrecsys/models/PGPR/tmp/lastfm/transe_embed.pkl)
- precomputed exported path CSVs in [xrecsys/paths/lastfm/agent_topk=25-50-1](/usr1/home/s125mdg43_08/eval_framework/xrecsys/paths/lastfm/agent_topk=25-50-1)

What is **not** available locally for `lastfm`:

- no `policy_paths_epoch*.pkl`
- no visible `train_agent/` checkpoint directory
- no lastfm policy-model snapshot analogous to the available `ml1m` one

This matters because the current `uid_topk.csv` user set matches the historical `tmp/lastfm/test_label.pkl` **exactly**, not the regenerated `test_label.generated.pkl`:

- overlap with current `tmp` test labels: `14642 / 14642`
- overlap with regenerated test labels: `9368 / 14642`

So the currently stored PGPR path artifacts are clearly tied to the historical `tmp/lastfm` label space.

That means a true canonical-compatible PGPR rebuild is probably **not**:

- “just swap in new labels and re-evaluate”

It is more likely one of these:

1. recover the missing original PGPR policy / path-generation artifacts for `lastfm`,
2. or rerun PGPR path prediction from a compatible model checkpoint,
3. or retrain PGPR if those original inference artifacts are no longer available.


## Canonical Dataset Standard v1

To avoid hard-coding a one-off `lastfm` fix, I started moving this into a reusable canonical dataset layer.

The formal standard is now documented in:

- [CANONICAL_DATASET_STANDARD.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/CANONICAL_DATASET_STANDARD.md)

The key design rule is:

> Every model may use its own compact internal ids, but every exported recommendation and explanation path must map back to canonical `uid` / `pid` before `xrecsys` evaluation.

The required canonical layout is:

```text
canonical_datasets/{dataset_name}_v1/
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
```

This is meant to generalize beyond `lastfm`:

- `lastfm_v1` first,
- `ml1m_v1` next,
- `amazon_v1` later, after the Amazon KG/product schema is fixed.


## First Execution: `lastfm_v1`

I added a reusable builder:

- [build_canonical_dataset.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_canonical_dataset.py)

First trial output:

- [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1)

Configuration used:

```bash
python scripts/data/canonical/build_canonical_dataset.py \
  --name lastfm_v1 \
  --source-dataset-dir xrecsys/datasets/lastfm \
  --out-dir runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1 \
  --product-id-policy xrecsys_kgid \
  --valid-policy per_user_latest_one_from_train \
  --product-entity song \
  --domain music
```

Generated split statistics:

| split | interactions | users | products |
|---|---:|---:|---:|
| train | 2,773,892 | 15,476 | 9,334 |
| valid | 15,303 | 15,303 | 3,473 |
| test | 697,133 | 14,620 | 7,590 |

Sanity check passed:

- all interaction files use 4 tab-separated columns,
- `train_label.pkl` matches `train.tsv.gz`,
- `valid_label.pkl` matches `valid.tsv.gz`,
- `test_label.pkl` matches `test.tsv.gz`.

So the first reusable canonical dataset instance now exists. The next step is to build model-specific views from it:

1. `lastfm_v1 -> UCPR view`,
2. `lastfm_v1 -> PGPR view`,
3. train/evaluate both models,
4. export both back to canonical `xrecsys` CSVs.


## First Model View: `lastfm_v1 -> UCPR`

I also implemented the first model-specific view builder:

- [build_ucpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_ucpr_view.py)

Output:

- [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/ucpr](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/ucpr)

The UCPR view uses compact internal ids, but saves remap tables back to canonical ids:

- `user_remap.tsv`: `canonical_uid -> ucpr_uid`
- `product_remap.tsv`: `canonical_pid -> ucpr_product_idx`

Generated UCPR split statistics:

| split | rows | users | products | bad rows |
|---|---:|---:|---:|---:|
| train | 2,773,892 | 15,476 | 9,334 | 0 |
| valid | 15,303 | 15,303 | 3,473 | 0 |
| test | 697,133 | 14,620 | 7,590 | 0 |

Generated entity files:

| entity | count |
|---|---:|
| user | 15,552 |
| product | 47,981 |
| artist | 3,385 |
| engineer | 1,662 |
| producer | 2,429 |
| genre | 5 |

This confirms the first full canonical flow:

```text
xrecsys/datasets/lastfm
  -> lastfm_v1 canonical dataset
  -> UCPR compact model view
```

The next harder step is `lastfm_v1 -> PGPR`, because PGPR's original data loader assumes a particular raw-id-to-kgid mapping in `preprocess.py`. For the canonical version, we need either:

1. a small PGPR dataset/view adapter that treats canonical `pid` as already canonical kgid, or
2. a generated PGPR-compatible view whose mapping files make PGPR's original raw-id mapping resolve back to the same canonical ids.


## Second Model View: `lastfm_v1 -> PGPR`

I chose option 2 so we do not modify PGPR source code.

New builder:

- [build_pgpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_pgpr_view.py)

Output:

- [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/pgpr](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/pgpr)

Design:

- PGPR still sees `train.txt.gz` / `test.txt.gz` as three-column `uid pid timestamp` files.
- PGPR still applies its original `raw id -> kgid` mapping logic.
- The view makes that mapping identity-style:
  - `canonical_uid -> canonical_uid`,
  - `canonical_pid -> canonical_pid`.

So PGPR's loader can stay unchanged, while the semantic result remains canonical.

Validation result:

```text
identity_label_validation:
  train:
    canonical_users: 15476
    rebuilt_users: 15476
    exact_match: true
  test:
    canonical_users: 14620
    rebuilt_users: 14620
    exact_match: true
```

This is an important sanity check:

- if PGPR preprocess reads this view using its normal raw-id mapping logic,
- it should rebuild labels equal to `lastfm_v1/labels/train_label.pkl` and `lastfm_v1/labels/test_label.pkl`.

So we now have both:

```text
lastfm_v1 -> UCPR compact view
lastfm_v1 -> PGPR-compatible identity-mapping view
```

## Canonical Preprocess Smoke Test: PGPR and UCPR

I then ran both generated views through each model's own preprocessing code in isolated smoke directories.

PGPR smoke directory:

- [pgpr_smoke_clean_153822](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/pgpr_smoke_clean_153822)

UCPR smoke directory:

- [ucpr_smoke_153538](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/ucpr_smoke_153538)

PGPR command shape:

```bash
cd <pgpr_smoke>/models/PGPR
python preprocess.py --dataset lastfm
```

PGPR result:

```text
review size: 2773892
train exact match against canonical labels: true
test exact match against canonical labels: true
```

UCPR command shape:

```bash
cd <ucpr_smoke>/models/UCPR
PYTHONPATH=<ucpr_smoke> python preprocess.py --dataset lfm1m
```

UCPR result after mapping compact ids back to canonical ids:

```text
train exact match against canonical labels: true
valid exact match against canonical labels: true
test exact match against canonical labels: true
```

This is the first concrete evidence that the canonical data layer can support both model families without forcing PGPR or UCPR to share an internal id scheme. The shared contract is only at the input/output boundary:

- canonical interactions and labels define the truth space,
- model views may remap internally,
- exported recommendations and paths must map back to canonical uid/pid before `xrecsys` evaluation.

The remaining work is no longer the canonical data layer itself; it is the expensive model stage:

1. train or recover PGPR policy artifacts from the PGPR canonical view,
2. train or recover UCPR policy artifacts from the UCPR canonical view,
3. extract each model's paths,
4. export both models back to canonical uid/pid CSVs,
5. rerun xrecsys on canonical labels.


## Recommended Verbal Summary for Supervisor

The shortest accurate summary is:

1. I traced the dramatic figure changes back to multiple sources rather than a single model effect.
2. The biggest confirmed issues were an `ETD-family` optimization bug in `xrecsys` and a narrow candidate-pool policy in the `VRKG4Rec` adapter.
3. `PGPR` is methodologically much cleaner inside `xrecsys`, so its tradeoff curves are more meaningful as explanation-quality tradeoffs.
4. `VRKG4Rec` currently reflects post-hoc explanation quality, not native path reasoning quality.
5. I also refined the tradeoff plotting code so the figures now better expose different recommendation metrics in a single-model setting.


## What Is Done vs Still Ongoing

### Done

- alpha-sweep generation mechanism reviewed and confirmed
- tradeoff plotting mechanism reviewed and confirmed
- ETD-family bug identified, fixed, and validated
- VRKG4Rec integration risks reviewed and documented
- PGPR adapter reviewed relative to original baseline logic
- PGPR single-model tradeoff figures regenerated in clearer form

### Ongoing

- deciding whether `VRKG4Rec cand50` should become a formal mechanism or remain a variant
- implementing a stronger latent-consistent retrieval mechanism for latent GNN models
- finishing `UCPR` evaluation alignment after successful native training / native eval / adapter export
- designing and validating `PGPR + UCPR` canonical labels so cross-model figures can be compared on the same truth space


## Related Documents

- [PROJECT_OVERVIEW.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PROJECT_OVERVIEW.md)
- [PIPELINE_RELIABILITY_LOG.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PIPELINE_RELIABILITY_LOG.md)
- [VRKG4REC_INTEGRATION_RISKS.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/VRKG4REC_INTEGRATION_RISKS.md)
- [LATENT_PATH_RETRIEVAL_PSEUDOCODE.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md)
