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

### 4. Training slowness is real but still not classified as a bug

Observed in VRKG4Rec training logs:
- training epochs are long,
- evaluation phases are also long,
- later epochs show some fluctuation.

Current interpretation:
- expensive runtime is confirmed,
- a training implementation bug is not yet confirmed.

## Remediation Log

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
