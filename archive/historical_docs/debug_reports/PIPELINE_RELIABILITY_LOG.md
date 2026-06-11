# Pipeline Reliability Log

This document is the running review log for the evaluation pipeline.

Use it to track:
- suspected reliability risks,
- confirmed issues,
- code or process changes we tried,
- validation results,
- the current priority list for follow-up work.

Update rule:
- After each meaningful review, fix, or experiment-validation pass, append a new dated entry.
- Keep "Current Status" and "Priority Queue" in sync with the latest evidence.
- Separate "confirmed" from "suspected" findings so we do not overstate conclusions.

## Current Status

### Overall Assessment

- `xrecsys` is a post-processing and reranking framework by design.
- Adapter-based path standardization is expected by the framework design.
- Current VRKG4Rec results are useful as exploratory evaluation outputs.
- Current VRKG4Rec explanation-quality results should not yet be treated as strong faithful-explanation evidence.

### Reliability Snapshot

| Area | Status | Notes |
| --- | --- | --- |
| `xrecsys` framework positioning | Expected | Intended for post-processing, not faithful internal reasoning verification |
| `xrecsys/main.py` control flow | Partially cleaned | Confirmed old code ran extra optimizations, but this did not change the three tested final alpha curves |
| `metrics.py` grouped statistics | Partially fixed | Empty-group warnings removed from tested ETDopt run; empty groups now render as `n/a` and still need root-cause analysis |
| ETD-family optimizations | Fixed in local changes | ETD-based rerankers previously collapsed many top-k lists; patched variant now refills remaining slots and materially changes stored ETD results in both VRKG4Rec and PGPR checks |
| VRKG4Rec adapter explanations | Caution | Current explanations are post-hoc paths reconstructed from embeddings and KG traversal |
| KG / ID mapping | Sensitive but not broken | No direct evidence of current mismatch, but the path is mapping-heavy |
| VRKG4Rec training runtime | Expensive but not proven broken | Epochs are long, but logs do not yet show a clear implementation error |
| PGPR/UCPR truth space alignment | Under active review | Adapter export is no longer the main suspect; cross-model label-space mismatch is now the leading comparability risk |

## Confirmed Findings

### 1. `xrecsys` is a post-processing framework by design

Based on the `XRecSys` framework paper and the linked theory paper:
- the framework assumes existing recommendations and candidate reasoning paths,
- the mapper / adapter layer is part of the intended design,
- the optimizer reranks already generated recommendations and paths.

Implication:
- using adapters is expected,
- explanation quality results should be interpreted as post-processing outputs,
- this framework alone does not prove model-faithful internal reasoning.

### 2. Old `xrecsys/main.py` ran extra optimizations

Confirmed behavior before the current review:
- running `--opt LIRopt` also generated output files for other alpha optimizations such as `ETDopt` and `SEPopt`.

Implication:
- the control flow was broader than intended,
- logs and result folders could contain outputs that were not explicitly requested in that run.

### 3. The tested `main.py` control-flow issue did not change three tested final alpha curves

We compared isolated old-vs-fixed runs for:
- `LIRopt`
- `ETDopt`
- `SEPopt`

For `lastfm / agent_topk=10-12-1`, the following files matched exactly between old and fixed versions:
- `LIRopt_moving_alpha_avg.csv`
- `ETDopt_moving_alpha_avg.csv`
- `SEPopt_moving_alpha_avg.csv`

Observed result:
- `max_abs_diff = 0.0` for all compared overall metrics in those three runs.

Implication:
- the old extra-optimization behavior is real,
- but for the three tested alpha sweeps, it did not affect the final saved moving-alpha averages.

### 4. Grouped metric warnings exist

During isolated reruns, we observed:
- `RuntimeWarning: Mean of empty slice`
- `invalid value encountered in scalar divide`
- grouped recommendation metrics with `nan` values for some age groups in at least one optimization log

