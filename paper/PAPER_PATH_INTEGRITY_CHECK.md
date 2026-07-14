# Paper Path Integrity Check

## 1. Current Draft Check

`paper/current_dissertation/FULL_DISSERTATION_CURRENT.md` exists and is SHA-256 identical to the selected V4 source. It contains 16 unchanged pipe tables and 29 citation keys.

## 2. Figure Link Check

| Image reference | Resolved path | Exists? | Action |
| --- | --- | --- | --- |
| figures/png/figure_3_1_framework_overview_final.png | paper/current_dissertation/figures/png/figure_3_1_framework_overview_final.png | Yes | Copied current asset |
| figures/png/figure_3_2_alpha_sweep_design_final.png | paper/current_dissertation/figures/png/figure_3_2_alpha_sweep_design_final.png | Yes | Copied current asset |
| figures/png/figure_3_3_validation_gate_flow_final.png | paper/current_dissertation/figures/png/figure_3_3_validation_gate_flow_final.png | Yes | Copied current asset |
| figures/png/figure_4_1_strict_ndcg_comparison_final.png | paper/current_dissertation/figures/png/figure_4_1_strict_ndcg_comparison_final.png | Yes | Copied current asset |
| figures/png/figure_4_2_explanation_endpoint_summary_final.png | paper/current_dissertation/figures/png/figure_4_2_explanation_endpoint_summary_final.png | Yes | Copied current asset |
| figures/png/figure_4_3_lir_tradeoff_final.png | paper/current_dissertation/figures/png/figure_4_3_lir_tradeoff_final.png | Yes | Copied current asset |
| figures/png/figure_4_4_sep_tradeoff_final.png | paper/current_dissertation/figures/png/figure_4_4_sep_tradeoff_final.png | Yes | Copied current asset |
| figures/png/figure_4_5_etd_tradeoff_final.png | paper/current_dissertation/figures/png/figure_4_5_etd_tradeoff_final.png | Yes | Copied current asset |
| figures/png/figure_5_1_pgpr_ucpr_ablation_final.png | paper/current_dissertation/figures/png/figure_5_1_pgpr_ucpr_ablation_final.png | Yes | Copied current asset |
| figures/png/figure_5_2_experiment_status_matrix_final.png | paper/current_dissertation/figures/png/figure_5_2_experiment_status_matrix_final.png | Yes | Copied current asset |
| figures/png/figure_c_1_amazon_boundary_flow_final.png | paper/current_dissertation/figures/png/figure_c_1_amazon_boundary_flow_final.png | Yes | Copied current asset |

## 3. Reference Check

`references/REFERENCES_CURRENT.bib`, `references/REFERENCES_DISPLAY_CURRENT.md`, and the compatibility `REFERENCES_ASSEMBLED_V1.bib` copy exist and match the archived assembly sources.

## 4. Evidence Check

| Evidence group | Copied file count | Status |
| --- | --- | --- |
| Literature review outputs | 8 | Present |
| Citation provenance | 5 | Present |
| Strict accuracy provenance | 1 | Present |
| Traceability | 1 | Present |
| Chapter evidence | 7 | Present |

## 5. Archive Check

All 25 recorded move destinations exist. 166 historical files are present in `_archive`; no selected V4 source file was moved.

## 6. Forbidden Action Check

All 252 pre-cleanup files are accounted for at their original or archived path with matching SHA-256. No delete command was used. `thesis_analysis_pack/` and `reports/` were not moved. No Word, PDF, or LaTeX file was generated.

## 7. Git Status Summary

Pre-cleanup status was clean. Final post-cleanup status categories: ` D`: 166, `??`: 12. All reported paths are under `paper/`: Yes.

Changes consist of archived paths, copied current/evidence files, and new manifests. Git may display these as deletions plus untracked destinations until staged; the hash audit proves non-destructive moves.

## 8. Integrity Result

**PASS_WITH_WARNINGS**

Warning: historical documents can contain textual references to their former pre-archive paths. Use `PAPER_ARCHIVE_MANIFEST.md` to resolve those paths.
