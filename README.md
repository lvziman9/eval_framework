# Native Path KG Recommendation Evaluation

This repository is being reorganized around a narrower and more defensible experiment:

```text
evaluate accuracy-explainability tradeoffs only for KG recommenders with native recommendation paths
```

Models without native paths may still be used as recommendation accuracy references, but they should not receive `LIR / SEP / ETD` scores through post-hoc path recovery.

## Current Source Of Truth

Start with these documents:

- [Native Path Experiment Architecture](/usr1/home/s125mdg43_08/eval_framework/docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md)
- [Canonical Dataset Standard](/usr1/home/s125mdg43_08/eval_framework/docs/guides/CANONICAL_DATASET_STANDARD.md)
- [Path Metrics Guide](/usr1/home/s125mdg43_08/eval_framework/docs/guides/PATH_METRICS_GUIDE.md)
- [Data Provenance](/usr1/home/s125mdg43_08/eval_framework/docs/guides/DATA_PROVENANCE.md)

## Active Framework

```text
adapters/
  base_adapter.py
  pgpr_adapter.py
  ucpr_adapter.py

scripts/data/canonical/
  build_canonical_dataset.py
  build_pgpr_view.py
  build_ucpr_view.py

scripts/analysis/
  tradeoff_analyzer.py

xrecsys/
  main.py
  metrics.py
  path_data_loader.py
  myutils.py
  optimizations.py
```

The current canonical dataset under active development is:

```text
runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1
```

Generated runs and logs are working artifacts. They should not be pushed wholesale.

## Model Policy

Native path models enter the main explainability experiment:

```text
PGPR
UCPR
CAFE
```

They should export:

```text
uid_topk.csv
pred_paths.csv
uid_pid_explanation.csv
```

Non-path KG recommenders are accuracy references only:

```text
KGIN
KGAT
MKR
CKE
RippleNet
LightGCN variants
```

They should export `uid_topk.csv` only, unless the model has a faithful native path mechanism.

## Archive

Historical framework sketches, old handoffs, and post-hoc VRKG materials are under:

```text
archive/
```

These files are kept for provenance and paper discussion, but they are no longer the active experiment path.

## Immediate TODO

1. Finish `PGPR` test, path export, canonical export, and xrecsys evaluation on `lastfm_v1`.
2. Finish `UCPR` policy/test/export/evaluation on `lastfm_v1`.
3. Add `CAFE` as the next native-path model.
4. Add one or two strong non-path KG baselines as accuracy references only.
5. Produce separate result tables for native-path metrics and accuracy-only baselines.

