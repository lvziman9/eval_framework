#!/usr/bin/env python3
"""Apply targeted V4 repairs to the latest V3 DOCX without rebuilding it."""

from __future__ import annotations

import copy
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}

ET.register_namespace("w", W)
ET.register_namespace("m", M)
ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
ET.register_namespace("wp", "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing")
ET.register_namespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
ET.register_namespace("pic", "http://schemas.openxmlformats.org/drawingml/2006/picture")


FIGURE_CAPTIONS = {
    "Figure 3.1.": "Figure 3.1. Implemented canonical native-path evaluation framework.",
    "Figure 3.2.": "Figure 3.2. Alpha-sweep experiment design and evidence separation.",
    "Figure 3.3.": "Figure 3.3. Validation gate for model-dataset export eligibility.",
    "Figure 4.1.": "Figure 4.1. Strict NDCG@10 comparison on LastFM and ML-1M.",
    "Figure 4.2.": "Figure 4.2. LIR, SEP, and ETD endpoints on validated LastFM and ML-1M rows.",
    "Figure 4.3.": "Figure 4.3. LIR-oriented trade-off curves for LastFM and ML-1M.",
    "Figure 4.4.": "Figure 4.4. SEP-oriented trade-off curves under the repository-specific objective.",
    "Figure 4.5.": "Figure 4.5. ETD-oriented trade-off curves for LastFM and ML-1M.",
    "Figure 5.1.": "Figure 5.1. PGPR/UCPR ablation trade-offs under the frozen original top-k item set.",
    "Figure 5.2.": "Figure 5.2. Validation-status matrix for canonical native-path experiments.",
    "Figure C.1.": "Figure C.1. Decision flow for the partial Amazon-Book KGAT boundary case.",
}

LOF_PAGES = {
    "Figure 3.1.": "16",
    "Figure 3.2.": "25",
    "Figure 3.3.": "25",
    "Figure 4.1.": "32",
    "Figure 4.2.": "34",
    "Figure 4.3.": "35",
    "Figure 4.4.": "37",
    "Figure 4.5.": "38",
    "Figure 5.1.": "43",
    "Figure 5.2.": "48",
    "Figure C.1.": "59",
}

METRIC_CITATION_TEXT = (
    "These displayed LIR, SEP, and ETD definitions carry external conceptual "
    "provenance from the XRecSys-related sources [5], [25]; their evaluated "
    "behaviour remains governed by the repository implementation."
)


def qn(tag: str) -> str:
    prefix, name = tag.split(":", 1)
    return f"{{{NS[prefix]}}}{name}"


def paragraph_text(p_el: ET.Element) -> str:
    return "".join((t.text or "") for t in p_el.findall(".//w:t", NS))


def set_plain_text(p_el: ET.Element, text: str) -> None:
    texts = p_el.findall(".//w:t", NS)
    if not texts:
        r_el = ET.SubElement(p_el, qn("w:r"))
        t_el = ET.SubElement(r_el, qn("w:t"))
        t_el.text = text
        return
    texts[0].text = text
    for t_el in texts[1:]:
        t_el.text = ""


def set_tabbed_text(p_el: ET.Element, left: str, right: str) -> None:
    """Replace paragraph content with left text, a tab, and right text."""
    ppr = p_el.find("./w:pPr", NS)
    ppr_copy = copy.deepcopy(ppr) if ppr is not None else None
    for child in list(p_el):
        p_el.remove(child)
    if ppr_copy is not None:
        p_el.append(ppr_copy)

    r_left = ET.SubElement(p_el, qn("w:r"))
    t_left = ET.SubElement(r_left, qn("w:t"))
    t_left.text = left

    r_tab = ET.SubElement(p_el, qn("w:r"))
    ET.SubElement(r_tab, qn("w:tab"))

    r_right = ET.SubElement(p_el, qn("w:r"))
    t_right = ET.SubElement(r_right, qn("w:t"))
    t_right.text = right


def make_plain_paragraph(text: str, ppr_source: ET.Element | None = None) -> ET.Element:
    p_el = ET.Element(qn("w:p"))
    if ppr_source is not None:
        p_el.append(copy.deepcopy(ppr_source))
    r_el = ET.SubElement(p_el, qn("w:r"))
    t_el = ET.SubElement(r_el, qn("w:t"))
    t_el.text = text
    return p_el


def make_tabbed_paragraph(
    left: str, right: str, ppr_source: ET.Element | None = None
) -> ET.Element:
    p_el = make_plain_paragraph("", ppr_source)
    set_tabbed_text(p_el, left, right)
    return p_el


