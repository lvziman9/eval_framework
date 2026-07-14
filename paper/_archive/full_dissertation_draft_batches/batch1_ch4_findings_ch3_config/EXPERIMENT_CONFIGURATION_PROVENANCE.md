# Experiment Configuration Provenance

## 1. Summary

This audit distinguishes configuration declared in accessible scripts from configuration recorded only in implementation logs or export tags. The repository contains no top-level `configs/`, `config/`, `conf/`, `models/`, `src/`, or `exports/` directory in the current worktree. The accessible sources are concentrated in `scripts/`, `reports/`, the registered thesis evidence pack, and tracked implementation guides.

The six-model LastFM and ML-1M output registry is accessible, but the historical `runs/debug_compare/` tree and `xrecsys/paths/` artifacts referenced by that registry are not present. Consequently, validated output identities and several declared model settings can be documented, but the exact checkpoint files, checkpoint hashes, and complete model-native hyperparameter sets cannot all be re-inspected. Missing values are reported as **not available in the current evidence package** rather than reconstructed from model names or expected defaults.

## 2. Configuration Evidence Located

| Evidence item | Path | Used for | Status | Notes |
| --- | --- | --- | --- | --- |
| Canonical result registry | `reports/tables/canonical_native_path_status_matrix.csv` | Dataset-model scope, strict metrics, export status, and registered primary paths | Accessible | Current strict-accuracy source at draft level; the twelve main primary JSON files are absent. |
| Export validation registry | `scripts/analysis/validate_canonical_export_evidence.py` | Canonical labels, model export tags, path directories, and evaluation top-k | Accessible | Registers all twelve LastFM/ML-1M model rows and validates at top-k 10. |
| Per-row export validation summaries | `reports/tables/canonical_export_validation/*.json` | Model/dataset identity, output tag, exact test-user gate, and PASS status | Accessible | Does not contain training hyperparameters or checkpoint identity. |
| Implementation log | `docs/guides/NATIVE_PATH_IMPLEMENTATION_LOG_2026-06-20.md` | PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM execution history | Accessible; historical record | Supplies declared run settings and completion context, but referenced run artifacts are not present in this worktree. |
| TPRec canonical pipeline | `scripts/hopwise/run_canonical_tprec_pipeline.sh`; `scripts/hopwise/tprec_runtime.py` | TransE, temporal pretraining, policy training, path constraints, beam inference, and export | Accessible | Applies directly to LastFM and ML-1M; the Amazon branch is blocked by timestamp semantics. |
| KGGLM canonical pipeline | `scripts/hopwise/run_canonical_kgglm_pipeline.sh`; `scripts/hopwise/canonical_config.py` | Two-stage training, architecture, optimiser settings, checkpoint selection, and export | Accessible | The script declares the formal configuration; generated checkpoint directories are absent. |
| PEARLM canonical pipeline | `scripts/hopwise/run_canonical_pearlm_pipeline.sh`; `scripts/hopwise/canonical_config.py` | Training, architecture, validation selection, and export | Accessible | The script declares the formal configuration; generated checkpoint directories are absent. |
| Shared xrecsys protocol | `scripts/hopwise/run_canonical_xrecsys_protocol.sh` | Baseline-first evaluation and LIR/SEP/ETD moving-alpha runs | Accessible | Separates the baseline from three objective-specific sweeps. |
| Sweep validator | `scripts/validation/validate_xrecsys_sweeps.py` | Alpha grid and required metrics | Accessible | Requires 21 alpha values from 0.00 to 1.00 in steps of 0.05. |
| Evaluation scripts | `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py` | Top-k contract and strict metric computation | Accessible | Both default to top-k 10; the evaluator permits explicitly short native-path lists when requested. |
| Ablation provenance | `reports/tables/ablation/pgpr_ucpr_path_module/provenance_validation.csv` | Frozen-item-set PGPR/UCPR ablation boundary | Accessible | Separate from the main six-model alpha sweeps and strict-accuracy table. |
| Artifact manifest | `reports/tables/canonical_native_path_artifact_manifest.json` | Hashes of accessible reports/scripts and historical artifact paths | Accessible but partial | Records historical run paths and hashes, but most referenced run files are absent from the current worktree. |

