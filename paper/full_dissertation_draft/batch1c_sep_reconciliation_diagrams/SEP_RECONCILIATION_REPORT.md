# SEP Reconciliation Report

## 1. Question

This report examines whether the dissertation may interpret a larger SEP value as evidence of a lower-degree, rarer, or more serendipitous bridge entity. The audit follows the accessible chain from the metric guide and XRecSys description through graph-degree construction, SEP-matrix generation, runtime lookup, alpha-sweep optimisation, and the separate PGPR/UCPR ablation reader.

The audit is read-only. It does not regenerate a matrix, rerun a sweep, alter an output, or change an experimental value.

## 2. Sources Inspected

| Source | Path | What was inspected | Finding | Confidence |
| --- | --- | --- | --- | --- |
| Path-metric guide | `docs/guides/PATH_METRICS_GUIDE.md` | SEP name, bridge anchor, degree semantics, and expected direction | Calls SEP “Serendipity of Explanation Path” and states that lower degree produces higher SEP. | verified |
| XRecSys repository description | `xrecsys/README.md` | Registered paper title and abstract | Names the underlying property “shared entity popularity”, not bridge-entity rarity. | verified |
| Graph degree construction | `xrecsys/models/PGPR/knowledge_graph.py` | Definition of `KnowledgeGraph.degrees` | Degree is the sum of adjacency counts over relations for each entity. | verified |
| SEP matrix loader and generator | `xrecsys/path_data_loader.py` | Cache precedence, degree normalisation, sort direction, EMA input, and assignment | Loads `sep_matrix.pkl` when present. Otherwise it sorts normalised degree ascending, replaces the values with ordinal indices, computes increasing EMA weights, and assigns those weights in ascending-degree order. | verified |
| Runtime bridge lookup | `xrecsys/myutils.py`; `xrecsys/metrics.py` | `path[-2]` extraction, missing-value handling, and user aggregation | SEP reads the bridge entity at `path[-2]`, looks up the matrix value, defaults a missing entry to zero, and averages available path scores. | verified |
| Main SEP optimiser | `xrecsys/optimizations.py` | Candidate ordering under `SEPopt` | The optimiser maximises `(1-alpha) * path_score + alpha * SEP_matrix_value`; larger matrix values are favoured. | verified |
| Sweep dispatcher and protocol | `xrecsys/main.py`; `scripts/hopwise/run_canonical_xrecsys_protocol.sh` | Whether the registered SEP sweep reaches the same metric and optimiser | `SEPopt` is dispatched to `optimize_SEP`, and metrics are computed from the same `PathDataLoader.SEP_matrix`. | verified |
| PGPR/UCPR ablation reader | `scripts/analysis/run_pgpr_ucpr_path_module_ablation.py` | Matrix source, candidate score, and direction | Loads the same dataset-level `sep_matrix.pkl`, uses its value directly, and maximises the SEP component in the ablation sweep. | verified |
| Cached matrix and historical run search | `xrecsys/`, `reports/`, `exports/`, and repository-wide filename search | Availability of `sep_matrix.pkl` and source export artifacts | No accessible SEP matrix cache was found; `exports/` is absent. Historical matrix values and hashes therefore cannot be inspected. | requires manual verification |
| Batch 1B chapters | `paper/full_dissertation_draft/batch1b_method_formalisation_evidence_refresh/` | Existing SEP caveat and remaining rarity wording | Batch 1B identified the conflict but still contains several rarity/serendipity formulations that require downgrading. | verified |

## 3. Guide Semantics

The guide defines the bridge anchor as `path[-2]` and describes SEP as a low-degree or unusual bridge-entity property. Its directional statement is unambiguous: lower degree should receive a higher SEP weight. That statement supports rarity- or serendipity-oriented wording if, and only if, the evaluated matrix implements the documented inverse relationship.

The local XRecSys README points in a different conceptual direction. Its registered paper title concerns popularity, and its abstract names the property “shared entity popularity”. This source is consistent with a direct popularity score but does not by itself prove the matrix used by the dissertation sweeps.

## 4. Code Behaviour

`KnowledgeGraph.compute_degrees()` counts the number of adjacent entities over all registered relations for each entity. `PathDataLoader.generate_SEP_matrix()` then performs the following operations separately for each entity type:

1. collect `(entity_id, degree)` pairs;
2. min-max normalise the degree values;
3. sort the pairs in ascending normalised-degree order;
4. call `normalized_ema()`;
5. inside `normalized_ema()`, discard the supplied degree values and replace them with ordinal positions `0, 1, ..., n-1`;
6. compute an exponentially weighted mean over those increasing positions;
7. min-max normalise the resulting sequence;
8. assign the increasing sequence back to entities in ascending-degree order.