Implication:
- grouped metric reporting is a live reliability concern,
- this is currently a stronger candidate issue than the tested `main.py` alpha-sweep control-flow bug.

### 5. PGPR and VRKG4Rec baseline coverage are materially different

Coverage audit on the currently mirrored `lastfm` artifacts showed:
- `PGPR / agent_topk=25-50-1`: `full_topk_users = 14541` out of `14642` test users
- `VRKG4Rec / agent_topk=10-12-1`: `full_topk_users = 13143` out of `14642` test users

This difference is visible across age groups as well.

Implication:
- the two models do not enter xrecsys evaluation with equally complete top-k coverage,
- shared framework bias can therefore affect them by different amounts,
- different tradeoff trends may partly reflect different coverage profiles, not only model behavior.

### 6. ETD-family optimizations had an additional top-k collapse bug

Implementation interpretation note:
- the original ETD-family implementation can be read as a more aggressive diversity-first procedure that allows the final list to stop early,
- the patched ETD-family implementation can be read as a constrained diversity-first procedure that still tries to preserve a valid top-k recommendation list,
- for the current xrecsys evaluation setup, the patched interpretation is easier to compare fairly against recommendation metrics such as `ndcg`, `hr`, `recall`, and `precision`.

Confirmed behavior before the current patch:
- `optimize_ETD` and ETD-based combo optimizations could stop after selecting a few diversity-favored items,
- they did not refill the remaining recommendation slots up to 10,
- this caused recommendation-metric coverage to collapse after optimization.

Observed example on `lastfm / agent_topk=10-12-1 / ETDopt alpha=1.0` before the patch:
- `baseline rec_metric_users = 13143`
- `after ETDopt rec_metric_users = 14`

Implication:
- pre-patch ETD tradeoff results could be strongly distorted for fixed-top-k recommendation evaluation, because recommendation metrics were computed on a drastically reduced user subset.
- this does not necessarily make the old ETD-first implementation meaningless; it means it corresponds to a different, more aggressive diversity-first definition than the fixed-top-k evaluation setting used elsewhere in the pipeline.

### 5. VRKG4Rec explanations are currently post-hoc

Current adapter behavior:
- load VRKG4Rec embeddings,
- enumerate reverse-KG paths,
- score candidate paths with similarity-based logic,
- export selected paths into xrecsys CSV format.

Implication:
- current VRKG4Rec explanation outputs are post-hoc explanations,
- they should not be described as model-native faithful reasoning paths without further evidence.

## Suspected Risks Still Under Review

### 1. `metrics.py` grouped statistics may be unstable

Open concerns:
- empty groups may be averaged without explicit guards,
- grouped `nan` values may affect confidence in subgroup analysis,
- recommendation and explanation statistics may not always rely on the exact same effective user subset.

### 2. VRKG4Rec path coverage may distort evaluation

Observed earlier in exported files:
- not every user receives a full top-10 path-backed recommendation list,
- some users have fewer than 10 entries,
- a small number of users have zero exported entries.

Open concern:
- recommendation metrics and explanation metrics may effectively summarize different subsets of users or items.

### 3. KG / remapping chain remains a high-sensitivity dependency

Current pipeline depends on multiple remapping layers:
- preprocessed `kg.pkl`,
- plain KG export,
- entity remap files,
- user remap files,
- adapter reconstruction logic.

Open concern:
- even if no direct mismatch has been observed yet, this is still a brittle part of the pipeline.

### 5. Cross-model label-space mismatch is now the leading risk for PGPR/UCPR comparison

Current evidence from `UCPR` review shows:
- native `UCPR` recommendation evaluation can run and gives reasonable metrics,
- the first `UCPR -> xrecsys` adapter preserves native top-k ordering,
- but `xrecsys` recommendation metrics become implausibly low under the current label source.

Observed comparison:
- `UCPR` adapter-exported users: `14620`
- `PGPR tmp/lastfm/test_label.pkl` users: `14642`
- intersection: only `9394`

