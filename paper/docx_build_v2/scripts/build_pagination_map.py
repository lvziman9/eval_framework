from __future__ import annotations

import json
from pathlib import Path
import re

from docx import Document


ROOT = Path(__file__).resolve().parents[3]
RAW_BODY = ROOT / "paper/docx_build_v2/intermediate/DISSERTATION_BODY_PANDOC_RAW.docx"
RENDER_TEXT = ROOT / "paper/docx_build_v2/intermediate/render_final/DISSERTATION_NTU_TEMPLATE_DRAFT_V2.txt"
RENDER_AUDIT = ROOT / "paper/docx_build_v2/reports/RENDER_AUDIT_FINAL.json"
OUTPUT = ROOT / "paper/docx_build_v2/intermediate/PAGINATION_MAP.json"

FRONT_PHYSICAL_START = 6
BODY_PHYSICAL_START = 13


def roman(number: int) -> str:
    values = [
        (1000, "m"),
        (900, "cm"),
        (500, "d"),
        (400, "cd"),
        (100, "c"),
        (90, "xc"),
        (50, "l"),
        (40, "xl"),
        (10, "x"),
        (9, "ix"),
        (5, "v"),
        (4, "iv"),
        (1, "i"),
    ]
    result = []
    for value, symbol in values:
        while number >= value:
            result.append(symbol)
            number -= value
    return "".join(result)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


raw_document = Document(RAW_BODY)
rendered_pages = RENDER_TEXT.read_text(encoding="utf-8", errors="replace").split("\f")
normalised_pages = [normalise(page) for page in rendered_pages]
render_audit = json.loads(RENDER_AUDIT.read_text(encoding="utf-8"))

headings = [
    paragraph.text.strip()
    for paragraph in raw_document.paragraphs
    if paragraph.style.style_id in {"Heading1", "Heading2", "Heading3"}
    and paragraph.text.strip() != "Abstract"
]

display_pages: dict[str, str] = {
    "Abstract": roman(8 - FRONT_PHYSICAL_START + 1),
    "Acknowledgements": roman(10 - FRONT_PHYSICAL_START + 1),
    "List of Figures": roman(11 - FRONT_PHYSICAL_START + 1),
    "List of Tables": roman(12 - FRONT_PHYSICAL_START + 1),
}
heading_candidates: dict[str, list[int]] = {}

for heading in headings:
    target = normalise(heading)
    if heading == "References":
        candidates = render_audit["references_pages"]
    elif heading == "Appendices":
        candidates = render_audit["appendices_pages"]
    else:
        candidates = [
            page_number
            for page_number, page_text in enumerate(normalised_pages, 1)
            if page_number >= BODY_PHYSICAL_START and target in page_text
        ]
    if not candidates:
        raise RuntimeError(f"Could not locate rendered heading: {heading}")
    heading_candidates[heading] = candidates
    physical_page = candidates[0]
    display_pages[heading] = str(physical_page - BODY_PHYSICAL_START + 1)

caption_candidates: dict[str, list[int]] = {}
for kind, page_group in [
    ("Figure", render_audit["figure_caption_pages"]),
    ("Table", render_audit["table_caption_pages"]),
]:
    for label, candidates in page_group.items():
        body_candidates = [page for page in candidates if page >= BODY_PHYSICAL_START]
        if not body_candidates:
            raise RuntimeError(f"Could not locate rendered {kind} {label}")
        identifier = f"{kind} {label}"
        caption_candidates[identifier] = body_candidates
        physical_page = body_candidates[0]
        display_pages[identifier] = str(physical_page - BODY_PHYSICAL_START + 1)

OUTPUT.write_text(
    json.dumps(
        {
            "render_source": str(RENDER_TEXT.relative_to(ROOT)),
            "front_physical_start": FRONT_PHYSICAL_START,
            "body_physical_start": BODY_PHYSICAL_START,
            "display_pages": display_pages,
            "heading_candidates": heading_candidates,
            "caption_candidates": caption_candidates,
            "mapped_heading_count": len(headings) + 4,
            "mapped_figure_count": len(render_audit["figure_caption_pages"]),
            "mapped_table_count": len(render_audit["table_caption_pages"]),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(OUTPUT)
