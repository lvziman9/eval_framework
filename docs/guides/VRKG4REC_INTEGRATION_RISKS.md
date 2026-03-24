# VRKG4Rec Integration Risk Notes

This note focuses only on the **currently used integration path** in this repository:

`VRKG4Rec checkpoint -> adapters/vrkg4rec_adapter.py -> xrecsys CSVs -> xrecsys metrics`

It intentionally ignores older external interpretability experiments and concentrates on the parts that are most likely to introduce large errors into the current evaluation pipeline.

## 1. Ranking Semantics May Already Be Changed Before Evaluation

### Why this is risky

The adapter first uses the model's item scores only to get a small candidate set, but it does **not** preserve the model's original ranking when writing the final `uid_topk.csv`.
Instead, it re-sorts items by the adapter's own path score.

That means the recommendation metrics computed by xrecsys may no longer correspond to the original VRKG4Rec ranking.

### Current code

From [adapters/vrkg4rec_adapter.py](/usr1/home/s125mdg43_08/eval_framework/adapters/vrkg4rec_adapter.py):

```python
u_emb = user_gcn_emb[vrkg_uid].unsqueeze(0)
item_scores = _torch.matmul(u_emb, all_item_emb.t()).squeeze(0)
top_item_ids = item_scores.topk(args.topk).indices.tolist()
```

This looks correct at first: the adapter starts from the model's recommendation score.

But later it writes the final top-k using a different score source:

```python
items_scored = sorted(pid_best.items(),
                      key=lambda kv: kv[1][0], reverse=True)
top_items          = items_scored[:args.topk]
uid_topk[xuid]     = [p for p, _ in top_items]
```

And `pid_best[pid][0]` comes from path scoring here:

```python
score = (_F.cosine_similarity(
             s_emb.unsqueeze(0), b_emb.unsqueeze(0)).item()
         + _F.cosine_similarity(
             b_emb.unsqueeze(0), target_emb.unsqueeze(0)).item()
         ) / 2.0
```

### Why this is likely wrong

If the goal is to evaluate **VRKG4Rec's original recommendation quality plus explanation quality**, then the final ranking should still reflect the model's original item ranking.

Right now the pipeline is closer to:

- get candidate items from VRKG4Rec,
- score paths with adapter logic,
- re-rank items by path score,
- then evaluate recommendation quality.

So the current `NDCG / HR / Recall / Precision` are very likely measuring a **hybrid ranking**, not the original VRKG4Rec ranking.

## 2. Items Without Explanations Can Still Enter `uid_topk`

### Why this is risky

The adapter can keep an item in `uid_topk.csv` even when path conversion fails and no explanation is written to `uid_pid_explanation.csv`.

This creates a mismatch:

- recommendation metrics still see the item,
- explanation metrics do not.

So the recommendation and explanation parts of the evaluation are no longer computed on exactly the same recommendation set.

### Current code

```python
path_str = convert_path(path_nodes, vrkg_uid, xuid, dataset, lookups, kg_G)
if path_str:
    pred_rows.append((xuid, pid, norm, -1, path_str))
    if pid not in pid_best or score > pid_best[pid][0]:
        pid_best[pid] = (score, path_str)
else:
    skipped_convert += 1
    if pid not in pid_best or score > pid_best[pid][0]:
        pid_best[pid] = (score, None)
```

Then later:

```python
uid_topk[xuid]     = [p for p, _ in top_items]
uid_pid_best[xuid] = {p: ps for p, (_, ps) in top_items if ps is not None}
```

### Why this is likely wrong

This means an item can appear in the final recommendation list while having no explanation path in the explanation file.

Under that condition:

- rec metrics and exp metrics are no longer aligned,
- explanation coverage is artificially lower than recommendation coverage,
- downstream tradeoff interpretation becomes harder to trust.

## 3. The Candidate Pool Is Probably Too Narrow

### Why this is risky

The adapter currently takes only the model's raw top-10 items and tries to find valid paths for those items.
If some of those 10 items have no valid explanation path, the adapter does **not** backfill with lower-ranked explainable items.

That means the baseline itself starts with a coverage defect.

### Current code

```python
top_item_ids = item_scores.topk(args.topk).indices.tolist()

user_raw = []
for target_entity_id in top_item_ids:
    paths = find_paths_for_item(
        vrkg_uid, target_entity_id, rev_adj,
        train_items_set, entity_gcn_emb,
        item_etype, lookups, args.topk_paths)
```

### Why this is likely wrong

This makes the adapter behave like:

- `raw top10 -> keep only explainable survivors`

instead of something closer to:

- `larger candidate pool -> choose final explainable top10`

We already validated this risk empirically.
Using a sandbox variant with `candidate_topk=50` while still outputting final top-10:

- original `full_topk_users = 13143`
- sandbox `full_topk_users = 14559`
- net `+1416`

So the current baseline shortfall is very likely dominated by candidate-pool policy, not by CSV writing noise.

See also:
- [coverage_summary.md](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-03-24_vrkg_adapter_pool/results/coverage_summary.md)

## 4. Why These Three Risks Matter More Than Older External Notes

These risks affect the pipeline **before** xrecsys computes the final metrics.
That makes them structurally more dangerous than many later-stage interpretation debates.

In particular:

1. if ranking semantics are changed, rec metrics stop meaning what we think they mean;
2. if items without explanations stay in top-k, rec/exp metrics stop referring to the same object set;
3. if the candidate pool is too narrow, baseline coverage is already distorted before any tradeoff optimization starts.

## 5. Recommended Decision Points

Before treating the VRKG4Rec lastfm integration as stable, the project should explicitly decide:

1. Should `uid_topk` preserve the original VRKG4Rec item ranking exactly?
2. Should an item be allowed into `uid_topk` if no valid explanation path can be exported for it?
3. Should the final explainable top-10 be selected from only the raw top-10 items, or from a larger candidate window?

These are not small implementation details.
They define what the current evaluation is actually measuring.