Implication:
- the main blocker for clean `PGPR` vs `UCPR` recommendation comparison is no longer top-k export fidelity,
- it is now the fact that different model paths are still effectively judged against different user / label spaces.

### 4. Training slowness is real but still not classified as a bug

Observed in VRKG4Rec training logs:
- training epochs are long,
- evaluation phases are also long,
- later epochs show some fluctuation.

Current interpretation:
- expensive runtime is confirmed,
- a training implementation bug is not yet confirmed.

## Remediation Log

### 2026-04-09 - UCPR native eval repaired and adapter fidelity reviewed

Scope:
- finished native `UCPR` test/evaluation debugging,
- wrote a first `UCPR -> xrecsys` adapter,
- checked whether the adapter changed native top-k ranking semantics.

Changes tried:
- repaired `rep-path-reasoning-recsys/models/UCPR/test.py` to fix:
  - boolean-as-function evaluation bug,
  - `test-only user` `KeyError`,
  - NumPy 2.0 `np.asfarray` incompatibility,
  - weak traceback visibility.
- added `adapters/ucpr_adapter.py` to export:
  - `pred_paths.csv`
  - `uid_topk.csv`
  - `uid_pid_explanation.csv`

Validation method:
- ran native `UCPR` evaluation to completion and recorded:
  - `precision = 0.0229`
  - `recall = 0.0090`
  - `ndcg = 0.0903`
  - `hit = 0.1684`
- reconstructed native top-k from `pred_paths.pkl` using the same logic as `UCPR evaluate_paths()`,
- compared reconstructed native top-k against adapter-exported `uid_topk.csv`.

Validation result:
- `checked users = 14620`
- `mismatches = 0`
- adapter top-k ordering is faithful to native `UCPR` ordering.

New conclusion:
- current implausibly low `xrecsys` recommendation metrics for `UCPR` are no longer best explained by adapter ranking drift,
- the strongest current explanation is label / user-space mismatch between the `UCPR` export and the historical `PGPR tmp` label source used by `xrecsys`.

Decision:
- treat canonical labels as the next reliability step for `PGPR + UCPR`,
- keep the current `UCPR` adapter as a valid schema-alignment layer,
- do not yet treat current cross-model rec-metric comparison as final.

### 2026-04-09 - Canonical labels implemented for PGPR/UCPR comparison

Scope:
- implemented a first shared truth-space layer for `PGPR + UCPR` on `lastfm`,
- kept the change low-coupling by adding an optional label override instead of replacing the historical default labels.

Changes tried:
- added [generate_canonical_labels.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/generate_canonical_labels.py),
- added `--labels_dir` to [main.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/main.py),
- updated [myutils.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/myutils.py) and [path_data_loader.py](/usr1/home/s125mdg43_08/eval_framework/xrecsys/path_data_loader.py) so `train_label.pkl` / `test_label.pkl` can be overridden without disturbing the default `PGPR tmp` path.

Validation method:
- generated canonical labels from:
  - `xrecsys/datasets/lastfm/train.txt.gz`
  - `xrecsys/datasets/lastfm/test.txt.gz`
  - `user_mappings.txt`
  - `product_mappings.txt`
- then reran baseline evaluation on copied path folders:
  - `agent_topk=25-50-1-canonical`
  - `agent_topk=10-12-1-ucpr-canonical`

Corrected canonical-label summary:
- `train_users = 15472`
- `test_users = 14642`
- `train_kept_interactions = 3238575`
- `test_kept_interactions = 713959`

Validation result:
- after correcting the product-column semantics in the generator, the canonical labels were verified to match the converted `UCPR test.txt.gz` exactly when mapped into UCPR compact space,
- `UCPR` improved from the previous near-zero xrecsys baseline to a native-like scale:
  - old `ndcg = 0.00070` -> corrected canonical `0.09905`
  - old `hr = 0.00100` -> corrected canonical `0.16891`
