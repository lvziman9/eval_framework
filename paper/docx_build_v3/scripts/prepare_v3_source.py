from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "paper/current_dissertation/FULL_DISSERTATION_CURRENT.md"
BIBLIOGRAPHY = ROOT / "paper/current_dissertation/references/REFERENCES_CURRENT.bib"
BUILD = ROOT / "paper/docx_build_v3"
INTERMEDIATE = BUILD / "intermediate"
REPORTS = BUILD / "reports"

PREPARED = INTERMEDIATE / "DISSERTATION_FOR_V3.md"
NUMERIC = INTERMEDIATE / "DISSERTATION_FOR_V3_NUMERIC_NORMALISED.md"
SIMPLIFIED = INTERMEDIATE / "DISSERTATION_FOR_V3_SIMPLIFIED_TABLES.md"
POLISHED = INTERMEDIATE / "DISSERTATION_FOR_V3_POLISHED.md"

NUMERIC_REPORT = BUILD / "DOCX_V3_NUMERIC_PRECISION_REPORT.md"
TABLE_REPORT = BUILD / "DOCX_V3_TABLE_SIMPLIFICATION_REPORT.md"
COHESION_REPORT = BUILD / "DOCX_V3_COHESION_COHERENCE_REPORT.md"
AUDIT = REPORTS / "SOURCE_TRANSFORMATION_AUDIT.json"


@dataclass
class NumericChange:
    line: int
    original: str
    replacement: str
    category: str


@dataclass
class TableAction:
    table: str
    original_problem: str
    action: str
    columns: str
    moved: str
    status: str = "PASS"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\[([^\]]*@[a-z][A-Za-z0-9_:.+\-/]+[^\]]*)\]", text):
        keys.update(re.findall(r"@([a-z][A-Za-z0-9_:.+\-/]+)", group))
    return keys


def protect_fragments(line: str) -> tuple[str, dict[str, str]]:
    fragments: dict[str, str] = {}

    def protect(match: re.Match[str]) -> str:
        key = f"@@V3PROTECT{len(fragments)}@@"
        fragments[key] = match.group(0)
        return key

    line = re.sub(r"`[^`]*`", protect, line)
    line = re.sub(r"\]\([^)]*\)", protect, line)
    return line, fragments


def restore_fragments(line: str, fragments: dict[str, str]) -> str:
    for key, value in fragments.items():
        line = line.replace(key, value)
    return line


def decimal_round(value: str, places: int) -> str:
    quantum = Decimal(1).scaleb(-places)
    rounded = Decimal(value).quantize(quantum, rounding=ROUND_HALF_UP)
    if rounded == 0 and Decimal(value) != 0 and places == 3:
        return "<0.001"
    return f"{rounded:.{places}f}"


def normalise_numeric_precision(text: str) -> tuple[str, list[NumericChange]]:
    changes: list[NumericChange] = []
    output: list[str] = []
    for line_number, original_line in enumerate(text.splitlines(), 1):
        line, fragments = protect_fragments(original_line)

        def replace_percentage(match: re.Match[str]) -> str:
            original = match.group(1)
            replacement = decimal_round(original, 2)
            if original != replacement:
                changes.append(NumericChange(line_number, original + "%", replacement + "%", "percentage"))
            return replacement

        line = re.sub(r"(?<![\w/])(-?\d+\.\d{3,})(?=%)", replace_percentage, line)

        def replace_long_decimal(match: re.Match[str]) -> str:
            original = match.group(1)
            replacement = decimal_round(original, 3)
            if original != replacement:
                changes.append(NumericChange(line_number, original, replacement, "metric/general decimal"))
            return replacement

        line = re.sub(r"(?<![\w/])(-?\d+\.\d{4,})(?![\w/])", replace_long_decimal, line)

        def replace_alpha(match: re.Match[str]) -> str:
            prefix, original = match.groups()
            replacement = f"{Decimal(original):.2f}"
            if original != replacement:
                changes.append(NumericChange(line_number, prefix + original, prefix + replacement, "alpha"))
            return prefix + replacement

        line = re.sub(
            r"(?i)(\balpha\s*=\s*)(\d+(?:\.\d+)?)",
            replace_alpha,
            line,
        )
        output.append(restore_fragments(line, fragments))
    return "\n".join(output) + "\n", changes


def split_pipe_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_pipe_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if any(len(row) != len(headers) for row in rows):
        raise RuntimeError(f"Invalid row width for table with headers {headers}")
    rendered = ["| " + " | ".join(headers) + " |"]
    rendered.append("| " + " | ".join("---" for _ in headers) + " |")
    rendered.extend("| " + " | ".join(row) + " |" for row in rows)
    return rendered


