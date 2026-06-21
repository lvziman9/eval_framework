# Native-Path Model Candidate Audit

Date: 2026-06-21

## Decision

The main baseline family is restricted to models that directly produce
verifiable knowledge-graph paths for their recommendations.

The immediate additions are:

1. **KGGLM** (RecSys 2024);
2. **PEARLM** (2023);
3. **TPRec** (TOIS 2022), only where real interaction timestamps exist.

Existing PGPR, UCPR, and CAFE remain in the main path baseline set.
KGIN, KGAT, and LightGCN are accuracy-only references and are deferred to an
optional appendix. They are not substitutes for native-path baselines.

## Strict Native-Path Gate

A model enters the main comparison only if:

1. it emits an explicit user-to-item path;
2. every consecutive edge can be validated against the benchmark KG or
   train-only collaborative KG;
3. the path is produced by the model's recommendation/reasoning process, not
   retrieved after an unrelated score was produced;
4. canonical user and item ids can be recovered;
5. a public implementation can be audited and run.

The path does not have to use reinforcement learning. Constrained language
generation is acceptable when invalid next tokens are masked from the actual
KG adjacency.

## Candidate Classification

| Candidate | Year | Native path status | Code status | Decision |
| --- | ---: | --- | --- | --- |
| KGGLM | 2024 | Generates generic KG paths, then fine-tunes for recommendation path reasoning | Official repository; authors recommend the Hopwise implementation | Integrate now, first priority |
| PEARLM | 2023 | KG-constrained decoding guarantees generated edges follow the KG | Official repository and Hopwise implementation | Integrate now, first priority |
| TPRec | 2022 | RL search emits explicit time-aware KG paths | Official repository and Hopwise implementation | Integrate on timestamped datasets |
| PR4SR | 2024 | Hierarchical RL emits session-to-item paths | No verified official runnable repository found; session and image-augmented KG protocol differs from ours | Watch list |
| Counterfactual path framework | 2024 | Learns explanation weights over path-based recommenders | No verified official runnable repository found; not yet established as a standalone path generator | Watch list |
| PLM-Rec | 2022 | Generates path-like token sequences | Unbounded decoding may generate edges absent from the KG | Exclude from strict main table; possible invalid-path ablation |
| KGLRR | 2024 | Uses KG reasoning internally | Its final explanation is not based on a predicted KG path | Exclude |
| KGIN / KGAT / LightGCN | 2019–2021 | Do not emit native recommendation paths | Runnable | Accuracy-only appendix |

No 2025 model with both a strict recommendation-path contract and a verified
public runnable implementation was found in this audit. Hopwise itself is a
CIKM 2025 library, not a new recommendation model.

## Why Hopwise Is Acceptable Here

Hopwise uses RecBole infrastructure for data loading, training, and metrics,
but its path models are not ordinary RecBole accuracy models:

- `PEARLM` and `KGGLM` use a path-language-model model type;
- their decoder is constrained by the tokenized KG adjacency;
- their explain interface returns recommendation scores and generated paths;
- `TPRec`, PGPR, and CAFE perform graph path search and return paths.

Therefore Hopwise is used as an implementation substrate for native-path
models. This is distinct from running KGIN or LightGCN and later attaching a
post-hoc explanation.

## Dataset Matrix

| Dataset | KGGLM | PEARLM | TPRec | Notes |
| --- | --- | --- | --- | --- |
| `canonical_ml1m_v1` | yes | yes | yes | Real timestamps and a compact KG |
| `canonical_lastfm_v1` | yes | yes | candidate | Real timestamps; TPRec relation constraints still need a canonical definition |
| `beauty_legacy_v1` | candidate | candidate | candidate | Historical no-validation protocol; use only after defining a non-leaking training protocol |
| `canonical_amazon_book_kgat_v1` | yes | yes | no | Benchmark KG is suitable, but timestamps are all `-1` |

The first full integration order is:

1. PEARLM on canonical ML1M;
2. KGGLM pretrain and fine-tune on canonical ML1M;
3. PEARLM and KGGLM on canonical LastFM;
4. PEARLM and KGGLM on canonical Amazon-book;
5. TPRec on canonical ML1M, then LastFM if its temporal relation projection
   passes audit.

