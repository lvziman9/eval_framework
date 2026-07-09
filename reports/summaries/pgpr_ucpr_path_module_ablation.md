# PGPR/UCPR Path-Module Ablation

Scope: PGPR is the main model; UCPR is the auxiliary model. Datasets are LastFM and ML-1M only.

Excluded by design: Amazon-Book classic baseline is not part of this ablation. Amazon-Book remains only an auxiliary large-dataset result from the existing main experiment.

The ablation is deterministic and read-only with respect to model artifacts: it consumes frozen uid_topk / uid_pid_explanation / pred_paths CSVs, canonical export validation JSON, and accuracy JSON. Legacy xrecsys alpha-sweep CSVs are not used for the main ablation because their optimizers can reconstruct top-k from the candidate pool at alpha=0.

Protocol: alpha=0 must exactly preserve the original recommender top-k ranking and original explanation path for every recommended item. For alpha>0, the module may only re-rank the frozen original top-k item set and/or choose alternative paths for those same items; it cannot introduce candidate-pool replacement items.

## Main Ablation Table

Use this table for the main text. It selects the largest explanation gain under a >=95% strict canonical NDCG-retention rule. When no alpha meets that rule, the row is explicitly marked as an endpoint exception.

| Dataset | Model | Module target | Selected alpha | Selection | NDCG retention | Explanation gain | NDCG scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 1.00 | max gain @ >=95% NDCG | 99.94% | 502.17% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | PGPR | SEP | 0.75 | max gain @ >=95% NDCG | 95.13% | 35.06% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | PGPR | ETD | 1.00 | max gain @ >=95% NDCG | 98.86% | 3.47% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 99.96% | 124.76% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | UCPR | SEP | 0.90 | max gain @ >=95% NDCG | 101.10% | 41.10% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 99.90% | 17.41% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | PGPR | LIR | 0.55 | max gain @ >=95% NDCG | 99.07% | 56.31% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | PGPR | SEP | 0.95 | max gain @ >=95% NDCG | 95.10% | 47.71% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | PGPR | ETD | 1.00 | max gain @ >=95% NDCG | 99.38% | 15.27% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 97.17% | 44.49% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | UCPR | SEP | 0.75 | max gain @ >=95% NDCG | 96.93% | 33.39% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 98.66% | 5.91% | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |

## Metric Scope

All rows in the main ablation use strict canonical NDCG@10, HR@10, Precision@10, and Recall@10 over the validated canonical test users. The earlier LastFM legacy sweep NDCG is intentionally excluded from the main table.

Strict accuracy provenance remains available below to connect these ablations to the validated main artifacts.

## Alpha=0 Baseline Preservation Validation

This validation is the key protocol check: every optimizer target must reproduce the frozen Original recommender exactly when alpha=0.

| Dataset | Model | Target | Exact top-k users | Exact explanation pairs | Top-k exact | Path exact | Max metric delta | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 14620/14620 | 145390/145390 | 100.00% | 100.00% | 0.00000000 | PASS |
| LastFM | PGPR | SEP | 14620/14620 | 145390/145390 | 100.00% | 100.00% | 0.00000000 | PASS |
| LastFM | PGPR | ETD | 14620/14620 | 145390/145390 | 100.00% | 100.00% | 0.00000000 | PASS |
| LastFM | UCPR | LIR | 14620/14620 | 140318/140318 | 100.00% | 100.00% | 0.00000000 | PASS |
| LastFM | UCPR | SEP | 14620/14620 | 140318/140318 | 100.00% | 100.00% | 0.00000000 | PASS |
| LastFM | UCPR | ETD | 14620/14620 | 140318/140318 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | PGPR | LIR | 6040/6040 | 60400/60400 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | PGPR | SEP | 6040/6040 | 60400/60400 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | PGPR | ETD | 6040/6040 | 60400/60400 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | UCPR | LIR | 6040/6040 | 50022/50022 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | UCPR | SEP | 6040/6040 | 50022/50022 | 100.00% | 100.00% | 0.00000000 | PASS |
| ML-1M | UCPR | ETD | 6040/6040 | 50022/50022 | 100.00% | 100.00% | 0.00000000 | PASS |

## Tradeoff Summary

This is the expanded version of the main table with selected strict-sweep NDCG and optimized metric values.

| Dataset | Model | Opt | Alpha | Selection | NDCG retention | Opt gain | Sweep NDCG | Opt value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 1.00 | max gain @ >=95% NDCG | 99.94% | 502.17% | 0.0309 | 0.0038 |
| LastFM | PGPR | SEP | 0.75 | max gain @ >=95% NDCG | 95.13% | 35.06% | 0.0294 | 0.7683 |
| LastFM | PGPR | ETD | 1.00 | max gain @ >=95% NDCG | 98.86% | 3.47% | 0.0306 | 0.1656 |
| LastFM | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 99.96% | 124.76% | 0.0374 | 0.0013 |
| LastFM | UCPR | SEP | 0.90 | max gain @ >=95% NDCG | 101.10% | 41.10% | 0.0378 | 0.7295 |
| LastFM | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 99.90% | 17.41% | 0.0373 | 0.1423 |
| ML-1M | PGPR | LIR | 0.55 | max gain @ >=95% NDCG | 99.07% | 56.31% | 0.1010 | 0.7222 |
| ML-1M | PGPR | SEP | 0.95 | max gain @ >=95% NDCG | 95.10% | 47.71% | 0.0969 | 0.7087 |
| ML-1M | PGPR | ETD | 1.00 | max gain @ >=95% NDCG | 99.38% | 15.27% | 0.1013 | 0.1875 |
| ML-1M | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 97.17% | 44.49% | 0.0838 | 0.6536 |
| ML-1M | UCPR | SEP | 0.75 | max gain @ >=95% NDCG | 96.93% | 33.39% | 0.0836 | 0.6583 |
| ML-1M | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 98.66% | 5.91% | 0.0851 | 0.2307 |

