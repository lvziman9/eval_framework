# Cleanup Candidates

Clearly safe to remove later if you want a leaner repo:
- `archive/duplicate_exports/scripts_figures_legacy/`
  Reason: exact duplicates of `reports/figures/tradeoff/` verified by checksum.
- `archive/raw_downloads/paths_lastfm.zip`
- `archive/raw_downloads/paths_ml1m.zip`
  Reason: raw download archives are no longer needed for day-to-day work once data is already unpacked.

Keep for now:
- `xrecsys/log/` and `xrecsys/results/`
  Reason: these remain the primary raw outputs produced by the evaluation engine.
- `runs/_mirrors/`
  Reason: helpful as a curated mirror until we decide whether to fully move away from reading directly from `xrecsys/log` and `xrecsys/results`.
- `docs/handoffs/2026-03-23/`
  Reason: historical snapshot; contains repeated files by design.

Ambiguous / optional later cleanup:
- `runs/pgpr/lastfm/baseline/baseline_handoff_2026-03-23.txt`
- `runs/vrkg4rec/lastfm/evaluation/baseline_handoff_2026-03-23.txt`
  Reason: these duplicate information now also mirrored from live xrecsys outputs, but they preserve the original handoff state.
