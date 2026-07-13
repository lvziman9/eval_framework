# Goal 3 Cleanup Status

## Outcome

Goal 3 cleanup retry is complete. The Chapter 4 draft package was physically rewritten to use explicit Markdown line structure suitable for continued drafting and later Word import.

## Files Audited

- `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`
- `paper/drafts_ch3_6/chapter4_tables.md`
- `paper/drafts_ch3_6/chapter4_figure_plan.md`
- `paper/drafts_ch3_6/chapter4_evidence_used.md`
- `paper/drafts_ch3_6/GOAL_3_CLEANUP_STATUS.md`
- `paper/drafts_ch3_6/THESIS_WRITING_TRACEABILITY_LOG.md`

## Files Rewritten

- `paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md`
- `paper/drafts_ch3_6/chapter4_tables.md`
- `paper/drafts_ch3_6/chapter4_figure_plan.md`
- `paper/drafts_ch3_6/chapter4_evidence_used.md`
- `paper/drafts_ch3_6/THESIS_WRITING_TRACEABILITY_LOG.md`
- `paper/drafts_ch3_6/GOAL_3_CLEANUP_STATUS.md`

## Formatting Actions

- Reflowed the Chapter 4 body into explicit physical lines while preserving paragraph boundaries.
- Kept every heading on an independent line with a blank line before the following content.
- Rewrote every table separator as explicit standard pipe-table syntax.
- Preserved one physical Markdown line per table row.
- Kept all table captions as independent paragraphs outside their tables.
- Kept all figure captions as independent paragraphs.
- Rewrote traceability table separators without changing any claim row or claim status.

## Content Preservation Audit

| Check | Result |
| --- | --- |
| Experimental facts and conclusions unchanged | Pass |
| Experimental numbers unchanged | Pass |
| Evidence paths unchanged | Pass |
| Chapter and section boundaries unchanged | Pass |
| Figure and table numbering unchanged | Pass |
| Citation status unchanged | Pass |
| Existing claim statuses unchanged | Pass |
| Chapter 5 content not added | Pass |

## Required Command Checks

### Chapter Heading Check

Command:

```bash
grep -n "## 4." paper/drafts_ch3_6/chapter4_accuracy_explainability_tradeoff_results_v1.md
```

Output:

```text
3:## 4.1 Experimental Scope and Result Organisation
24:## 4.2 Strict Accuracy Results
42:## 4.3 Explanation Metric Endpoint Results
62:## 4.4 LIR-oriented Trade-off Results
83:## 4.5 SEP-oriented Trade-off Results
103:## 4.6 ETD-oriented Trade-off Results
122:## 4.7 Cross-Dataset Comparison
```

### Chapter Table Check

Command:

```bash
head -n 20 paper/drafts_ch3_6/chapter4_tables.md
```

Output:

```text
# Chapter 4 Tables

## Table 4.1 Strict Accuracy Results on LastFM and ML-1M

| Dataset | Model | HR@10 | NDCG@10 | Precision@10 | Recall@10 | Evidence path |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| LastFM | PGPR | 0.186389 | 0.030905 | 0.025356 | 0.017731 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | UCPR | 0.216416 | 0.037377 | 0.031129 | 0.023155 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | CAFE | 0.180233 | 0.030214 | 0.025718 | 0.018639 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | TPRec | 0.188919 | 0.038981 | 0.032736 | 0.022307 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | KGGLM | 0.125855 | 0.021319 | 0.016409 | 0.014191 | `reports/tables/canonical_native_path_status_matrix.csv` |
| LastFM | PEARLM | 0.099590 | 0.015960 | 0.012736 | 0.009047 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | PGPR | 0.511258 | 0.101896 | 0.092914 | 0.042342 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | UCPR | 0.441887 | 0.086215 | 0.066391 | 0.037913 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | CAFE | 0.554305 | 0.116655 | 0.107119 | 0.052024 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | TPRec | 0.474503 | 0.094220 | 0.089702 | 0.043772 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | KGGLM | 0.168874 | 0.033649 | 0.019305 | 0.010506 | `reports/tables/canonical_native_path_status_matrix.csv` |
| ML-1M | PEARLM | 0.214735 | 0.035303 | 0.027119 | 0.011040 | `reports/tables/canonical_native_path_status_matrix.csv` |

**Table 4.1.** Strict top-10 accuracy results for the six validated native-path model rows on LastFM and ML-1M. Values are present in both `thesis_analysis_pack/final_accuracy_summary_table.md` and the accessible canonical status matrix; they are not alpha-sweep values.
```