## 3. Model Training / Inference Configuration

| Model | Dataset | Training / inference source | Key parameters found | Missing parameters | Evidence path | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| PGPR | LastFM | Trained checkpoint reused for deterministic native inference; canonical export registered as `25-50-1-pgpr-canonical-native-score` | Policy checkpoint epoch 50; beam `25-50-1`; inference batching recorded as 16 users; evaluation top-k 10 | Learning rate, training batch size, embedding dimension, exact checkpoint path/hash, and seed are not available in the current evidence package | Implementation log; `scripts/analysis/validate_canonical_export_evidence.py`; `reports/tables/canonical_export_validation/lastfm_pgpr.json` | High for export identity and beam; medium for historical training provenance because checkpoint is absent |
| PGPR | ML-1M | Canonical model view followed by formal TransE, policy training, native inference, and export | TransE 30 epochs; policy 50 epochs; beam `25-50-1`; evaluation top-k 10 | Learning rate, training batch size, embedding dimension, exact checkpoint path/hash, and seed are not available in the current evidence package | Implementation log; export registry; `reports/tables/canonical_export_validation/ml1m_pgpr.json` | High for registered output and declared stage counts; checkpoint requires manual verification |
| UCPR | LastFM | Existing trained checkpoint reused for matched-beam native inference | Policy checkpoint epoch 30; `max_acts=50`; beam `25-50-1`; beam batch size 4; evaluation top-k 10 | Learning rate, training batch size, embedding dimension, exact checkpoint path/hash, and seed are not available in the current evidence package | Implementation log; export registry; `reports/tables/canonical_export_validation/lastfm_ucpr.json` | High for registered inference settings; checkpoint requires manual verification |
| UCPR | ML-1M | Formal TransE and policy run followed by matched-beam inference | TransE 30 epochs; policy 40 epochs; beam `25-50-1`; evaluation top-k 10 | Learning rate, training batch size, embedding dimension, exact checkpoint path/hash, and seed are not available in the current evidence package | Implementation log; export registry; `reports/tables/canonical_export_validation/ml1m_ucpr.json` | High for declared stage counts and registered output; checkpoint requires manual verification |
| CAFE | LastFM | Canonical CAFE view, fixed-epoch neural-symbolic training, native program inference, and export | 20 training epochs; fixed epoch-20 checkpoint; pseudo-validation disabled; evaluation top-k 10 | Learning rate, training batch size, random seed, exact embedding dimension for this run, and checkpoint path/hash are not available in the current evidence package | Implementation log; `scripts/model_patches/patch_cafe_runtime.py`; export registry; `reports/tables/canonical_export_validation/lastfm_cafe.json` | High for epoch and output identity; other model-native settings require manual verification |
| CAFE | ML-1M | Canonical CAFE view aligned to the formal UCPR TransE embedding, followed by fixed-epoch training and native export | 20 training epochs; embedding dimension 100; source UCPR TransE checkpoint epoch 30; evaluation top-k 10 | Learning rate, training batch size, random seed, and exact CAFE/UCPR checkpoint paths and hashes are not available in the current evidence package | Implementation log; `scripts/data/canonical/build_cafe_view.py`; export registry; `reports/tables/canonical_export_validation/ml1m_cafe.json` | High for documented alignment and registered output; checkpoint files are absent |
| TPRec | LastFM | Canonical TransE, temporal pretraining, policy training, deterministic beam export | TransE 50 epochs with dimension 100 and learning rate `1e-3`; temporal pretraining 5 epochs at `1e-3`; policy 50 epochs at `1e-4`; train batch 4096; eval batch 4; maximum path length 3; beam `25-50-1`; top-k 10 | Random seed and exact generated checkpoint paths/hashes are not available in the current evidence package | `scripts/hopwise/run_canonical_tprec_pipeline.sh`; `scripts/hopwise/tprec_runtime.py`; export registry | High for script-declared configuration; generated artifacts require manual verification |
| TPRec | ML-1M | Canonical TransE, temporal pretraining, policy training, deterministic beam export | TransE 50 epochs with dimension 100 and learning rate `1e-3`; temporal pretraining 5 epochs at `1e-3`; policy 50 epochs at `1e-4`; train batch 2048; eval batch 8; maximum path length 3; beam `25-50-1`; top-k 10 | Random seed and exact generated checkpoint paths/hashes are not available in the current evidence package | `scripts/hopwise/run_canonical_tprec_pipeline.sh`; `scripts/hopwise/tprec_runtime.py`; export registry | High for script-declared configuration; generated artifacts require manual verification |
| KGGLM | LastFM and ML-1M | Canonical two-stage KG-only pretraining and recommendation-path fine-tuning, followed by constrained path export | Generic-path pretraining setting 3 epochs; fine-tuning 2 epochs; embedding size 768; 12 heads; 6 layers; train batch 256; learning rate `2e-4`; weight decay 0.01; warmup 250; 25 paths per user; 25 beams; top-k 10 | Random seed and exact selected pretraining/fine-tuning checkpoint paths and hashes are not available in the current evidence package | `scripts/hopwise/run_canonical_kgglm_pipeline.sh`; `scripts/hopwise/canonical_config.py`; export registry | High for script-declared settings and registered outputs; checkpoint identity requires manual verification |
| PEARLM | LastFM and ML-1M | Canonical training with validation-based checkpoint selection, followed by constrained path export | 50 epochs; embedding size 768; 12 heads; 6 layers; train batch 64; learning rate `2e-4`; weight decay 0.01; warmup 250; evaluation every 5 epochs; stopping step 5; 25 paths per user; 25 beams; top-k 10 | Random seed and exact selected checkpoint path/hash are not available in the current evidence package | `scripts/hopwise/run_canonical_pearlm_pipeline.sh`; `scripts/hopwise/canonical_config.py`; export registry | High for script-declared settings and registered outputs; checkpoint identity requires manual verification |

