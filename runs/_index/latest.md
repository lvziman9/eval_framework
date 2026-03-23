# Latest Experiment Pointers

Current repository role:
- Keep PGPR embedded under `xrecsys/models/PGPR/`.
- Treat other recommenders as external model repositories.
- Mirror the key experiment records here under `runs/`, not the full external codebase.

Current known pointers:
- PGPR LastFM baseline: `runs/pgpr/lastfm/baseline/baseline_handoff_2026-03-23.txt`
- VRKG4Rec LastFM baseline: `runs/vrkg4rec/lastfm/evaluation/baseline_handoff_2026-03-23.txt`
- VRKG4Rec adapter logs: `runs/vrkg4rec/lastfm/adapter/`
- Historical handoff snapshot: `docs/handoffs/2026-03-23/`
- Current evaluation outputs still produced by xrecsys under `xrecsys/log/` and `xrecsys/results/`.

How to use `runs/` going forward:
- `training/`: external training logs, config snapshots, checkpoint manifest.
- `adapter/`: adapter commands, extraction logs, path export notes.
- `evaluation/`: baseline and optimization result logs copied or linked from xrecsys outputs.
- `path_exports/`: notes/manifests for generated path CSV folders.
- `notes/`: short human summaries of what happened in a run.
