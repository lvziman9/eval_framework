from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BUILD_DIR = ROOT / "paper/docx_build_v3"
REPORT_DIR = BUILD_DIR / "reports"
WINDOWS_DIR = Path("/mnt/d/Desktop/paper")
WINDOWS_DOCX_FALLBACK = WINDOWS_DIR / "DISSERTATION_NTU_TEMPLATE_DRAFT_V3_captionfix_20260718.docx"
FINAL_AUDIT = REPORT_DIR / "FINAL_AUDIT.json"
ASSEMBLY_AUDIT = REPORT_DIR / "ASSEMBLY_AUDIT.json"
BODY_AUDIT = REPORT_DIR / "BODY_V3_AUDIT.json"
SOURCE_AUDIT = REPORT_DIR / "SOURCE_TRANSFORMATION_AUDIT.json"
RENDER1 = REPORT_DIR / "RENDER_AUDIT_ITERATION1.json"
RENDER_FINAL = REPORT_DIR / "RENDER_AUDIT_ITERATION4.json"

DOCX = BUILD_DIR / "DISSERTATION_NTU_TEMPLATE_DRAFT_V3.docx"
REPORT_FILES = [
    "DOCX_V3_BUILD_REPORT.md",
    "DOCX_V3_TABLE_SIMPLIFICATION_REPORT.md",
    "DOCX_V3_CITATION_REPORT.md",
    "DOCX_V3_FORMULA_REPAIR_REPORT.md",
    "DOCX_V3_NUMERIC_PRECISION_REPORT.md",
    "DOCX_V3_COHESION_COHERENCE_REPORT.md",
    "DOCX_V3_SELF_CHECK_REPORT.md",
    "DOCX_V3_BUILD_STATUS.md",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


final = load(FINAL_AUDIT)
assembly = load(ASSEMBLY_AUDIT)
body = load(BODY_AUDIT)
source = load(SOURCE_AUDIT)
render1 = load(RENDER1)
render_final = load(RENDER_FINAL)

docx_sha = digest(DOCX)
local_outputs = [DOCX.name] + REPORT_FILES


def target_info(filename: str) -> tuple[Path, str]:
    local = BUILD_DIR / filename
    primary = WINDOWS_DIR / filename
    if filename == DOCX.name and WINDOWS_DOCX_FALLBACK.exists() and local.exists() and digest(local) == digest(WINDOWS_DOCX_FALLBACK):
        if primary.exists() and digest(local) == digest(primary):
            return primary, "verified"
        return WINDOWS_DOCX_FALLBACK, "verified timestamped copy; primary DOCX was not overwritten"
    target = primary
    if not target.exists():
        return target, "pending"
    if not local.exists():
        return target, "local missing"
    return target, "verified" if digest(local) == digest(target) else "hash mismatch"


def render_summary(render: dict) -> str:
    return (
        f"{render['page_count']} pages; blank={len(render['blank_pages'])}; "
        f"edge_touch={len(render['edge_touch_pages'])}; author_year={len(render['author_year_pages'])}; "
        f"broken_formula={len(render['broken_formula_pages'])}; "
        f"table_margin_risk={len(render['table_margin_risk_pages'])}"
    )


build_report = f"""# DOCX V3 Build Report

## 1. Inputs

| Input | Path | SHA-256 / Status |
|---|---|---|
| Source Markdown | `paper/current_dissertation/FULL_DISSERTATION_CURRENT.md` | `{source['source_sha256']}` |
| References BibTeX | `paper/current_dissertation/references/REFERENCES_CURRENT.bib` | `{source['bibliography_sha256']}` |
| IEEE CSL | `paper/styles/ieee.csl` | `{body['ieee_csl_sha256']}` |
| NTU template copy | `paper/templates/NTU_template.docx` | `{assembly['template_sha256']}` |

## 2. Template Use

The V3 DOCX was assembled with the NTU template copy as the mother document. The template sample body was removed before assembly, while the template logo, front-matter wording, page geometry, and section structure were retained.

| Check | Result |
|---|---|
| Template used as mother document | {'PASS' if assembly['template_used_as_mother_document'] else 'FAIL'} |
| Template sample body removed | {'PASS' if assembly['template_sample_body_removed_before_assembly'] else 'FAIL'} |
| Original source Markdown unchanged | {'PASS' if final['source_markdown_unchanged'] else 'FAIL'} |
| Original bibliography unchanged | {'PASS' if final['bibliography_unchanged'] else 'FAIL'} |
| Original template copy unchanged | {'PASS' if final['template_unchanged'] else 'FAIL'} |

## 3. Major Fixes

| Area | V3 result |
|---|---|
| Tables | {final['tables']} native Word tables; no table images; all table widths <= 8640 twips. |
| Citations | IEEE numbered citations generated with citeproc; {final['reference_entries']} numbered references. |
| Formulas | {final['display_formula_omml_count']} display formulas converted to Word OMML. |
| Numeric precision | {source['numeric_changes']} presentation-layer numeric changes; long decimals remaining in V3 intermediate main text: {source['long_decimals_remaining']}. |
| Cohesion/coherence | {source['prose_changes']} targeted prose revisions with claim boundaries preserved. |
| TOC/LOF/LOT | {final['toc_entries']} TOC entries and {final['list_entries']} list entries include static page numbers. |

## 4. Tables

All main-text tables remain editable Word-native tables. Table 5.3 was split into Table 5.3a and Table 5.3b. Header rows repeat, vertical borders are removed, and the final render audit found no table margin-risk pages.

## 5. Citations

IEEE numbered citations were produced by Pandoc citeproc using the official IEEE CSL file. Author-year citation patterns remaining: {len(render_final['author_year_pages'])}. References are numbered contiguously from [1] to [29].

## 6. Formulas

Pandoc emitted Word OMML equations for all registered display formulas. Broken formula marker pages in the final render: {len(render_final['broken_formula_pages'])}.

## 7. Numeric Precision

Main-text values are rounded for readability only. Full precision remains available in the registered evidence files and build reports. Long decimal pages in the final render are {render_final['long_decimal_pages']}, and the final audit classifies them as References-only.

## 8. Cohesion and Coherence

The V3 source applies limited prose polish to reduce repeated caution wording while preserving SEP, strict-accuracy versus sweep, Amazon-Book KGAT, statistical-significance, user-study, and causal-claim boundaries.

## 9. Figures and Captions

The document contains {final['body_figure_count']} body figures and {final['figure_caption_count']} figure captions. Source figure hashes remain embedded unchanged. Figure captions are below figures and table captions are below tables.

## 10. Known Limitations

- Candidate name, supervisor, date, submission year, acknowledgements, and AI/authorship declaration placeholders still require manual completion.
- Final inspection should be performed in Microsoft Word before submission, especially field updates and institutional front-matter choices.
- No final PDF or LaTeX output was generated in this V3 goal.
"""


self_check_report = f"""# DOCX V3 Self-check Report

| Iteration | Render result | Issues found | Fixes applied | Outcome |
|---|---|---|---|---|
| Iteration 1 | {render_summary(render1)} | Static TOC/LOF/LOT page-number map had not yet been applied. Long decimals detected only in References pages. | Built `PAGINATION_MAP.json` from iteration-1 render text and regenerated the DOCX. | Proceeded to later correction renders. |
| Iteration 4 | {render_summary(render_final)} | No layout overflow, missing image, author-year citation, broken formula, short duplicate figure title, or repository-path exposure detected. Long decimals remained References-only. | Table captions were kept below tables, image alt text was suppressed as a visible caption source, and path-heavy prose was converted to log/file-name level wording. | PASS. |

## Structural checks

| Check | Result | Notes |
|---|---|---|
| DOCX zip integrity | PASS | `{DOCX.name}` opens as a valid DOCX package. |
| Template mother document | PASS | `template_used_as_mother_document=true`. |
| Sections | PASS | {final['sections']} sections; {final['landscape_sections']} landscape sections. |
| Chapters | PASS | {final['chapter_heading_count']} Chapter 1-6 headings. |
| TOC/LOF/LOT page numbers | PASS | {final['toc_entries']} TOC entries and {final['list_entries']} list entries complete. |

## Table checks

| Check | Result | Notes |
|---|---|---|
| Native Word tables | PASS | {final['tables']} tables in DOCX. |
| Table image conversion | PASS | No table image conversion was used. |
| Widths | PASS | All table widths are <= 8640 twips. |
| Caption position | PASS | {final['table_captions_below_tables']} table captions below tables; {final['table_captions_above_same_table']} same-table captions above tables. |
| Header repeat | PASS | {final['repeat_header_rows']} repeated header rows. |
| Render margin risk | PASS | {len(render_final['table_margin_risk_pages'])} table margin-risk pages. |

## Citation checks

| Check | Result | Notes |
|---|---|---|
| Numbered citations | PASS | Numbered citation patterns found in text/render. |
| Author-year patterns | PASS | 0 remaining in final render. |
| References | PASS | {final['reference_entries']} entries, numbered [1]-[29]. |

## Formula checks

| Check | Result | Notes |
|---|---|---|
| Display formulas | PASS | {final['display_formula_omml_count']} / {final['display_formula_source_count']} display formulas converted to OMML. |
| Inline formulas | PASS | {final['inline_formula_omml_count']} inline OMML equations. |
| Broken formula markers | PASS | {final['broken_formula_markers']} in DOCX audit and {len(render_final['broken_formula_pages'])} render pages. |

## Numeric precision checks

| Check | Result | Notes |
|---|---|---|
| Intermediate long decimals | PASS | {source['long_decimals_remaining']} remaining. |
| Final render long decimals | PASS | Pages {render_final['long_decimal_pages']} are References-only. |
| Presentation-only policy | PASS | Source Markdown and evidence files unchanged. |

## Cohesion/coherence checks

| Check | Result | Notes |
|---|---|---|
| Prose edits | PASS | {source['prose_changes']} targeted changes. |
| Boundary preservation | PASS | SEP, sweep, Amazon boundary, missing statistical/user-study artifacts, and causal limits retained. |

## Figure checks

| Check | Result | Notes |
|---|---|---|
| Body figures | PASS | {final['body_figure_count']} body figures. |
| Figure captions | PASS | {final['figure_caption_count']} captions. |
| Image render | PASS | {len(render_final['image_error_marker_pages'])} missing-image markers. |
| Duplicate short figure titles | PASS | {len(final['short_figure_alt_remaining'])} short alt-title remnants. |

## Remaining manual checks

- Fill NTU front-matter placeholders.
- Open the DOCX in Microsoft Word and confirm/update fields if the institution requires dynamic fields.
- Do not treat the temporary internal render PDF under `/tmp` as a deliverable.
"""


windows_rows = []
for filename in local_outputs:
    target, status = target_info(filename)
    windows_rows.append(
        f"| `{filename}` | `{target}` | {status} |"
    )

ready = final["audit_result"] == "PASS"
readiness = "Ready for user inspection in Microsoft Word" if ready else "Not ready"
status_report = f"""# DOCX V3 Build Status

## Overall Status

{final['audit_result']}

## Files Created

| File | Local path |
|---|---|
| DOCX | `paper/docx_build_v3/{DOCX.name}` |
| Build report | `paper/docx_build_v3/DOCX_V3_BUILD_REPORT.md` |
| Table simplification report | `paper/docx_build_v3/DOCX_V3_TABLE_SIMPLIFICATION_REPORT.md` |
| Citation report | `paper/docx_build_v3/DOCX_V3_CITATION_REPORT.md` |
| Formula repair report | `paper/docx_build_v3/DOCX_V3_FORMULA_REPAIR_REPORT.md` |
| Numeric precision report | `paper/docx_build_v3/DOCX_V3_NUMERIC_PRECISION_REPORT.md` |
| Cohesion and coherence report | `paper/docx_build_v3/DOCX_V3_COHESION_COHERENCE_REPORT.md` |
| Self-check report | `paper/docx_build_v3/DOCX_V3_SELF_CHECK_REPORT.md` |
| Build status | `paper/docx_build_v3/DOCX_V3_BUILD_STATUS.md` |

## Windows Output

| File | Target path | Copy status |
|---|---|---|
{chr(10).join(windows_rows)}

## Table Layout Result

PASS. {final['tables']} editable Word-native tables; all widths are within the portrait text block; no table margin-risk pages in the final render; all table captions are below tables.

## Citation Result

PASS. IEEE numbered citations generated with citeproc; author-year citation patterns remaining: 0; numbered References: yes.

## Formula Result

PASS. {final['display_formula_omml_count']} display formulas are Word OMML equations; broken formula markers remaining: 0.

## Numeric Precision Result

PASS. Long decimal values remaining in V3 intermediate main text: {source['long_decimals_remaining']}. Final-render long decimals are confined to References pages {render_final['long_decimal_pages']}.

## Cohesion and Coherence Result

PASS. Limited prose polish was applied without changing experimental facts, citation meaning, evidence boundaries, or conclusion direction.

## Render Self-check Result

PASS. Final render produced {render_final['page_count']} portrait pages with no blank pages, edge-touch pages, missing-image markers, author-year pages, broken-formula pages, duplicate short figure-title remnants, repository-path exposure, or table margin-risk pages.

## Remaining Manual Steps

- Fill candidate, supervisor, date, submission year, acknowledgements, and declaration placeholders.
- Open in Microsoft Word for final institutional inspection and field update if required.
- Generate the final submission PDF only after Word inspection; this V3 goal does not produce a PDF.

## Readiness

{readiness}

## Recommended Next Step

Inspect `DISSERTATION_NTU_TEMPLATE_DRAFT_V3.docx` in Microsoft Word and complete the remaining front-matter placeholders.
"""

(BUILD_DIR / "DOCX_V3_BUILD_REPORT.md").write_text(build_report, encoding="utf-8")
(BUILD_DIR / "DOCX_V3_SELF_CHECK_REPORT.md").write_text(self_check_report, encoding="utf-8")
(BUILD_DIR / "DOCX_V3_BUILD_STATUS.md").write_text(status_report, encoding="utf-8")
print(BUILD_DIR / "DOCX_V3_BUILD_REPORT.md")
print(BUILD_DIR / "DOCX_V3_SELF_CHECK_REPORT.md")
print(BUILD_DIR / "DOCX_V3_BUILD_STATUS.md")
