from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "paper/current_dissertation/FULL_DISSERTATION_CURRENT.md"
OUTPUT = ROOT / "paper/docx_build/intermediate/DISSERTATION_FOR_DOCX.md"
AUDIT = ROOT / "paper/docx_build/reports/SOURCE_PREPARATION_AUDIT.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def replace_section(text: str, heading: str, next_marker: str, replacement: str) -> str:
    pattern = rf"(?ms)^{re.escape(heading)}\n.*?(?=^{re.escape(next_marker)}(?:\n|$))"
    updated, count = re.subn(pattern, f"{heading}\n\n{replacement}\n\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not replace front-matter section: {heading}")
    return updated


source_text = SOURCE.read_text(encoding="utf-8")
source_images = re.findall(r"!\[([^]]*)\]\(([^)]+)\)", source_text)
if len(source_images) != 11:
    raise RuntimeError(f"Expected 11 source image links, found {len(source_images)}")

image_rows = []


def rewrite_image(match: re.Match[str]) -> str:
    alt, original = match.groups()
    original_path = Path(original)
    if original_path.suffix.lower() != ".png":
        raise RuntimeError(f"DOCX source must use PNG, found: {original}")
    source_image = ROOT / "paper/current_dissertation" / original_path
    if not source_image.is_file():
        fallback = ROOT / "paper/current_dissertation/figures/png" / original_path.name
        if not fallback.is_file():
            raise RuntimeError(f"Missing figure image: {original}")
        source_image = fallback
    stable_path = source_image.relative_to(ROOT).as_posix()
    image_rows.append(
        {
            "original": original,
            "docx_source_path": stable_path,
            "sha256": digest(source_image),
        }
    )
    return f"![{alt}]({stable_path})"


prepared = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", rewrite_image, source_text)
prepared = replace_section(
    prepared,
    "## Table of Contents",
    "## List of Figures",
    "[Table of Contents to be updated in Microsoft Word before final PDF export.]",
)
prepared = replace_section(
    prepared,
    "## List of Figures",
    "## List of Tables",
    "[List of Figures to be updated in Microsoft Word before final PDF export.]",
)
prepared = replace_section(
    prepared,
    "## List of Tables",
    "---",
    "[List of Tables to be updated in Microsoft Word before final PDF export.]",
)

prepared_images = re.findall(r"!\[([^]]*)\]\(([^)]+)\)", prepared)
if len(prepared_images) != 11:
    raise RuntimeError("Prepared image count changed unexpectedly")
for _, path_text in prepared_images:
    if not (ROOT / path_text).is_file():
        raise RuntimeError(f"Prepared image path does not resolve: {path_text}")

source_citations = sorted(set(re.findall(r"@([A-Za-z0-9_:.+\-/]+)", source_text)))
prepared_citations = sorted(set(re.findall(r"@([A-Za-z0-9_:.+\-/]+)", prepared)))
if source_citations != prepared_citations:
    raise RuntimeError("Citation-key set changed during source preparation")

source_captions = re.findall(r"(?m)^\*\*(?:Figure|Table) [^\n]+", source_text)
prepared_captions = re.findall(r"(?m)^\*\*(?:Figure|Table) [^\n]+", prepared)
if source_captions != prepared_captions:
    raise RuntimeError("Figure/table captions changed during source preparation")

OUTPUT.write_text(prepared, encoding="utf-8")
AUDIT.write_text(
    json.dumps(
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": digest(SOURCE),
            "prepared": str(OUTPUT.relative_to(ROOT)),
            "prepared_sha256": digest(OUTPUT),
            "image_count": len(image_rows),
            "images": image_rows,
            "citation_key_count": len(source_citations),
            "citation_keys_preserved": True,
            "caption_count": len(source_captions),
            "captions_preserved": True,
            "pipe_table_count": len(re.findall(r"(?m)^\|(?:\s*:?-{3,}:?\s*\|)+\s*$", prepared)),
            "field_placeholders": [
                "Table of Contents",
                "List of Figures",
                "List of Tables",
            ],
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