- `PGPR` instead collapsed under the corrected canonical labels:
  - historical `ndcg = 0.08596` -> corrected canonical `0.00234`
  - historical `hr = 0.18183` -> corrected canonical `0.00439`

New conclusion:
- the original near-zero `UCPR` xrecsys rec metrics were caused by label-space mismatch, and the corrected canonical labels fix that problem,
- the remaining cross-model comparability problem now points much more strongly at `PGPR` artifact-space mismatch,
- the current `UCPR` adapter/export path is substantially more trustworthy than before.

Decision:
- keep corrected canonical labels as the preferred comparison direction,
- treat `UCPR` as successfully aligned to the raw-split truth space for baseline recommendation evaluation,
- next review should focus on why the currently stored `PGPR` path artifacts do not belong to that same truth space.

### 2026-04-09 - Root cause narrowed to split-interpretation mismatch in raw lastfm product ids

Scope:
- investigated why corrected canonical labels align cleanly with `UCPR` but collapse `PGPR`,
- compared the raw `lastfm train/test.txt.gz` product column against both possible interpretations:
  - xrecsys internal `kgid`
  - raw dataset product id mapped through `product_mappings.txt`

Validation result:
- train total interactions: `17,551,186`
- train product column matching `kgid`: `2,789,195` (`15.89%`)
- train product column matching raw-id mapping: `3,238,575` (`18.45%`)
- train matching both: `990,320` (`5.64%`)

- test total interactions: `4,395,646`
- test product column matching `kgid`: `697,133` (`15.86%`)
- test product column matching raw-id mapping: `713,959` (`16.24%`)
- test matching both: `215,571` (`4.90%`)

Interpretation:
- the raw `lastfm` split files are not currently behaving like a single unambiguous product-id space for the whole pipeline,
- `PGPR preprocess.py` historically assumes the product column is a raw dataset product id,
- the `UCPR` conversion path effectively retained the subset consistent with the xrecsys-internal product-id interpretation used there,
- therefore the two model families have been attached to different surviving subsets of the same raw split files.

Additional source-chain evidence:
- the official [xrecsys README](/usr1/home/s125mdg43_08/eval_framework/xrecsys/README.md) asks users to download three separate LASTFM bundles:
  - preprocessed datasets,
  - precomputed paths,
  - `models/PGPR/tmp/lastfm` assets,
- so the current local mismatch should not be over-interpreted as “the original PGPR Google Drive data was wrong”; it is more likely a local asset-alignment problem between bundles.
- direct inspection also showed that current `tmp/lastfm` label items are a subset of the `kgid` column in `product_mappings.txt`, not the raw `lastfmid` column,
- while the raw split filtered under the two competing interpretations yields the two user counts we have been seeing downstream:
  - `14620` under `kgid` filtering,
  - `14642` under raw-product-id filtering.
- regenerated local labels (`train_label.generated.pkl` / `test_label.generated.pkl`) match the current `datasets/lastfm` raw-product-id interpretation exactly,
- but the historical Google-Drive-style `train_label.pkl` / `test_label.pkl` do not; they have the same sizes but different user sets,
- the currently stored PGPR path artifacts in `agent_topk=25-50-1` match the historical `tmp/lastfm/test_label.pkl` user set exactly, not the regenerated one,
- and there is no local `lastfm` `policy_paths_epoch*.pkl` or visible agent checkpoint to cheaply regenerate canonical-compatible PGPR paths.

Decision:
- stop treating `PGPR` and `UCPR` baseline mismatch as an adapter-only issue,
- treat it as a raw-split interpretation mismatch that must be resolved before final cross-model tradeoff figures are claimed comparable,
- next step should decide which product-id interpretation becomes the formal canonical evaluation standard and then regenerate or recover the affected PGPR model artifacts accordingly.

### 2026-04-14 - Canonical dataset standard drafted and `lastfm_v1` smoke-built

Scope:
- generalized the canonical-label idea into a reusable canonical dataset layer,
- documented the project-level standard for future `lastfm`, `ml1m`, and `amazon` variants,
- implemented a first reusable builder for xrecsys-style source datasets.

