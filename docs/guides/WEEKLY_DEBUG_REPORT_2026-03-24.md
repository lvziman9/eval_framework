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

`VRKG4Rec` is not a native path-reasoning model in this setup. Its explanations are post-hoc.

The integration path is:

1. rank items from latent model outputs,
2. search for a path afterward,
3. convert the found path into `xrecsys` format,
4. then evaluate explanation metrics.

This differs from `PGPR`, where path reasoning is much closer to the model's original mechanism.


## VRKG4Rec Integration Risk 1: Candidate Pool Too Narrow

The main narrow-pool issue is in [vrkg4rec_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/vrkg4rec_adapter.py).

The adapter first truncates candidates to raw top-k items:

```python
top_item_ids = item_scores.topk(args.topk).indices.tolist()
```

Then it only tries to find explanation paths for those items.

This means:

- if some raw top-10 items have no valid path,
- the adapter does not backfill from item 11, 12, 13, ...
- so the final explainable top-k becomes shorter than 10.

This was not just inferred from code. It was validated empirically:

- original `VRKG4Rec` baseline full top-10 users: `13143`
- sandbox `cand50` full top-10 users: `14559`

So the baseline coverage gap was largely caused by the adapter's selection policy.


## VRKG4Rec Integration Risk 2: Ranking Semantics May Drift

Another risk in [vrkg4rec_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/vrkg4rec_adapter.py) is that the final `uid_topk` is not guaranteed to preserve the model's original ranking score semantics.

The adapter first selects items using model scores, but then best paths are scored and used in downstream export logic. This makes it possible for the exported top-k to reflect path scoring heuristics rather than the original recommender ranking alone.

This matters because recommendation metrics such as:

- `NDCG`
- `HR`
- `Recall`
- `Precision`

are only cleanly interpretable if the exported recommendation list still corresponds to the intended model ranking.


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
5. UCPR main training has been launched.

This matters because it shows we are no longer only debugging old results; we are also building the next path-reasoning baseline on our own dataset.

This part is still ongoing, so it should be presented as progress, not as a finished result.


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
- completing `UCPR` training and later integrating it into the same evaluation framework


## Related Documents

- [PROJECT_OVERVIEW.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PROJECT_OVERVIEW.md)
- [PIPELINE_RELIABILITY_LOG.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PIPELINE_RELIABILITY_LOG.md)
- [VRKG4REC_INTEGRATION_RISKS.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/VRKG4REC_INTEGRATION_RISKS.md)
- [LATENT_PATH_RETRIEVAL_PSEUDOCODE.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md)
