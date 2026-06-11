# Latent Path Retrieval Pseudocode

This note records a reusable post-hoc explanation strategy for **latent / GNN-based recommenders** that do not natively output explicit reasoning paths.

Typical target models:
- VRKG4Rec-like embedding or GNN recommenders
- future latent KG recommenders that rank items but do not expose explicit path traces

The goal is **not** to claim recovery of the model's true internal path.
Instead, the goal is:

- generate a candidate set of short KG paths,
- score those paths by consistency with the model's latent user-item signal,
- export the best path(s) in xrecsys-compatible format.

---

## 1. Problem Setup

Given:
- a trained recommender model,
- user embeddings `U`,
- item embeddings `I`,
- optional entity / relation embeddings,
- a KG over the evaluation dataset,
- a set of users to recommend for,

we want to build:
- `pred_paths.csv`
- `uid_topk.csv`
- `uid_pid_explanation.csv`

for xrecsys.

---

## 2. Design Principles

1. Keep path structures short and metric-compatible.
   xrecsys expects path structures where:
   - `path[1]` can act as the interaction anchor for LIR,
   - `path[-2]` can act as the bridge entity for SEP,
   - `path[-1][0]` can act as the explanation type for ETD.

2. Separate three layers clearly:
   - candidate item generation,
   - candidate path enumeration,
   - latent-consistency scoring.

3. Do not claim faithfulness unless independently validated.
   This is a **representative path retrieval** strategy, not proof of the model's internal reasoning chain.

---

## 3. High-Level Pipeline

```text
for each user u:
    1. get model-ranked candidate items C(u)
    2. for each item i in C(u):
         enumerate metric-compatible KG paths P(u, i)
    3. for each path p in P(u, i):
         compute latent-consistency score s(u, i, p)
    4. choose best path p* for each item i
    5. choose final top-k items for export
    6. write xrecsys CSV rows
```

---

## 4. Candidate Item Selection

Two policy variants are possible.

### Variant A: strict raw-topK policy

```python
candidate_items = topk_items_from_model(user=u, k=K)
```

Meaning:
- explanations are searched only for the model's raw top-K items.
- this preserves closeness to the original ranking,
- but may produce incomplete explainable top-k lists.

### Variant B: candidate-window policy

```python
candidate_items = topk_items_from_model(user=u, k=CANDIDATE_K)
final_export_k = K
```

Meaning:
- explanations are searched in a larger item pool,
- final export still keeps only top-K items,
- this improves explainable coverage,
- but changes the selection mechanism.

---

## 5. Candidate Path Enumeration

For xrecsys compatibility, prefer short paths of the form:

```text
user -> seed_item -> bridge_entity -> target_item
```

or, if absolutely necessary:

```text
user -> seed_item -> target_item
```

Pseudocode:

```python
def enumerate_candidate_paths(user_id, target_item, user_train_items, kg, max_hops=3):
    candidates = []

    for seed_item in user_train_items:
        # Example 2-hop / 3-hop constrained search
        if kg.has_edge(seed_item, target_item):
            candidates.append([user_id, seed_item, target_item])

        for bridge in kg.neighbors(seed_item):
            if kg.has_edge(bridge, target_item):
                candidates.append([user_id, seed_item, bridge, target_item])

    return candidates
```

Key rule:
- enumerate only paths that can later be mapped into xrecsys path strings with stable `LIR/SEP/ETD` semantics.

---

## 6. Path Representation

A path must be converted into a vector-like representation before scoring.

### Minimal option: pooled node embeddings

```python
def build_path_vector(path_nodes, entity_embeds):
    node_vecs = [entity_embeds[n] for n in path_nodes if n in entity_embeds]
    return mean(node_vecs)
```

### Slightly richer option: seed + bridge + target composition

```python
def build_path_vector(path, entity_embeds, relation_embeds=None):
    if len(path) == 4:
        _, seed, bridge, target = path
        vecs = [entity_embeds[seed], entity_embeds[bridge], entity_embeds[target]]
    else:
        _, seed, target = path
        vecs = [entity_embeds[seed], entity_embeds[target]]
    return mean(vecs)
```

### Future extension
- relation-aware encoder,
- GRU / Transformer path encoder,
- path-type embedding plus node pooling.

---

## 7. User-Item Latent Query Vector

Construct a latent query representing why user `u` and item `i` fit together.

### Simple option

```python
def build_ui_query(user_emb, item_emb):
    return mean([user_emb, item_emb])
```

### Alternative options

```python
def build_ui_query(user_emb, item_emb):
    return concat(user_emb, item_emb)
```

or

```python
def build_ui_query(user_emb, item_emb):
    return item_emb - user_emb
```