Amazon-Book KGAT must remain separate from the complete table above. The status matrix records complete rows for PGPR, KGGLM, and PEARLM, but no approved explanation sweeps. UCPR, CAFE, and TPRec remain BLOCKED/N/A. Amazon-specific attempted or formal settings must not be transferred to LastFM or ML-1M, and a blocked configuration must not be presented as a completed training result.

## 4. Evaluation and Sweep Configuration

| Component | Setting | Evidence path | Confidence | Notes |
| --- | --- | --- | --- | --- |
| Canonical evaluation cut-off | Top-k 10 | `scripts/validation/validate_xrecsys_export.py`; `scripts/validation/evaluate_uid_topk.py` | High | Applies to validated recommendation exports and strict metrics. |
| Strict ranking metrics | HR@10, NDCG@10, Precision@10, Recall@10 | `scripts/validation/evaluate_uid_topk.py`; status matrix | High | Current draft values come from the two matching summaries, not accessible primary JSON files. |
| Sweep baseline | Baseline evaluated before each moving-alpha objective | `scripts/hopwise/run_canonical_xrecsys_protocol.sh` | High | Baseline and moving-alpha artifacts are separate. |
| Alpha grid | 21 values: 0.00 to 1.00 inclusive, step 0.05 | `scripts/validation/validate_xrecsys_sweeps.py` | High | Validator rejects missing, extra, or non-uniform alpha rows. |
| Sweep objectives | `LIRopt`, `SEPopt`, `ETDopt` | `scripts/hopwise/run_canonical_xrecsys_protocol.sh`; sweep validator | High | Each objective is run separately. |
| Paired ranking metrics | NDCG, HR, Recall, Precision | `scripts/validation/validate_xrecsys_sweeps.py` | High | These are sweep metrics and are not substitutes for strict accuracy. |
| Explanation metrics | LIR, SEP, ETD | `scripts/validation/validate_xrecsys_sweeps.py`; `docs/guides/PATH_METRICS_GUIDE.md` | High for recorded outputs | Exact implementation and data assumptions remain repository-specific. |
| Complete main sweep scope | PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM on LastFM and ML-1M | Export validation manifest; registered trade-off CSV bundles | High | Amazon is excluded from this complete scope. |
| Random seed for main model training | Not available in the current evidence package | Accessible scripts and reports searched | Low / unresolved | Do not infer a common seed from framework or library defaults. |
| Statistical repetitions | Not available in the current evidence package | Traceability log and limitations record | Unresolved | No statistical-significance artifact is registered. |
| PGPR/UCPR ablation | Frozen original top-k item set; exact alpha=0 preservation; separate 95% NDCG-retention analysis | `reports/tables/ablation/pgpr_ucpr_path_module/` | High | Separate evidence stream from the six-model sweeps. |
| Amazon explanation sweeps | Not applicable under current approved evidence | Status matrix and handoff | High | No approved timestamp, SEP, or ETD denominator protocol is registered. |

