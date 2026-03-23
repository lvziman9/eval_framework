# Explainability Benchmark Framework

A unified framework for evaluating the explainability quality of knowledge graph-enhanced recommendation models, using the metrics defined in [Balloccu et al., SIGIR 2022](https://dl.acm.org/doi/10.1145/3477495.3532041).

---

## Architecture

```
eval_framework/
├── adapters/                       # Model output → xrecsys CSV format converters
│   ├── base_adapter.py            # Shared utilities (format_path, write_csvs, ...)
│   ├── pgpr_adapter.py            # Reads policy_paths_epoch<N>.pkl → 3 CSVs
│   ├── vrkg4rec_adapter.py        # Loads VRKG4Rec checkpoint, extracts paths via
│   │                              #   O(deg²) reverse-KG enumeration → 3 CSVs
│   ├── vrkg4rec_data_prep.py      # Converts xrecsys data → VRKG4Rec training format
│   └── vrkg_lookups/<dataset>/    # Pre-exported lookup tables (entity map, KG JSON)
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
| Model training/inference | `pgpr_env`, `vrkg4rec`, ... | Generate raw pkl / ckpt output |
| Adapter + Evaluation | `eval_frame` | Convert pkl → CSV, compute LIR/SEP/ETD |
| VRKG4Rec adapter only | `vrkg4rec` | Needs PyTorch + VRKG4Rec modules for embedding extraction |

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

### VRKG4Rec full pipeline

```bash
# Step 1: prepare data (run once, in eval_frame env)
conda run -n eval_frame python adapters/vrkg4rec_data_prep.py \
    --dataset lastfm

# Step 2: train (in vrkg4rec env, GPU recommended)
conda run -n vrkg4rec python /path/to/vrkg4rec/main.py \
    --dataset xrecsys_lastfm --gpu_id 0

# Step 3: extract paths + write CSVs (in vrkg4rec env)
conda run -n vrkg4rec python adapters/vrkg4rec_adapter.py \
    --vrkg4rec-dir /path/to/vrkg4rec \
    --ckpt weights/model_xrecsys_lastfm.ckpt \
    --dataset lastfm \
    --topk 10 --topk-paths 5 --gpu-id 1

# Step 4: evaluate (in eval_frame env)
cd xrecsys && conda run -n eval_frame python main.py \
    --dataset lastfm --agent_topk 10-12-1 --eval_baseline True
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
| VRKG4Rec paths (lastfm, epoch ~20) | `xrecsys/paths/lastfm/agent_topk=10-12-1/` |
| KG / label pkl (ml1m) | `xrecsys/models/PGPR/tmp/ml1m/` |
| KG / label pkl (lastfm) | `xrecsys/models/PGPR/tmp/lastfm/` |
| SEP/LIR cache (auto-generated) | `xrecsys/models/PGPR/tmp/{dataset}/sep_matrix.pkl` |
| VRKG4Rec entity/uid lookups | `adapters/vrkg_lookups/lastfm/` |
| VRKG4Rec training data | `/path/to/vrkg4rec/data/xrecsys_lastfm/` (15,549 users, 47,982 items) |

---

## Results

Completed evaluations are saved to:
- `xrecsys/log/{dataset}/agent_topk={tag}/baseline.txt` — human-readable summary
- `xrecsys/results/{dataset}/agent_topk={tag}/` — full CSV distributions

### PGPR baseline (ml1m, agent_topk=25-50-1)

| Metric | Overall |
|--------|------|
| NDCG | 0.292 |
| HR | 0.553 |
| Recall | 0.050 |
| Precision | 0.104 |
| **LIR** | **0.163** |
| **SEP** | **0.460** |
| **ETD** | **0.153** |

### PGPR baseline (lastfm, agent_topk=25-50-1)

| Metric | Overall |
|--------|------|
| NDCG | 0.086 |
| HR | 0.182 |
| Recall | 0.010 |
| Precision | 0.027 |
| **LIR** | **0.597** |
| **SEP** | **0.341** |
| **ETD** | **0.130** |

### VRKG4Rec (lastfm, epoch ~20, agent_topk=10-12-1)

14,642 test users · 697,222 paths extracted.

| Metric | Overall | Male | Female |
|--------|---------|------|--------|
| NDCG | **0.152** | 0.153 | 0.147 |
| HR | **0.242** | 0.243 | 0.236 |
| Recall | 0.017 | 0.017 | 0.017 |
| Precision | 0.045 | 0.045 | 0.044 |
| **LIR** | **0.049** | 0.051 | 0.040 |
| **SEP** | **0.929** | 0.927 | 0.931 |
| **ETD** | **0.214** | 0.215 | 0.212 |

**Notes:**
- NDCG/HR significantly higher than PGPR (+77% / +33%) reflecting stronger recommendation quality.
- LIR is low (0.049) because most paths go through `category` bridges (`song→category→song`), which are 2-hop indirect paths penalised by the LIR formula. Direct user-item interaction edges score higher but are rarer in this KG structure.
- SEP is very high (0.929) indicating paths tend to pass through low-popularity entities (niche categories/artists).
- Training was still ongoing (~epoch 20); results may improve with a fully converged checkpoint.

---

## References

- Balloccu et al., *Post Processing Recommender Systems with Knowledge Graphs for Recency, Popularity, and Diversity of Explanations*, SIGIR 2022. [Paper](https://dl.acm.org/doi/10.1145/3477495.3532041) · [Code](https://github.com/giacoballoccu/explanation-quality-recsys)
- Xian et al., *Reinforcement Knowledge Graph Reasoning for Explainable Recommendation*, SIGIR 2019. [Paper](https://arxiv.org/abs/1906.00091)


