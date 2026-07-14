# Method Formalisation Notes

## 1. What Batch 1 Already Fixed

Batch 1 strengthened Chapter 4 with result-level findings, curve-pattern interpretation, and an empirical pattern summary while preserving the registered experimental values. It also extended Chapter 3.6 with the top-k setting, the 21-point alpha grid, the separation of strict accuracy from alpha-sweep metrics, and a provenance boundary for model-native configuration.

Those Chapter 4 findings remain the baseline for Batch 1B and are not rewritten. The Batch 1 configuration audit also remains authoritative for accessible and unavailable model settings.

## 2. Remaining Formalisation Gap

The Batch 1 chapters described the evaluation workflow accurately but did not yet provide one coherent mathematical notation for canonical identifiers, native paths, export evidence, validation eligibility, strict metrics, explanation metrics, sweep deltas, ablation retention, and boundary sets. Standalone Table 3.6, Table 5.2, Table 5.4, and the registered figure captions also retained evidence wording that pre-dated the current citation and strict-accuracy audits.

Batch 1B addresses only this formalisation and evidence-display gap. The formulas formalise the evaluation framework; they do not define a new recommender architecture, training procedure, or recommender model.

## 3. Definitions Needed in Chapter 3

Chapter 3 requires a notation set for datasets, canonical users and items, knowledge graphs, models, model-dataset rows, recommendation lists, native paths, validation eligibility, explanation objectives, and the alpha control parameter. It also requires explicit canonical return mappings from model-specific identifier spaces.

The native-path contract needs formal definitions for the top-k list, path triples, endpoint conditions, path validity, the three-file export package, and the explanation set. The validation checks need a binary eligibility gate that distinguishes reportable rows from boundary evidence.

Strict HR@K, Precision@K, Recall@K, DCG@K, and NDCG@K must be stated separately from paired sweep metrics. LIR, SEP, and ETD require verified path anchors, repository-specific definitions, and user- and dataset-level aggregation. The alpha sweep requires abstract top-k notation because one common linear score formula does not match all three objective implementations.

## 4. Formula Notation Needed in Chapter 4

Chapter 4 requires endpoint deltas for each explanation objective and its paired sweep NDCG. The deltas make the already reported direction and magnitude explicit without adding a new result, ratio, statistical test, or causal explanation.

The Batch 1 findings, numerical endpoints, curve descriptions, and empirical pattern summary remain unchanged. Delta notation supplements those findings and continues to distinguish sweep NDCG from strict NDCG@10.

## 5. Formula Notation Needed in Chapter 5

Chapter 5 requires a baseline-preservation indicator for the registered PGPR/UCPR ablation, an NDCG-retention ratio, and a constrained operating-point definition under the existing 95% retention rule. It also requires eligible and boundary sets derived from the Chapter 3 validation gate.

These formulas formalise the registered ablation and boundary evidence only. They do not extend mechanism evidence beyond PGPR and UCPR, define six-model superiority, or convert the Amazon-Book KGAT boundary case into a complete experiment.

## 6. Tables and Captions Still Requiring Refresh

Table 3.6 must replace the obsolete implication that primary strict-accuracy JSON files are accessible with the canonical status matrix plus matching final summary and the explicit `0/12` caveat. It must also retain the separation of strict accuracy, alpha sweeps, ablation, and boundary evidence and record that checkpoint hashes, seeds, and several model-native hyperparameters are not frozen.

Table 5.2 must use the verified citation register for UCPR, KGGLM, and XRecSys while keeping PEARLM's final venue and DOI unresolved. Table 5.4 must consolidate the missing user-study, statistical-significance, strict-primary-artifact, repository-specific metric, partial Amazon, bibliography, and reproducibility caveats.

Figures 3.1-5.2 require captions that identify whether each item is a conceptual workflow, strict result, alpha-sweep result, ablation result, or validation-status display. Optional Figures 4.5 and 4.6 remain appendix candidates.

## 7. Formulas Not to Add

Batch 1B does not add model-internal training objectives for PGPR, UCPR, CAFE, TPRec, KGGLM, or PEARLM. It does not add a statistical-significance formula, a user-study utility or trust formula, or a composite explanation-quality score.

A universal linear alpha-sweep formula is not added. `xrecsys/optimizations.py` directly shows linear candidate-score weighting for LIR and SEP, but ETD uses path-type bins and an unseen-type bonus. The shared notation therefore remains the implementation-specific abstract function \(S_{\alpha}^{m,d,q}\).

No trade-off efficiency ratio, new model objective, new training configuration, or inferred checkpoint identity is introduced.

## 8. Evidence Boundaries

Strict accuracy values are traceable at draft level to `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`. The twelve expected row-level primary JSON artifacts remain inaccessible (`0/12`) and must not be described as inspected or verified.

Alpha-sweep metrics come from the registered trade-off CSVs and do not replace strict accuracy. PGPR/UCPR ablation evidence is stronger for baseline preservation and bounded controllability but remains limited to its frozen-item-set protocol. CAFE, TPRec, KGGLM, and PEARLM mechanism interpretations remain descriptive rather than causal.

The SEP anchor is verified, but the intended weight direction is not closed. The path-metric guide states that lower-degree bridge entities receive higher weights, whereas the accessible matrix-generation code sorts degree ascending and assigns increasing EMA weights. This discrepancy requires manual formula/code verification and is not resolved by changing existing values in Batch 1B.

Amazon-Book KGAT remains a partial boundary case. LIR, SEP, and ETD use the verified XRecSys paper as their conceptual source, while their exact evaluated implementation is repository-specific. No statistical-significance or user-study artifact is available. PEARLM final venue and publisher DOI, exact checkpoint paths and hashes, seeds, several model-native hyperparameters, and final BibTeX formatting require manual verification.
