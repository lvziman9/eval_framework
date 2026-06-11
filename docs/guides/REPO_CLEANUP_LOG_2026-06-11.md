# Repository Cleanup Log

Date: 2026-06-11

This cleanup pass reorganized the repository around the native-path experiment direction.

## Active Principle

Only models with native recommendation paths should enter the main `LIR / SEP / ETD` explainability evaluation.

Non-path KG recommenders can still be used as accuracy references, but post-hoc paths should not be used for the main explainability scores.

## Active Folders After Cleanup

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

docs/guides/
  CANONICAL_DATASET_STANDARD.md
  NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md
  PATH_METRICS_GUIDE.md
  DATA_PROVENANCE.md
  REPO_CLEANUP_LOG_2026-06-11.md
```

## Archived

Moved to `archive/historical_code/posthoc_vrkg/`:

- `adapters/vrkg4rec_adapter.py`
- `adapters/vrkg4rec_data_prep.py`
- `adapters/vrkg_lookups/`

Moved to `archive/historical_code/legacy_eval/`:

- `run_eval.py`
- `setup.py`
- `examples/`

Moved to `archive/historical_docs/posthoc_vrkg/`:

- `docs/guides/VRKG4REC_INTEGRATION_RISKS.md`
- `docs/guides/LATENT_PATH_RETRIEVAL_PSEUDOCODE.md`

Moved to `archive/historical_docs/early_framework/`:

- `docs/plans/`
- `docs/handoffs/`

Moved to `archive/historical_docs/debug_reports/`:

- `docs/guides/PROJECT_OVERVIEW.md`
- `docs/guides/WEEKLY_DEBUG_REPORT_2026-03-24.md`
- `docs/guides/PIPELINE_RELIABILITY_LOG.md`
- `docs/guides/CANONICAL_DATASET_PROGRESS_SUMMARY_2026-05-12.md`

## Not Cleaned Yet

The following were intentionally left alone:

- `runs/debug_compare/`, because it contains active training and canonical-dataset workspaces,
- `xrecsys/log/`, because it contains raw evaluation output,
- `reports/`, because it contains curated figures and tables.

These should be curated later rather than removed blindly.