## Local Reproducibility Evidence

Local environment:

- Python 3.11.14;
- Torch 2.5.1 + CUDA 12.1;
- Hopwise 0.9.1.post1;
- path-language-model dependencies installed.

Added:

- `scripts/hopwise/build_canonical_hopwise_view.py`;
- `scripts/hopwise/smoke_prepare_native_path.py`;
- `scripts/hopwise/run_canonical_native_path.py`.

Completed checks:

- PEARLM loads canonical ML1M fixed splits and KG: `PASS`;
- KGGLM loads canonical ML1M fixed splits and KG: `PASS`;
- PEARLM loads canonical LastFM fixed splits and KG: `PASS`;
- KGGLM loads canonical Amazon-book fixed splits and all 2,557,746 KG triples:
  `PASS`;
- PEARLM samples 6,040 training paths on the complete canonical ML1M training
  split: `PASS`;
- PEARLM initializes its KG-constrained decoder with 54,147,840 parameters:
  `PASS`.
- KGGLM samples 9,056 generic KG pretraining paths on canonical ML1M and
  initializes its 54,147,840-parameter model: `PASS`.

The compact one-epoch PEARLM ML1M integration run completed on physical GPU 2:

- two Transformer layers, embedding size 128, four attention heads;
- 6,040 sampled training paths;
- 48 training batches in 3.39 seconds;
- all 6,040 test users evaluated in 12 seconds;
- Recall@10 `0.0068`;
- NDCG@10 `0.0243`;
- Hit@10 `0.1781`;
- Precision@10 `0.0203`;
- Fidelity@10 `0.1`.

This is explicitly an integration smoke, not a final paper configuration.

## Compatibility Fixes Found During the Audit

### Inactive linked catalog items

Hopwise assumes every item in `.link` occurs in at least one interaction.
Canonical views may retain KG-linked catalog items with no interaction.

The Hopwise view now filters only those inactive `.link` rows:

- ML1M: 69 inactive link rows removed from the model view;
- LastFM: 38,389 inactive link rows removed from the model view;
- Amazon-book: no rows removed.

Interactions and KG triples are preserved byte-for-byte. Full reports and
SHA-256 hashes are written with each view.

### Quadratic relation lookup

Hopwise path sampling builds a dense `|V| x |V|` relation matrix to recover
edge relation ids. This is infeasible for LastFM and Amazon-book.

The canonical runner replaces it at runtime with an edge dictionary whose
memory is `O(|E|)`. On ML1M, complete path sampling then finishes in about
seven seconds.

### KGGLM lazy pretraining sampler

The current KGGLM dataset implementation has two broken branches:

- its parallel branch creates a lazy `joblib` generator but never consumes it;
- its serial branch calls the worker without the required sampling arguments.

The canonical smoke runner installs a corrected serial sampler. It generated
9,056 non-empty generic KG paths on ML1M; the smoke now fails explicitly if
sampling returns only the empty tokenizer record.

### Short native-path recommendation lists

CAFE produced fewer than ten unique unseen path-ending items for 44 of 22,363
Beauty users. Non-path items are not inserted merely to fill the list.

The canonical evaluator now supports explicit short-list evaluation:

- missing slots count as non-hits;
- Precision@10 always divides by ten;
- slot coverage and short-user counts are reported;
- NDCG uses the correct ideal ranking based on the number of relevant items.

CAFE Beauty passes with 99.9656% slot coverage.

## Primary Sources

- Hopwise: https://github.com/tail-unica/hopwise
- KGGLM: https://github.com/mirkomarras/kgglm
- PEARLM paper: https://arxiv.org/abs/2310.16452
- PEARLM code: https://github.com/Chris1nexus/pearlm
- TPRec paper: https://arxiv.org/abs/2108.02634
- TPRec code: https://github.com/Go0day/TPRec
- PR4SR: https://arxiv.org/abs/2403.00832
- Counterfactual path framework: https://arxiv.org/abs/2401.05744
