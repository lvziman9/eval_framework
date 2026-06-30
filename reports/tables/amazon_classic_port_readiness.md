# Amazon Classic Native-Path Port Readiness

Generated at `2026-06-30T08:52:16.361828+00:00`.

Dataset: `canonical_amazon_book_kgat_v1`.

Overall status: `BLOCKED`.

This report is intentionally a readiness gate, not an accuracy result. A blocked row means the model is not yet an honest runnable Amazon-book KGAT baseline.

| Model | Readiness | Checks passed | Failed gates | Required next actions |
|---|---:|---:|---|---|
| PGPR | Ready | 12/12 | None | No further PGPR Amazon action required for the current formal row.<br>Do not launch larger PGPR Amazon variants unless explicitly approved. |
| UCPR | Blocked | 7/8 | Formal Amazon UCPR export and accuracy validation exist | Do not relaunch UCPR Amazon policy training on the shared server by default.<br>Resume only with an explicitly approved smaller protocol or dedicated high-memory GPU allocation.<br>If resumed, require policy completion, full-user streaming export, strict export validation, and strict accuracy validation before formal reporting. |
| CAFE | Blocked | 0/2 | DATASET_CONFIG includes Amazon<br>CLI model-dataset choices include an Amazon option | Build a compatible Amazon UCPR view first.<br>Add executable Amazon CAFE entity/relation schema and metapaths.<br>Validate that CAFE emits non-empty native paths mapped back to canonical uid/pid. |
| TPRec | Blocked | 5/6 | Amazon timestamps support formal TPRec temporal rewards | Keep Amazon TPRec formal reporting blocked while canonical timestamps are sentinel -1.<br>Either rebuild Amazon-book KGAT with real interaction timestamps or define an explicitly labeled non-temporal TPRec ablation protocol.<br>Only after timestamp semantics are approved, run full TPRec training/export with strict full-user validation. |

## Check evidence

| Model | Check | Result | Evidence |
|---|---|---:|---|
| PGPR | RELATION_FILES includes amazon_book_kgat_v1 or amazon | PASS | available keys=['amazon_book_kgat_v1', 'lastfm', 'ml1m'] |
| PGPR | PRODUCT_ENTITIES includes Amazon book entity | PASS | available keys=['amazon_book_kgat_v1', 'lastfm', 'ml1m'] |
| PGPR | CLI model-dataset choices include an Amazon option | PASS | parser choices are derived from RELATION_FILES keys=['amazon_book_kgat_v1', 'lastfm', 'ml1m'] |
| PGPR | Generated Amazon PGPR view round-trips canonical labels | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_view_metadata.json exact_splits=['test', 'train', 'valid'] |
| PGPR | Isolated Amazon PGPR runtime preprocess smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_runtime_preprocess_smoke.json status=PASS split_exact={'train': True, 'test': True} core_files_exist=True |
| PGPR | Amazon PGPR TransE one-batch forward/backward smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_forward_smoke.json status=PASS batch_shape=[64, 11] loss=18.71475601196289 gradient_tensors=21 |
| PGPR | Amazon PGPR TransE training smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_transe_training_smoke.json status=PASS epoch=1 embed_size_ok=True checkpoint_exists=True embedding_exists=True |
| PGPR | Amazon PGPR policy environment and beam smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_env_smoke.json status=PASS manual_pattern_ok=True beam_path_count=4 beam_book_endings=4 |
| PGPR | Amazon PGPR policy training smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_training_smoke.json status=PASS epoch=1 run_name=train_agent_amazon_smoke_e1_a250_h32-16 checkpoint_exists=True shape_checks={'actor.weight': True, 'critic.weight': True, 'l1.weight': True, 'l2.weight': True} |
| PGPR | Amazon PGPR policy inference smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_policy_inference_smoke.json status=PASS users=8 path_count=191 book_ending_path_count=170 finite_probability_rows=191/191 |
| PGPR | Amazon PGPR adapter/export smoke validation passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/pgpr/pgpr_export_smoke_validation.json status=PASS pred_path_rows=166 candidate_users=8 explanations=80 require_all_test_users=False |
| PGPR | Formal Amazon PGPR export and accuracy validation exist | PASS | runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_export_validation.json status=PASS; runs/debug_compare/2026-06-20_native_path_expansion/pgpr_amazon_book_kgat_accuracy.json status=PASS |
| UCPR | DATASET_CONFIG includes Amazon | PASS | available keys=['amazon_book_kgat_v1', 'lastfm', 'ml1m'] |
| UCPR | CLI model-dataset choices include an Amazon option | PASS | parser choices are derived from DATASET_CONFIG |
| UCPR | Generated Amazon UCPR view round-trips canonical labels | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/preprocessed/ucpr_view_metadata.json exact_splits=['test', 'train', 'valid'] users=70679 products=24915 relations=9 skipped={'test': 0, 'train': 0, 'valid': 0} |
| UCPR | UCPR adapter supports Amazon book path aliases | PASS | adapters/ucpr_adapter.py maps Amazon UCPR product paths to canonical book endpoints and strips relation suffixes=True |
| UCPR | Active UCPR runtime supports Amazon path semantics | PASS | scripts/model_patches/patch_ucpr_amazon_runtime.py has Amazon runtime constants/path-pattern patch=True |
| UCPR | Isolated Amazon UCPR runtime preprocess smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_runtime_preprocess_smoke.json status=PASS exact_splits=['test', 'train', 'valid'] review_rows=581835 user_purchase_edges=581835 |
| UCPR | Amazon UCPR TransE one-batch forward/backward smoke passes | PASS | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/ucpr/ucpr_transe_forward_smoke.json status=PASS batch_shape=[64, 11] loss=24.95353126525879 gradient_tensors=21 relations=10 |
| UCPR | Formal Amazon UCPR export and accuracy validation exist | FAIL | missing formal outputs: ['runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_export_validation.json', 'runs/debug_compare/2026-06-20_native_path_expansion/ucpr_amazon_book_kgat_accuracy.json'] |
| CAFE | DATASET_CONFIG includes Amazon | FAIL | available keys=['lastfm', 'ml1m'] |
| CAFE | CLI model-dataset choices include an Amazon option | FAIL | parser choices are derived from DATASET_CONFIG |
| TPRec | canonical_path_constraints supports canonical_amazon_book_kgat_v1 | PASS | tprec_runtime.py defines Amazon relation-token path constraints |
| TPRec | run_canonical_tprec.py CLI accepts canonical_amazon_book_kgat_v1 | PASS | run_canonical_tprec.py parser choices include Amazon |
| TPRec | export_tprec_paths.py aliases canonical_amazon_book_kgat_v1 | PASS | export_tprec_paths.py maps Amazon products to canonical book endpoints |
| TPRec | pipeline case statement supports canonical_amazon_book_kgat_v1 | PASS | run_canonical_tprec_pipeline.sh contains an Amazon case with a timestamp gate |
| TPRec | Hopwise Amazon view is present and preserves interactions/KG | PASS | runs/debug_compare/2026-06-20_native_path_expansion/hopwise_data/canonical_amazon_book_kgat_v1/hopwise_view_manifest.json status=PASS kept_link_rows=24915 dropped_link_rows=0 |
| TPRec | Amazon timestamps support formal TPRec temporal rewards | FAIL | runs/debug_compare/2026-06-20_native_path_expansion/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json status=BLOCKED formal_temporal_reward_approved=False timestamp_policy=-1 train_sentinel_fraction=1.0 |