Files:
- [CANONICAL_DATASET_STANDARD.md](/usr1/home/s125mdg43_08/eval_framework/docs/guides/CANONICAL_DATASET_STANDARD.md)
- [build_canonical_dataset.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_canonical_dataset.py)

First output:
- [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1)

Policy used for first `lastfm_v1` trial:
- canonical user id: raw LastFM user id mapped to xrecsys kgid through `user_mappings.txt`,
- canonical product id: xrecsys internal product `kgid`,
- interaction format: `uid\tpid\trating\ttimestamp`,
- validation split: latest one training interaction per eligible user.

Generated split statistics:
- train: `2,773,892` interactions, `15,476` users, `9,334` products,
- valid: `15,303` interactions, `15,303` users, `3,473` products,
- test: `697,133` interactions, `14,620` users, `7,590` products.

Sanity check:
- each interaction row has four columns,
- each label pkl exactly matches its corresponding interaction split,
- no mismatch was found between interaction counts and label-entry counts.

Next step:
- generate `lastfm_v1` model-specific views for `UCPR` and `PGPR`,
- retrain or rerun both models from the same canonical dataset,
- export both back to canonical xrecsys CSVs before drawing cross-model tradeoff figures.

Follow-up:
- implemented the first model-specific view builder:
  - [build_ucpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_ucpr_view.py)
- generated `lastfm_v1 -> UCPR` compact view under:
  - [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/ucpr](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/ucpr)
- UCPR view sanity check passed:
  - train: `2,773,892` rows, `15,476` users, `9,334` products,
  - valid: `15,303` rows, `15,303` users, `3,473` products,
  - test: `697,133` rows, `14,620` users, `7,590` products,
  - no malformed rows,
  - no skipped canonical users/products during view conversion.
- implemented the second model-specific view builder:
  - [build_pgpr_view.py](/usr1/home/s125mdg43_08/eval_framework/scripts/data/canonical/build_pgpr_view.py)
- generated `lastfm_v1 -> PGPR` identity-mapping view under:
  - [runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/pgpr](/usr1/home/s125mdg43_08/eval_framework/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/model_views/pgpr)
- PGPR view sanity check passed:
  - PGPR-style raw-id mapping reconstructs canonical train labels exactly,
  - PGPR-style raw-id mapping reconstructs canonical test labels exactly,
  - no PGPR source-code modification is needed for this data view.

### 2026-03-24 - PGPR ETDopt validation after refill fix

Scope:
- validated whether the ETD refill change also affects `PGPR` outputs, not only `VRKG4Rec`,
- compared `PGPR / lastfm / agent_topk=25-50-1 / ETDopt` old vs patched outputs.

Validation method:
- ran patched `ETDopt` in `runs/debug_compare/2026-03-24_pgpr_etd_fix/code_sandbox/`,
- compared the generated `ETDopt_moving_alpha_avg.csv` against the stored `xrecsys/results` file,
- saved the comparison summary to `runs/debug_compare/2026-03-24_pgpr_etd_fix/results/summary.md`.

Validation result:
- `PGPR ETDopt` also changed materially after the refill fix,
- major maximum absolute differences included `hr = 0.242328`, `ETD = 0.234060`, `LIR = 0.057289`, and `ndcg = 0.029778`,
- this shows the ETD-family implementation issue is not specific to VRKG4Rec.

Decision:
- treat old `PGPR ETDopt` results as unreliable for fixed-top-k comparison under the old ETD-first implementation,
- extend the caution around ETD-family outputs to both model families, not only VRKG4Rec.

### 2026-03-23 - Full ETD-family output validation after refill fix

Scope:
- compared patched ETD-family alpha-sweep outputs against the currently stored `xrecsys/results` files,
- covered `ETDopt`, `ETD_LIR_opt`, `ETD_SEP_opt`, and `ETD_SEP_LIR_opt` on `lastfm / agent_topk=10-12-1`.