def iter_body_paragraphs(root: ET.Element) -> list[ET.Element]:
    body = root.find(".//w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")
    return [child for child in list(body) if child.tag == qn("w:p")]


def body_element_index(root: ET.Element, target: ET.Element) -> int:
    body = root.find(".//w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")
    for idx, child in enumerate(list(body)):
        if child is target:
            return idx
    raise RuntimeError("target paragraph is not a direct body child")


def patch_document_xml(xml_bytes: bytes) -> tuple[bytes, dict[str, int]]:
    root = ET.fromstring(xml_bytes)
    body = root.find(".//w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")

    stats = {
        "figure_captions_shortened": 0,
        "lof_entries_shortened": 0,
        "appendix_f_heading_split": 0,
        "toc_appendix_f_inserted": 0,
        "metric_formula_citation_inserted": 0,
    }

    paragraphs = iter_body_paragraphs(root)

    # Shorten visible figure captions and their static List of Figures entries.
    for p_el in paragraphs:
        text = paragraph_text(p_el).strip()
        for prefix, caption in FIGURE_CAPTIONS.items():
            if not text.startswith(prefix):
                continue
            style = p_el.find("./w:pPr/w:pStyle", NS)
            style_val = style.attrib.get(f"{{{W}}}val", "") if style is not None else ""
            if style_val == "ListEntry":
                set_tabbed_text(p_el, caption, LOF_PAGES[prefix])
                stats["lof_entries_shortened"] += 1
            else:
                set_plain_text(p_el, caption)
                stats["figure_captions_shortened"] += 1
            break

    paragraphs = iter_body_paragraphs(root)

    # Repair the compressed Appendix F heading.
    appendix_marker = " ## Appendix F: Citation and Provenance Notes"
    for p_el in paragraphs:
        text = paragraph_text(p_el)
        if appendix_marker not in text:
            continue
        before = text.replace(appendix_marker, "").rstrip()
        set_plain_text(p_el, before)

        appendix_e = next(
            (
                candidate
                for candidate in paragraphs
                if paragraph_text(candidate).strip()
                == "Appendix E: Boundary-Case and Reproducibility Caveats"
            ),
            None,
        )
        ppr_source = appendix_e.find("./w:pPr", NS) if appendix_e is not None else None
        heading = make_plain_paragraph(
            "Appendix F: Citation and Provenance Notes", ppr_source
        )
        body.insert(body_element_index(root, p_el) + 1, heading)
        stats["appendix_f_heading_split"] += 1
        break

    paragraphs = iter_body_paragraphs(root)

    # Add Appendix F to the static Table of Contents, after the V3 evidence note.
    if not any(paragraph_text(p).startswith("Appendix F: Citation") for p in paragraphs[:120]):
        for p_el in paragraphs[:120]:
            if paragraph_text(p_el).strip() == "V3 Main-table Evidence Detail Note60":
                ppr_source = p_el.find("./w:pPr", NS)
                toc_entry = make_tabbed_paragraph(
                    "Appendix F: Citation and Provenance Notes", "60", ppr_source
                )
                body.insert(body_element_index(root, p_el) + 1, toc_entry)
                stats["toc_appendix_f_inserted"] += 1
                break

    paragraphs = iter_body_paragraphs(root)

    # Add an explicit external citation near the LIR/SEP/ETD displayed formulas,
    # while leaving original OMML formula runs untouched.
    if not any(METRIC_CITATION_TEXT in paragraph_text(p) for p in paragraphs):
        for p_el in paragraphs:
            text = paragraph_text(p_el)
            if "The corresponding path-level definitions are" not in text:
                continue
            ppr_source = p_el.find("./w:pPr", NS)
            citation_p = make_plain_paragraph(METRIC_CITATION_TEXT, ppr_source)
            body.insert(body_element_index(root, p_el) + 1, citation_p)
            stats["metric_formula_citation_inserted"] += 1
            break

    return ET.tostring(root, encoding="utf-8", xml_declaration=True), stats


def patch_docx(src: Path, dst: Path) -> dict[str, int]:
    with zipfile.ZipFile(src, "r") as zin:
        doc_xml, stats = patch_document_xml(zin.read("word/document.xml"))
        with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = doc_xml
                zout.writestr(item, data)
    return stats


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: patch_v4_docx.py SOURCE.docx OUTPUT.docx", file=sys.stderr)
        return 2
    src = Path(argv[1])
    dst = Path(argv[2])
    stats = patch_docx(src, dst)
    for key, value in stats.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
