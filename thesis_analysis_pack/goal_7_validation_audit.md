
# Goal 7: Validation and Quality-Control Audit

## Goal Number

Goal 7

## Current Task

Find export, canonical, and path validation evidence; summarize passed, blocked, and N/A cases; and explain validation-first evaluation as a dissertation contribution.

## Validation Status Table

| Dataset | Model | Validation status | Canonical test users | Top-k users | Pred-path rows | Explanation rows | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lastfm | PGPR | PASS | 14620 | 14620 | 11695015 | 145390 | reports/tables/canonical_export_validation/lastfm_pgpr.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| lastfm | UCPR | PASS | 14620 | 14620 | 5294784 | 140318 | reports/tables/canonical_export_validation/lastfm_ucpr.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| lastfm | CAFE | PASS | 14620 | 14620 | 2056564 | 145440 | reports/tables/canonical_export_validation/lastfm_cafe.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| lastfm | TPRec | PASS | 14620 | 14620 | 1928716 | 138067 | reports/tables/canonical_export_validation/lastfm_tprec.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| lastfm | KGGLM | PASS | 14620 | 14620 | 191102 | 128496 | reports/tables/canonical_export_validation/lastfm_kgglm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| lastfm | PEARLM | PASS | 14620 | 14620 | 183538 | 126145 | reports/tables/canonical_export_validation/lastfm_pearlm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | PGPR | PASS | 6040 | 6040 | 5457838 | 60400 | reports/tables/canonical_export_validation/ml1m_pgpr.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | UCPR | PASS | 6040 | 6040 | 2543087 | 50022 | reports/tables/canonical_export_validation/ml1m_ucpr.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | CAFE | PASS | 6040 | 6040 | 2349585 | 60400 | reports/tables/canonical_export_validation/ml1m_cafe.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | TPRec | PASS | 6040 | 6040 | 4218974 | 60399 | reports/tables/canonical_export_validation/ml1m_tprec.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | KGGLM | PASS | 6040 | 6040 | 18761 | 18761 | reports/tables/canonical_export_validation/ml1m_kgglm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| ml1m | PEARLM | PASS | 6040 | 6040 | 44986 | 38798 | reports/tables/canonical_export_validation/ml1m_pearlm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| amazon_book_kgat_v1 | KGGLM | PASS | 70591 | 70591 | 1326486 | 655285 | reports/tables/canonical_export_validation/amazon_book_kgat_v1_kgglm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| amazon_book_kgat_v1 | PEARLM | PASS | 70591 | 70591 | 885270 | 578518 | reports/tables/canonical_export_validation/amazon_book_kgat_v1_pearlm.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| amazon_book_kgat_v1 | PGPR | PASS | 70591 | 70591 | 4109983 | 705846 | reports/tables/canonical_export_validation/amazon_book_kgat_v1_pgpr.json | Exact test-user coverage in top-k export; path endpoint and top-k/explanation consistency enforced by validation script. |
| Amazon-Book KGAT | UCPR | BLOCKED / N/A | N/A | N/A | N/A | N/A | reports/tables/amazon_classic_port_readiness.json | Amazon UCPR data view, adapter aliases, runtime schema patch, and preprocess/TransE-forward smokes are PASS; formal training pipeline status=FAILED, stage=line_193, policy=train_agent_amazon_formal_e40_b16_d100, policy_batch=16, beam=25-5-1, run_inference=0; strict full-user export/accuracy still pending |
| Amazon-Book KGAT | CAFE | BLOCKED / N/A | N/A | N/A | N/A | N/A | reports/tables/amazon_classic_port_readiness.json | Needs Amazon schema/data-builder port and compatible UCPR view/TransE checkpoint |
| Amazon-Book KGAT | TPRec | BLOCKED / N/A | N/A | N/A | N/A | N/A | reports/tables/amazon_classic_port_readiness.json | Amazon TPRec structural path constraints/runtime entrypoints are wired; formal temporal TPRec remains blocked because canonical timestamps are sentinel -1 |

## Validation Gates Evidenced in Repository

- Canonical user coverage: `scripts/validation/validate_xrecsys_export.py` checks that `uid_topk.csv` covers the exact canonical test-user set when `require_all_test_users` is enabled.
- UID/PID endpoint consistency: the same validator parses each path and checks that it starts with the expected user and ends with the expected product type and pid.
- Seen-item leakage: both `validate_xrecsys_export.py` and `evaluate_uid_topk.py` reject training/validation items appearing in recommendations.
- Top-k/explanation consistency: `uid_topk.csv` and `uid_pid_explanation.csv` must contain the same recommended `(uid, pid)` pairs.
- Path score sanity: `pred_paths.csv` `path_score` and `path_prob` must be finite and within the expected range.
- Short-list policy: `evaluate_uid_topk.py` supports explicit short lists while preserving the denominator and counting missing slots as non-hits.

## Why This Matters

Native-path explainability is meaningful only when the path is faithful to the recommendation output and valid under canonical user/item ids. The validation gate is therefore not an implementation detail; it is part of the evaluation framework's research contribution. It prevents invalid path endpoints, missing users, seen-item leakage, and post-hoc explanation substitution from entering Chapter 4/5 claims.

## Generated Files

- `thesis_analysis_pack/goal_7_validation_audit.md`
- `thesis_analysis_pack/validation_status_table.md`

## Next Goal

Goal 8: Existing figure inventory.
