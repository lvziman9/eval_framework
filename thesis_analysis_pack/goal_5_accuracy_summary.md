
# Goal 5: Accuracy Result Summary

## Goal Number

Goal 5

## Current Task

Extract existing accuracy metrics for completed dataset-model rows, focusing on HR@10, NDCG@10, Precision@10, and Recall@10. Missing or blocked values remain N/A.

## Final Accuracy Summary

| Dataset | Model | HR@10 | NDCG@10 | Precision@10 | Recall@10 | Status | Evidence file path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | 0.186389 | 0.030905 | 0.025356 | 0.017731 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json |
| LastFM | UCPR | 0.216416 | 0.037377 | 0.031129 | 0.023155 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json |
| LastFM | CAFE | 0.180233 | 0.030214 | 0.025718 | 0.018639 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/cafe_lastfm_accuracy.json |
| LastFM | TPRec | 0.188919 | 0.038981 | 0.032736 | 0.022307 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_lastfm_v1/accuracy.json |
| LastFM | KGGLM | 0.125855 | 0.021319 | 0.016409 | 0.014191 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_lastfm_v1/accuracy.json |
| LastFM | PEARLM | 0.099590 | 0.015960 | 0.012736 | 0.009047 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_lastfm_v1/accuracy.json |
| ML-1M | PGPR | 0.511258 | 0.101896 | 0.092914 | 0.042342 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json |
| ML-1M | UCPR | 0.441887 | 0.086215 | 0.066391 | 0.037913 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json |
| ML-1M | CAFE | 0.554305 | 0.116655 | 0.107119 | 0.052024 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/cafe_ml1m_accuracy.json |
| ML-1M | TPRec | 0.474503 | 0.094220 | 0.089702 | 0.043772 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_ml1m_v1/accuracy.json |
| ML-1M | KGGLM | 0.168874 | 0.033649 | 0.019305 | 0.010506 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_ml1m_v1/accuracy.json |
| ML-1M | PEARLM | 0.214735 | 0.035303 | 0.027119 | 0.011040 | Complete + figures | runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_ml1m_v1/accuracy.json |
| Amazon-Book KGAT | KGGLM | 0.012665 | 0.003022 | 0.001383 | 0.004747 | Complete | runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1/accuracy.json |
| Amazon-Book KGAT | PEARLM | 0.029338 | 0.010716 | 0.003100 | 0.015404 | Complete | runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1/accuracy.json |
| Amazon-Book KGAT | PGPR | 0.054851 | 0.015723 | 0.005787 | 0.027237 | Complete | runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json |
| Amazon-Book KGAT | UCPR | N/A | N/A | N/A | N/A | Blocked | Amazon UCPR data view, adapter aliases, runtime schema patch, and preprocess/TransE-forward smokes are PASS; formal training pipeline status=FAILED, stage=line_193, policy=train_agent_amazon_formal_e40_b16_d100, policy_batch=16, beam=25-5-1, run_inference=0; strict full-user export/accuracy still pending |
| Amazon-Book KGAT | CAFE | N/A | N/A | N/A | N/A | Blocked | Needs Amazon schema/data-builder port and compatible UCPR view/TransE checkpoint |
| Amazon-Book KGAT | TPRec | N/A | N/A | N/A | N/A | Blocked | Amazon TPRec structural path constraints/runtime entrypoints are wired; formal temporal TPRec remains blocked because canonical timestamps are sentinel -1 |

## Key Accuracy Findings

- LastFM: best HR@10 is UCPR (0.216416); best NDCG@10 is TPRec (0.038981).
- ML-1M: best HR@10 is CAFE (0.554305); best NDCG@10 is CAFE (0.116655).
- Amazon-Book KGAT: best HR@10 is PGPR (0.054851); best NDCG@10 is PGPR (0.015723).
- Amazon-Book KGAT has complete accuracy rows for KGGLM, PEARLM, and PGPR only; UCPR, CAFE, and TPRec are blocked and must remain N/A.
- Strict accuracy values are taken from the status matrix and the per-row `accuracy.json` evidence paths. They should not be replaced by alpha-sweep CSV metric columns.

## Generated Files

- `thesis_analysis_pack/goal_5_accuracy_summary.md`
- `thesis_analysis_pack/final_accuracy_summary_table.md`

## Next Goal

Goal 6: Explanation metric summary.
