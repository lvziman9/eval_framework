# Current Artifact Map

Primary sources of truth:
- Raw evaluation engine outputs: `xrecsys/log/` and `xrecsys/results/`
- Curated run mirror: `runs/`
- Curated figures/tables: `reports/`

Conventions used now:
- `runs/pgpr/...` mirrors baseline artifacts associated with PGPR-style `agent_topk=25-50-1` outputs.
- `runs/vrkg4rec/...` mirrors baseline artifacts associated with VRKG4Rec-style `agent_topk=10-12-1` outputs.
- `runs/_mirrors/` keeps bulk copies of xrecsys logs/results without changing the original xrecsys layout.
- `reports/figures/tradeoff/` contains promoted tradeoff figures for quick access.
- `reports/tables/optimization_metrics/` contains promoted tradeoff CSV tables for quick access.
