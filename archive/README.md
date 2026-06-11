# Archive

This directory keeps historical materials that are no longer on the active experiment path.

The current active project direction is documented in:

- [Native Path Experiment Architecture](/usr1/home/s125mdg43_08/eval_framework/docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md)
- [Canonical Dataset Standard](/usr1/home/s125mdg43_08/eval_framework/docs/guides/CANONICAL_DATASET_STANDARD.md)

## Directory Roles

```text
historical_code/
  legacy_eval/
    Old root-level evaluation scaffold, including the previous run_eval.py and setup.py.

  posthoc_vrkg/
    VRKG4Rec and post-hoc path recovery adapter code. This is no longer part of the
    main explainability scoring line because post-hoc paths are not faithful native paths.

historical_docs/
  early_framework/
    Older plans and handoff snapshots.

  posthoc_vrkg/
    Notes about VRKG4Rec risks and latent path retrieval. Kept as provenance and
    negative evidence for excluding post-hoc explanations from main LIR/SEP/ETD scoring.

duplicate_exports/
  Previously identified duplicate figure/table exports.

raw_downloads/
  Raw downloaded archives kept only when needed for provenance.
```

## Cleanup Rule

Archive files may be cited for history, but active work should not depend on them unless they are explicitly restored into the main framework.
