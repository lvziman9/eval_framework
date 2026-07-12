# Chapter 4 Evidence Used

## Evidence Register

| Evidence ID | Repo-relative path | Evidence type | Used in section | Claim supported | Notes |
| --- | --- | --- | --- | --- | --- |
| INT-CH4-001 | `paper/drafts_ch3_6/CHAPTER_BOUNDARY_MAP.md` | Chapter-boundary evidence | 4.1, 4.7 | Chapter 4 contains main results; mechanism, ablation, limitations, and the Amazon boundary case belong to Chapter 5. | Boundary retained. |
| INT-CH4-002 | `paper/drafts_ch3_6/FIGURE_TABLE_MASTER_PLAN.md` | Figure/table planning evidence | 4.2-4.4 | Core Chapter 4 figure numbering and intended evidence roles. | Existing figures only. |
| INT-CH4-003 | `paper/drafts_ch3_6/chapter3_framework_implementation_and_verification_v2.md` | Methodology context | 4.1 | LastFM and ML-1M provide complete six-model native-path comparisons; evidence streams are separated. | Referenced for continuity, not changed. |
| INT-CH4-004 | `thesis_analysis_pack/final_accuracy_summary_table.md` | Strict accuracy evidence | 4.2; Table 4.1 | HR@10, NDCG@10, Precision@10, and Recall@10 for LastFM and ML-1M. | Alpha-sweep values excluded; listed primary JSON paths are not present in the current worktree. |
| INT-CH4-005 | `thesis_analysis_pack/final_explanation_summary_table.md` | Alpha-sweep endpoint evidence | 4.3-4.7; Table 4.2 | LIR, SEP, and ETD endpoints at alpha=0 and alpha=1. | Values come from NDCG alpha-sweep CSVs. |
| INT-CH4-006 | `thesis_analysis_pack/validation_status_table.md` | Validation evidence | 4.1 | The six LastFM and six ML-1M rows pass validation; Amazon is incomplete. | Blocked Amazon rows are not ranked. |
| INT-CH4-007 | `docs/guides/PATH_METRICS_GUIDE.md` | Metric-definition evidence | 4.3-4.6 | LIR measures linked-interaction recency, SEP bridge-entity serendipity, and ETD path-type diversity. | Internal implementation guide; primary publication remains unverified. |
| INT-CH4-008 | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` | Alpha-sweep curve evidence | 4.3-4.6 | LastFM metric endpoints and paired sweep ranking values for LIR, SEP, and ETD. | Canonical promoted six-model bundle. |
| INT-CH4-009 | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` | Alpha-sweep curve evidence | 4.3-4.6 | ML-1M metric endpoints and paired sweep ranking values for LIR, SEP, and ETD. | Canonical promoted six-model bundle. |
| INT-CH4-010 | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | Strict accuracy figure | 4.2; Figure 4.1 | LastFM HR@10 and NDCG@10 comparison. | Existing figure; not regenerated. |
| INT-CH4-011 | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | Strict accuracy figure | 4.2; Figure 4.2 | ML-1M HR@10 and NDCG@10 comparison. | Existing figure; not regenerated. |
| INT-CH4-012 | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Alpha-sweep figure | 4.3; Figure 4.3 | LIR, SEP, and ETD endpoint comparison. | Existing figure; not regenerated. |
| INT-CH4-013 | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | Alpha-sweep figure | 4.4; Figure 4.4 | LIR-NDCG trade-off curves for both main datasets. | Existing figure; not regenerated. |
| INT-CH4-014 | `thesis_analysis_pack/figure_caption_suggestions.md` | Caption-planning evidence | Figure plan | Captions and caveats for canonical trade-off figures. | Chapter placement adapted to the current Goal 3 boundary. |
| INT-CH4-015 | `thesis_analysis_pack/generated_figure_captions.md` | Figure-provenance evidence | Figure plan; Table 4.3 | Data sources and caveats for the four core figures. | No figure generation performed in Goal 3. |
| INT-CH4-016 | `thesis_analysis_pack/goal_10_insight_notes.md` | Prepared result notes | 4.2, 4.7 | Dataset-dependent strict leaders and separation of metric roles. | Mechanism-oriented suggestions were not transferred into Chapter 4. |
| INT-CH4-017 | `thesis_analysis_pack/goal_11_chapter_5_material_pack.md` | Boundary evidence | 4.1, 4.7 | Mechanism analysis, ablation, and Amazon boundary discussion are reserved for Chapter 5. | Used to enforce exclusion, not to draft Chapter 5. |
| INT-CH4-018 | `reports/tables/canonical_native_path_status_matrix.csv` | Accessible strict accuracy evidence | 4.2; Table 4.1 | The same twelve LastFM and ML-1M strict accuracy rows and values reported in the final accuracy summary. | Present in the current worktree and used as the accessible row-level evidence table. |

## Exact Metric Evidence Files

Strict accuracy values are present in both `thesis_analysis_pack/final_accuracy_summary_table.md` and `reports/tables/canonical_native_path_status_matrix.csv`. The latter is the accessible evidence path used in Table 4.1. The source summary also records a primary per-row JSON path for each model, but those JSON files are not present in the current worktree and require manual checking before final submission.

The explanation endpoints and paired sweep NDCG values are taken from these six CSV files:

- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv`
- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.csv`
- `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.csv`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.csv`
- `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.csv`

## Required Input Audit

All files and directories explicitly required by Goal 3 were present and read. The primary strict-accuracy JSON files referenced inside the required summary table were not present in the current worktree; their values were independently matched against the accessible canonical status matrix.

## Unsupported or Uncertain Claims

| Claim | Problem | Action taken | Status |
| --- | --- | --- | --- |
| A primary external publication for the XRecSys LIR/SEP/ETD definitions. | The citation remains unverified in the existing citation audit. | Metric definitions are attributed only to the repository implementation guide; no external citation was invented. | Requires manual check |
| Direct inspection of the twelve primary LastFM and ML-1M strict-accuracy JSON files. | The paths are recorded in the final accuracy summary and status matrix, but the JSON files are absent from the current worktree. | Values were matched between the required summary table and the accessible canonical status matrix; primary JSON provenance still requires manual check. | Requires manual check |
| A complete Amazon-Book KGAT six-model trade-off comparison. | Current evidence contains only three complete rows and no reportable explanation alpha sweeps. | Amazon is excluded from the main Chapter 4 analysis and reserved for Chapter 5. | Unsupported and excluded |
| A causal or mechanism-level explanation for model-specific curve shapes. | Endpoint and curve evidence establish observed behaviour but not causal mechanism. | Chapter 4 reports observations only; mechanism interpretation is deferred to Chapter 5. | Deferred |
| A state-of-the-art or new-recommender-model claim. | Not supported by the dissertation scope or evidence. | No such claim is made. | Excluded |

## Evidence Separation Statement

Strict accuracy evidence, alpha-sweep trade-off evidence, and ablation evidence were kept separate. No ablation values were used in Chapter 4. Native-path explanation results were not conflated with post-hoc explanation; the main comparison contains validated native-path rows only.
