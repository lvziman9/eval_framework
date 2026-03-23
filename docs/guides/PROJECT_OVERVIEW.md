# Project Overview

This repository is the evaluation and experiment-tracking hub for explainability benchmarking of KG-aware recommender systems.

Current model boundary:
- Embedded model stack: `PGPR` remains inside `xrecsys/models/PGPR/` because xrecsys depends on it directly.
- External model stacks: models such as `VRKG4Rec` are expected to live outside this repository.
- Adapter responsibility: convert model outputs or checkpoints into xrecsys-compatible path CSVs.
- Evaluation responsibility: run xrecsys metrics over those exported paths.

Directory roles:
- `adapters/`: model-specific conversion and data-prep logic.
- `xrecsys/`: evaluation engine, datasets, path files, logs, and results.
- `runs/`: mirrored experiment records for both internal and external models.
- `reports/`: curated figures, tables, and summaries.
- `docs/guides/`: durable project documentation.
- `docs/plans/`: planning and roadmap documents that may not match current implementation.
- `docs/handoffs/`: historical snapshots and exported handoff packages.
- `archive/`: deprecated or temporary artifacts not needed for the main workflow.