Validation method:
- ran the patched ETD-family sweeps in `runs/debug_compare/2026-03-23_etd_fix/code_sandbox/`,
- compared the generated `*_moving_alpha_avg.csv` files against the current stored result files,
- saved the comparison summary to `runs/debug_compare/2026-03-23_etd_fix/results/summary.md`.

Validation result:
- `ETDopt` changed substantially after the refill fix, including large recommendation-metric differences (`hr` max abs diff `0.221109`, `ndcg` max abs diff `0.139098`),
- `ETD_LIR_opt` also changed substantially (`hr` max abs diff `0.194652`, `ndcg` max abs diff `0.145070`),
- `ETD_SEP_opt` was unchanged in the current comparison (`max_abs_diff = 0.0` across compared overall metrics),
- `ETD_SEP_LIR_opt` changed moderately (`ETD` max abs diff `0.013978`, `SEP` max abs diff `0.010114`, `ndcg` max abs diff `0.008082`).

Decision:
- treat previously stored `ETDopt` and `ETD_LIR_opt` tradeoff outputs as unreliable for fixed-top-k comparison under the old implementation,
- treat `ETD_SEP_opt` as unchanged in the current evidence,
- keep the refill fix as the preferred variant when recommendation-quality and explanation-quality metrics are expected to be compared on a stable top-k setting,
- use the sandbox summary as the current reference until formal reruns are promoted.

### 2026-03-23 - ETD top-k refill fix

Scope:
- reviewed ETD-based rerankers after coverage audit showed that recommendation-metric users collapsed after ETD optimization,
- targeted `optimize_ETD`, `optimize_ETD_LIR`, `optimize_ETD_SEP`, and `optimize_ETD_SEP_LIR`.

Changes tried:
- added a refill step that appends the best remaining unseen item candidates after the diversity-priority phase,
- preserved the ETD-first selection stage, but forced the final recommendation list to keep filling toward top-10 whenever enough candidates exist.

Validation method:
- reran the coverage audit on `lastfm / agent_topk=10-12-1 / ETDopt alpha=1.0`,
- compared `full_topk_users` and `rec_metric_users` before and after the patch.

Validation result:
- before the patch, `ETDopt alpha=1.0` reduced `rec_metric_users` from `13143` to `14`,
- after the patch, the same audit produced `full_topk_users = 14552` and `rec_metric_users = 14552`,
- this shows the ETD-family top-k collapse was real and the refill fix materially restored recommendation coverage.

Decision:
- keep this fix for the fixed-top-k evaluation setting, because it restores comparability between explanation optimization and recommendation metrics,
- interpret the patched version as a constrained ETD-first variant rather than the only valid ETD definition,
- next verify how much the repaired ETD-family curves change in full evaluation outputs.

### 2026-03-23 - Empty-group metrics stabilization

Scope:
- reviewed `xrecsys/metrics.py` and `xrecsys/main.py` handling of grouped recommendation metrics,
- targeted the `Mean of empty slice` and `nan` outputs observed during `ETDopt` validation.

Changes tried:
- added `safe_mean()` and `format_metric_value()` to `xrecsys/metrics.py`,
- changed grouped metric printing to render empty groups as `n/a` instead of `nan`,
- changed `xrecsys/main.py` CSV export paths to avoid direct `np.mean()` on empty grouped rec-metric lists.

Validation method:
- reran isolated `ETDopt` validation on `lastfm / agent_topk=10-12-1 / alpha=1.0`,
- checked stderr for numpy warnings,
- checked the generated log output for grouped metric formatting.

Validation result:
- `Mean of empty slice` warnings disappeared in the tested rerun,
- empty recommendation groups now print as `n/a`,
- explanation metrics remained numerically unchanged in the tested log tail.

Decision:
- keep this fix, because it improves stability and readability without changing non-empty metric values,
- continue investigating why some recommendation subgroups are empty after optimization.

