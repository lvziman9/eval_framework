# Explainability Benchmark Framework

A unified framework for evaluating the explainability quality of knowledge graph-enhanced recommendation models, using the metrics defined in [Balloccu et al., SIGIR 2022](https://dl.acm.org/doi/10.1145/3477495.3532041).

---

## Architecture

```
eval_framework/
├── adapters/                       # Model output → xrecsys CSV format converters
│   ├── base_adapter.py            # Shared utilities (format_path, write_csvs, ...)
│   ├── pgpr_adapter.py            # Reads policy_paths_epoch<N>.pkl → 3 CSVs
│   └── vrkg4rec_adapter.py        # Reads VRKG4Rec paths.pkl → 3 CSVs
│
├── xrecsys/                        # Clone of giacoballoccu/explanation-quality-recsys
│   ├── datasets/{ml1m,lastfm}/    # Dataset files
│   ├── paths/{ml1m,lastfm}/       # Precomputed / adapter-generated path CSVs
│   │   └── agent_topk=<tag>/
│   │       ├── pred_paths.csv
│   │       ├── uid_topk.csv
│   │       └── uid_pid_explanation.csv
│   ├── models/PGPR/tmp/           # kg.pkl, label.pkl, transe_embed.pkl
│   ├── main.py                    # xrecsys evaluation entry point
│   ├── metrics.py                 # LIR / SEP / ETD / NDCG / HR / Recall
│   └── path_data_loader.py        # Loads CSVs → path_data object
│
├── run_eval.py                     # Unified entry point (convert + evaluate)
├── log.md                          # Development log
└── README.md
```

**Key design principle**: environment decoupling via file I/O.

| Layer | Conda env | Responsibility |
|-------|-----------|----------------|
| Model training/inference | `pgpr_env`, `vrkg_env`, ... | Generate raw pkl output |
| Adapter + Evaluation | `eval_frame` | Convert pkl → CSV, compute LIR/SEP/ETD |

---

## Evaluation Metrics

All metrics come from **xrecsys** ([Balloccu et al., SIGIR 2022](https://dl.acm.org/doi/10.1145/3477495.3532041)):

| Metric | Description |
|--------|-------------|
| **LIR** | Link Interaction Recency — favours paths through recently-interacted entities ↑ |
| **SEP** | Shared Entity Popularity — favours paths through niche/surprising entities ↑ |
| **ETD** | Explanation Type Diversity — favours diverse path relation types ↑ |
| NDCG | Normalized Discounted Cumulative Gain ↑ |
| HR | Hit Rate ↑ |
| Recall | Recall@K ↑ |
| Precision | Precision@K ↑ |

---

## Quick Start

### Prerequisites

```bash
conda activate eval_frame
cd eval_framework/
```

### Full pipeline (convert PGPR output + evaluate)

```bash
python run_eval.py \
    --model pgpr \
    --dataset ml1m \
    --pkl xrecsys/models/PGPR/tmp/ml1m/train_agent/policy_paths_epoch50.pkl \
    --topk 10
```

### Evaluate only (CSVs already exist)

```bash
# Using precomputed paths (agent_topk=25-50-1)
python run_eval.py \
    --model pgpr \
    --dataset ml1m \
    --agent-topk-tag 25-50-1 \
    --skip-convert

# Log to file instead of stdout
python run_eval.py \
    --model pgpr \
    --dataset lastfm \
    --agent-topk-tag 25-50-1 \
    --skip-convert \
    --log-file results/lastfm_eval.log
```

### Convert only (no evaluation)

```bash
python run_eval.py \
    --model pgpr \
    --dataset ml1m \
    --pkl xrecsys/models/PGPR/tmp/ml1m/train_agent/policy_paths_epoch50.pkl \
    --topk 10 \
    --skip-eval
```

---

## Adding a New Model

1. Add `adapters/newmodel_adapter.py` — implement `convert(pkl_path, dataset, xrecsys_dir, topk, agent_topk_tag)` that writes three CSVs to `xrecsys/paths/{dataset}/agent_topk={tag}/`.
2. Register the model in `run_eval.py` (`SUPPORTED_MODELS` + adapter branch in `run_adapter()`).

The three CSV files must follow the xrecsys schema:

| File | Columns | Notes |
|------|---------|-------|
| `pred_paths.csv` | uid, pid, path_score, path_prob, path | path: space-joined `(relation, etype, eid)` triples |
| `uid_topk.csv` | uid, top10 | top10: space-separated pid list, highest-score first |
| `uid_pid_explanation.csv` | uid, pid, path | one best path per uid-pid pair in top-K |

Path string example:
```
self_loop user 1 watched movie 466 belong_to category 86 belong_to movie 956
```

---

## Datasets & Pre-computed Files

| Item | Location |
|------|----------|
| ml1m dataset | `xrecsys/datasets/ml1m/` |
| lastfm dataset | `xrecsys/datasets/lastfm/` |
| Precomputed PGPR paths (ml1m) | `xrecsys/paths/ml1m/agent_topk=25-50-1/` |
| Precomputed PGPR paths (lastfm) | `xrecsys/paths/lastfm/agent_topk=25-50-1/` |
| KG / label pkl (ml1m) | `xrecsys/models/PGPR/tmp/ml1m/` |
| KG / label pkl (lastfm) | `xrecsys/models/PGPR/tmp/lastfm/` |
| SEP/LIR cache (auto-generated) | `xrecsys/models/PGPR/tmp/{dataset}/sep_matrix.pkl` |

---

## Results

Completed evaluations are saved to:
- `xrecsys/log/{dataset}/agent_topk={tag}/baseline.txt` — human-readable summary
- `xrecsys/results/{dataset}/agent_topk={tag}/` — full CSV distributions

### PGPR baseline (ml1m, agent_topk=25-50-1)

| Metric | Overall |
|--------|---------|
| NDCG | 0.292 |
| HR | 0.553 |
| Recall | 0.050 |
| Precision | 0.104 |
| **LIR** | **0.163** |
| **SEP** | **0.460** |
| **ETD** | **0.153** |

---

## References

- Balloccu et al., *Post Processing Recommender Systems with Knowledge Graphs for Recency, Popularity, and Diversity of Explanations*, SIGIR 2022. [Paper](https://dl.acm.org/doi/10.1145/3477495.3532041) · [Code](https://github.com/giacoballoccu/explanation-quality-recsys)
- Xian et al., *Reinforcement Knowledge Graph Reasoning for Explainable Recommendation*, SIGIR 2019. [Paper](https://arxiv.org/abs/1906.00091)


