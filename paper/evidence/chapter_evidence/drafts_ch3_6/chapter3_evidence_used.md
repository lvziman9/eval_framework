# Chapter 3 Evidence Used

| Evidence ID | Repo-relative path | Evidence type | Used in section | Claim supported | Notes |
| --- | --- | --- | --- | --- | --- |
| INT-CH3-001 | `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` | methodology evidence | 3.1-3.6 | Chapter 3 framework design, pipeline stages, and diagram basis. | Main prepared Chapter 3 source. |
| INT-CH3-002 | `docs/guides/CANONICAL_DATASET_STANDARD.md` | methodology evidence | 3.2 | Canonical dataset defines shared users, products, splits, labels, KG provenance, and export mapping. | Primary canonical-layer evidence. |
| INT-CH3-003 | `docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md` | methodology evidence | 3.1, 3.3 | Native-path models receive explanation scoring; non-path models are accuracy-only references. | Supports native/post-hoc separation. |
| INT-CH3-004 | `docs/guides/PATH_METRICS_GUIDE.md` | methodology evidence | 3.3, 3.4 | LIR, SEP, and ETD depend on native path structure. | Internal metric implementation guide. |
| INT-CH3-005 | `thesis_analysis_pack/validation_status_table.md` | validation evidence | 3.4, 3.5 | LastFM and ML-1M have six PASS rows; Amazon-Book KGAT has three PASS and three blocked/N/A rows. | Validation summary. |
| INT-CH3-006 | `thesis_analysis_pack/final_accuracy_summary_table.md` | strict accuracy evidence | 3.5 | Strict accuracy is available for complete LastFM, ML-1M, and partial Amazon rows. | Strict accuracy only. |
| INT-CH3-007 | `thesis_analysis_pack/final_explanation_summary_table.md` | alpha-sweep evidence | 3.5, 3.6 | Explanation endpoint examples exist for LastFM and ML-1M; Amazon explanation sweeps are N/A. | Must not replace strict accuracy. |
| INT-CH3-008 | `reports/tables/ablation/pgpr_ucpr_path_module/` | ablation evidence | 3.6 | Ablation setup exists for Chapter 5. | Mention setup only in Chapter 3. |
| EXT-CH3-001 | `paper/drafts_ch3_6/EXTERNAL_CITATION_AUDIT.md` | external citation | 3.1, 3.3 | Background citation seeds for native-path and KG recommender models. | Some entries require manual venue/DOI checks. |

## Unsupported or Uncertain Chapter 3 Claims

| Claim | Problem | Required action | Status |
| --- | --- | --- | --- |
| Exact final venue/DOI for PGPR, CAFE, TPRec, KGAT, KGIN, LightGCN, PEARLM. | Search verified arXiv seeds but not publisher metadata. | Manually verify before final dissertation references. | Open |
| UCPR external paper metadata. | Not found with available search. | Add only after primary source is verified. | Open |
| KGGLM external paper metadata. | Not found with available search. | Add only after primary source is verified. | Open |
| XRecSys/LIR/SEP/ETD primary publication. | Not found with available search. | Use repo docs for implementation evidence; cite only after manual verification. | Open |