### 2026-03-23 - Initial reliability review and control-flow cleanup attempt

Scope:
- reviewed `xrecsys`, adapter, KG provenance, and VRKG4Rec training logs,
- tested whether `xrecsys/main.py` control-flow cleanup changes final alpha curves.

Changes tried:
- rewrote `xrecsys/main.py` so each requested optimization is run explicitly,
- reloaded fresh `PathDataLoader` objects for isolated reruns,
- avoided broad implicit execution of extra optimizations.

Validation method:
- created isolated comparison sandboxes outside the repo,
- compared old vs fixed outputs for:
  - `LIRopt`
  - `ETDopt`
  - `SEPopt`
- compared the generated `*_moving_alpha_avg.csv` files directly.

Validation result:
- old behavior definitely generated extra optimization outputs,
- the three tested final alpha-curve CSVs remained numerically identical,
- therefore this cleanup improved code behavior but did not change the tested final results.

Decision:
- treat the `main.py` cleanup as optional code hygiene for now,
- do not claim it fixes the dramatic curve behavior,
- shift investigation priority toward grouped metrics, coverage, and adapter semantics.


### 2026-03-24 - Tradeoff plotting refinement

Scope:
- refined `scripts/analysis/tradeoff_analyzer.py` so the report plots are easier to interpret,
- expanded the plotted recommendation metrics beyond `ndcg`.

Changes tried:
- added support for `precision` and `recall` in addition to `ndcg` and `hr`,
- changed the figure from a single two-panel plot into faceted alpha-sweep tradeoff plots,
- replaced the old marker-heavy legend with two clearer legend layers:
  - color = model,
  - line style = recommendation metric vs explanation-metric relative change,
- kept alpha endpoint annotations, but changed the endpoint markers to a clearer `o` / `X` pair.

Rationale:
- the old plot centered too much on `ndcg`,
- the old second-panel legend mixed color, line style, and marker shape in a way that was hard to parse,
- small circle / square markers were hard to distinguish at report resolution.

Interpretation update:
- the top row should be described as alpha-sweep tradeoff curves rather than a strict Pareto frontier,
- the bottom row still shows relative change from `alpha=0`, so it remains useful for trend reading,
  but percentage changes should still be interpreted carefully when the baseline metric is small.


### 2026-03-24 - Tradeoff display direction update

Display decision:
- for report reading, prefer a `single-model, multi-rec-metric` comparison figure first,
- defer the `multi-model, single-rec-metric` comparison figure as a follow-up TODO.

Reason:
- when the main question is `how one model trades explanation quality against multiple recommendation metrics`,
  overlaying `ndcg / hr / precision / recall` in one model-centered figure is easier to read than splitting them into many panels,
- cross-model comparison remains useful, but is better treated as a second report mode rather than the default first figure.

Current implementation status:
- `scripts/analysis/tradeoff_analyzer.py` now prioritizes the single-model multi-metric mode,
- multi-model comparison is intentionally left as a documented next step.


### 2026-03-24 - Tradeoff figure layout fix

Scope:
- fixed the overlap between the title and legends in the refined single-model tradeoff figure.

Changes tried:
- moved the recommendation-metric legend to the upper figure margin,
- moved the reading-guide legend to the lower figure margin,
- increased figure height slightly,
- replaced the old unconstrained `tight_layout()` call with an explicit `rect=[0.03, 0.12, 0.97, 0.86]` layout box.

Result:
- the formal PGPR tradeoff output now renders without the previous title/legend collision.

## Priority Queue

### Immediate Next Checks

1. Audit how missing or short baseline top-k lists propagate into grouped and overall metrics.
2. Identify why VRKG4Rec baseline exports still leave a non-trivial set of users below top-10.
3. Decide how repaired ETD-family sandbox outputs should be promoted into formal results for both VRKG4Rec and PGPR.

### After That