## Figures

- reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg
- reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg

## Provenance

| Dataset | Model | Role | Export | Accuracy | Canonical users | Top-k users | Pred path rows | Slot coverage | Validated accuracy NDCG | Strict baseline NDCG | Max rec delta | Alpha=0 preservation | NDCG scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | main | PASS | PASS | 14620 | 14620 | 11695015 | 0.9945 | 0.0309 | 0.0309 | 0.00000000 | PASS | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| LastFM | UCPR | auxiliary | PASS | PASS | 14620 | 14620 | 5294784 | 0.9598 | 0.0374 | 0.0374 | 0.00000000 | PASS | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | PGPR | main | PASS | PASS | 6040 | 6040 | 5457838 | 1.0000 | 0.1019 | 0.1019 | 0.00000000 | PASS | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |
| ML-1M | UCPR | auxiliary | PASS | PASS | 6040 | 6040 | 2543087 | 0.8282 | 0.0862 | 0.0862 | 0.00000000 | PASS | strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking |

## Qualitative Explanation Cases

These cases are qualitative illustrations of the strict alpha=1 ETD module; quantitative evidence is the validated alpha sweep above.

| Dataset | Model | User | Unique path types | Changed top-10 positions |
| --- | --- | --- | --- | --- |
| LastFM | PGPR | 34 | 1 -> 2 | 7 |
| LastFM | UCPR | 2086 | 1 -> 2 | 2 |
| ML-1M | PGPR | 0 | 1 -> 2 | 5 |
| ML-1M | UCPR | 36 | 1 -> 2 | 3 |

Detailed cases are in `reports/cases/ablation/pgpr_ucpr_path_module_cases.md` and the companion JSON file.

## Appendix: Alpha=1 Endpoint Stress Test

Do not use this as the main ablation table. These rows show the extreme alpha=1 setting; large recommendation drops are expected for some targets and help characterize the performance-explainability boundary.

| Dataset | Model | Role | Condition | Opt | Alpha | NDCG | HR | Precision | Recall | LIR | SEP | ETD | NDCG delta | Opt metric delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | main | Original recommender | none | 0.00 | 0.0309 | 0.1864 | 0.0254 | 0.0177 | 0.0006 | 0.5688 | 0.1601 | 0.00% |  |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0309 | 0.1864 | 0.0254 | 0.0177 | 0.0038 | 0.5685 | 0.1598 | -0.06% | 502.17% |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0276 | 0.1864 | 0.0254 | 0.0177 | 0.0006 | 0.7683 | 0.1656 | -10.54% | 35.06% |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | ETD | 1.00 | 0.0306 | 0.1864 | 0.0254 | 0.0177 | 0.0006 | 0.5710 | 0.1656 | -1.14% | 3.47% |
| LastFM | UCPR | auxiliary | Original recommender | none | 0.00 | 0.0374 | 0.2164 | 0.0311 | 0.0232 | 0.0006 | 0.5170 | 0.1212 | 0.00% |  |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0374 | 0.2164 | 0.0311 | 0.0232 | 0.0013 | 0.5170 | 0.1212 | -0.04% | 124.76% |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0371 | 0.2164 | 0.0311 | 0.0232 | 0.0005 | 0.7295 | 0.1430 | -0.64% | 41.10% |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | ETD | 1.00 | 0.0373 | 0.2164 | 0.0311 | 0.0232 | 0.0006 | 0.5268 | 0.1423 | -0.10% | 17.41% |
| ML-1M | PGPR | main | Original recommender | none | 0.00 | 0.1019 | 0.5113 | 0.0929 | 0.0423 | 0.4620 | 0.4798 | 0.1626 | 0.00% |  |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0986 | 0.5113 | 0.0929 | 0.0423 | 0.7222 | 0.4884 | 0.1584 | -3.20% | 56.31% |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0958 | 0.5113 | 0.0929 | 0.0423 | 0.4661 | 0.7087 | 0.1580 | -5.95% | 47.71% |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | ETD | 1.00 | 0.1013 | 0.5113 | 0.0929 | 0.0423 | 0.4636 | 0.4797 | 0.1875 | -0.62% | 15.27% |
| ML-1M | UCPR | auxiliary | Original recommender | none | 0.00 | 0.0862 | 0.4419 | 0.0664 | 0.0379 | 0.4524 | 0.4935 | 0.2178 | 0.00% |  |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0838 | 0.4419 | 0.0664 | 0.0379 | 0.6536 | 0.4911 | 0.2178 | -2.83% | 44.49% |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0809 | 0.4419 | 0.0664 | 0.0379 | 0.4439 | 0.6583 | 0.2192 | -6.20% | 33.39% |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | ETD | 1.00 | 0.0851 | 0.4419 | 0.0664 | 0.0379 | 0.4515 | 0.4905 | 0.2307 | -1.34% | 5.91% |