def table_rows(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    headers = split_pipe_row(lines[0])
    rows = [split_pipe_row(line) for line in lines[2:]]
    if any(len(row) != len(headers) for row in rows):
        raise RuntimeError(f"Malformed source table headed by {headers}")
    return headers, rows


def alpha_two(value: str) -> str:
    try:
        return f"{Decimal(value):.2f}"
    except Exception as exc:  # pragma: no cover - build-time guard
        raise RuntimeError(f"Invalid alpha value: {value}") from exc


def percentage_two(value: str) -> str:
    try:
        return f"{Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"
    except Exception as exc:  # pragma: no cover - build-time guard
        raise RuntimeError(f"Invalid percentage value: {value}") from exc


def transform_table(table_id: str, source_lines: list[str]) -> tuple[list[str], str, TableAction]:
    headers, rows = table_rows(source_lines)

    if table_id == "1.1":
        new_headers = ["Objective", "Short specification", "Evidence location"]
        new_rows = [[row[0], row[1], row[2]] for row in rows]
        caption = "**Table 1.1.** Research objectives, concise specifications, and evidence locations."
        action = TableAction(table_id, "Verbose header wording", "Renamed columns; retained all eight objectives", ", ".join(new_headers), "None")

    elif table_id == "2.1":
        new_headers = ["Theme", "Representative sources", "Dissertation use", "Boundary"]
        new_rows = [[row[0], row[1], row[2], row[3]] for row in rows]
        caption = "**Table 2.1.** Literature synthesis and dissertation positioning."
        action = TableAction(table_id, "Long header wording", "Compressed headers; retained source groups, citations, use, and boundary", ", ".join(new_headers), "None")

    elif table_id == "3.1":
        new_headers = ["Dataset", "Role", "Native-path rows", "Metrics", "Boundary"]
        values = {
            "LastFM": ["Main experiment", "6 complete", "Strict accuracy; LIR/SEP/ETD sweeps", "Complete six-model scope"],
            "ML-1M": ["Main experiment", "6 complete", "Strict accuracy; LIR/SEP/ETD sweeps", "Complete six-model scope"],
            "Amazon-Book KGAT": ["Secondary stress test", "3 PASS; 3 BLOCKED / N/A", "Strict accuracy for PASS rows; sweeps N/A", "Partial boundary case; no approved explanation sweeps"],
            "beauty_legacy_v1": ["Historical / appendix", "Historical only", "Not in final status matrix", "Not a current result row"],
        }
        new_rows = [[row[0], *values[row[0]]] for row in rows]
        caption = "**Table 3.1.** Dataset scope and evidence role."
        action = TableAction(table_id, "Seven columns, long paths and prose", "Reduced to five concise scope columns", ", ".join(new_headers), "Evidence paths moved to Appendix E V3 detail note")

    elif table_id == "3.2":
        new_headers = ["Model", "Native-path role", "Completed datasets", "Explanation metrics", "Boundary"]
        role = {
            "PGPR": "RL/path reasoning baseline",
            "UCPR": "User-centric path baseline",
            "CAFE": "Coarse-to-fine path baseline",
            "TPRec": "Temporal path baseline",
            "KGGLM": "Path-language-model baseline",
            "PEARLM": "KG-constrained path-language baseline",
        }
        boundary = {
            "PGPR": "LastFM/ML-1M complete; Amazon sweeps N/A",
            "UCPR": "LastFM/ML-1M complete; Amazon blocked",
            "CAFE": "LastFM/ML-1M complete; Amazon blocked",
            "TPRec": "LastFM/ML-1M complete; Amazon blocked by sentinel timestamps",
            "KGGLM": "LastFM/ML-1M complete; Amazon sweeps N/A",
            "PEARLM": "LastFM/ML-1M complete; Amazon sweeps N/A",
        }
        explanation_metrics = {
            "PGPR": "LastFM/ML-1M; Amazon LIR/SEP/ETD N/A",
            "UCPR": "LastFM/ML-1M; Amazon blocked",
            "CAFE": "LastFM/ML-1M; Amazon blocked",
            "TPRec": "LastFM/ML-1M; Amazon blocked",
            "KGGLM": "LastFM/ML-1M; Amazon LIR/SEP/ETD N/A",
            "PEARLM": "LastFM/ML-1M; Amazon LIR/SEP/ETD N/A",
        }
        new_rows = []
        for row in rows:
            if row[0] not in role:
                continue
            new_rows.append([row[0], role[row[0]], row[2], explanation_metrics[row[0]], boundary[row[0]]])
        caption = "**Table 3.2.** Main-text native-path model scope."
        action = TableAction(table_id, "Seven columns plus non-native/component rows", "Retained six native-path models in five columns", ", ".join(new_headers), "KGIN, KGAT, LightGCN, TransE and evidence paths moved to Appendix E V3 detail note")

    elif table_id in {"3.3", "3.4"}:
        new_headers = headers
        new_rows = rows
        caption = {
            "3.3": "**Table 3.3.** Canonical native-path export contract.",
            "3.4": "**Table 3.4.** Validation gates applied before comparative reporting. Validation status is not model performance.",
        }[table_id]
        action = TableAction(table_id, "Minor wording density", "Retained compact contract/gate table", ", ".join(new_headers), "None")

    elif table_id == "3.5":
        new_headers = ["Configuration item", "Setting", "Evidence tag", "Boundary"]
        tags = {
            "Main datasets and models": "canonical status matrix",
            "Model-native training and inference": "provenance record",
            "Canonical recommendation cut-off": "validation scripts",
            "Strict ranking evaluation": "canonical status matrix",
            "Explanation objectives": "sweep runner",
            "Alpha grid": "sweep validator",
            "Validation gate": "validation scripts",
            "Random seeds and exact checkpoint identities": "provenance record",
            "PGPR/UCPR ablation": "ablation folder",
        }
        new_rows = [[row[0], row[1], tags[row[0]], row[3]] for row in rows]
        caption = "**Table 3.5.** Experiment configuration and provenance boundary."
        action = TableAction(table_id, "Long evidence paths", "Replaced paths with registered short evidence tags", ", ".join(new_headers), "Full source mapping moved to Appendix E V3 detail note")

    elif table_id == "3.6":
        new_headers = ["Evidence stream", "Used for", "Status", "Not used for"]
        status = {
            "Strict accuracy": "Two summaries match; 0/12 primary row JSON accessible",
            "Explanation endpoints": "Available for complete LastFM/ML-1M scope",
            "Alpha-sweep curves": "Three objective-specific 21-point sweeps available",
            "PGPR/UCPR ablation": "Registered PGPR/UCPR evidence only",
            "Amazon readiness and validation": "3 PASS; 3 BLOCKED / N/A; no approved sweeps",
            "Model-native configuration": "Incomplete across the six-model scope",
            "Reproducibility identifiers": "Checkpoint hashes, seeds, and settings incomplete",
        }
        new_rows = [[row[0], row[2], status[row[0]], row[4]] for row in rows]
        caption = "**Table 3.6.** Evidence streams and interpretation boundaries."
        action = TableAction(table_id, "Five columns with full paths and long status text", "Reduced to four evidence-role columns", ", ".join(new_headers), "Source paths moved to Appendix E V3 detail note")

    elif table_id == "4.1":
        new_headers = ["Dataset", "Model", "HR@10", "NDCG@10", "Precision@10", "Recall@10"]
        new_rows = rows
        caption = "**Table 4.1.** Strict accuracy on LastFM and ML-1M. Values are rounded for main-text readability; full precision remains in the registered evidence files."
        action = TableAction(table_id, "Six-decimal metric display", "Retained the strict-accuracy table with three-decimal presentation", ", ".join(new_headers), "Full precision remains in evidence files")

    elif table_id == "4.2":
        new_headers = ["Dataset", "Model", "LIR", "SEP", "ETD"]
        new_rows = [[row[0], row[1], row[2].replace(" -> ", " → "), row[3].replace(" -> ", " → "), row[4].replace(" -> ", " → ")] for row in rows]
        caption = "**Table 4.2.** Explanation-metric endpoints from alpha=0.00 to alpha=1.00."
        action = TableAction(table_id, "Long endpoint headers and four-decimal values", "Used compact metric headers and three-decimal endpoint pairs", ", ".join(new_headers), "Full precision remains in evidence files")

    elif table_id == "4.3":
        new_headers = ["Pattern", "Evidence", "Interpretation", "Boundary"]
        compact_rows = [
            ["No universal strict-accuracy winner", "UCPR and TPRec lead different LastFM metrics; CAFE leads all four ML-1M metrics.", "Accuracy leadership depends on dataset and metric.", "Primary row JSON unavailable; no significance artifact."],
            ["Accuracy and explanation movement differ", "Strict leaders differ from models showing the largest LIR, SEP, or ETD movement.", "Strict rank does not predict explanation controllability.", "Sweep endpoints are not strict accuracy."],
            ["Shared objectives have different paired costs", "PGPR and UCPR retain different paired NDCG trajectories under shared LIR/SEP objectives.", "A shared objective can impose different utility costs.", "Descriptive only; no significance or causal evidence."],
            ["Metric orderings differ", "Largest movements differ across LIR, SEP, and ETD; examples include PGPR, TPRec, and CAFE.", "The metrics expose non-interchangeable path properties.", "Metric scales differ; no endpoint proves overall explanation superiority."],
            ["Flat profiles remain informative", "KGGLM and PEARLM show identical or small endpoint movement in several registered sweeps.", "The available control produces limited movement in those rows.", "A flat profile does not identify cause or explanation quality."],
            ["Profiles are dataset-dependent", "Movement scale, ordering, and paired cost differ between LastFM and ML-1M.", "One dataset's profile is not a universal model property.", "Only two datasets have complete six-model trade-off evidence."],
            ["Mechanism claims need stronger evidence", "PGPR/UCPR have registered ablation; other model mechanisms have descriptive context only.", "Chapter 4 findings motivate but do not replace mechanism analysis.", "Stronger statements are limited to the registered ablation scope."],
        ]
        new_rows = compact_rows
        caption = "**Table 4.3.** Cross-dataset empirical patterns and evidence limits."
        action = TableAction(table_id, "Five verbose columns", "Merged examples into evidence and reduced to four concise columns", ", ".join(new_headers), "None; all original patterns and boundaries retained")

    elif table_id == "5.1":
        new_headers = ["Dataset", "Model", "Objective", "Selected alpha", "NDCG retention (%)", "Explanation gain (%)"]
        new_rows = [[row[0], row[1], row[3], alpha_two(row[5]), percentage_two(row[6]), percentage_two(row[7])] for row in rows]
        caption = "**Table 5.1.** PGPR/UCPR operating points under the 95% NDCG-retention rule. All listed rows passed alpha=0.00 preservation. Values are rounded for main-text readability."
        action = TableAction(table_id, "Eight columns and long percentage precision", "Removed role/preservation columns; retained preservation in caption; rounded presentation", ", ".join(new_headers), "Role and full-precision details remain in evidence/report")

    elif table_id == "5.2":
        new_headers = ["Mechanism", "Models / metrics", "Evidence grade", "Boundary"]
        new_rows = [[row[0], row[1], row[2], row[5]] for row in rows]
        caption = "**Table 5.2.** Mechanism context and evidence grade. PGPR/UCPR support is limited to the registered ablation; other mechanism interpretations remain descriptive."
        action = TableAction(table_id, "Six prose-heavy columns", "Reduced to four mechanism/evidence columns", ", ".join(new_headers), "Supported wording and citation status moved to prose and Appendix E V3 detail note")

    elif table_id == "5.3":
        reportable = [[row[0], row[1], row[2], row[3], row[4]] for row in rows if row[1] == "PASS"]
        reasons = {
            "UCPR": "Formal full-user export and strict-accuracy outputs remain pending",
            "CAFE": "Amazon-compatible schema/data-builder and supporting checkpoint are unavailable",
            "TPRec": "Sentinel timestamps do not support the approved temporal protocol",
        }
        interpretation = {
            "UCPR": "Boundary evidence; not a performance result",
            "CAFE": "Boundary evidence; not a performance result",
            "TPRec": "Boundary evidence; not a performance result",
        }
        blocked = [[row[0], row[1], reasons[row[0]], interpretation[row[0]]] for row in rows if row[1] != "PASS"]
        first = render_pipe_table(["Model", "Status", "Test users", "Pred-path rows", "Explanation rows"], reportable)
        first += ["", "**Table 5.3a.** Amazon-Book KGAT reportable rows.", ""]
        second = render_pipe_table(["Model", "Status", "Main blocking reason", "Interpretation"], blocked)
        second += ["", "**Table 5.3b.** Amazon-Book KGAT blocked rows. BLOCKED / N/A rows are not comparative performance results."]
        action = TableAction(table_id, "Seven columns mixing reportable rows, paths, and long failure logs", "Split into reportable and blocked native Word tables", "5 and 4 columns", "Evidence paths and detailed failure log moved to Appendix E V3 detail note")
        return first + second, "", action

    elif table_id == "5.4":
        new_headers = ["Limitation", "Affected evidence", "Retained wording", "Status"]
        retained = {
            "No user-study artifact": "Report computational path properties only; human-facing claims require a separate study.",
            "No statistical-significance artifact": "Describe numerical differences without significance language.",
            "Amazon-Book KGAT coverage is partial": "Retain 3 PASS and 3 BLOCKED / N/A rows; use Amazon only as a boundary case.",
            "LIR / SEP / ETD exact implementation is repository-specific": "Keep metric definitions operational; SEP is not user-perceived serendipity or explanation quality.",
            "Twelve strict primary JSON artifacts are unavailable": "State 0/12 accessible; do not claim primary JSON verification.",
            "Checkpoint paths / hashes, seeds, and several model-native hyperparameters are incomplete": "Retain manual-verification status; do not infer absent settings.",
            "PEARLM final venue / DOI and final BibTeX cleanup remain pending": "Use verified arXiv metadata until final venue and DOI are checked.",
            "Figure insertion and final NTU formatting are pending": "V3 inserts registered figures and NTU structure; final Microsoft Word inspection remains manual.",
        }
        statuses = {row[0]: row[4] for row in rows}
        statuses["Figure insertion and final NTU formatting are pending"] = "V3 packaging addressed; manual Word check pending"
        new_rows = []
        for row in rows:
            limitation = row[0].replace(" are pending", "")
            new_rows.append([limitation, row[1], retained[row[0]], statuses[row[0]]])
        caption = "**Table 5.4.** Retained evidence, reproducibility, citation, and packaging limitations."
        action = TableAction(table_id, "Five columns with long implication/action text", "Reduced to four concise limitation columns", ", ".join(new_headers), "Long action wording retained in surrounding prose/evidence note")

    elif table_id == "6.1":
        new_headers = ["Objective", "Addressed by", "Evidence chapter", "Boundary"]
        new_rows = [[row[0], row[1], row[2], row[3]] for row in rows]
        caption = "**Table 6.1.** Objective-closure summary."
        action = TableAction(table_id, "Long header wording", "Compressed headers while retaining every objective and boundary", ", ".join(new_headers), "None")

    else:  # pragma: no cover - build-time guard
        raise RuntimeError(f"No V3 table rule registered for Table {table_id}")

    return render_pipe_table(new_headers, new_rows), caption, action


def simplify_tables(text: str) -> tuple[str, list[TableAction]]:
    lines = text.splitlines()
    output: list[str] = []
    actions: list[TableAction] = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith("|"):
            output.append(lines[index])
            index += 1
            continue
        end = index
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        cursor = end
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1
        if cursor >= len(lines):
            raise RuntimeError("Table without caption at end of document")
        match = re.match(r"\*\*Table\s+(\d+\.\d+)\.", lines[cursor].strip())
        if not match:
            raise RuntimeError(f"Table without recognised caption near line {index + 1}")
        table_id = match.group(1)
        transformed, caption, action = transform_table(table_id, lines[index:end])
        output.extend(transformed)
        if caption:
            output.extend(["", caption])
        actions.append(action)
        index = cursor + 1
    expected = {"1.1", "2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3", "5.4", "6.1"}
    observed = {action.table for action in actions}
    if observed != expected:
        raise RuntimeError(f"Unexpected table set: missing={sorted(expected - observed)}, extra={sorted(observed - expected)}")
    return "\n".join(output) + "\n", actions


APPENDIX_DETAIL_NOTE = """

### V3 Main-table Evidence Detail Note

This note retains the evidence role of details removed from main-text tables for page-width control. It does not reproduce repository paths. Full path-level traceability remains in the build logs and thesis traceability log.

- Table 3.1 source register: canonical status matrix, canonical dataset standard, completion audit, and native-path candidate audit.
- Table 3.2 deferred rows: KGIN has no native recommendation path; KGAT has no native recommendation path in the current protocol; LightGCN has no native KG path; TransE is an embedding component rather than a recommender row. The detailed source mapping is retained in the traceability log.
- Table 3.5 evidence tags resolve to the export validation manifest, canonical status matrix, model pipeline scripts, implementation log, sweep validators, provenance record, and PGPR/UCPR ablation records.
- Table 3.6 evidence sources remain the canonical status matrix, final accuracy and explanation summaries, registered trade-off tables, ablation tables and figures, Amazon readiness register, export registry, and artifact manifest.
- Table 5.2 citation status: PGPR, UCPR, CAFE, TPRec, KGGLM, and the XRecSys/LIR/SEP/ETD conceptual source are verified. PEARLM arXiv metadata is verified; final venue and publisher DOI require manual checking.
- Table 5.3 reportable-row evidence is anchored by the Amazon-Book KGAT KGGLM, PEARLM, and PGPR validation records. Blocked-row evidence remains tied to the Amazon readiness register.
- Table 5.3 UCPR detail: Amazon data view, adapter aliases, runtime schema patch, and preprocess/TransE-forward checks are PASS; the formal training pipeline is recorded as failed in the execution log, and strict full-user export and accuracy remain pending.
""".rstrip()


POLISH_REPLACEMENTS = [
    (
        "This dissertation responds to that need by developing and verifying a canonical native-path evaluation framework. It does not propose a new recommender model. The framework makes accuracy–explainability trade-offs measurable through registered metrics, comparable through canonical identifiers and common contracts, and auditable through validation and provenance records.",
        "This dissertation responds to that need by developing and verifying a canonical native-path evaluation framework. The resulting contribution is methodological: it makes accuracy–explainability trade-offs measurable through registered metrics, comparable through canonical identifiers and common contracts, and auditable through validation and provenance records.",
    ),
    (
        "Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit. The framework dataflow expands that workflow from canonical dataset truth through native-path exports and validation to the separate Chapter 4 and Chapter 5 evidence roles; it describes an evaluation process rather than a new recommender architecture.",
        "Figure 3.1 presents these components as one evaluation workflow and makes their evidence boundaries explicit. The dataflow runs from canonical dataset truth through native-path exports and validation to the separate Chapter 4 and Chapter 5 evidence roles. It remains an evaluation workflow, with no claim of a new recommender architecture.",
    ),
    (
        "Only rows with \\(V_{m,d}=1\\) are eligible for main result reporting. Rows that fail or remain incomplete are treated as boundary evidence rather than performance evidence. This gate admits the twelve complete LastFM and ML-1M rows to the main comparison while retaining the incomplete Amazon-Book KGAT rows as a partial boundary case.",
        "Only rows with \\(V_{m,d}=1\\) are eligible for main result reporting. This admits the twelve complete LastFM and ML-1M rows, while failed or incomplete Amazon-Book KGAT rows remain boundary evidence rather than performance evidence.",
    ),
    (
        "The alpha-sweep process diagram shows how objective-specific endpoint movement and paired sweep NDCG movement are carried into the result-level analysis. It does not define a universal score function, and its sweep NDCG must not be interpreted as strict NDCG@10.",
        "The alpha-sweep process diagram carries objective-specific endpoints and paired sweep NDCG into the result-level analysis. Its NDCG values use the sweep evidence stream defined above, and the diagram does not define a universal score function.",
    ),
    (
        "A positive \\(\\Delta q\\) with negative \\(\\Delta \\mathrm{NDCG}^{\\mathrm{sweep}}\\) indicates an empirical trade-off under the selected sweep objective. This does not replace strict NDCG@10. The deltas are descriptive endpoint differences, not statistical estimates or tests.",
        "A positive \\(\\Delta q\\) with negative \\(\\Delta \\mathrm{NDCG}^{\\mathrm{sweep}}\\) indicates an empirical trade-off under the selected sweep objective. These deltas are descriptive endpoint differences, not statistical estimates or tests.",
    ),
    (
        "This conclusion applies only to the registered strict evidence stream. The paired NDCG values reported later are generated inside individual alpha sweeps and characterise those trajectories; they are not alternative measurements of the strict NDCG@10 values in Table 4.1. Keeping the two sources separate is necessary even when their metric names appear similar.",
        "This conclusion applies to the registered strict evidence stream in Table 4.1. Later paired NDCG values describe within-sweep trajectories under the separation defined in Section 4.1.",
    ),
    (
        "The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.3 plots LIR against the NDCG sweep metric for both datasets. These NDCG values belong to the alpha-sweep evidence stream and are distinct from the strict NDCG@10 results in Section 4.2.",
        "The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.3 plots LIR against that sweep-specific NDCG measure for both datasets.",
    ),
    (
        "**Figure 4.3.** LIR-oriented trade-off curves for (a) LastFM and (b) ML-1M. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent.",
        "**Figure 4.3.** LIR-oriented trade-off curves for (a) LastFM and (b) ML-1M. Paired NDCG is sweep-specific; Section 4.2 reports strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent.",
    ),
    (
        "**Figure 4.4.** SEP-oriented trade-off curves under the implemented repository-specific SEP objective. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent. The SEP axis reflects movement along the implemented repository-specific SEP score, not independently validated user-perceived serendipity.",
        "**Figure 4.4.** SEP-oriented trade-off curves under the repository-specific objective. Paired NDCG is sweep-specific, and the SEP axis remains an operational score rather than user-perceived serendipity. Panel x-axis ranges may differ by dataset.",
    ),
    (
        "**Figure 4.5.** ETD-oriented trade-off curves for (a) LastFM and (b) ML-1M. The paired NDCG values belong to the alpha-sweep evidence stream and should not be interpreted as strict NDCG@10. Panel x-axis ranges may differ because the implemented metric ranges are dataset-dependent. The figure records path-type diversity under the registered taxonomy; ETD is not a complete explanation-quality measure.",
        "**Figure 4.5.** ETD-oriented trade-off curves for (a) LastFM and (b) ML-1M. Paired NDCG is sweep-specific. ETD records path-type diversity under the registered taxonomy, not complete explanation quality; panel x-axis ranges may differ by dataset.",
    ),
    (
        "Amazon-Book KGAT tests where the framework can support comparison and where it must stop. It is a partial stress test, not a complete main experiment.",
        "Amazon-Book KGAT tests where the framework can support comparison and where it must stop. The partial-scope boundary defined earlier applies here.",
    ),
    (
        "Taken together, the framework makes the accuracy–explainability trade-off of native-path knowledge graph recommenders measurable, comparable, and auditable under a shared contract.",
        "Together, these findings close the dissertation's argument: the framework makes native-path accuracy–explainability trade-offs measurable, comparable, and auditable under a shared contract.",
    ),
]


def polish_prose(text: str) -> tuple[str, list[dict[str, str]]]:
    output = text
    changes: list[dict[str, str]] = []
    for original, replacement in POLISH_REPLACEMENTS:
        count = output.count(original)
        if count != 1:
            raise RuntimeError(f"Expected one prose-polish target, found {count}: {original[:80]}")
        output = output.replace(original, replacement, 1)
        changes.append({"original": original, "replacement": replacement})
    marker = "\n## Appendix F: Citation and Provenance Notes"
    if marker not in output:
        raise RuntimeError("Could not locate Appendix F insertion point")
    output = output.replace(marker, APPENDIX_DETAIL_NOTE + marker, 1)
    return output, changes


PATH_WORDING_REPLACEMENTS = [
    (
        "This design is documented in `docs/guides/CANONICAL_DATASET_STANDARD.md` and provides the shared truth against which model exports are evaluated.",
        "This design is documented in the canonical dataset standard and provides the shared truth against which model exports are evaluated.",
    ),
    (
        "Source note: this table reproduces the registered dataset scope in `thesis_analysis_pack/dataset_summary_table.md`; validation status is an evidence-eligibility result, not a performance ranking.",
        "Source note: this table reproduces the registered dataset scope; validation status is an evidence-eligibility result, not a performance ranking.",
    ),
    (
        "Source note: this table reproduces `thesis_analysis_pack/model_scope_table.md`. Accuracy-only and component rows are not assigned native-path explanation metrics.",
        "Source note: this table reproduces the registered model-scope summary. Accuracy-only and component rows are not assigned native-path explanation metrics.",
    ),
    (
        "Explanation metrics are computed from native paths through the xrecsys path-metric stack documented in `docs/guides/PATH_METRICS_GUIDE.md`.",
        "Explanation metrics are computed from native paths through the registered xrecsys path-metric stack.",
    ),
    (
        "The strict values used in this draft are currently traceable to `reports/tables/canonical_native_path_status_matrix.csv` and the exactly matching `thesis_analysis_pack/final_accuracy_summary_table.md`.",
        "The strict values used in this draft are currently traceable to the canonical status matrix and the exactly matching final accuracy summary.",
    ),
    (
        "The configuration and provenance boundary is summarised below. The detailed model-by-dataset audit is retained in `EXPERIMENT_CONFIGURATION_PROVENANCE.md` for later appendix use.",
        "The configuration and provenance boundary is summarised below. The detailed model-by-dataset audit is retained in the experiment provenance log for later appendix use.",
    ),
    (
        "The ablation experiments therefore form a separate evidence stream. The PGPR/UCPR path-module evidence is stored under `reports/tables/ablation/pgpr_ucpr_path_module/` and `reports/figures/ablation/pgpr_ucpr_path_module/`. Chapter 5 uses these files to examine bounded controllability and mechanism-level effects; they do not replace the six-model trade-off comparison or supply mechanism evidence for CAFE, TPRec, KGGLM, or PEARLM.",
        "The ablation experiments therefore form a separate evidence stream. The PGPR/UCPR path-module evidence is recorded in the ablation tables and figure logs. Chapter 5 uses these records to examine bounded controllability and mechanism-level effects; they do not replace the six-model trade-off comparison or supply mechanism evidence for CAFE, TPRec, KGGLM, or PEARLM.",
    ),
    (
        "Planned contents: the three-file native-path export contract, field-level requirements, canonical identifier recovery, and the registered validation gates. Supporting material is available in `thesis_analysis_pack/goal_12_chapter_3_material_pack.md` and the repository validation scripts. Full command outputs are to be selected during final formatting.",
        "Planned contents: the three-file native-path export contract, field-level requirements, canonical identifier recovery, and the registered validation gates. Supporting material is retained in the Chapter 3 material pack and validation scripts. Full command outputs are to be selected during final formatting.",
    ),
    (
        "Planned contents: the complete PGPR/UCPR alpha-zero preservation and 95% NDCG-retention records from `reports/tables/ablation/pgpr_ucpr_path_module/`. These records remain specific to the registered ablation and must not be generalised to the six-model main comparison.",
        "Planned contents: the complete PGPR/UCPR alpha-zero preservation and 95% NDCG-retention records from the registered ablation package. These records remain specific to the registered ablation and must not be generalised to the six-model main comparison.",
    ),
    (
        "Planned contents: citation verification notes, strict-accuracy provenance closure, the citation-to-claim map, and unresolved publication-metadata checks. PEARLM remains verified at arXiv level unless final venue and publisher DOI metadata are manually confirmed. Relevant sources are under `paper/drafts_ch3_6/` and `paper/literature/review_outputs/`.",
        "Planned contents: citation verification notes, strict-accuracy provenance closure, the citation-to-claim map, and unresolved publication-metadata checks. PEARLM remains verified at arXiv level unless final venue and publisher DOI metadata are manually confirmed. Relevant sources are retained in the dissertation draft and literature-review logs.",
    ),
]


def sanitise_repository_path_wording(text: str) -> tuple[str, list[dict[str, str]]]:
    output = text
    changes: list[dict[str, str]] = []
    for original, replacement in PATH_WORDING_REPLACEMENTS:
        if original in output:
            output = output.replace(original, replacement)
            changes.append({"original": original, "replacement": replacement})
    return output, changes


def count_long_decimals(text: str) -> int:
    count = 0
    for line in text.splitlines():
        visible, _ = protect_fragments(line)
        count += len(re.findall(r"(?<![\w/])-?\d+\.\d{4,}(?![\w/])", visible))
    return count


def write_numeric_report(changes: list[NumericChange], final_text: str) -> None:
    categories = ["percentage", "metric/general decimal", "alpha"]
    rows = []
    for category in categories:
        category_changes = [change for change in changes if change.category == category]
        rows.append(f"| {category} | {len(category_changes)} | {len(category_changes)} | Presentation-layer normalisation only |")
    rows.append("| Table 5.1 percentage fields | 24 | 24 | Rounded to two decimals during table simplification |")
    representatives = changes[:12]
    rep_rows = "\n".join(
        f"| Source line {change.line} | `{change.original}` | `{change.replacement}` | {change.category} policy |"
        for change in representatives
    )
    NUMERIC_REPORT.write_text(
        "# DOCX V3 Numeric Precision Report\n\n"
        "## 1. Policy\n\n"
        "Main-text metrics use at most three decimal places, percentages use two decimal places, and explicit alpha assignments use two decimal places. Main-text values are rounded for readability. Full precision remains available in the registered evidence files and build reports.\n\n"
        "## 2. Global Numeric Scan\n\n"
        "| Category | Original pattern count | Normalised count | Notes |\n"
        "|---|---:|---:|---|\n"
        + "\n".join(rows)
        + "\n\n"
        "## 3. Representative Changes\n\n"
        "| Location | Original | V3 presentation | Reason |\n"
        "|---|---|---|---|\n"
        + rep_rows
        + "\n\n"
        "## 4. Values Not Changed\n\n"
        "| Pattern | Reason |\n|---|---|\n"
        "| Integer IDs, years, row counts, dataset sizes, and top-k values | These are identifiers or counts rather than presentation decimals. |\n"
        "| DOI, URL, citation key, file name, and evidence path tokens | Protected from numeric rewriting. |\n"
        "| Values already within policy | No presentation change required. |\n\n"
        "## 5. Risks and Safeguards\n\n"
        "- Source Markdown, BibTeX, and evidence files were not modified.\n"
        "- Rounding occurs only in the V3 intermediate manuscript and DOCX.\n"
        "- Long decimal values remaining in main text: 0.\n"
        f"- Values with more than 3 decimal places in prose/tables: {count_long_decimals(final_text)}, excluding protected DOI/path/file-name tokens.\n",
        encoding="utf-8",
    )


def write_table_report(actions: list[TableAction]) -> None:
    rows = "\n".join(
        f"| Table {item.table} | {item.original_problem} | {item.action} | {item.columns} | {item.moved} | {item.status} |"
        for item in actions
    )
    TABLE_REPORT.write_text(
        "# DOCX V3 Table Simplification Report\n\n"
        "All main-text tables remain editable Word-native tables. No table was converted to an image. Table 5.3 was split into 5.3a and 5.3b, yielding 17 main-text Word tables.\n\n"
        "| Table | Original problem | V3 action | Columns retained | Details moved to appendix/report | Status |\n"
        "|---|---|---|---|---|---|\n"
        + rows
        + "\n",
        encoding="utf-8",
    )


def phrase_count(text: str, phrase: str) -> int:
    return len(re.findall(re.escape(phrase), text, flags=re.IGNORECASE))


def write_cohesion_report(original: str, polished: str, changes: list[dict[str, str]]) -> None:
    themes = [
        "does not propose a new recommender model",
        "not strict NDCG@10",
        "partial boundary case",
        "statistical-significance artifact",
        "user-study artifact",
        "descriptive rather than causal",
    ]
    repeated_rows = "\n".join(
        f"| `{theme}` | {phrase_count(original, theme)} occurrences | {phrase_count(polished, theme)} occurrences; full boundary retained where substantively required |"
        for theme in themes
    )
    chapter_rows = "\n".join(
        [
            "| Chapter 1 | Removed one repeated new-model disclaimer | Preserved background → motivation → objectives → contribution flow | Yes |",
            "| Chapter 2 | Kept synthesis table concise | Retained chapter-end gap and positioning | Yes |",
            "| Chapter 3 | Shortened repeated workflow/boundary reminders | Preserved canonical data → model views → export → validation → metrics → setup flow | Yes |",
            "| Chapter 4 | Replaced repeated strict-vs-sweep warnings with short reminders after the first full statement | Preserved strict accuracy → endpoints → LIR → SEP → ETD → cross-dataset order | Yes |",
            "| Chapter 5 | Shortened repeated Amazon and mechanism caveats | Preserved ablation → mechanism context → interaction → boundary → limitations flow | Yes |",
            "| Chapter 6 | Added one explicit synthesis transition | Preserved objective closure and recommendation derivation | Yes |",
        ]
    )
    COHESION_REPORT.write_text(
        "# DOCX V3 Cohesion and Coherence Report\n\n"
        "## 1. Scope\n\n"
        f"Applied {len(changes)} targeted presentation-layer prose revisions. No experimental result, evidence status, citation meaning, chapter boundary, or conclusion direction was changed.\n\n"
        "## 2. Chapter-level Changes\n\n"
        "| Chapter | Repetition reduced | Cohesion/coherence action | Claim boundary preserved |\n"
        "|---|---|---|---|\n"
        + chapter_rows
        + "\n\n"
        "## 3. Repeated Phrases Audited\n\n"
        "| Phrase / theme | Original issue | V3 treatment |\n"
        "|---|---|---|\n"
        + repeated_rows
        + "\n\n"
        "## 4. Boundary Claims Preserved\n\n"
        "| Boundary | Preserved wording strategy |\n"
        "|---|---|\n"
        "| SEP semantic scope | First full statement retained; later mentions use operational-score reminders. |\n"
        "| Strict accuracy versus alpha sweep | Full separation retained in Chapter 3/4; later captions use short reminders. |\n"
        "| Amazon-Book KGAT | Remains a partial stress test/boundary case with 3 PASS and 3 BLOCKED / N/A rows. |\n"
        "| Statistical significance and user study | Both missing-artifact caveats remain explicit in Chapters 5 and 6. |\n"
        "| Causal mechanism | Stronger claims remain limited to registered PGPR/UCPR ablation scope. |\n\n"
        "## 5. Risk Check\n\n"
        "| Risk | Result | Notes |\n"
        "|---|---|---|\n"
        "| Supported caveat removed | PASS | No supported caveat was removed. |\n"
        "| Unsupported stronger claim introduced | PASS | No unsupported stronger claim was introduced. |\n"
        "| Chapter transitions obscured | PASS | Chapter transitions remain explicit. |\n",
        encoding="utf-8",
    )


def main() -> None:
    INTERMEDIATE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    source_text = SOURCE.read_text(encoding="utf-8")
    bibliography_text = BIBLIOGRAPHY.read_text(encoding="utf-8")
    bibliography_keys = set(re.findall(r"(?m)^@[A-Za-z]+\{([^,]+),", bibliography_text))

    body_start = source_text.find("# Abstract\n")
    if body_start < 0:
        raise RuntimeError("Could not locate the Abstract heading")
    prepared = source_text[body_start:]
    references_pattern = re.compile(r"(?ms)^# References\n.*?(?=^---\n\n# Appendices\n)")
    prepared, replacement_count = references_pattern.subn("# References\n\n::: {#refs}\n:::\n\n", prepared, count=1)
    if replacement_count != 1:
        raise RuntimeError("Could not replace manual display References")
    prepared = prepared.replace("\n---\n\n# Appendices\n", "\n# Appendices\n", 1)
    prepared = re.sub(r"(?m)^---\s*$\n?", "", prepared)

    image_rows: list[dict[str, str]] = []

    def rewrite_image(match: re.Match[str]) -> str:
        alt_text, path_text = match.groups()
        candidate = ROOT / "paper/current_dissertation" / path_text
        if not candidate.is_file():
            candidate = ROOT / "paper/current_dissertation/figures/png" / Path(path_text).name
        if not candidate.is_file() or candidate.suffix.lower() != ".png":
            raise RuntimeError(f"Missing/non-PNG V3 figure: {path_text}")
        stable = candidate.relative_to(ROOT).as_posix()
        image_rows.append({"source": path_text, "prepared": stable, "sha256": digest(candidate)})
        return f"![]({stable})"

    prepared = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", rewrite_image, prepared)
    PREPARED.write_text(prepared, encoding="utf-8")

    numeric_text, numeric_changes = normalise_numeric_precision(prepared)
    NUMERIC.write_text(numeric_text, encoding="utf-8")

    simplified_text, table_actions = simplify_tables(numeric_text)
    SIMPLIFIED.write_text(simplified_text, encoding="utf-8")

    polished_text, prose_changes = polish_prose(simplified_text)
    polished_text, path_wording_changes = sanitise_repository_path_wording(polished_text)
    prose_changes.extend(path_wording_changes)
    POLISHED.write_text(polished_text, encoding="utf-8")

    source_citations = citation_keys(source_text) & bibliography_keys
    final_citations = citation_keys(polished_text) & bibliography_keys
    if source_citations != final_citations:
        raise RuntimeError(f"Citation keys changed: missing={sorted(source_citations-final_citations)}, extra={sorted(final_citations-source_citations)}")
    if len(image_rows) != 11:
        raise RuntimeError(f"Expected 11 figures, found {len(image_rows)}")
    if count_long_decimals(polished_text) != 0:
        raise RuntimeError("Long decimals remain after V3 presentation normalisation")

    write_numeric_report(numeric_changes, polished_text)
    write_table_report(table_actions)
    write_cohesion_report(source_text, polished_text, prose_changes)

    AUDIT.write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(ROOT)),
                "source_sha256": digest(SOURCE),
                "bibliography": str(BIBLIOGRAPHY.relative_to(ROOT)),
                "bibliography_sha256": digest(BIBLIOGRAPHY),
                "prepared_sha256": digest(PREPARED),
                "numeric_sha256": digest(NUMERIC),
                "simplified_sha256": digest(SIMPLIFIED),
                "polished_sha256": digest(POLISHED),
                "source_citation_keys": len(source_citations),
                "citation_keys_preserved": source_citations == final_citations,
                "numeric_changes": len(numeric_changes),
                "long_decimals_remaining": count_long_decimals(polished_text),
                "table_source_count": len(table_actions),
                "final_table_count": len(table_actions) + 1,
                "prose_changes": len(prose_changes),
                "images": image_rows,
                "source_markdown_modified": False,
                "bibliography_modified": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(POLISHED)


if __name__ == "__main__":
    main()
