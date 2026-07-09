# Goal 0: Repository Quick Audit

## Goal 编号

Goal 0

## 当前任务

快速审计仓库结构，识别与 dissertation 写作最相关的 docs、results、figures、validation、scripts 和 archive/provenance 目录，并建立后续 Goals 的证据地图。

## 已检查路径

| Category | Checked paths | Dissertation use |
| --- | --- | --- |
| Project positioning docs | `README.md`; `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`; `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/PATH_METRICS_GUIDE.md`; `docs/guides/DATA_PROVENANCE.md` | Define the research scope, canonical framework, metric definitions, and native-path policy. |
| Current report summaries | `reports/summaries/experiment_summaries/current_artifact_map.md`; `reports/tables/canonical_native_path_status_matrix.md`; `reports/tables/canonical_native_path_status_matrix.csv` | Primary evidence for current experiment status, completed rows, blocked rows, and reportable results. |
| Results and logs | `xrecsys/log/`; `xrecsys/results/`; `runs/`; `runs/debug_compare/2026-06-20_native_path_expansion/` | Raw and curated accuracy/explanation/export artifacts. Use through promoted reports whenever possible. |
| Curated tables | `reports/tables/`; `reports/tables/canonical_export_validation/`; `reports/tables/tradeoff_insights/`; `reports/tables/optimization_metrics/`; `reports/tables/ablation/` | Thesis-ready evidence tables and validation summaries. |
| Curated figures | `reports/figures/tradeoff/`; `reports/figures/comparisons/`; `reports/figures/baseline/`; `reports/figures/ablation/`; `results/figures/` | Candidate dissertation figures. Canonical trade-off bundles are the main figure source. |
| Validation scripts and evidence | `scripts/validation/`; `reports/tables/canonical_export_validation/manifest.json`; per-row JSON files under `reports/tables/canonical_export_validation/` | Validation-first evidence for export contract, user coverage, and path consistency. |
| Report generation scripts | `scripts/analysis/`; especially `scripts/analysis/regenerate_canonical_native_path_reports.sh` mentioned by the completion audit | Reproducibility evidence only. Do not rerun training; report scripts are used as provenance. |
| Active adapters/pipeline code | `adapters/`; `scripts/data/canonical/`; `xrecsys/` | Framework design evidence for Chapter 3. Do not modify. |
| Historical material | `archive/`; `runs/_mirrors/`; `archive/historical_docs/`; `archive/historical_code/` | Provenance or appendix material. Not a primary current-status source unless explicitly needed. |

## 关键发现

1. The repository's stated dissertation-relevant scope is not a new recommender model; it is an evaluation framework for KG recommenders with native recommendation paths. `README.md` explicitly narrows the experiment to accuracy-explainability trade-offs for models with native recommendation paths and warns against assigning `LIR / SEP / ETD` to non-path models via post-hoc recovery.
2. The strongest current source of truth is `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md`, updated on `2026-06-30` Asia/Singapore. It says LastFM and ML-1M canonical native-path baselines are complete, Amazon-Book is partially complete, export validation passes for 15 completed rows, and three Amazon classic-model rows remain blocked.
3. The machine-readable status file is `reports/tables/canonical_native_path_status_matrix.csv`, with a readable companion in `reports/tables/canonical_native_path_status_matrix.md`. This should be the main source for completed/blocked dataset-model rows.
4. Current reportable rows total 18 dataset-model entries: 15 complete rows and 3 blocked Amazon-Book KGAT rows, according to `docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md` and `reports/tables/canonical_native_path_status_matrix.md`.
5. LastFM and ML-1M have six-model alpha-sweep figure bundles: `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` and `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/`. Amazon-Book alpha sweeps are marked `N/A` because of timestamp/SEP/ETD denominator limitations.
6. `reports/summaries/experiment_summaries/current_artifact_map.md` defines the current artifact organization: raw outputs in `xrecsys/log/` and `xrecsys/results/`, curated run mirrors in `runs/`, and promoted thesis-style figures/tables in `reports/`.
7. README TODO items must not be treated as completed facts. Later Goals should privilege `reports/`, `docs/guides/`, validation JSONs, status matrices, and promoted figure/table artifacts.
8. The worktree already had unrelated modified files before this analysis began, mostly in ablation reports/scripts. This pack should avoid changing existing results, model code, adapter code, dataset code, and evaluation pipeline code.

## Repo Map

| Area | Main paths | Type | Use in dissertation | Caution |
| --- | --- | --- | --- | --- |
| Active design docs | `docs/guides/` | docs | Chapter 1 positioning, Chapter 3 method design, metric definitions, provenance | Check against current reports before using older plans. |
| Current result tables | `reports/tables/canonical_native_path_status_matrix.*`; `reports/tables/canonical_native_path_artifact_manifest.json` | results / inventory | Main experiment status, completed rows, blocked rows, evidence routing | Treat as authoritative for current state. |
| Export validation | `reports/tables/canonical_export_validation/*.json` | validation | Validation-first framework contribution; export contract evidence | Use per-row JSONs and manifest for PASS/N/A/blocked status. |
| Accuracy artifacts | `runs/debug_compare/2026-06-20_native_path_expansion/**/accuracy.json`; paths listed in status matrix | results | Accuracy summary tables and Chapter 4/5 comparisons | Use only existing JSONs; do not recalculate by rerunning model pipelines. |
| Explanation/trade-off artifacts | `reports/figures/tradeoff/**/*.csv`; `reports/tables/tradeoff_insights/*.csv`; `reports/tables/optimization_metrics/*.csv` | results / figures | LIR/SEP/ETD trade-off evidence and figures | Prefer canonical six-model bundles for LastFM/ML-1M. |
| Thesis candidate figures | `reports/figures/tradeoff/**/*.png`; `reports/figures/ablation/**/*.svg`; `reports/figures/comparisons/`; `results/figures/` | figures | Chapter 4/5 figures and appendix | Some older folders duplicate canonical bundles; mark uncertain if duplicate. |
| Raw xrecsys outputs | `xrecsys/log/`; `xrecsys/results/`; `xrecsys/paths/` | results / raw exports | Provenance, raw metric and path evidence | Prefer curated reports/tables unless a value is missing. |
| Reproducibility scripts | `scripts/analysis/`; `scripts/validation/`; `scripts/data/canonical/` | scripts | Explain framework implementation and reproducibility design | Do not run training or export scripts that mutate result artifacts. |
| Model/adapters | `adapters/`; `xrecsys/models/`; model-specific folders under `scripts/` | scripts / code | Chapter 3 method description and model scope audit | Do not modify. |
| Historical/archive | `archive/`; `runs/_mirrors/`; `archive/historical_docs/` | archive / provenance | Background, appendix, evolution from post-hoc to native-path framing | Not primary evidence for final experiment status. |

## 生成文件

- `thesis_analysis_pack/goal_0_repo_map.md`
- `thesis_analysis_pack/PROGRESS.md`

## 下一步 Goal

Goal 1: Research positioning. Use `README.md`, `docs/guides/`, `reports/tables/canonical_native_path_status_matrix.md`, and the completion audit to formulate the dissertation as a canonical native-path evaluation framework, derive research questions, and define contributions with evidence paths.
