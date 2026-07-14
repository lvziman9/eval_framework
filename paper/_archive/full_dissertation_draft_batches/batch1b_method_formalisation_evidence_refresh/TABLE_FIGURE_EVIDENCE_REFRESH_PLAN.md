# Table and Figure Evidence Refresh Plan

## 1. Scope

This plan refreshes evidence-role wording for Table 3.6, Table 5.2, Table 5.4, and Figures 3.1-5.2. It does not regenerate figures, insert images into the dissertation, change experimental values, or perform final NTU, Word, PDF, or Markdown formatting.

The revised standalone text is stored in `REVISED_TABLES_AND_CAPTIONS.md`. Existing table and figure source files remain unchanged.

## 2. Source Review

| Item | Current source | Issue identified | Refresh action | Status |
| --- | --- | --- | --- | --- |
| Table 3.6 | `paper/drafts_ch3_6/chapter3_tables.md` | Strict accuracy row refers to accuracy JSONs without stating that none of the twelve expected files is accessible. | Use the canonical status matrix plus matching final summary and retain the `0/12` caveat; add configuration-freeze limits. | Refreshed in standalone output |
| Table 5.2 | `paper/drafts_ch3_6/chapter5_tables.md` | UCPR, KGGLM, XRecSys, and other citation statuses pre-date the verified register. | Use verified primary-source status, retain PEARLM partial status, and distinguish ablation-supported from descriptive mechanism wording. | Refreshed in standalone output |
| Table 5.4 | `paper/drafts_ch3_6/chapter5_tables.md` | Citation and provenance caveats are stale or distributed across several rows; SEP guide/code weight direction is unresolved. | Consolidate user-study, significance, Amazon, metric-implementation, strict-primary-artifact, bibliography, configuration, and SEP verification caveats. | Refreshed in standalone output |
| Figures 3.1-3.2 | Chapter 3 figure specifications and integration plan | Figure 3.2 source wording can imply accessible strict JSON artifacts. | State conceptual and evidence-separation roles; use accessible strict summaries and the missing-primary caveat. | Captions refreshed |
| Figures 4.1-4.6 | Chapter 4 tables, figure plan, and integration plan | Captions need explicit strict-versus-sweep roles. | Identify strict figures separately from alpha-sweep figures; keep Figures 4.5-4.6 optional or appendix. | Captions refreshed |
| Figures 5.1-5.2 | Chapter 5 figure plan and integration plan | Ablation and validation-status roles need explicit boundaries. | State frozen-item-set ablation scope and identify the Amazon matrix as validation status, not performance ranking. | Captions refreshed |

## 3. Revised Table Placement

| Table | Proposed placement | Evidence role | Required boundary |
| --- | --- | --- | --- |
| Table 3.6 | Chapter 3.6 | Register the distinct experiment and provenance streams. | Strict accuracy, alpha sweep, ablation, and boundary status remain separate; configuration is not frozen. |
| Table 5.2 | Chapter 5.2 | Grade mechanism context and citation closure. | Stronger evidence is limited to the registered PGPR/UCPR ablation; other model-specific mechanism interpretations remain descriptive. |
| Table 5.4 | Chapter 5.5 | Consolidate limitations and submission actions. | Missing evidence must not be converted into results or final citation claims. |

## 4. Revised Caption Placement

| Figure | Proposed placement | Main text or appendix | Evidence role |
| --- | --- | --- | --- |
| Figure 3.1 | Chapter 3.1 | Main text | Conceptual framework and validation workflow |
| Figure 3.2 | Chapter 3.6 | Main text | Conceptual separation of strict, sweep, and ablation streams |
| Figure 4.1 | Chapter 4.2 | Main text | LastFM strict accuracy |
| Figure 4.2 | Chapter 4.2 | Main text | ML-1M strict accuracy |
| Figure 4.3 | Chapter 4.3 | Main text | Alpha-sweep explanation endpoints |
| Figure 4.4 | Chapter 4.4 | Main text | LIR-sweep paired response |
| Figure 4.5 | Chapter 4.5 | Optional / appendix | SEP-sweep paired response |
| Figure 4.6 | Chapter 4.6 | Optional / appendix | ETD-sweep paired response |
| Figure 5.1 | Chapter 5.1 | Main text | PGPR/UCPR ablation under the registered retention protocol |
| Figure 5.2 | Chapter 5.4 | Main text | Validation and boundary status |

## 5. Evidence Wording Rules

1. Strict accuracy values are traceable to the accessible canonical status matrix and matching dissertation summary table; the twelve primary JSON artifacts are not accessible.
2. Alpha-sweep NDCG is paired sweep evidence and must not be called strict NDCG@10.
3. LIR, SEP, and ETD are computational path properties under repository-specific implementations, not user-perceived explanation quality; the SEP low-degree / high-weight interpretation remains subject to guide/code reconciliation.
4. PGPR/UCPR ablation supports bounded controllability under its registered scope and does not establish six-model superiority.
5. Amazon-Book KGAT is a partial boundary case with three PASS and three BLOCKED / N/A rows, not a complete main experiment.
6. External papers support model or conceptual context; repository artifacts support experimental values.

## 6. Deferred Work

Final numbering style, caption typography, image insertion, panel assembly, pagination, cross-references, bibliography generation, and NTU Word/PDF formatting remain deferred. Figure files are not regenerated in Batch 1B.
