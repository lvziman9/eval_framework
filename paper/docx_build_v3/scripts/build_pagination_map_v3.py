from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from docx import Document


ROOT = Path(__file__).resolve().parents[3]
RAW_BODY = ROOT / "paper/docx_build_v3/intermediate/BODY_V3_IEEE.docx"
ITERATION = sys.argv[1] if len(sys.argv) > 1 else "iteration1"
RENDER_TEXT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
    f"/tmp/v3_render_{ITERATION}/DISSERTATION_NTU_TEMPLATE_DRAFT_V3.txt"
)
RENDER_AUDIT = ROOT / "paper/docx_build_v3/reports" / f"RENDER_AUDIT_{ITERATION.upper()}.json"
OUTPUT = ROOT / "paper/docx_build_v3/intermediate/PAGINATION_MAP.json"

FRONT_PHYSICAL_START = 7
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
    result: list[str] = []
    for value, symbol in values:
        while number >= value:
            result.append(symbol)
            number -= value
    return "".join(result)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def loose_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def front_display_page(physical_page: int) -> str:
    return roman(physical_page - FRONT_PHYSICAL_START + 1)


def body_display_page(physical_page: int) -> str:
    return str(physical_page - BODY_PHYSICAL_START + 1)


def locate_front_page(label: str, pages: list[str]) -> int:
    for page_number, page_text in enumerate(pages, 1):
        if not (FRONT_PHYSICAL_START <= page_number < BODY_PHYSICAL_START):
            continue
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        if lines and lines[0] == label:
            return page_number
    raise RuntimeError(f"Could not locate front-matter page: {label}")


raw_document = Document(RAW_BODY)
rendered_pages = RENDER_TEXT.read_text(encoding="utf-8", errors="replace").split("\f")
normalised_pages = [normalise(page) for page in rendered_pages]
loose_pages = [loose_key(page) for page in rendered_pages]
render_audit = json.loads(RENDER_AUDIT.read_text(encoding="utf-8"))

headings = [
    paragraph.text.strip()
    for paragraph in raw_document.paragraphs
    if paragraph.style.style_id in {"Heading1", "Heading2", "Heading3"}
    and paragraph.text.strip()
    and paragraph.text.strip() != "Abstract"
]

display_pages: dict[str, str] = {}
heading_candidates: dict[str, list[int]] = {}

for front_label in ["Abstract", "Acknowledgements", "List of Figures", "List of Tables"]:
    physical_page = locate_front_page(front_label, rendered_pages)
    display_pages[front_label] = front_display_page(physical_page)
    heading_candidates[front_label] = [physical_page]

for heading in headings:
    target = normalise(heading)
    loose_target = loose_key(heading)
    if heading == "References":
        candidates = render_audit["references_pages"]
    elif heading == "Appendices":
        candidates = render_audit["appendices_pages"]
    else:
        candidates = [
            page_number
            for page_number, (page_text, loose_page_text) in enumerate(
                zip(normalised_pages, loose_pages), 1
            )
            if page_number >= BODY_PHYSICAL_START
            and (target in page_text or loose_target in loose_page_text)
        ]
    if not candidates:
        raise RuntimeError(f"Could not locate rendered heading: {heading}")
    heading_candidates[heading] = candidates
    display_pages[heading] = body_display_page(candidates[0])

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
        display_pages[identifier] = body_display_page(body_candidates[0])

OUTPUT.write_text(
    json.dumps(
        {
            "render_source": str(RENDER_TEXT),
            "render_audit": str(RENDER_AUDIT.relative_to(ROOT)),
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
