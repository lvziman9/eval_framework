# Main Text vs Appendix Figure Decision

| Figure | Main text / appendix | Reason | Action |
| --- | --- | --- | --- |
| Figure 3.1 framework overview | Main text | Establishes the evaluation architecture used by later chapters | Regenerate and retain |
| Figure 3.2 alpha-sweep design | Main text | Makes the strict/sweep/ablation evidence separation explicit | Regenerate and retain |
| Figure 3.3 validation gate flow | Main text | Defines reportability before result interpretation | Replace Mermaid and retain |
| Figure 4.1 strict NDCG@10 | Main text | Supports the central strict-accuracy comparison without mixing metrics | Replace two mixed charts with one figure |
| Figure 4.2 endpoint summary | Main text | Provides a compact cross-objective endpoint view beyond the row-by-row table | Regenerate and retain |
| Figure 4.3 LIR trade-off | Main text | Supports the LIR result narrative with complete trajectories | Regenerate and retain |
| Figure 4.4 SEP trade-off | Main text | Preserves the required SEP trend analysis and frozen semantic boundary | Regenerate and retain |
| Figure 4.5 ETD trade-off | Main text | Supports the ETD result narrative with complete trajectories | Regenerate and retain |
| Figure 5.1 PGPR/UCPR ablation | Main text | Supplies the registered controllability evidence while exposing the subset boundary | Regenerate and retain |
| Figure 5.2 experiment-status matrix | Main text | Summarises reportability and the partial Amazon boundary | Regenerate and retain |
| Figure C.1 Amazon boundary flow | Appendix C | The flow is useful for auditability but duplicates the main Table 5.3 and Figure 5.2 boundary account | Replace Mermaid, renumber, and move |

No separate HR@10 appendix figure is included. Table 4.1 preserves the full strict metric set, and the main narrative does not require an additional HR-only visual.
