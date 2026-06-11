# Data Provenance

This note explains where the repository's datasets, KG files, labels, and path artifacts come from, and which files are actually used during evaluation.

## 1. High-level split

There are four different artifact layers in this repository:

1. Dataset layer
- Location: `xrecsys/datasets/{lastfm,ml1m}/`
- Contents: train/test interactions, entity tables, relation tables, mappings, and dataset-specific raw KG resources.

2. Evaluation-ready PGPR tmp layer
- Location: `xrecsys/models/PGPR/tmp/{lastfm,ml1m}/`
- Contents: `kg.pkl`, `train_label.pkl`, `test_label.pkl`, `transe_embed.pkl`, plus cached `lir_matrix.pkl` and `sep_matrix.pkl`.
- This is the layer actually consumed by the xrecsys evaluation code.

3. Path export layer
- Location: `xrecsys/paths/{lastfm,ml1m}/agent_topk=*/`
- Contents: exported path CSV files used by xrecsys metrics.

4. Archive/download layer
- Location: `archive/raw_downloads/`
- Contents: historical raw downloads when retained.
- Note: previously retained `paths_lastfm.zip` and `paths_ml1m.zip` were removed during the 2026-06-11 cleanup because they were not runtime sources of truth.

## 2. Dataset sources

The unpacked datasets are present at:
- `xrecsys/datasets/lastfm/`
- `xrecsys/datasets/ml1m/`

Representative files include:
- Shared interaction files: `train.txt`, `test.txt`
- Entity tables: `entities/*.txt`
- Relation tables: `relations/*.txt`
- Mapping files: `mappings/*.txt`

Dataset-specific KG-related raw resources:
- LastFM: `xrecsys/datasets/lastfm/kg-completion/kg_final.txt`
- ML1M: `xrecsys/datasets/ml1m/joint-kg/dataset.dat`

These dataset directories are the raw/preprocessed data layer, but the evaluation code does not directly use them as the final KG object.

## 3. Where the KG used in evaluation comes from

The KG actually used by evaluation is:
- `xrecsys/models/PGPR/tmp/lastfm/kg.pkl`
- `xrecsys/models/PGPR/tmp/ml1m/kg.pkl`

This is the canonical runtime KG for xrecsys metrics and path loading.

Related runtime files in the same directory:
- `train_label.pkl`
- `test_label.pkl`
- `transe_embed.pkl`
- `lir_matrix.pkl`
- `sep_matrix.pkl`

In other words:
- Dataset files under `xrecsys/datasets/` provide the raw/preprocessed corpus.
- `kg.pkl` under `xrecsys/models/PGPR/tmp/` is the evaluation-ready KG object that xrecsys actually loads.

## 4. Original vs regenerated KG/labels

For both datasets, the repository contains pairs such as:
- `kg.pkl`
- `kg.generated.pkl`
- `train_label.pkl`
- `train_label.generated.pkl`
- `test_label.pkl`
- `test_label.generated.pkl`

Interpretation:
- `*.generated.pkl` files are regenerated locally from preprocessing.
- The plain `*.pkl` files are the retained canonical versions used in evaluation.

Why the canonical `kg.pkl` is kept:
- The development log states that the path CSV entity IDs align with the original author-provided `kg.pkl`.
- Because of this alignment requirement, the repository keeps the original-style `kg.pkl` as the evaluation source of truth.
- The regenerated versions are preserved as backup/reference artifacts.

## 5. Where labels come from

Evaluation labels are loaded from:
- `xrecsys/models/PGPR/tmp/lastfm/train_label.pkl`
- `xrecsys/models/PGPR/tmp/lastfm/test_label.pkl`
- `xrecsys/models/PGPR/tmp/ml1m/train_label.pkl`
- `xrecsys/models/PGPR/tmp/ml1m/test_label.pkl`

These labels are part of the PGPR/xrecsys tmp layer and are used by:
- recommendation quality metrics
- filtering seen items
- train/test split logic in adapters and evaluation

## 6. Where path CSVs come from

The path CSVs live at:
- `xrecsys/paths/lastfm/agent_topk=10-12-1/`
- `xrecsys/paths/lastfm/agent_topk=25-50-1/`
- `xrecsys/paths/ml1m/agent_topk=10-12-1/`
- `xrecsys/paths/ml1m/agent_topk=25-50-1/`

These folders contain files such as:
- `pred_paths.csv`
- `best_pred_paths.csv`
- `uid_topk.csv`
- `uid_pid_explanation.csv`
- optionally `user2timestamp.csv`
- optionally `uid_pid_timestamp.csv`

Historical download archives were previously kept under `archive/raw_downloads/`, but they are not part of the active runtime path source.

Important distinction:
- Raw zip files, when present, are historical downloads only.
- The live runtime path files are the unpacked files under `xrecsys/paths/`.

## 7. Current completeness check

Based on the repository state checked during cleanup:

Fully present:
- `ml1m/agent_topk=10-12-1`
- `ml1m/agent_topk=25-50-1`
- `lastfm/agent_topk=10-12-1`

Partially mismatched against the archived zip listing:
- `lastfm/agent_topk=25-50-1`

Specifically missing in the unpacked directory while present in the archived zip listing:
- `user2timestamp.csv`
- `uid_pid_timestamp.csv`

This does not change the fact that the active path directory exists and is usable, but it is worth remembering if someone asks whether the unpacked folder is byte-for-byte identical to the original zip contents.

## 8. Best short answer to "Where did the KG come from?"

Use this answer:

- The raw dataset and KG-related source files are stored in `xrecsys/datasets/{dataset}/`.
- The evaluation pipeline itself uses the serialized KG object in `xrecsys/models/PGPR/tmp/{dataset}/kg.pkl`.
- The repository also keeps locally regenerated backups as `kg.generated.pkl`, but the canonical evaluation KG is `kg.pkl` because it matches the entity IDs used by the path CSV exports.

## 9. Related references

- Project development history: `archive/historical_docs/early_framework/plans/log.md`
- Path format and metric assumptions: `docs/guides/PATH_METRICS_GUIDE.md`
- Current repository architecture: `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`
- Historical repository overview: `archive/historical_docs/debug_reports/PROJECT_OVERVIEW.md`
