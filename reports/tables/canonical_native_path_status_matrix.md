# Canonical Native-Path Status Matrix

Generated from current workspace artifacts on `2026-06-30` Asia/Singapore.

Machine-readable companion: `reports/tables/canonical_native_path_status_matrix.csv`.

Export validation evidence: `reports/tables/canonical_export_validation/manifest.json`.
The CSV includes per-row `export_evidence` JSON paths.

Amazon classic-model readiness evidence: `reports/tables/amazon_classic_port_readiness.json` and `reports/tables/amazon_classic_port_readiness.md`.

Artifact manifest: `reports/tables/canonical_native_path_artifact_manifest.json`.

This table separates three states:

- `Complete`: formal accuracy/export checks are present and passed.
- `Complete + figures`: formal checks passed and canonical alpha-sweep figures/CSVs are available.
- `Blocked`: not an honest runnable baseline on this dataset until schema/runtime support is added.

Amazon-book alpha-sweep figures are intentionally marked `N/A`: the dataset has no approved canonical timestamp/SEP/ETD denominator yet.

| Dataset | Model | Stage | Users | HR@10 | NDCG@10 | Export validation | Alpha-sweep figures | Primary evidence |
|---|---|---:|---:|---:|---:|---|---|---|
| LastFM | PGPR | Complete + figures | 14,620 | 0.186389 | 0.030905 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json` |
| LastFM | UCPR | Complete + figures | 14,620 | 0.216416 | 0.037377 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json` |
| LastFM | CAFE | Complete + figures | 14,620 | 0.180233 | 0.030214 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/cafe_lastfm_accuracy.json` |
| LastFM | TPRec | Complete + figures | 14,620 | 0.188919 | 0.038981 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_lastfm_v1/accuracy.json` |
| LastFM | KGGLM | Complete + figures | 14,620 | 0.125855 | 0.021319 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_lastfm_v1/accuracy.json` |
| LastFM | PEARLM | Complete + figures | 14,620 | 0.099590 | 0.015960 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_lastfm_v1/accuracy.json` |
| ML-1M | PGPR | Complete + figures | 6,040 | 0.511258 | 0.101896 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json` |
| ML-1M | UCPR | Complete + figures | 6,040 | 0.441887 | 0.086215 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json` |
| ML-1M | CAFE | Complete + figures | 6,040 | 0.554305 | 0.116655 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/cafe_ml1m_accuracy.json` |
| ML-1M | TPRec | Complete + figures | 6,040 | 0.474503 | 0.094220 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/tprec_formal/canonical_ml1m_v1/accuracy.json` |
| ML-1M | KGGLM | Complete + figures | 6,040 | 0.168874 | 0.033649 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_ml1m_v1/accuracy.json` |
| ML-1M | PEARLM | Complete + figures | 6,040 | 0.214735 | 0.035303 | PASS | Complete | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_ml1m_v1/accuracy.json` |
| Amazon-Book KGAT | KGGLM | Complete | 70,591 | 0.012665 | 0.003022 | PASS | N/A | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1/accuracy.json` |
| Amazon-Book KGAT | PEARLM | Complete | 70,591 | 0.029338 | 0.010716 | PASS | N/A | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1/accuracy.json` |
| Amazon-Book KGAT | PGPR | Complete | 70,591 | 0.054851 | 0.015723 | PASS | N/A | `runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json` |
| Amazon-Book KGAT | UCPR | Blocked | N/A | N/A | N/A | N/A | N/A | Amazon UCPR data view, adapter aliases, runtime schema patch, and preprocess/TransE-forward smokes are PASS; formal training pipeline status=FAILED, stage=line_193, policy=train_agent_amazon_formal_e40_b16_d100, policy_batch=16, beam=25-5-1, run_inference=0; strict full-user export/accuracy still pending |
| Amazon-Book KGAT | CAFE | Blocked | N/A | N/A | N/A | N/A | N/A | Needs Amazon schema/data-builder port and compatible UCPR view/TransE checkpoint |
| Amazon-Book KGAT | TPRec | Blocked | N/A | N/A | N/A | N/A | N/A | Amazon TPRec structural path constraints/runtime entrypoints are wired; formal temporal TPRec remains blocked because canonical timestamps are sentinel -1 |

## Figure and export bundles

| Bundle | Status | Files | Evidence |
|---|---:|---:|---|
| LastFM six-model alpha-sweep bundle | Complete | 12 PNG + 12 CSV | `reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model` |
| ML-1M six-model alpha-sweep bundle | Complete | 12 PNG + 12 CSV | `reports/figures/tradeoff/canonical_ml1m_native_paths_v2` |
| Amazon KGGLM native-path export | Complete | 4,412 shards | `runs/debug_compare/2026-06-20_native_path_expansion/kgglm_formal/canonical_amazon_book_kgat_v1` |
| Amazon PEARLM native-path export | Complete | 4,412 shards | `runs/debug_compare/2026-06-20_native_path_expansion/pearlm_formal_bestval10/canonical_amazon_book_kgat_v1` |
| Amazon PGPR native-path export | Complete | 4,109,983 rows | `xrecsys/paths/amazon_book_kgat_v1/agent_topk=pgpr-amazon-formal-e50_a250_beam10-12-1` |

## Amazon formal comparison

| Model | Users | Raw paths | Pred-path rows | Explanations | HR@10 | NDCG@10 | Slot coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| KGGLM | 70,591 | 1,327,552 | 1,326,486 | 655,285 | 0.012665 | 0.003022 | 0.928284 |
| PEARLM | 70,591 | 887,376 | 885,270 | 578,518 | 0.029338 | 0.010716 | 0.819535 |
| PGPR | 70,591 | 4,109,983 | 4,109,983 | 705,846 | 0.054851 | 0.015723 | 0.999909 |

## Amazon classic-port acceptance criteria

The remaining Amazon UCPR/CAFE/TPRec rows are blocked rather than failed.
A future port should be treated as a schema/runtime task with the following
acceptance gates before any formal comparison is reported.

Shared gates:

- define one approved Amazon product/entity/relation projection from
  `canonical_amazon_book_kgat_v1`;
- preserve canonical train/valid/test label semantics and prove remaps back to
  canonical user/item ids;
- produce a smoke export with native paths and `include-all-test-users`
  behavior;
- pass `validate_xrecsys_export.py --require-all-test-users`;
- pass `evaluate_uid_topk.py` with strict full-user coverage, allowing only
  naturally short recommendation lists;
- document whether Amazon alpha-sweeps remain `N/A` or become reportable under
  an approved timestamp/SEP/ETD denominator.

Model-specific gates:

| Model | Required porting work before launch |
|---|---|
| UCPR | Amazon data view, adapter book aliases, runtime schema patch, isolated preprocess smoke, and one-batch TransE forward/backward smoke now pass; next run TransE/policy training, native-path export, and strict full-user validation before formal reporting. |
| CAFE | Build on the compatible Amazon UCPR view and UCPR TransE checkpoint; add executable Amazon CAFE schema/metapaths and verify non-empty native path execution. |
| TPRec | Amazon relation-token path constraints, CLI choices, export aliases, and the pipeline case are wired; the default Amazon pipeline stops at the timestamp gate because all canonical timestamps are sentinel `-1`. Formal TPRec needs real timestamps or an explicitly labeled non-temporal ablation protocol. |