1. Review VRKG4Rec adapter score semantics versus original model ranking scores.
2. Revisit whether tradeoff plots should include absolute-value views in addition to percentage-change views.
3. Inspect the external VRKG4Rec training and evaluation code for possible performance bottlenecks.

## Update Template

When appending the next entry, use this structure:

```text
### YYYY-MM-DD - Short title

Scope:
- ...

Changes tried:
- ...

Validation method:
- ...

Validation result:
- ...

Decision:
- ...
```

### 2026-03-24 - VRKG4Rec candidate-pool sandbox validation

Scope:
- tested whether the VRKG4Rec baseline coverage gap is mainly caused by limiting path extraction to the model's raw top-10 items,
- kept the official adapter untouched and ran the experiment from an in-repo sandbox under `runs/debug_compare/2026-03-24_vrkg_adapter_pool/`.

Changes tried:
- copied `adapters/vrkg4rec_adapter.py` into the sandbox,
- added a sandbox-only `--candidate-topk` argument,
- kept final output at top-10 items, but expanded the internal item pool from 10 to 50 before checking which items have valid explanation paths,
- wrote the sandbox output to `xrecsys/paths/lastfm/agent_topk=10-12-1-cand50`.

Validation method:
- reran the sandbox adapter with `--topk 10 --candidate-topk 50`,
- compared the original baseline tag `10-12-1` against the sandbox tag `10-12-1-cand50`,
- audited `uid_topk.csv` and `uid_pid_explanation.csv` coverage with `runs/debug_compare/2026-03-24_vrkg_adapter_pool/results/coverage_compare.py`.

Validation result:
- original baseline:
  - `full_topk_users = 13143`
  - `lt10_users = 1499`
  - `zero_users = 78`
- candidate-pool sandbox:
  - `full_topk_users = 14559`
  - `lt10_users = 83`
  - `zero_users = 77`
- net change:
  - `full_topk_users = +1416`
  - `lt10_users = -1416`
  - `zero_users = -1`
- this strongly supports the earlier diagnosis that the baseline shortfall is mostly caused by the adapter only attempting path extraction on the raw top-10 items and not backfilling with lower-ranked explainable items.

Decision:
- treat the VRKG4Rec baseline coverage gap as primarily an adapter candidate-pool policy issue,
- keep the sandbox result as evidence that a larger internal item pool almost eliminates the coverage problem,
- do not promote the sandbox adapter into the official adapter yet; first decide whether the project wants a strict raw-top10 explainability policy or a fixed-top10-explainable policy.

### 2026-04-14 - Canonical LastFM PGPR/UCPR preprocess smoke test

Scope:
- tested whether the new `lastfm_v1` canonical dataset can feed both PGPR and UCPR through each model's own preprocessing code,
- used isolated smoke workspaces under `runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/`,
- did not overwrite historical PGPR/UCPR baseline directories.

Changes tried:
- generated a PGPR-compatible identity-mapping view,
- generated a UCPR compact-id view with explicit remap tables,
- copied each model's source into a smoke workspace and ran native preprocess there.

Validation method:
- PGPR: compare native `train_label.pkl` and `test_label.pkl` against canonical labels directly,
- UCPR: convert compact UCPR label ids back through `user_remap.tsv` and `product_remap.tsv`, then compare against canonical labels.

Validation result:
- PGPR native preprocessing:
  - train users/items: `15476 / 2773892`
  - test users/items: `14620 / 697133`
  - exact match with canonical labels: `true`
- UCPR native preprocessing after remap:
  - train users/items: `15476 / 2773892`
  - valid users/items: `15303 / 15303`
  - test users/items: `14620 / 697133`
  - exact match with canonical labels: `true`

Decision:
- treat the canonical LastFM data layer as smoke-validated for PGPR and UCPR preprocessing,
- proceed to expensive model-stage runs from the canonical views,
- keep the evaluation contract unchanged: model internals may use their own ids, but exported recommendations and paths must map back to canonical uid/pid before `xrecsys` evaluation.