For an entity type with more than one entry, this accessible generator is rank-based and directionally increasing: entities later in the ascending-degree order receive larger weights. Consequently, a higher-degree entity normally receives a value at least as large as a lower-degree entity. Equal-degree entities can receive different values because stable sort order and ordinal position break ties. A one-entry entity type receives zero because the normalisation range is zero.

This behaviour is inconsistent with the guide's low-degree / high-SEP statement. It is more consistent with the README's shared-entity-popularity description.

## 5. Matrix Generation Direction

For the current accessible generator, the supported directional statement is:

```text
higher degree or a later ascending-degree rank -> higher SEP matrix weight, subject to tie-order effects
```

The unsupported statement is:

```text
lower degree -> higher SEP matrix weight
```

This is a static conclusion about the accessible generator. It is not artifact-level proof about the historical matrices used to produce the registered sweep CSVs, because the loader gives precedence to cached `sep_matrix.pkl` files and no such files or hashes are present in the current evidence package.

## 6. Runtime SEP Lookup

`get_related_entity(path)` returns the entity type and identifier from the penultimate path triple. `SEP_single()` and `topks_SEP()` use those fields to retrieve `SEP_matrix[bridge_etype][bridge_eid]`, defaulting a missing key to `0.0`. The runtime metric does not invert, complement, negate, or otherwise transform the retrieved value.

The path anchor is therefore verified. The semantic direction depends entirely on the matrix content.

## 7. Alpha-Sweep Use of SEP

The main alpha-sweep and the ablation both favour larger SEP matrix values:

- `xrecsys/main.py` dispatches `SEPopt` to `optimize_SEP()`;
- `optimize_SEP()` sorts candidates in descending order of a path-score / SEP-value blend;
- `compute_exp_metrics()` reports averages obtained from the same in-memory SEP matrix;
- `run_canonical_xrecsys_protocol.sh` runs `SEPopt` as one of the three objective-specific sweeps;
- the PGPR/UCPR ablation loads the dataset-level cache and uses the SEP value directly in its maximisation rule.

Thus, alpha increasing toward the SEP objective favours a higher stored SEP value. No accessible runtime code reverses that direction. The exact matrix used by the historical registered outputs remains unavailable.

## 8. Reconciliation Decision

**Decision: guide wording appears stale.**

The guide's low-degree / high-SEP wording conflicts with both the current accessible generator and the XRecSys README's shared-entity-popularity description. The current implementation can be described as a repository-specific degree-derived, rank-weighted bridge-entity score. It cannot safely be described as an inverse-degree rarity score.

The decision is complete at code level but incomplete at historical-artifact level. Until the original cached matrices and their provenance are recovered, the dissertation must retain a manual-verification caveat for the registered SEP sweep values.

## 9. Impact on Dissertation Wording

The revised chapters should use:

> SEP is a repository-specific degree-derived bridge-entity score.

They may also state that the accessible optimiser favours higher stored SEP values. They should not interpret a larger SEP endpoint as direct evidence of lower degree, rarity, novelty, unexpectedness, serendipity, usefulness, or overall explanation quality.

Chapter 4 may retain all registered SEP values and empirical movement statements. It should describe them as SEP-weight movement or degree-derived bridge-entity-score movement. Result-level comparisons remain valid as comparisons of the recorded metric values, but the previous rarity-oriented semantic gloss is downgraded.

## 10. Required Manual Verification

1. Recover the exact `sep_matrix.pkl` used for LastFM and ML-1M registered sweeps.
2. Record each matrix path, SHA-256 hash, generation timestamp, producing commit, and command or run manifest.
3. Recover or identify the matching `kg.pkl` and record its hash.
4. Join every matrix entry to the corresponding graph degree and verify the actual direction separately for each entity type.
5. Check equal-degree ties, single-entry types, missing bridge entities, and zero defaults.
6. Confirm whether all six models on each dataset used the same cached matrix.
7. Confirm whether the PGPR/UCPR ablation used the same matrix version as the main six-model sweep.
8. Decide whether the guide should be corrected to popularity/rank-weight semantics or the generator should be corrected and all affected outputs regenerated under a separately approved experiment task.
9. Freeze final dissertation wording only after the matrix and generator provenance agree.

No item in this checklist is executed by Batch 1C.
