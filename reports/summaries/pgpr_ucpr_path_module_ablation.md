# PGPR/UCPR Path-Module Ablation

Scope: PGPR is the main model; UCPR is the auxiliary model. Datasets are LastFM and ML-1M only.

Excluded by design: Amazon-Book classic baseline is not part of this ablation. Amazon-Book remains only an auxiliary large-dataset result from the existing main experiment.

The ablation is deterministic and read-only with respect to model artifacts: it consumes frozen xrecsys alpha-sweep CSVs, canonical export validation JSON, and accuracy JSON.

## Main Ablation Table

Use this table for the main text. It selects the largest explanation gain under a >=95% within-sweep NDCG-retention rule. When no alpha meets that rule, the row is explicitly marked as an endpoint exception.

| Dataset | Model | Module target | Selected alpha | Selection | NDCG retention | Explanation gain | NDCG scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 0.95 | max gain @ >=95% NDCG | 99.03% | 191.62% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | PGPR | SEP | 0.30 | max gain @ >=95% NDCG | 95.22% | 62.41% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | PGPR | ETD | 0.40 | max gain @ >=95% NDCG | 95.37% | 84.25% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 98.02% | 146.74% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | UCPR | SEP | 1.00 | max gain @ >=95% NDCG | 98.58% | 80.58% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 100.75% | 53.16% | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| ML-1M | PGPR | LIR | 0.25 | max gain @ >=95% NDCG | 95.36% | 98.87% | canonical-all-users sweep NDCG |
| ML-1M | PGPR | SEP | 0.15 | max gain @ >=95% NDCG | 96.62% | 82.75% | canonical-all-users sweep NDCG |
| ML-1M | PGPR | ETD | 1.00 | no >=95%; alpha=1 endpoint | 80.32% | 219.19% | canonical-all-users sweep NDCG |
| ML-1M | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 96.10% | 62.26% | canonical-all-users sweep NDCG |
| ML-1M | UCPR | SEP | 1.00 | max gain @ >=95% NDCG | 95.68% | 50.07% | canonical-all-users sweep NDCG |
| ML-1M | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 115.07% | 17.31% | canonical-all-users sweep NDCG |

## Metric Scope

LastFM alpha sweeps use sweep-internal legacy NDCG. In this report, LastFM NDCG is used only for within-sweep retention and should not be mixed with the strict main-experiment accuracy NDCG. ML-1M sweeps use the canonical-all-users sweep protocol.

Strict accuracy provenance remains available below to connect these ablations to the validated main artifacts.

## Tradeoff Summary

This is the expanded version of the main table with selected sweep NDCG and optimized metric values.

| Dataset | Model | Opt | Alpha | Selection | NDCG retention | Opt gain | Sweep NDCG | Opt value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | LIR | 0.95 | max gain @ >=95% NDCG | 99.03% | 191.62% | 0.1119 | 0.0219 |
| LastFM | PGPR | SEP | 0.30 | max gain @ >=95% NDCG | 95.22% | 62.41% | 0.1076 | 0.9238 |
| LastFM | PGPR | ETD | 0.40 | max gain @ >=95% NDCG | 95.37% | 84.25% | 0.1077 | 0.2950 |
| LastFM | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 98.02% | 146.74% | 0.1231 | 0.0118 |
| LastFM | UCPR | SEP | 1.00 | max gain @ >=95% NDCG | 98.58% | 80.58% | 0.1238 | 0.9336 |
| LastFM | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 100.75% | 53.16% | 0.1265 | 0.1856 |
| ML-1M | PGPR | LIR | 0.25 | max gain @ >=95% NDCG | 95.36% | 98.87% | 0.0972 | 0.9190 |
| ML-1M | PGPR | SEP | 0.15 | max gain @ >=95% NDCG | 96.62% | 82.75% | 0.0984 | 0.8768 |
| ML-1M | PGPR | ETD | 1.00 | no >=95%; alpha=1 endpoint | 80.32% | 219.19% | 0.0818 | 0.5191 |
| ML-1M | UCPR | LIR | 1.00 | max gain @ >=95% NDCG | 96.10% | 62.26% | 0.0829 | 0.7342 |
| ML-1M | UCPR | SEP | 1.00 | max gain @ >=95% NDCG | 95.68% | 50.07% | 0.0825 | 0.7406 |
| ML-1M | UCPR | ETD | 1.00 | max gain @ >=95% NDCG | 115.07% | 17.31% | 0.0992 | 0.2555 |

## Figures

- reports/figures/ablation/pgpr_ucpr_path_module/lastfm_ndcg_tradeoff.svg
- reports/figures/ablation/pgpr_ucpr_path_module/ml1m_ndcg_tradeoff.svg

## Provenance

