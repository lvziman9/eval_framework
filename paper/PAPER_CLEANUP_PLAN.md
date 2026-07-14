# Paper Cleanup Plan

## 1. Purpose

Create a stable current-dissertation entry point, a curated evidence view, and a non-destructive archive for superseded paper outputs before NTU template formatting.

## 2. Active Current Structure

`paper/current_dissertation/` contains the exact V4 draft copy, its 11 referenced PNG figures, matching SVG figures, current references, eight status/style reports, and the academic figure regeneration script.

## 3. Evidence Structure

`paper/evidence/` contains copied literature-review outputs, citation provenance, strict-accuracy provenance, the thesis traceability log, refined Chapter 1-3 evidence, and Chapter 3-6 evidence-used registers. Original evidence files remain in place.

## 4. Archive Structure

Only explicit superseded batch directories, old assembly/figure-production packages, old root-level drafts, and old integration reports were moved. The selected V4 finalisation source remains in place.

## 5. Files Not Moved

- `paper/full_dissertation_draft/figure_table_caption_asset_finalization_v1/`: selected current source.
- `paper/drafts_ch3_6/`: source provenance and historical chapter paths.
- `paper/drafts_ch3_6/figures/`: retained because legacy drafts may reference it.
- `paper/literature/review_outputs/`: evidence source retained after copying.
- `paper/literature/raw_pdfs/`: source corpus, do not touch.
- `paper/chapter_1_3_refined_evidence/`: evidence source retained after copying.

## 6. Manual Review Items

Historical chapter drafts may retain references to pre-cleanup paths. The archive manifest is the authoritative old-to-new mapping. Do not move the remaining `drafts_ch3_6` tree without a dedicated reference audit.

## 7. Next Step After Cleanup

Use `paper/current_dissertation/FULL_DISSERTATION_CURRENT.md` for NTU template formatting and controlled PDF preparation.