## 5. Recommended Chapter 3 Configuration Table

| Configuration item | Setting / provenance | Evidence source | Interpretation boundary |
| --- | --- | --- | --- |
| Main datasets and models | LastFM and ML-1M; six validated native-path models on each dataset | Export validation manifest and status matrix | Amazon-Book KGAT is a partial boundary case, not a third complete main experiment. |
| Model-native training and inference | Heterogeneous model-specific pipelines; directly available settings are documented in this provenance audit | Model scripts, implementation log, and export registry | The framework does not claim identical internal hyperparameter spaces. |
| Canonical recommendation cut-off | Top-k 10 | Validation and strict-evaluation scripts | Short native-path lists may remain short; no non-path padding is introduced. |
| Strict ranking evaluation | HR@10, NDCG@10, Precision@10, Recall@10 | Status matrix and final accuracy summary | The twelve expected primary JSON files are unavailable. |
| Explanation objectives | Separate LIR-, SEP-, and ETD-oriented sweeps | Shared xrecsys protocol | The three objectives are non-interchangeable and repository-specific in exact implementation. |
| Alpha sweep | 0.00 to 1.00 inclusive at 0.05 intervals, yielding 21 points | Sweep validator | Paired sweep ranking metrics are not strict accuracy results. |
| Validation gate | Exact canonical test-user coverage, unique top-k items, leakage checks, endpoint checks, and explanation alignment | Export validator and per-row validation summaries | PASS establishes contract conformity, not universal model correctness. |
| Ablation | PGPR main and UCPR auxiliary, frozen original top-k item set, exact alpha=0 preservation | Ablation provenance directory | Does not replace the six-model sweep or prove mechanisms for other models. |
| Unavailable configuration | Seeds, several PGPR/UCPR/CAFE optimiser settings, and exact checkpoint identities | Current evidence audit | Parameters not accessible in the current evidence package are not reconstructed or inferred. |

## 6. Appendix Recommendation

The final dissertation should keep the concise table from Section 5 in Chapter 3.6 and place the detailed model-by-dataset table from Section 3 in an appendix or reproducibility supplement. Before final submission, that appendix should be refreshed from an archived run package containing the exact configuration files, selected checkpoint paths, checkpoint hashes, runtime environment, and seeds. Training parameters should not be moved into Chapter 4, whose role is empirical result reporting and result-level interpretation.

## 7. Caveats

1. The historical run tree and generated checkpoint files are absent from the current worktree; checkpoint identity therefore requires manual verification.
2. Detailed model-native hyperparameters are retained in their respective configuration or execution sources where available; parameters not accessible in the current evidence package are not reconstructed or inferred.
3. Script defaults are reported only when the formal pipeline invokes the script without overriding them. A default from an unrelated smoke or Amazon port is not transferred to a main LastFM/ML-1M run.
4. Strict accuracy remains supported by the canonical status matrix and exactly matching final summary, with `0/12` expected primary row-level JSON artifacts accessible.
5. Sweep ranking metrics, strict accuracy, and the PGPR/UCPR ablation remain separate evidence streams.
6. No statistical-significance artifact or user-study artifact is available.
7. LIR, SEP, and ETD have external conceptual provenance, but their exact evaluated implementation is repository-specific.
8. Amazon-Book KGAT remains a partial boundary case with no approved explanation sweeps.
9. Non-PGPR/UCPR mechanism interpretations remain descriptive rather than causal.
10. PEARLM final venue and publisher DOI remain subject to manual verification.
