from __future__ import annotations

import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
PAGES_DIR = ROOT / "paper/docx_build/rendered_pages"
TEXT_PATH = ROOT / "paper/docx_build/intermediate/internal_render/DISSERTATION_NTU_TEMPLATE_DRAFT_RENDERED.txt"
REPORT_DIR = ROOT / "paper/docx_build/reports"
CONTACT_DIR = REPORT_DIR / "contact_sheets"
AUDIT = REPORT_DIR / "RENDER_AUDIT.json"

page_paths = sorted(PAGES_DIR.glob("page-*.png"))
if not page_paths:
    raise RuntimeError("No rendered page PNGs found")

CONTACT_DIR.mkdir(parents=True, exist_ok=True)
expected_size = None
page_rows = []
blank_pages = []
edge_touch_pages = []
dimension_mismatches = []

for index, path in enumerate(page_paths, 1):
    with Image.open(path) as image:
        image.load()
        if expected_size is None:
            expected_size = image.size
        if image.size != expected_size:
            dimension_mismatches.append(index)
        gray = image.convert("L")
        histogram = gray.histogram()
        pixel_count = image.width * image.height
        near_white = sum(histogram[250:]) / pixel_count
        mask = gray.point(lambda value: 255 if value < 245 else 0)
        bbox = mask.getbbox()
        if near_white > 0.998 or bbox is None:
            blank_pages.append(index)
        edge_touch = False
        if bbox is not None:
            left, top, right, bottom = bbox
            edge_touch = left <= 4 or top <= 4 or right >= image.width - 4 or bottom >= image.height - 4
            if edge_touch:
                edge_touch_pages.append(index)
        page_rows.append(
            {
                "page": index,
                "file": str(path.relative_to(ROOT)),
                "width": image.width,
                "height": image.height,
                "near_white_ratio": round(near_white, 6),
                "content_bbox": list(bbox) if bbox is not None else None,
                "edge_touch": edge_touch,
            }
        )

font = ImageFont.load_default()
thumb_width = 255
thumb_height = 330
label_height = 18
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
            thumb = page.convert("RGB")
            thumb.thumbnail((thumb_width - 8, thumb_height - 8))
            x = (offset % columns) * thumb_width + (thumb_width - thumb.width) // 2
            y = (offset // columns) * (thumb_height + label_height) + label_height
            sheet.paste(thumb, (x, y))
            draw.text((x + 4, y - label_height + 3), f"Page {page_number}", fill="black", font=font)
    output = CONTACT_DIR / f"pages_{chunk_start + 1:03d}_{chunk_start + len(chunk):03d}.png"
    sheet.save(output)
    contact_paths.append(str(output.relative_to(ROOT)))

rendered_text = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
pages_text = rendered_text.split("\f")


def pages_matching(pattern: str) -> list[int]:
    regex = re.compile(pattern, re.MULTILINE)
    return [index for index, text in enumerate(pages_text, 1) if regex.search(text)]


chapter_pages = {
    str(chapter): pages_matching(rf"Chapter\s+{chapter}\b")
    for chapter in range(1, 7)
}
figure_caption_pages = {}
for label in ["3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "C.1"]:
    figure_caption_pages[label] = pages_matching(rf"Figure\s+{re.escape(label)}\.")
table_caption_pages = {}
for label in ["1.1", "2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3", "5.4", "6.1"]:
    table_caption_pages[label] = pages_matching(rf"Table\s+{re.escape(label)}\.")

replacement_character_pages = [
    index for index, text in enumerate(pages_text, 1) if "\ufffd" in text
]
error_marker_pages = [
    index
    for index, text in enumerate(pages_text, 1)
    if re.search(r"(?i)(image cannot be displayed|error displaying image|read-error|missing image)", text)
]

AUDIT.write_text(
    json.dumps(
        {
            "page_count": len(page_paths),
            "expected_dimensions": list(expected_size) if expected_size else None,
            "dimension_mismatches": dimension_mismatches,
            "blank_pages": blank_pages,
            "edge_touch_pages": edge_touch_pages,
            "replacement_character_pages": replacement_character_pages,
            "image_error_marker_pages": error_marker_pages,
            "chapter_pages": chapter_pages,
            "references_pages": pages_matching(r"^References\s*$"),
            "appendices_pages": pages_matching(r"^Appendices\s*$"),
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
