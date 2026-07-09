
# Goal 4: Final Result File Inventory

## Goal Number

Goal 4

## Current Task

Locate final/canonical/native-path/accuracy/explanation/validation artifacts and explain how each should support the dissertation.

## Inventory

| File path | File type | Dataset | Model | Metrics included | Can be used in Chapter 4 or Chapter 5? | Notes / caveats |
| --- | --- | --- | --- | --- | --- | --- |
| reports/tables/canonical_native_path_status_matrix.csv | CSV | All | All | Stage, users, HR@10, NDCG@10, Precision@10, Recall@10, validation, evidence paths | Chapter 4 and 5 | Primary machine-readable final status table. |
| reports/tables/canonical_export_validation/manifest.json | JSON | All complete rows | 15 complete rows | canonical users, top-k users, pred path rows, explanation rows, status | Chapter 3, 4, and 5 | Validation-first evidence; use with per-row JSON summaries. |
| reports/tables/amazon_classic_port_readiness.json | JSON | Amazon-Book KGAT | PGPR, UCPR, CAFE, TPRec | Readiness checks, blockers, required next steps | Chapter 5 limitations | Use to justify blocked rows; current status is BLOCKED overall with PGPR ready and UCPR/CAFE/TPRec blocked. |
| runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json | JSON | LastFM | PGPR | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_pgpr.json | JSON | LastFM | PGPR | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json | JSON | LastFM | UCPR | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_ucpr.json | JSON | LastFM | UCPR | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/cafe_lastfm_accuracy.json | JSON | LastFM | CAFE | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_cafe.json | JSON | LastFM | CAFE | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_lastfm_v1/accuracy.json | JSON | LastFM | TPRec | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_tprec.json | JSON | LastFM | TPRec | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_lastfm_v1/accuracy.json | JSON | LastFM | KGGLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_kgglm.json | JSON | LastFM | KGGLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_lastfm_v1/accuracy.json | JSON | LastFM | PEARLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/lastfm_pearlm.json | JSON | LastFM | PEARLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json | JSON | ML-1M | PGPR | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_pgpr.json | JSON | ML-1M | PGPR | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json | JSON | ML-1M | UCPR | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_ucpr.json | JSON | ML-1M | UCPR | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/cafe_ml1m_accuracy.json | JSON | ML-1M | CAFE | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_cafe.json | JSON | ML-1M | CAFE | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_ml1m_v1/accuracy.json | JSON | ML-1M | TPRec | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_tprec.json | JSON | ML-1M | TPRec | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_ml1m_v1/accuracy.json | JSON | ML-1M | KGGLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_kgglm.json | JSON | ML-1M | KGGLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_ml1m_v1/accuracy.json | JSON | ML-1M | PEARLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Status: Complete + figures; validation: PASS |
| reports/tables/canonical_export_validation/ml1m_pearlm.json | JSON | ML-1M | PEARLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1/accuracy.json | JSON | Amazon-Book KGAT | KGGLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Amazon alpha-sweep N/A until approved timestamp/SEP/ETD denominator exists |
| reports/tables/canonical_export_validation/amazon_book_kgat_v1_kgglm.json | JSON | Amazon-Book KGAT | KGGLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1/accuracy.json | JSON | Amazon-Book KGAT | PEARLM | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Amazon alpha-sweep N/A until approved timestamp/SEP/ETD denominator exists |
| reports/tables/canonical_export_validation/amazon_book_kgat_v1_pearlm.json | JSON | Amazon-Book KGAT | PEARLM | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json | JSON | Amazon-Book KGAT | PGPR | HR@10, NDCG@10, Precision@10, Recall@10 | Chapter 4 | Amazon alpha-sweep N/A until approved timestamp/SEP/ETD denominator exists |
| reports/tables/canonical_export_validation/amazon_book_kgat_v1_pgpr.json | JSON | Amazon-Book KGAT | PGPR | Export validation: canonical users, top-k users, pred paths, explanations | Chapter 3/4 validation | Per-row validation evidence. |
| N/A | N/A | Amazon-Book KGAT | UCPR | N/A | Chapter 5 limitations | Amazon UCPR data view, adapter aliases, runtime schema patch, and preprocess/TransE-forward smokes are PASS; formal training pipeline status=FAILED, stage=line_193, policy=train_agent_amazon_formal_e40_b16_d100, policy_batch=16, beam=25-5-1, run_inference=0; strict full-user export/accuracy still pending |
| N/A | N/A | Amazon-Book KGAT | CAFE | N/A | Chapter 5 limitations | Needs Amazon schema/data-builder port and compatible UCPR view/TransE checkpoint |
| N/A | N/A | Amazon-Book KGAT | TPRec | N/A | Chapter 5 limitations | Amazon TPRec structural path constraints/runtime entrypoints are wired; formal temporal TPRec remains blocked because canonical timestamps are sentinel -1 |
| reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/ | PNG + CSV bundle | LastFM | Six native-path models | LIR/SEP/ETD versus HR/NDCG/Precision/Recall alpha sweeps | Chapter 4 and 5 | Canonical figure bundle; prefer over older duplicate LastFM folders. |
| reports/figures/tradeoff/canonical_ml1m_native_paths_v2/ | PNG + CSV bundle | ML-1M | Six native-path models | LIR/SEP/ETD versus HR/NDCG/Precision/Recall alpha sweeps | Chapter 4 and 5 | Canonical figure bundle; prefer over older duplicate ML-1M folders. |
| reports/tables/tradeoff_insights/ml1m_canonical_language_model_ndcg_tradeoff_summary.csv | CSV | ML-1M | KGGLM, PEARLM | Language-model trade-off endpoint summary | Appendix or Chapter 5 | Useful for language-model-specific discussion; not a replacement for status matrix accuracy. |

## Selection Guidance

1. Use `reports/tables/canonical_native_path_status_matrix.csv` as the main index for final rows and evidence paths.
2. Use per-row `accuracy.json` files for strict top-k accuracy values.
3. Use `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model/` and `reports/figures/tradeoff/canonical_ml1m_native_paths_v2/` for explanation trade-off figures and CSVs.
4. Use `reports/tables/canonical_export_validation/manifest.json` and per-row validation JSONs for validation claims.
5. Treat older duplicate figure folders as uncertain unless the dissertation specifically needs historical evolution.
6. Treat Amazon-Book KGAT explanation alpha sweeps as N/A until an approved timestamp/SEP/ETD denominator exists.

## Generated Files

- `thesis_analysis_pack/goal_4_result_file_inventory.md`

## Next Goal

Goal 5: Accuracy result summary.
