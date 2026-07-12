# Chapter 3 Tables

## Table 3.1 Canonical Dataset and Model-View Design Requirements

| Requirement | Description | Evidence |
| --- | --- | --- |
| Canonical users and products | Each dataset defines the user and item identifiers used for evaluation. | `docs/guides/CANONICAL_DATASET_STANDARD.md` |
| Shared interaction splits | Train, validation, and test interactions are defined at the canonical layer. | `docs/guides/CANONICAL_DATASET_STANDARD.md` |
| Evaluation labels | Canonical labels are used by the evaluation layer. | `docs/guides/CANONICAL_DATASET_STANDARD.md` |
| KG provenance | The upstream KG source and model-specific projections are documented. | `docs/guides/CANONICAL_DATASET_STANDARD.md`; `docs/guides/DATA_PROVENANCE.md` |
| Model-specific views | Models may remap or filter internal graph representations. | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` |
| Canonical export mapping | Exported recommendations and paths must map back to canonical `uid/pid`. | `docs/guides/CANONICAL_DATASET_STANDARD.md` |

## Table 3.2 Native-Path Export Contract

| File | Required for native-path models | Required for accuracy-only references | Purpose | Evidence |
| --- | --- | --- | --- | --- |
| `uid_topk.csv` | Yes | Yes | Stores ranked top-k recommendations by canonical user. | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` |
| `pred_paths.csv` | Yes | No | Stores recommendation path candidates or selected paths. | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` |
| `uid_pid_explanation.csv` | Yes | No | Stores the explanation path for each user-item recommendation. | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md`; `docs/guides/PATH_METRICS_GUIDE.md` |

## Table 3.3 Evaluation Metrics

| Metric | Category | Input evidence | Interpretation boundary |
| --- | --- | --- | --- |
| HR@10 | Strict accuracy | `uid_topk.csv`; canonical labels | Main ranking accuracy metric. |
| NDCG@10 | Strict accuracy | `uid_topk.csv`; canonical labels | Ranking quality with position discount. |
| Precision@10 | Strict accuracy | `uid_topk.csv`; canonical labels | Fraction of top-10 recommendations that are relevant. |
| Recall@10 | Strict accuracy | `uid_topk.csv`; canonical labels | Fraction of relevant items recovered in top-10. |
| LIR | Explanation metric | Native path and training timestamps | Linked interaction recency; alpha-sweep evidence only in later trade-off analysis. |
| SEP | Explanation metric | Native path and KG degree data | Serendipity of explanation bridge entity. |
| ETD | Explanation metric | Native path relation type | Diversity of explanation path types. |

## Table 3.4 Validation Checks

| Check | Purpose | Evidence |
| --- | --- | --- |
| Canonical test-user coverage | Ensures all expected test users are represented. | `thesis_analysis_pack/validation_status_table.md` |
| Top-k user coverage | Confirms recommendation lists exist for the canonical test-user set. | `thesis_analysis_pack/validation_status_table.md` |
| Duplicate recommendation check | Prevents repeated top-k items from inflating metrics. | `scripts/validation/validate_xrecsys_export.py` |
| Seen-item leakage check | Checks that training items are not improperly reported as recommendations. | `scripts/validation/validate_xrecsys_export.py` |
| Path endpoint consistency | Confirms paths start and end at the expected user/item. | `scripts/validation/validate_xrecsys_export.py` |
| Top-k/explanation alignment | Confirms explanations correspond to reported recommendations. | `scripts/validation/validate_xrecsys_export.py` |
| Score-range validity | Checks metric and score ranges where applicable. | `scripts/validation/validate_xrecsys_export.py` |

## Table 3.5 Framework Verification Summary

| Dataset | Complete rows | Blocked / N/A rows | Verification interpretation | Evidence |
| --- | --- | --- | --- | --- |
| LastFM | PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM | None in main six-model scope | Complete main dataset. | `thesis_analysis_pack/validation_status_table.md` |
| ML-1M | PGPR, UCPR, CAFE, TPRec, KGGLM, PEARLM | None in main six-model scope | Complete main dataset. | `thesis_analysis_pack/validation_status_table.md` |
| Amazon-Book KGAT | KGGLM, PEARLM, PGPR | UCPR, CAFE, TPRec | Partial stress test / boundary case. | `thesis_analysis_pack/validation_status_table.md`; `reports/tables/amazon_classic_port_readiness.json` |

## Table 3.6 Trade-off and Ablation Experiment Design

| Evidence category | Source | Used for | Must not be used for |
| --- | --- | --- | --- |
| Strict accuracy | `thesis_analysis_pack/final_accuracy_summary_table.md`; accuracy JSONs | Main accuracy comparison. | Replacing alpha-sweep trade-off curves. |
| Explanation endpoints | `thesis_analysis_pack/final_explanation_summary_table.md`; trade-off CSVs | Endpoint verification and explanation summary. | Strict accuracy reporting. |
| Alpha-sweep curves | Canonical LastFM and ML-1M trade-off CSV/figure bundles | Accuracy-explainability trade-off analysis. | Claiming state-of-the-art model performance. |
| Ablation tables | `reports/tables/ablation/pgpr_ucpr_path_module/` | Chapter 5 controllability and mechanism analysis. | Main six-model comparison. |
| Amazon readiness/status | `reports/tables/amazon_classic_port_readiness.json`; status matrix | Boundary-case discussion. | Complete main trade-off experiment. |

## Table 3.7 Representative Alpha-Sweep Endpoint Verification Examples

| Dataset | Model | Metric | Alpha=0 | Alpha=1 | Evidence | Interpretation limit |
| --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 0.0062 | 0.0219 | `thesis_analysis_pack/final_explanation_summary_table.md` | Endpoint verification only; not strict accuracy. |
| LastFM | CAFE | SEP | 0.7308 | 0.9890 | `thesis_analysis_pack/final_explanation_summary_table.md` | Endpoint verification only; not strict accuracy. |
| ML-1M | PGPR | LIR | 0.4655 | 0.9627 | `thesis_analysis_pack/final_explanation_summary_table.md` | Endpoint verification only; not strict accuracy. |
| ML-1M | CAFE | ETD | 0.2902 | 0.8542 | `thesis_analysis_pack/final_explanation_summary_table.md` | Endpoint verification only; not strict accuracy. |