Choice depends on the model family and what empirically aligns best with path selection quality.

---

## 8. Latent-Consistency Scoring

Score each candidate path by how well it matches the user-item latent signal.

### Minimal scoring function

```python
def latent_consistency_score(user_emb, item_emb, path_vec):
    ui_query = build_ui_query(user_emb, item_emb)
    return cosine_similarity(ui_query, path_vec)
```

### Hybrid scoring function

```python
def latent_consistency_score(user_emb, item_emb, path_vec, structural_score,
                             alpha=0.7):
    ui_query = build_ui_query(user_emb, item_emb)
    latent_score = cosine_similarity(ui_query, path_vec)
    return alpha * latent_score + (1 - alpha) * structural_score
```

Where `structural_score` can be:
- relation prior,
- short-path bonus,
- path validity bonus,
- bridge rarity bonus,
- local embedding smoothness.

---

## 9. Best Path Per Item

```python
def choose_best_path_for_item(user_emb, item_emb, candidate_paths, entity_embeds):
    best_path = None
    best_score = -inf

    for path in candidate_paths:
        path_vec = build_path_vector(path, entity_embeds)
        score = latent_consistency_score(user_emb, item_emb, path_vec)
        if score > best_score:
            best_score = score
            best_path = path

    return best_path, best_score
```

---

## 10. Final Export Strategy

Two output strategies are possible.

### Strategy A: preserve original ranking order

```python
final_items = []
for item in candidate_items_in_original_model_order:
    if item has valid exported path:
        final_items.append(item)
    if len(final_items) == K:
        break
```

Use when the project wants recommendation metrics to stay as close as possible to the original model ranking.

### Strategy B: latent explainable top-k

```python
valid_items = [
    (item, best_path_score[item], best_path[item])
    for item in candidate_items
    if item has valid path
]
valid_items.sort(by=best_path_score, descending=True)
final_items = valid_items[:K]
```

Use when the project wants a jointly explainable top-k recommendation output.

---

## 11. xrecsys Path Conversion

After selecting a path, convert it into the xrecsys string format.

```python
def convert_to_xrecsys_path(path_nodes, lookup_tables, kg):
    # map node ids back to xrecsys local ids
    # recover relation names from KG edges
    # format as:
    # self_loop user uid rel item seed rel bridge_type bridge_id rel item pid
    return path_str
```

Important:
- `path[1]` must be a real training interaction item for LIR,
- `path[-2]` must be a meaningful bridge entity for SEP,
- `path[-1][0]` must be a stable relation label for ETD.

---

## 12. Generic End-to-End Pseudocode

```python
def export_latent_paths(model, users, kg, train_labels, K=10, candidate_k=50):
    pred_rows = []
    uid_topk = {}
    uid_pid_best = {}

    user_embeds, item_embeds, entity_embeds = model.export_embeddings()

    for u in users:
        ranked_items = model.rank_items(u, topk=candidate_k)
        user_results = []

        for item in ranked_items:
            candidate_paths = enumerate_candidate_paths(
                user_id=u,
                target_item=item,
                user_train_items=train_labels[u],
                kg=kg,
            )
            if not candidate_paths:
                continue

            best_path, best_score = choose_best_path_for_item(
                user_emb=user_embeds[u],
                item_emb=item_embeds[item],
                candidate_paths=candidate_paths,
                entity_embeds=entity_embeds,
            )

            path_str = convert_to_xrecsys_path(best_path, lookup_tables=None, kg=kg)
            if path_str is None:
                continue

            pred_rows.append((u, item, best_score, -1, path_str))
            user_results.append((item, best_score, path_str))

        # choose final top-k by the chosen export policy
        final_results = select_final_topk(user_results, K=K)
        uid_topk[u] = [item for item, _, _ in final_results]
        uid_pid_best[u] = {item: path_str for item, _, path_str in final_results}

    return pred_rows, uid_topk, uid_pid_best
```

---

## 13. Recommended First Implementation for This Repo

For the current repository, a practical first version would be:

1. keep the current short-path enumeration idea,
2. replace the current local cosine averaging with a clearer latent-consistency score,
3. test both:
   - strict raw-topK export,
   - candidate-window export,
4. compare:
   - coverage,
   - baseline metrics,
   - tradeoff behavior.

---

## 14. What This Method Can and Cannot Claim

### It can support
- a more principled post-hoc explanation selection method,
- better alignment between latent recommendation signals and exported KG paths,
- a reusable adapter design for multiple latent KG models.

### It cannot directly prove
- that the retrieved path is the true internal reasoning chain of the model,
- that the model actually executed that exact path during prediction.

So the correct interpretation is:

**latent-consistent representative path retrieval**, not strict faithful path recovery.