| Dataset | Model | Role | Export | Accuracy | Canonical users | Top-k users | Pred path rows | Slot coverage | Strict accuracy NDCG | Sweep NDCG scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | main | PASS | PASS | 14620 | 14620 | 11695015 | 0.9945 | 0.0309 | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| LastFM | UCPR | auxiliary | PASS | PASS | 14620 | 14620 | 5294784 | 0.9598 | 0.0374 | sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy |
| ML-1M | PGPR | main | PASS | PASS | 6040 | 6040 | 5457838 | 1.0000 | 0.1019 | canonical-all-users sweep NDCG |
| ML-1M | UCPR | auxiliary | PASS | PASS | 6040 | 6040 | 2543087 | 0.8282 | 0.0862 | canonical-all-users sweep NDCG |

## Qualitative Explanation Cases

These cases are qualitative illustrations only; they are not quantitative evidence and are not a full alpha-sweep reproduction.

| Dataset | Model | User | Unique path types | Changed top-10 positions |
| --- | --- | --- | --- | --- |
| LastFM | PGPR | 12294 | 2 -> 5 | 3 |
| LastFM | UCPR | 12294 | 2 -> 4 | 2 |
| ML-1M | PGPR | 0 | 1 -> 6 | 4 |
| ML-1M | UCPR | 0 | 2 -> 3 | 1 |

Detailed cases are in `reports/cases/ablation/pgpr_ucpr_path_module_cases.md` and the companion JSON file.

## Appendix: Alpha=1 Endpoint Stress Test

Do not use this as the main ablation table. These rows show the extreme alpha=1 setting; large recommendation drops are expected for some targets and help characterize the performance-explainability boundary.

| Dataset | Model | Role | Condition | Opt | Alpha | NDCG | HR | Precision | Recall | LIR | SEP | ETD | NDCG delta | Opt metric delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LastFM | PGPR | main | Original recommender | none | 0.00 | 0.1130 | 0.1875 | 0.0255 | 0.0110 | 0.0075 | 0.5688 | 0.1601 | 0.00% |  |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0680 | 0.0921 | 0.0106 | 0.0048 | 0.0219 | 0.5551 | 0.1690 | -39.80% | 191.64% |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0676 | 0.0937 | 0.0107 | 0.0048 | 0.0080 | 0.9877 | 0.2481 | -40.11% | 73.65% |
| LastFM | PGPR | main | Recommender + proposed explanation/path module | ETD | 1.00 | 0.1049 | 0.1608 | 0.0202 | 0.0090 | 0.0070 | 0.5978 | 0.3552 | -7.11% | 121.90% |
| LastFM | UCPR | auxiliary | Original recommender | none | 0.00 | 0.1256 | 0.2197 | 0.0316 | 0.0150 | 0.0048 | 0.5170 | 0.1212 | 0.00% |  |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | LIR | 1.00 | 0.1231 | 0.1998 | 0.0294 | 0.0134 | 0.0118 | 0.5097 | 0.1153 | -1.98% | 146.74% |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | SEP | 1.00 | 0.1238 | 0.2067 | 0.0278 | 0.0127 | 0.0054 | 0.9336 | 0.1698 | -1.42% | 80.58% |
| LastFM | UCPR | auxiliary | Recommender + proposed explanation/path module | ETD | 1.00 | 0.1265 | 0.2091 | 0.0299 | 0.0135 | 0.0048 | 0.5343 | 0.1856 | 0.75% | 53.16% |
| ML-1M | PGPR | main | Original recommender | none | 0.00 | 0.1019 | 0.5113 | 0.0929 | 0.0423 | 0.4621 | 0.4798 | 0.1626 | 0.00% |  |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0619 | 0.3495 | 0.0510 | 0.0205 | 0.9627 | 0.4752 | 0.1448 | -39.21% | 108.33% |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0579 | 0.3260 | 0.0459 | 0.0180 | 0.4726 | 0.9833 | 0.1764 | -43.18% | 104.95% |
| ML-1M | PGPR | main | Recommender + proposed explanation/path module | ETD | 1.00 | 0.0818 | 0.4323 | 0.0667 | 0.0288 | 0.4756 | 0.4915 | 0.5191 | -19.68% | 219.19% |
| ML-1M | UCPR | auxiliary | Original recommender | none | 0.00 | 0.0862 | 0.4419 | 0.0664 | 0.0379 | 0.4525 | 0.4935 | 0.2178 | 0.00% |  |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | LIR | 1.00 | 0.0829 | 0.4233 | 0.0622 | 0.0348 | 0.7342 | 0.4867 | 0.2208 | -3.90% | 62.26% |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | SEP | 1.00 | 0.0825 | 0.4187 | 0.0620 | 0.0340 | 0.4448 | 0.7406 | 0.2206 | -4.32% | 50.07% |
| ML-1M | UCPR | auxiliary | Recommender + proposed explanation/path module | ETD | 1.00 | 0.0992 | 0.3978 | 0.0809 | 0.0389 | 0.4582 | 0.4845 | 0.2555 | 15.07% | 17.31% |
