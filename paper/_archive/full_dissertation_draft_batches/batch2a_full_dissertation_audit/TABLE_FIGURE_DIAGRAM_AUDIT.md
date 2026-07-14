# Table, Figure, and Diagram Audit

The V5 placement decision is authoritative where it conflicts with older chapter plans. In particular, Figure 4.5 is a main-text SEP figure. This audit recommends later placement only; it does not render, edit, or renumber any asset.

| Table / figure / diagram | Proposed location | Evidence role | Main text / appendix | Risk | Required action |
| --- | --- | --- | --- | --- | --- |
| Table 3.1 Canonical dataset and model-view requirements | Section 3.2 | Defines shared truth and permitted heterogeneous views | Main text | Low | Keep as the compact implementation-requirement summary. |
| Table 3.2 Native-path export contract | Section 3.3 | Defines required recommendation, path, and explanation artifacts | Main text | Low | Keep; ensure artifact names and native-path scope match the prose. |
| Table 3.3 Evaluation metrics | Section 3.4 | Separates strict accuracy from LIR, SEP, and ETD | Main text | High | Replace the stale SEP description with the frozen repository-specific operational wording. |
| Table 3.4 Validation checks | Section 3.4 | Defines reportability checks | Main text | Low | Keep and align its statuses with the formal validation gate. |
| Table 3.5 Framework verification summary | Section 3.5 | Shows complete main scope and Amazon boundary | Main text | Low | Keep PASS versus BLOCKED/N/A interpretation explicit. |
| Table 3.6 Evidence streams and provenance boundaries | Section 3.6 | Prevents strict, sweep, ablation, and boundary evidence mixing | Main text | Medium | Use the V5 revised version as authoritative; retain all provenance caveats. |
| Table 3.7 Representative endpoint verification examples | End of Chapter 3 | Demonstrates source-to-endpoint traceability | Appendix | Medium | Move to appendix if retained; it duplicates Chapter 4 endpoint reporting. |
| Table 4.1 Strict accuracy results | Section 4.2 | Reports four strict metrics for twelve main rows | Main text | High | Keep summary-level provenance and the unavailable-primary-JSON caveat with the caption or note. |
| Table 4.2 Explanation metric endpoints | Section 4.3 | Reports alpha=0 to alpha=1 LIR, SEP, and ETD endpoints | Main text | Low | Keep sweep labels explicit and separate from strict accuracy. |
| Table 4.3 Figure inventory | Evidence appendix or production manifest | Maps figures to sources and evidence roles | Appendix | Medium | Do not present as a research result; update Figure 4.5 from optional to main text. |
| Table 5.1 Ablation evidence summary | Section 5.1, with full detail in appendix if needed | Reports alpha-zero preservation and 95% retention selections for PGPR/UCPR | Main text plus appendix detail | Medium | Keep a concise main table and move long paths/precision-heavy detail to the appendix without changing values. |
| Table 5.2 Mechanism context and evidence grade | Section 5.3 | Separates ablation-supported and descriptive mechanism interpretation | Main text | High | Use the V5 revised citation and SEP wording; exclude the stale Chapter 5 source table. |
| Table 5.3 Amazon boundary summary | Section 5.4 | Shows three PASS and three BLOCKED/N/A rows | Main text | Low | Keep unavailable evidence visible and do not rank blocked rows. |
| Table 5.4 Limitations and required actions | Section 5.5 | Consolidates evidence, metric, citation, and reproducibility limits | Main text | High | Use the V5 revised table; exclude stale degree/popularity/serendipity and citation-status text. |
| Figure 3.1 Framework overview | Section 3.1 | Shows canonical dataflow, export, validation, and reporting | Main text | Low | Insert the existing asset with the frozen caption; merge D3.1 content rather than adding a duplicate figure. |
| Figure 3.2 Alpha-sweep design | Section 3.6 | Shows objective-specific sweeps and evidence separation | Main text | Low | Insert the existing asset; merge D4.1 and D3.5 content and label sweep NDCG explicitly. |
| Figure 4.1 LastFM strict accuracy | Section 4.2 | Visualises strict HR@10 and NDCG@10 | Main text | High | Retain the summary-level provenance caveat; do not imply statistical significance. |
| Figure 4.2 ML-1M strict accuracy | Section 4.2 | Visualises strict HR@10 and NDCG@10 | Main text | High | Retain the summary-level provenance caveat; do not imply statistical significance. |
| Figure 4.3 Explanation endpoints | Section 4.3 | Compares alpha-sweep endpoint movement | Main text | Medium | Keep SEP operational wording and state that endpoints are not strict accuracy or human evidence. |
| Figure 4.4 LIR-oriented sweep | Section 4.4 | Shows LIR movement with paired sweep NDCG | Main text | Low | Label the ranking axis as sweep evidence and retain dataset/model scope. |
| Figure 4.5 SEP-oriented sweep | Section 4.5 | Shows one of the clearest implemented SEP trade-off profiles | Main text | Medium | Follow the V5 placement decision; use the frozen caption and do not infer rarity, direction, or user-perceived serendipity. |
| Figure 4.6 ETD-oriented sweep | Section 4.6 or appendix | Shows ETD movement with paired sweep NDCG | Appendix preferred | Low | Retain only if it adds value beyond Table 4.2 and the text; preserve the taxonomy caveat. |
| Figure 5.1 PGPR/UCPR ablation | Section 5.1 | Shows bounded ablation trade-offs and retained operating points | Main text | Low | Keep PGPR/UCPR, frozen-item-set, alpha-zero, and retention scope in the caption. |
| Figure 5.2 Validation-status matrix | Section 5.4 | Shows experiment reportability and Amazon boundary | Main text | Low | State that status is not performance and blocked rows are not ranked. |
| D3.1 Framework dataflow | Merge into Figure 3.1 | Expands canonical-to-reporting workflow | Main text, merged | Medium | Do not render as an additional figure; consolidate with Figure 3.1 to reduce density. |
| D3.2 Validation gate flowchart | Section 3.4 | Shows the reportability decision | Main text | Low | Render later as a compact monochrome vector only if Figure 3.1 cannot show the gate clearly. |
| D3.3 Single-example trace | Section 3.3 or appendix | Illustrates artifact alignment without experimental values | Appendix/table preferred | Medium | Use the corrected V5 `j*` trace as a table; do not present placeholders as observed evidence. |
| D3.4 Metric-anchor schematic | Section 3.4 or appendix | Maps seed item, bridge entity, and path type to LIR, SEP, and ETD | Appendix preferred | Medium | Render only after frozen SEP wording is applied; a compact notation table may be clearer. |
| D4.1 Alpha-sweep process | Merge into Figure 3.2 | Shows objective-specific movement and paired sweep NDCG | Main text, merged | Medium | Consolidate with Figure 3.2 instead of creating a second process figure. |
| D3.5 Evidence-stream separation | Merge into Figure 3.2 | Prevents strict, endpoint, sweep, ablation, and boundary mixing | Main text, merged | Low | Give streams distinct labels without implying a common scale. |
| D4.2 Trade-off pattern schematic | Section 4.7 | Summarises descriptive pattern types | Main text table | Medium | Keep as a table, not a plotted quadrant, to avoid implying quantitative coordinates or a new metric. |
| D5.1 Ablation evidence flow | Section 5.1 or appendix | Shows baseline preservation, sweep, retention, and bounded interpretation | Appendix preferred | Medium | Use Figure 5.1 as main evidence; render this only as protocol support if needed. |
| D5.2 95% retention operating point | Appendix | Explains the registered selection rule | Appendix | Low | Keep threshold explicitly limited to PGPR/UCPR ablation. |
| D5.3 Amazon boundary flow | Appendix | Shows export, validation, and sweep availability decisions | Appendix | Low | Use Figure 5.2 as the main boundary visual and retain this as supplementary process detail. |

The intended main-text visual set is already substantial. Merging related conceptual diagrams avoids repeating evidence roles and leaves the appendix for trace, metric-anchor, retention, and boundary process detail. Any later SVG rendering belongs to Batch 2E and must preserve the frozen captions and source assets.
