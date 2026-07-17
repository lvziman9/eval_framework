from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ITERATION = sys.argv[1] if len(sys.argv) > 1 else "iteration1"
PAGES_DIR = ROOT / "paper/docx_build_v3/rendered_pages" / ITERATION
TEXT_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"/tmp/v3_render_{ITERATION}/DISSERTATION_NTU_TEMPLATE_DRAFT_V3.txt")
REPORT_DIR = ROOT / "paper/docx_build_v3/reports"
CONTACT_DIR = REPORT_DIR / f"contact_sheets_{ITERATION}"
AUDIT = REPORT_DIR / f"RENDER_AUDIT_{ITERATION.upper()}.json"

page_paths = sorted(PAGES_DIR.glob("page-*.png"))
if not page_paths:
    raise RuntimeError("No rendered page PNG files were found")

CONTACT_DIR.mkdir(parents=True, exist_ok=True)
page_rows = []
blank_pages = []
edge_touch_pages = []
unexpected_dimension_pages = []

for page_number, path in enumerate(page_paths, 1):
    with Image.open(path) as image:
        image.load()
        orientation = "portrait" if image.height >= image.width else "landscape"
        expected = (850, 1100) if orientation == "portrait" else (1100, 850)
        if image.size != expected:
            unexpected_dimension_pages.append(page_number)
        gray = image.convert("L")
        histogram = gray.histogram()
        pixel_count = image.width * image.height
        near_white = sum(histogram[250:]) / pixel_count
        mask = gray.point(lambda value: 255 if value < 245 else 0)
        bbox = mask.getbbox()
        if near_white > 0.998 or bbox is None:
            blank_pages.append(page_number)
        edge_touch = False
        if bbox is not None:
            left, top, right, bottom = bbox
            edge_touch = left <= 4 or top <= 4 or right >= image.width - 4 or bottom >= image.height - 4
            if edge_touch:
                edge_touch_pages.append(page_number)
        page_rows.append(
            {
                "page": page_number,
                "file": str(path.relative_to(ROOT)),
                "width": image.width,
                "height": image.height,
                "orientation": orientation,
                "near_white_ratio": round(near_white, 6),
                "content_bbox": list(bbox) if bbox is not None else None,
                "edge_touch": edge_touch,
            }
        )

font = ImageFont.load_default()
thumb_width = 275
thumb_height = 300
label_height = 20
columns = 4
chunk_size = 20
contact_paths = []
for chunk_start in range(0, len(page_paths), chunk_size):
    chunk = page_paths[chunk_start : chunk_start + chunk_size]
    rows = (len(chunk) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    for offset, path in enumerate(chunk):
        page_number = chunk_start + offset + 1
        with Image.open(path) as page:
            thumbnail = page.convert("RGB")
            thumbnail.thumbnail((thumb_width - 10, thumb_height - 10), Image.Resampling.LANCZOS)
            x = (offset % columns) * thumb_width + (thumb_width - thumbnail.width) // 2
            y = (offset // columns) * (thumb_height + label_height) + label_height
            sheet.paste(thumbnail, (x, y))
            draw.text((x + 4, y - label_height + 3), f"Page {page_number}", fill="black", font=font)
    output = CONTACT_DIR / f"pages_{chunk_start + 1:03d}_{chunk_start + len(chunk):03d}.png"
    sheet.save(output)
    contact_paths.append(str(output.relative_to(ROOT)))

rendered_text = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
pages_text = rendered_text.split("\f")


def pages_matching(pattern: str) -> list[int]:
    expression = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
    return [index for index, text in enumerate(pages_text, 1) if expression.search(text)]


chapter_pages = {
    str(chapter): pages_matching(rf"Chapter\s+{chapter}\b")
    for chapter in range(1, 7)
}
figure_caption_pages = {
    label: pages_matching(rf"Figure\s+{re.escape(label)}\.")
    for label in ["3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "C.1"]
}
table_caption_pages = {
    label: pages_matching(rf"Table\s+{re.escape(label)}\.")
    for label in ["1.1", "2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3a", "5.3b", "5.4", "6.1"]
}

replacement_character_pages = [
    index for index, text in enumerate(pages_text, 1) if "\ufffd" in text
]
error_marker_pages = [
    index
    for index, text in enumerate(pages_text, 1)
    if re.search(r"image cannot be displayed|error displaying image|read-error|missing image", text, re.IGNORECASE)
]

author_year_pages = pages_matching(
    r"\((?:Guo et al\.\s+2022|Zhang and Chen\s+2020|Balloccu et al\.\s+2022[a-z]?)\)"
)
numbered_citation_pages = pages_matching(r"\[[0-9]+(?:\s*[-–,]\s*[0-9]+)*\]")
broken_formula_pages = pages_matching(r"^\s*\[\s*(?:U|I|=|p_|phi|\\phi).+\]\s*$")
long_decimal_pages = pages_matching(r"(?<![\w/])\d+\.\d{4,}(?![\w/])")

table_pages = sorted({page for pages in table_caption_pages.values() for page in pages})
table_margin_risk_pages = []
for page in table_pages:
    if page <= len(page_rows):
        bbox = page_rows[page - 1]["content_bbox"]
        if bbox and (bbox[0] < 80 or bbox[2] > 775):
            table_margin_risk_pages.append(page)

AUDIT.write_text(
    json.dumps(
        {
            "iteration": ITERATION,
            "page_count": len(page_paths),
            "portrait_pages": sum(row["orientation"] == "portrait" for row in page_rows),
            "landscape_pages": sum(row["orientation"] == "landscape" for row in page_rows),
            "unexpected_dimension_pages": unexpected_dimension_pages,
            "blank_pages": blank_pages,
            "edge_touch_pages": edge_touch_pages,
            "replacement_character_pages": replacement_character_pages,
            "image_error_marker_pages": error_marker_pages,
            "author_year_pages": author_year_pages,
            "numbered_citation_pages": numbered_citation_pages,
            "broken_formula_pages": broken_formula_pages,
            "long_decimal_pages": long_decimal_pages,
            "table_pages": table_pages,
            "table_margin_risk_pages": table_margin_risk_pages,
            "chapter_pages": chapter_pages,
            "references_pages": pages_matching(r"^\s*References\s*$"),
            "appendices_pages": pages_matching(r"^\s*Appendices\s*$"),
            "figure_caption_pages": figure_caption_pages,
            "table_caption_pages": table_caption_pages,
            "contact_sheets": contact_paths,
            "pages": page_rows,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(AUDIT)
