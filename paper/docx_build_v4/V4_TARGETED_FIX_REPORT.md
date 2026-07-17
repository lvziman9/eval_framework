# V4 Targeted Fix Report

Source DOCX:

- `DISSERTATION_NTU_TEMPLATE_DRAFT_V3_captionfix_20260718.docx`

Output DOCX:

- `paper/docx_build_v4/DISSERTATION_NTU_TEMPLATE_DRAFT_V4_TARGETED_FIX.docx`

SHA-256:

- `252ece894de7c54d4a1f463f294e682052781f1b22ceefc3f550b436540e5fbe`

## Changes Made

- Shortened 11 visible figure captions.
- Shortened 11 matching List of Figures entries.
- Restored List of Figures and Appendix F Table of Contents entries as caption/title, tab leader, and right-side page number.
- Preserved figure numbering and page-number entries from the latest DOCX.
- Repaired the compressed Appendix F Markdown residue by splitting it into an independent heading.
- Added Appendix F to the static Table of Contents.
- Added one visible external citation note before the displayed LIR / SEP / ETD formula group: `[5], [25]`.

## Formula Policy

- The existing Word/OMML formulas were preserved.
- No self-defined framework formulas were given external citations.
- Standard framework mappings, validation-gate notation, alpha-sweep notation, and ablation-selection notation were not externally cited.
- LIR / SEP / ETD received a visible citation note because their conceptual provenance is external.

## Checks

- LibreOffice headless render succeeded.
- Rendered PDF page count: 79.
- `oMath` count before/after: 88 / 88.
- `oMathPara` count before/after: 31 / 31.
- No rendered `## Appendix` residue found.
- No rendered `remain pending. ##` residue found.
- Rendered List of Figures checked visually after tab-leader repair.
- No rendered repository path patterns found for `/home/lvzi`, `eval_framework`, `paper/drafts`, `results/`, `reports/`, `docs/`, or `artifacts/`.

## Not Changed

- No experimental values were changed.
- No conclusions were rewritten.
- No chapter boundaries were changed.
- No table numbers or figure numbers were changed.
- No reference-list entries were added or removed.