### Figure Plan Table Check

Command:

```bash
head -n 20 paper/drafts_ch3_6/chapter4_figure_plan.md
```

Output:

```text
# Chapter 4 Figure Plan

## Core Figures

| Figure | Title | Existing file | Data source | Intended section | Status | Caveat |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Figure 4.1 | LastFM accuracy comparison | `reports/figures/thesis_final/lastfm_accuracy_hr_ndcg.png` | Strict per-row accuracy evidence indexed by `reports/tables/canonical_native_path_status_matrix.csv` | 4.2 | Existing; use without regeneration | Displays HR@10 and NDCG@10 only; Table 4.1 supplies Precision@10 and Recall@10. |
| Figure 4.2 | ML-1M accuracy comparison | `reports/figures/thesis_final/ml1m_accuracy_hr_ndcg.png` | Strict per-row accuracy evidence indexed by `reports/tables/canonical_native_path_status_matrix.csv` | 4.2 | Existing; use without regeneration | Displays HR@10 and NDCG@10 only; Table 4.1 supplies Precision@10 and Recall@10. |
| Figure 4.3 | Explanation metric alpha endpoints | `reports/figures/thesis_final/explanation_metric_alpha_endpoints.png` | Canonical LastFM v4 six-model and ML-1M v2 LIR/SEP/ETD NDCG alpha-sweep CSVs | 4.3 | Existing; use without regeneration | Endpoints are alpha-sweep evidence, not strict accuracy. |
| Figure 4.4 | LIR-NDCG trade-off | `reports/figures/thesis_final/lir_ndcg_tradeoff_lastfm_ml1m.png` | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_LIR_ndcg_models.csv`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_LIR_ndcg_models.csv` | 4.4 | Existing; use without regeneration | NDCG is the alpha-sweep ranking metric and must remain separate from strict NDCG@10. |

## Optional or Appendix Figures

| Figure | Title | Existing files | Intended section | Status | Selection note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Optional Figure 4.5 | SEP-oriented trade-off results | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_SEP_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_SEP_ndcg_models.png` | 4.5 or appendix | Existing; no composite figure generated | Use as two dataset panels if the final chapter has space; otherwise retain as appendix candidates. |
| Optional Figure 4.6 | ETD-oriented trade-off results | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/tradeoff_lastfm_ETD_ndcg_models.png`; `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/tradeoff_ml1m_ETD_ndcg_models.png` | 4.6 or appendix | Existing; no composite figure generated | Use as two dataset panels if the final chapter has space; otherwise retain as appendix candidates. |

## Draft Captions
```

## Remaining Evidence Issues

- The primary external publication for the XRecSys LIR/SEP/ETD definitions still requires manual verification.
- The twelve primary strict-accuracy JSON paths recorded by the summary table are not present in the current worktree; their values match the accessible canonical status matrix, but primary JSON provenance still requires manual checking.
- Amazon-Book KGAT still lacks a complete six-model explanation alpha-sweep result set and remains excluded from the main Chapter 4 analysis.
- Causal explanations for model-specific trade-off curves remain deferred to Chapter 5.

## Pause Point

The Chapter 4 package is formatting-ready for continued writing and later Word import. Goal 4 may begin when explicitly requested. Chapter 5 was not entered during this cleanup retry.
