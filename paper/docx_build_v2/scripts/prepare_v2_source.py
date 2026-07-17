from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "paper/current_dissertation/FULL_DISSERTATION_CURRENT.md"
BIBLIOGRAPHY = ROOT / "paper/current_dissertation/references/REFERENCES_CURRENT.bib"
OUTPUT = ROOT / "paper/docx_build_v2/intermediate/DISSERTATION_BODY_FOR_DOCX.md"
AUDIT = ROOT / "paper/docx_build_v2/reports/SOURCE_PREPARATION_AUDIT.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for citation_group in re.findall(r"\[([^\]]*@[a-z][A-Za-z0-9_:.+\-/]+[^\]]*)\]", text):
        keys.update(re.findall(r"@([a-z][A-Za-z0-9_:.+\-/]+)", citation_group))
    return keys


source_text = SOURCE.read_text(encoding="utf-8")
bibliography_text = BIBLIOGRAPHY.read_text(encoding="utf-8")
bibliography_keys = set(re.findall(r"(?m)^@[A-Za-z]+\{([^,]+),", bibliography_text))

body_start = source_text.find("# Abstract\n")
if body_start < 0:
    raise RuntimeError("Could not locate the Abstract heading")
prepared = source_text[body_start:]

references_pattern = re.compile(
    r"(?ms)^# References\n.*?(?=^---\n\n# Appendices\n)"
)
prepared, replacement_count = references_pattern.subn(
    "# References\n\n::: {#refs}\n:::\n\n",
    prepared,
    count=1,
)
if replacement_count != 1:
    raise RuntimeError("Could not replace the manual display-list References section")
prepared = prepared.replace("\n---\n\n# Appendices\n", "\n# Appendices\n", 1)
prepared = re.sub(r"(?m)^---\s*$\n?", "", prepared)

image_rows: list[dict[str, str]] = []


def rewrite_image(match: re.Match[str]) -> str:
    alt_text, original_path_text = match.groups()
    original_path = Path(original_path_text)
    candidate = ROOT / "paper/current_dissertation" / original_path
    if not candidate.is_file():
        candidate = ROOT / "paper/current_dissertation/figures/png" / original_path.name
    if not candidate.is_file():
        raise RuntimeError(f"Missing figure image: {original_path_text}")
    if candidate.suffix.lower() != ".png":
        raise RuntimeError(f"DOCX display asset is not PNG: {candidate}")
    stable_path = candidate.relative_to(ROOT).as_posix()
    image_rows.append(
        {
            "source_link": original_path_text,
            "prepared_link": stable_path,
            "sha256": digest(candidate),
        }
    )
    return f"![{alt_text}]({stable_path})"


prepared = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", rewrite_image, prepared)

source_keys = citation_keys(source_text) & bibliography_keys
prepared_keys = citation_keys(prepared) & bibliography_keys
missing_bibliography_keys = sorted(citation_keys(source_text) - bibliography_keys)
if source_keys != prepared_keys:
    raise RuntimeError("Citation-key set changed while preparing the DOCX body")
if missing_bibliography_keys:
    raise RuntimeError(f"Missing bibliography entries: {missing_bibliography_keys}")
if len(image_rows) != 11:
    raise RuntimeError(f"Expected 11 figures, found {len(image_rows)}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
AUDIT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(prepared, encoding="utf-8")
AUDIT.write_text(
    json.dumps(
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": digest(SOURCE),
            "bibliography": str(BIBLIOGRAPHY.relative_to(ROOT)),
            "bibliography_sha256": digest(BIBLIOGRAPHY),
            "prepared": str(OUTPUT.relative_to(ROOT)),
            "prepared_sha256": digest(OUTPUT),
            "manual_reference_display_list_replaced_for_docx": True,
            "citation_key_count": len(source_keys),
            "citation_keys_preserved": source_keys == prepared_keys,
            "image_count": len(image_rows),
            "images": image_rows,
            "source_markdown_modified": False,
            "bibliography_modified": False,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(OUTPUT)
