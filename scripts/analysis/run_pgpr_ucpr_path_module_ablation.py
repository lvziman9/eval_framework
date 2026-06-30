#!/usr/bin/env python3
"""
PGPR/UCPR path-module ablation report generator.

This script is intentionally read-only with respect to model artifacts: it
consumes frozen xrecsys result CSVs plus canonical validation JSON files and
writes derived ablation tables, SVG tradeoff figures, and lightweight
explanation cases.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


EXPECTED_ALPHAS = [round(i * 0.05, 2) for i in range(21)]
REC_METRICS = ("ndcg", "hr", "precision", "recall")
EXP_METRICS = ("LIR", "SEP", "ETD")
ALL_METRICS = REC_METRICS + EXP_METRICS


@dataclass(frozen=True)
class Artifact:
    dataset: str
    dataset_label: str
    model: str
    role: str
    result_dir: Path
    paths_dir: Path
    export_validation_json: Path
    accuracy_json: Path
    sweep_protocol: str
    ndcg_scope: str


ARTIFACTS = [
    Artifact(
        dataset="lastfm",
        dataset_label="LastFM",
        model="PGPR",
        role="main",
        result_dir=Path("xrecsys/results/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score"),
        paths_dir=Path("xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score"),
        export_validation_json=Path("reports/tables/canonical_export_validation/lastfm_pgpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json"),
        sweep_protocol="xrecsys legacy-exact-k alpha sweep; export/accuracy provenance is canonical full-user PASS",
        ndcg_scope="sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy",
    ),
    Artifact(
        dataset="lastfm",
        dataset_label="LastFM",
        model="UCPR",
        role="auxiliary",
        result_dir=Path("xrecsys/results/lastfm/agent_topk=25-50-1-ucpr-canonical-matched"),
        paths_dir=Path("xrecsys/paths/lastfm/agent_topk=25-50-1-ucpr-canonical-matched"),
        export_validation_json=Path("reports/tables/canonical_export_validation/lastfm_ucpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json"),
        sweep_protocol="xrecsys legacy-exact-k alpha sweep; export/accuracy provenance is canonical full-user PASS",
        ndcg_scope="sweep-internal legacy NDCG; use only for within-sweep retention, not for cross-table comparison with strict accuracy",
    ),
    Artifact(
        dataset="ml1m",
        dataset_label="ML-1M",
        model="PGPR",
        role="main",
        result_dir=Path("xrecsys/results/ml1m/agent_topk=25-50-1-pgpr-canonical-ml1m-canonical-all-users"),
        paths_dir=Path("xrecsys/paths/ml1m/agent_topk=25-50-1-pgpr-canonical-ml1m"),
        export_validation_json=Path("reports/tables/canonical_export_validation/ml1m_pgpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json"),
        sweep_protocol="xrecsys canonical-all-users alpha sweep",
        ndcg_scope="canonical-all-users sweep NDCG",
    ),
    Artifact(
        dataset="ml1m",
        dataset_label="ML-1M",
        model="UCPR",
        role="auxiliary",
        result_dir=Path("xrecsys/results/ml1m/agent_topk=25-50-1-ucpr-canonical-ml1m-canonical-all-users"),
        paths_dir=Path("xrecsys/paths/ml1m/agent_topk=25-50-1-ucpr-canonical-ml1m"),
        export_validation_json=Path("reports/tables/canonical_export_validation/ml1m_ucpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json"),
        sweep_protocol="xrecsys canonical-all-users alpha sweep",
        ndcg_scope="canonical-all-users sweep NDCG",
    ),
]


def pct(numerator: float, denominator: float) -> float:
    if denominator == 0 or math.isnan(denominator):
        return float("nan")
    return numerator / abs(denominator) * 100.0


def pct_change(value: float, baseline: float) -> float:
    return pct(value - baseline, baseline)


def fmt_float(value: object, digits: int = 4) -> str:
    if value is None:
        return ""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(fval):
        return ""
    return f"{fval:.{digits}f}"


def fmt_pct(value: object, digits: int = 2) -> str:
    if value is None:
        return ""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(fval):
        return ""
    return f"{fval:.{digits}f}%"


def read_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def ensure_inputs(artifact: Artifact) -> None:
    if artifact.dataset not in {"lastfm", "ml1m"}:
        raise ValueError(f"Dataset is not allowed in this ablation: {artifact.dataset}")
    required = [
        artifact.result_dir / "baseline_avg.csv",
        artifact.result_dir / "LIRopt_moving_alpha_avg.csv",
        artifact.result_dir / "SEPopt_moving_alpha_avg.csv",
        artifact.result_dir / "ETDopt_moving_alpha_avg.csv",
        artifact.paths_dir / "uid_topk.csv",
        artifact.paths_dir / "uid_pid_explanation.csv",
        artifact.paths_dir / "pred_paths.csv",
        artifact.export_validation_json,
        artifact.accuracy_json,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required ablation inputs:\n" + "\n".join(missing))

    validation = read_json(artifact.export_validation_json)
    if validation.get("status") != "PASS":
        raise ValueError(f"Export validation is not PASS: {artifact.export_validation_json}")
    accuracy = read_json(artifact.accuracy_json)
    if accuracy.get("status") != "PASS":
        raise ValueError(f"Accuracy validation is not PASS: {artifact.accuracy_json}")


def read_overall_table(path: Path) -> Dict[float, Dict[str, float]]:
    by_alpha: Dict[float, Dict[str, float]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        expected = {"alpha", "metric", "group", "data"}
        if not expected.issubset(reader.fieldnames or []):
            raise ValueError(f"Malformed result CSV: {path}")
        for row in reader:
            if row["group"] != "Overall":
                continue
            alpha = round(float(row["alpha"]), 2)
            metric = row["metric"]
            if metric not in ALL_METRICS:
                continue
            by_alpha.setdefault(alpha, {})[metric] = float(row["data"])
    return by_alpha


def validate_alpha_table(path: Path, by_alpha: Dict[float, Dict[str, float]]) -> None:
    found = sorted(by_alpha)
    if found != EXPECTED_ALPHAS:
        raise ValueError(f"Incomplete alpha sweep in {path}: found={found}")
    for alpha in EXPECTED_ALPHAS:
        missing = [metric for metric in ALL_METRICS if metric not in by_alpha[alpha]]
        if missing:
            raise ValueError(f"Missing metrics for alpha={alpha} in {path}: {missing}")


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_main_ablation_rows(tradeoff_rows: Sequence[dict]) -> List[dict]:
    rows = []
    for row in tradeoff_rows:
        recommended_use = "main ablation table"
        if str(row.get("constraint", "")).startswith("no alpha"):
            recommended_use = "endpoint exception; discuss separately"
        rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "module_target": row["optimized_metric"],
            "selected_alpha": row["alpha"],
            "selection_rule": row["constraint"],
            "ndcg_retention_pct": row["ndcg_retention_pct"],
            "explanation_gain_pct": row["optimized_metric_gain_pct"],
            "sweep_ndcg": row["ndcg"],
            "explanation_metric_value": row[row["optimized_metric"]],
            "ndcg_scope": row["ndcg_scope"],
            "recommended_use": recommended_use,
        })
    return rows


def rows_to_markdown(rows: Sequence[dict], columns: Sequence[Tuple[str, str]]) -> str:
    header = "| " + " | ".join(label for _, label in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for row in rows:
        values = []
        for key, _ in columns:
            value = row.get(key, "")
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def endpoint_row(
    artifact: Artifact,
    module: str,
    opt_metric: str,
    alpha: float,
    metrics: Dict[str, float],
    baseline: Dict[str, float],
) -> dict:
    row = {
        "dataset": artifact.dataset_label,
        "model": artifact.model,
        "role": artifact.role,
        "module": module,
        "optimized_metric": opt_metric,
        "alpha": alpha,
        "sweep_protocol": artifact.sweep_protocol,
        "ndcg_scope": artifact.ndcg_scope,
    }
    for metric in ALL_METRICS:
        row[metric] = metrics.get(metric, float("nan"))
        row[f"{metric}_delta_pct"] = pct_change(metrics.get(metric, float("nan")), baseline.get(metric, float("nan")))
    return row


def build_ablation_tables(artifacts: Sequence[Artifact]) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    endpoint_rows: List[dict] = []
    curve_rows: List[dict] = []
    tradeoff_rows: List[dict] = []
    provenance_rows: List[dict] = []

    for artifact in artifacts:
        ensure_inputs(artifact)
        validation = read_json(artifact.export_validation_json)
        accuracy = read_json(artifact.accuracy_json)

        provenance_rows.append({
            "dataset": artifact.dataset_label,
            "model": artifact.model,
            "role": artifact.role,
            "export_status": validation.get("status"),
            "accuracy_status": accuracy.get("status"),
            "canonical_test_users": validation.get("canonical_test_users"),
            "topk_users": validation.get("topk_users"),
            "candidate_users": validation.get("candidate_users"),
            "explanations": validation.get("explanations"),
            "pred_path_rows": validation.get("pred_path_rows"),
            "accuracy_hr": accuracy.get("metrics", {}).get("hr"),
            "accuracy_ndcg": accuracy.get("metrics", {}).get("ndcg"),
            "accuracy_precision": accuracy.get("metrics", {}).get("precision"),
            "accuracy_recall": accuracy.get("metrics", {}).get("recall"),
            "slot_coverage": accuracy.get("recommendation_coverage", {}).get("slot_coverage"),
            "sweep_protocol": artifact.sweep_protocol,
            "ndcg_scope": artifact.ndcg_scope,
            "result_dir": str(artifact.result_dir),
            "paths_dir": str(artifact.paths_dir),
        })

        baseline_table = read_overall_table(artifact.result_dir / "baseline_avg.csv")
        validate_alpha_table(artifact.result_dir / "baseline_avg.csv", baseline_table)
        baseline = baseline_table[0.0]
        endpoint_rows.append(endpoint_row(artifact, "Original recommender", "none", 0.0, baseline, baseline))

        for exp_metric in EXP_METRICS:
            opt_name = f"{exp_metric}opt"
            path = artifact.result_dir / f"{opt_name}_moving_alpha_avg.csv"
            sweep = read_overall_table(path)
            validate_alpha_table(path, sweep)

            endpoint_rows.append(
                endpoint_row(
                    artifact,
                    "Recommender + proposed explanation/path module",
                    exp_metric,
                    1.0,
                    sweep[1.0],
                    baseline,
                )
            )

            best: Optional[dict] = None
            for alpha in EXPECTED_ALPHAS:
                metrics = sweep[alpha]
                ndcg_retention = pct(metrics["ndcg"], baseline["ndcg"])
                exp_gain = pct_change(metrics[exp_metric], baseline[exp_metric])
                curve_row = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": alpha,
                    "ndcg_retention_pct": ndcg_retention,
                    "optimized_metric_gain_pct": exp_gain,
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    curve_row[metric] = metrics[metric]
                    curve_row[f"{metric}_delta_pct"] = pct_change(metrics[metric], baseline[metric])
                curve_rows.append(curve_row)

                candidate = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": alpha,
                    "constraint": "max explanation gain with NDCG retention >= 95%",
                    "ndcg_retention_pct": ndcg_retention,
                    "optimized_metric_gain_pct": exp_gain,
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    candidate[metric] = metrics[metric]
                    candidate[f"{metric}_delta_pct"] = pct_change(metrics[metric], baseline[metric])
                if ndcg_retention >= 95.0:
                    if best is None or (
                        candidate["optimized_metric_gain_pct"],
                        candidate["alpha"],
                    ) > (
                        best["optimized_metric_gain_pct"],
                        best["alpha"],
                    ):
                        best = candidate

            if best is None:
                endpoint = sweep[1.0]
                best = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": 1.0,
                    "constraint": "no alpha retained >=95% NDCG; reporting alpha=1 endpoint",
                    "ndcg_retention_pct": pct(endpoint["ndcg"], baseline["ndcg"]),
                    "optimized_metric_gain_pct": pct_change(endpoint[exp_metric], baseline[exp_metric]),
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    best[metric] = endpoint[metric]
                    best[f"{metric}_delta_pct"] = pct_change(endpoint[metric], baseline[metric])
            tradeoff_rows.append(best)

    return endpoint_rows, curve_rows, tradeoff_rows, provenance_rows


def metric_at(rows: Sequence[dict], dataset: str, model: str, exp_metric: str) -> List[dict]:
    return [
        row for row in rows
        if row["dataset"] == dataset and row["model"] == model and row["optimized_metric"] == exp_metric
    ]


def nice_num(value: float) -> str:
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def scale(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if src_max == src_min:
        return (dst_min + dst_max) / 2.0
    return dst_min + (value - src_min) / (src_max - src_min) * (dst_max - dst_min)


def svg_polyline(points: Sequence[Tuple[float, float]], color: str) -> str:
    data = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{data}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'


def render_tradeoff_svg(curve_rows: Sequence[dict], dataset_label: str, out_path: Path) -> None:
    colors = {"PGPR": "#1565C0", "UCPR": "#C62828"}
    width = 1180
    height = 480
    margin_left = 72
    panel_gap = 48
    panel_width = (width - margin_left - 42 - 2 * panel_gap) / 3
    panel_height = 285
    panel_top = 96
    panel_bottom = panel_top + panel_height
    title = f"{dataset_label}: Performance-explainability tradeoff"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#212121">{html.escape(title)}</text>',
        '<text x="32" y="60" font-family="Arial, sans-serif" font-size="13" fill="#555">Y axis: within-sweep NDCG retention vs Original. X axis: optimized explanation gain. Markers show alpha=0 and alpha=1.</text>',
    ]
    if dataset_label == "LastFM":
        parts.append('<text x="32" y="76" font-family="Arial, sans-serif" font-size="12" fill="#777">LastFM uses sweep-internal legacy NDCG for retention only; strict main-experiment accuracy NDCG is reported separately in provenance.</text>')

    for idx, exp_metric in enumerate(EXP_METRICS):
        panel_left = margin_left + idx * (panel_width + panel_gap)
        panel_right = panel_left + panel_width
        panel_rows = [row for row in curve_rows if row["dataset"] == dataset_label and row["optimized_metric"] == exp_metric]
        x_values = [float(row["optimized_metric_gain_pct"]) for row in panel_rows]
        y_values = [float(row["ndcg_retention_pct"]) for row in panel_rows]
        x_min = min([0.0] + x_values)
        x_max = max([1.0] + x_values)
        y_min = min([95.0] + y_values)
        y_max = max([101.0] + y_values)
        x_pad = max(1.0, (x_max - x_min) * 0.08)
        y_pad = max(0.5, (y_max - y_min) * 0.08)
        x_min -= x_pad
        x_max += x_pad
        y_min -= y_pad
        y_max += y_pad

        parts.extend([
            f'<rect x="{panel_left:.2f}" y="{panel_top}" width="{panel_width:.2f}" height="{panel_height}" fill="#fafafa" stroke="#dddddd"/>',
            f'<text x="{(panel_left + panel_right) / 2:.2f}" y="{panel_top - 18}" font-family="Arial, sans-serif" font-size="16" font-weight="700" text-anchor="middle" fill="#212121">{exp_metric}</text>',
        ])
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = panel_left + frac * panel_width
            y = panel_top + frac * panel_height
            parts.append(f'<line x1="{x:.2f}" y1="{panel_top}" x2="{x:.2f}" y2="{panel_bottom}" stroke="#e6e6e6" stroke-width="1"/>')
            parts.append(f'<line x1="{panel_left:.2f}" y1="{y:.2f}" x2="{panel_right:.2f}" y2="{y:.2f}" stroke="#e6e6e6" stroke-width="1"/>')
        y95 = scale(95.0, y_min, y_max, panel_bottom, panel_top)
        parts.append(f'<line x1="{panel_left:.2f}" y1="{y95:.2f}" x2="{panel_right:.2f}" y2="{y95:.2f}" stroke="#777" stroke-width="1.2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{panel_right - 4:.2f}" y="{y95 - 5:.2f}" font-family="Arial, sans-serif" font-size="11" text-anchor="end" fill="#555">95%</text>')

        for model in ("PGPR", "UCPR"):
            rows = sorted(
                [row for row in panel_rows if row["model"] == model],
                key=lambda row: float(row["alpha"]),
            )
            points = [
                (
                    scale(float(row["optimized_metric_gain_pct"]), x_min, x_max, panel_left, panel_right),
                    scale(float(row["ndcg_retention_pct"]), y_min, y_max, panel_bottom, panel_top),
                )
                for row in rows
            ]
            if not points:
                continue
            color = colors[model]
            parts.append(svg_polyline(points, color))
            x0, y0 = points[0]
            x1, y1 = points[-1]
            parts.append(f'<circle cx="{x0:.2f}" cy="{y0:.2f}" r="4.6" fill="{color}" stroke="#fff" stroke-width="1.4"/>')
            parts.append(f'<rect x="{x1 - 4.8:.2f}" y="{y1 - 4.8:.2f}" width="9.6" height="9.6" fill="{color}" stroke="#fff" stroke-width="1.4"/>')

        parts.extend([
            f'<text x="{panel_left:.2f}" y="{panel_bottom + 28}" font-family="Arial, sans-serif" font-size="12" fill="#444">{nice_num(x_min)}%</text>',
            f'<text x="{panel_right:.2f}" y="{panel_bottom + 28}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(x_max)}%</text>',
            f'<text x="{(panel_left + panel_right) / 2:.2f}" y="{panel_bottom + 44}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#444">{exp_metric} gain (%)</text>',
            f'<text x="{panel_left - 10:.2f}" y="{panel_bottom:.2f}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(y_min)}%</text>',
            f'<text x="{panel_left - 10:.2f}" y="{panel_top + 4:.2f}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(y_max)}%</text>',
        ])
        if idx == 0:
            parts.append(f'<text x="22" y="{(panel_top + panel_bottom) / 2:.2f}" font-family="Arial, sans-serif" font-size="13" text-anchor="middle" fill="#444" transform="rotate(-90 22 {(panel_top + panel_bottom) / 2:.2f})">NDCG retention (%)</text>')

    legend_y = height - 28
    legend_x = 430
    for offset, model in enumerate(("PGPR", "UCPR")):
        x = legend_x + offset * 125
        color = colors[model]
        parts.append(f'<line x1="{x}" y1="{legend_y}" x2="{x + 26}" y2="{legend_y}" stroke="{color}" stroke-width="2.6"/>')
        parts.append(f'<circle cx="{x + 13}" cy="{legend_y}" r="4" fill="{color}" stroke="#fff" stroke-width="1"/>')
        parts.append(f'<text x="{x + 34}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">{model}</text>')
    parts.append(f'<circle cx="{legend_x + 265}" cy="{legend_y}" r="4.6" fill="#555" stroke="#fff" stroke-width="1"/>')
    parts.append(f'<text x="{legend_x + 276}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">alpha=0</text>')
    parts.append(f'<rect x="{legend_x + 352}" y="{legend_y - 4.8}" width="9.6" height="9.6" fill="#555" stroke="#fff" stroke-width="1"/>')
    parts.append(f'<text x="{legend_x + 367}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">alpha=1</text>')
    parts.append("</svg>")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts) + "\n")


def path_type(path: str) -> str:
    tokens = path.split()
    if len(tokens) < 3:
        return "unknown"
    return tokens[-3]


def baseline_topk(paths_dir: Path) -> Dict[int, List[int]]:
    topk: Dict[int, List[int]] = {}
    with (paths_dir / "uid_topk.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            values = [int(value) for value in row["top10"].split() if value]
            topk[int(row["uid"])] = values
    return topk


def baseline_explanations(paths_dir: Path) -> Dict[int, Dict[int, str]]:
    explanations: Dict[int, Dict[int, str]] = {}
    with (paths_dir / "uid_pid_explanation.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            uid = int(row["uid"])
            pid = int(row["pid"])
            explanations.setdefault(uid, {})[pid] = row["path"]
    return explanations


def select_etd_candidates(candidates: Sequence[dict], limit: int = 10) -> List[dict]:
    bins: Dict[str, List[dict]] = {}
    for candidate in candidates:
        bins.setdefault(candidate["path_type"], []).append(candidate)
    for path_list in bins.values():
        path_list.sort(key=lambda item: item["path_score"], reverse=True)

    selected: List[dict] = []
    selected_pids = set()
    seen_types = set()
    while len(selected) < limit and bins:
        best_type = ""
        best_score = -float("inf")
        for current_type, path_list in list(bins.items()):
            while path_list and path_list[0]["pid"] in selected_pids:
                path_list.pop(0)
            if not path_list:
                bins.pop(current_type, None)
                continue
            candidate = path_list[0]
            bonus = 1.0 if current_type not in seen_types else 0.0
            score = candidate["path_score"] + bonus
            if score > best_score:
                best_score = score
                best_type = current_type
        if not best_type:
            break
        chosen = bins[best_type].pop(0)
        selected.append(chosen)
        selected_pids.add(chosen["pid"])
        seen_types.add(best_type)
        if not bins.get(best_type):
            bins.pop(best_type, None)

    for candidate in sorted(candidates, key=lambda item: item["path_score"], reverse=True):
        if len(selected) >= limit:
            break
        if candidate["pid"] in selected_pids:
            continue
        selected.append(candidate)
        selected_pids.add(candidate["pid"])

    return sorted(selected, key=lambda item: item["path_score"], reverse=True)


def compact_items(items: Sequence[dict], limit: int = 10) -> List[dict]:
    compact = []
    for rank, item in enumerate(items[:limit], start=1):
        compact.append({
            "rank": rank,
            "pid": item["pid"],
            "path_type": item["path_type"],
            "path_score": item.get("path_score"),
            "path": item["path"],
        })
    return compact


def build_case_for_artifact(artifact: Artifact, max_completed_users: int) -> dict:
    topk = baseline_topk(artifact.paths_dir)
    explanations = baseline_explanations(artifact.paths_dir)
    pred_path = artifact.paths_dir / "pred_paths.csv"
    best_case: Optional[dict] = None

    def evaluate(uid: int, candidates: List[dict]) -> Optional[dict]:
        if uid not in topk or uid not in explanations:
            return None
        original_items = []
        for pid in topk[uid][:10]:
            path = explanations[uid].get(pid)
            if path is None:
                continue
            original_items.append({
                "pid": pid,
                "path_type": path_type(path),
                "path_score": None,
                "path": path,
            })
        if len(original_items) < 5:
            return None

        module_items = select_etd_candidates(candidates)
        if len(module_items) < 5:
            return None
        original_types = {item["path_type"] for item in original_items}
        module_types = {item["path_type"] for item in module_items}
        original_pids = [item["pid"] for item in original_items]
        module_pids = [item["pid"] for item in module_items]
        gain = len(module_types) - len(original_types)
        changed = sum(1 for left, right in zip(original_pids, module_pids) if left != right)
        if len(module_pids) > len(original_pids):
            changed += len(module_pids) - len(original_pids)
        return {
            "dataset": artifact.dataset_label,
            "model": artifact.model,
            "role": artifact.role,
            "user_id": uid,
            "case_type": "qualitative explanation case",
            "quantitative_use": "illustration only; not a metric proof and not a full alpha-sweep reproduction",
            "module": "ETD path module at alpha=1",
            "original_unique_path_types": len(original_types),
            "module_unique_path_types": len(module_types),
            "unique_path_type_gain": gain,
            "changed_top10_positions": changed,
            "original_top10": compact_items(original_items),
            "module_top10": compact_items(module_items),
        }

    current_uid: Optional[int] = None
    candidates: List[dict] = []
    completed = 0
    with pred_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            uid = int(row["uid"])
            if current_uid is None:
                current_uid = uid
            if uid != current_uid:
                case = evaluate(current_uid, candidates)
                if case is not None:
                    if best_case is None or (
                        case["unique_path_type_gain"],
                        case["changed_top10_positions"],
                    ) > (
                        best_case["unique_path_type_gain"],
                        best_case["changed_top10_positions"],
                    ):
                        best_case = case
                    if case["unique_path_type_gain"] > 0 and case["changed_top10_positions"] > 0:
                        return case
                completed += 1
                if completed >= max_completed_users:
                    break
                current_uid = uid
                candidates = []
            candidates.append({
                "pid": int(row["pid"]),
                "path_score": float(row["path_score"]),
                "path_prob": float(row["path_prob"]),
                "path": row["path"],
                "path_type": path_type(row["path"]),
            })

    if current_uid is not None and completed < max_completed_users:
        case = evaluate(current_uid, candidates)
        if case is not None and (
            best_case is None or (
                case["unique_path_type_gain"],
                case["changed_top10_positions"],
            ) > (
                best_case["unique_path_type_gain"],
                best_case["changed_top10_positions"],
            )
        ):
            best_case = case

    if best_case is None:
        raise ValueError(f"No usable explanation case found for {artifact.dataset_label}/{artifact.model}")
    return best_case


def write_cases(cases: Sequence[dict], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# PGPR/UCPR Path-Module Qualitative Explanation Cases",
        "",
        "Cases compare the frozen Original recommender top-10 against a deterministic ETD path-module reconstruction at alpha=1.",
        "",
        "These cases are qualitative illustrations only; they are not a metric proof and are not a full alpha-sweep reproduction.",
        "",
    ]
    for case in cases:
        lines.extend([
            f"## {case['dataset']} / {case['model']} / user {case['user_id']}",
            "",
            f"- Role: {case['role']}",
            f"- Case type: {case['case_type']}",
            f"- Module: {case['module']}",
            f"- Unique path types: {case['original_unique_path_types']} -> {case['module_unique_path_types']}",
            f"- Changed top-10 positions: {case['changed_top10_positions']}",
            "",
            "Original recommender sample:",
            "",
        ])
        for item in case["original_top10"]:
            lines.append(f"- rank {item['rank']}: pid={item['pid']}, type={item['path_type']}, path=`{item['path']}`")
        lines.extend(["", "Path module sample:", ""])
        for item in case["module_top10"]:
            lines.append(
                f"- rank {item['rank']}: pid={item['pid']}, type={item['path_type']}, "
                f"score={fmt_float(item['path_score'], 4)}, path=`{item['path']}`"
            )
        lines.append("")
    md_path.write_text("\n".join(lines) + "\n")


def render_report(
    out_path: Path,
    main_rows: Sequence[dict],
    endpoint_rows: Sequence[dict],
    tradeoff_rows: Sequence[dict],
    provenance_rows: Sequence[dict],
    cases: Sequence[dict],
    figure_paths: Sequence[Path],
) -> None:
    main_md_rows = []
    for row in main_rows:
        selection = "max gain @ >=95% NDCG"
        if str(row.get("selection_rule", "")).startswith("no alpha"):
            selection = "no >=95%; alpha=1 endpoint"
        main_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "target": row["module_target"],
            "alpha": fmt_float(row["selected_alpha"], 2),
            "selection": selection,
            "retention": fmt_pct(row["ndcg_retention_pct"]),
            "gain": fmt_pct(row["explanation_gain_pct"]),
            "scope": row["ndcg_scope"],
        })

    endpoint_md_rows = []
    for row in endpoint_rows:
        endpoint_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "module": row["module"],
            "opt": row["optimized_metric"],
            "alpha": fmt_float(row["alpha"], 2),
            "ndcg": fmt_float(row["ndcg"], 4),
            "hr": fmt_float(row["hr"], 4),
            "precision": fmt_float(row["precision"], 4),
            "recall": fmt_float(row["recall"], 4),
            "LIR": fmt_float(row["LIR"], 4),
            "SEP": fmt_float(row["SEP"], 4),
            "ETD": fmt_float(row["ETD"], 4),
            "ndcg_delta": fmt_pct(row["ndcg_delta_pct"]),
            "opt_delta": "" if row["optimized_metric"] == "none" else fmt_pct(row[f"{row['optimized_metric']}_delta_pct"]),
        })

    tradeoff_md_rows = []
    for row in tradeoff_rows:
        constraint = "max gain @ >=95% NDCG"
        if str(row.get("constraint", "")).startswith("no alpha"):
            constraint = "no >=95%; alpha=1 endpoint"
        tradeoff_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "opt": row["optimized_metric"],
            "alpha": fmt_float(row["alpha"], 2),
            "constraint": constraint,
            "ndcg_ret": fmt_pct(row["ndcg_retention_pct"]),
            "gain": fmt_pct(row["optimized_metric_gain_pct"]),
            "ndcg": fmt_float(row["ndcg"], 4),
            "metric": fmt_float(row[row["optimized_metric"]], 4),
        })

    provenance_md_rows = []
    for row in provenance_rows:
        provenance_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "export": row["export_status"],
            "accuracy": row["accuracy_status"],
            "users": row["canonical_test_users"],
            "topk": row["topk_users"],
            "paths": row["pred_path_rows"],
            "coverage": fmt_float(row["slot_coverage"], 4),
            "strict_ndcg": fmt_float(row["accuracy_ndcg"], 4),
            "scope": row["ndcg_scope"],
        })

    case_md_rows = []
    for case in cases:
        case_md_rows.append({
            "dataset": case["dataset"],
            "model": case["model"],
            "user": case["user_id"],
            "types": f"{case['original_unique_path_types']} -> {case['module_unique_path_types']}",
            "changed": case["changed_top10_positions"],
        })

    lines = [
        "# PGPR/UCPR Path-Module Ablation",
        "",
        "Scope: PGPR is the main model; UCPR is the auxiliary model. Datasets are LastFM and ML-1M only.",
        "",
        "Excluded by design: Amazon-Book classic baseline is not part of this ablation. Amazon-Book remains only an auxiliary large-dataset result from the existing main experiment.",
        "",
        "The ablation is deterministic and read-only with respect to model artifacts: it consumes frozen xrecsys alpha-sweep CSVs, canonical export validation JSON, and accuracy JSON.",
        "",
        "## Main Ablation Table",
        "",
        "Use this table for the main text. It selects the largest explanation gain under a >=95% within-sweep NDCG-retention rule. When no alpha meets that rule, the row is explicitly marked as an endpoint exception.",
        "",
        rows_to_markdown(
            main_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("target", "Module target"),
                ("alpha", "Selected alpha"),
                ("selection", "Selection"),
                ("retention", "NDCG retention"),
                ("gain", "Explanation gain"),
                ("scope", "NDCG scope"),
            ],
        ),
        "",
        "## Metric Scope",
        "",
        "LastFM alpha sweeps use sweep-internal legacy NDCG. In this report, LastFM NDCG is used only for within-sweep retention and should not be mixed with the strict main-experiment accuracy NDCG. ML-1M sweeps use the canonical-all-users sweep protocol.",
        "",
        "Strict accuracy provenance remains available below to connect these ablations to the validated main artifacts.",
        "",
        "## Tradeoff Summary",
        "",
        "This is the expanded version of the main table with selected sweep NDCG and optimized metric values.",
        "",
        rows_to_markdown(
            tradeoff_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("opt", "Opt"),
                ("alpha", "Alpha"),
                ("constraint", "Selection"),
                ("ndcg_ret", "NDCG retention"),
                ("gain", "Opt gain"),
                ("ndcg", "Sweep NDCG"),
                ("metric", "Opt value"),
            ],
        ),
        "",
        "## Figures",
        "",
    ]
    for figure in figure_paths:
        lines.append(f"- {figure}")
    lines.extend([
        "",
        "## Provenance",
        "",
        rows_to_markdown(
            provenance_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("role", "Role"),
                ("export", "Export"),
                ("accuracy", "Accuracy"),
                ("users", "Canonical users"),
                ("topk", "Top-k users"),
                ("paths", "Pred path rows"),
                ("coverage", "Slot coverage"),
                ("strict_ndcg", "Strict accuracy NDCG"),
                ("scope", "Sweep NDCG scope"),
            ],
        ),
        "",
        "## Qualitative Explanation Cases",
        "",
        "These cases are qualitative illustrations only; they are not quantitative evidence and are not a full alpha-sweep reproduction.",
        "",
        rows_to_markdown(
            case_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("user", "User"),
                ("types", "Unique path types"),
                ("changed", "Changed top-10 positions"),
            ],
        ),
        "",
        "Detailed cases are in `reports/cases/ablation/pgpr_ucpr_path_module_cases.md` and the companion JSON file.",
        "",
        "## Appendix: Alpha=1 Endpoint Stress Test",
        "",
        "Do not use this as the main ablation table. These rows show the extreme alpha=1 setting; large recommendation drops are expected for some targets and help characterize the performance-explainability boundary.",
        "",
        rows_to_markdown(
            endpoint_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("role", "Role"),
                ("module", "Condition"),
                ("opt", "Opt"),
                ("alpha", "Alpha"),
                ("ndcg", "NDCG"),
                ("hr", "HR"),
                ("precision", "Precision"),
                ("recall", "Recall"),
                ("LIR", "LIR"),
                ("SEP", "SEP"),
                ("ETD", "ETD"),
                ("ndcg_delta", "NDCG delta"),
                ("opt_delta", "Opt metric delta"),
            ],
        ),
        "",
    ])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PGPR/UCPR path-module ablation artifacts")
    parser.add_argument("--out-tables", default="reports/tables/ablation/pgpr_ucpr_path_module")
    parser.add_argument("--out-figures", default="reports/figures/ablation/pgpr_ucpr_path_module")
    parser.add_argument("--out-cases", default="reports/cases/ablation")
    parser.add_argument("--out-summary", default="reports/summaries/pgpr_ucpr_path_module_ablation.md")
    parser.add_argument("--case-user-limit", type=int, default=250)
    args = parser.parse_args()

    out_tables = Path(args.out_tables)
    out_figures = Path(args.out_figures)
    out_cases = Path(args.out_cases)
    out_summary = Path(args.out_summary)

    endpoint_rows, curve_rows, tradeoff_rows, provenance_rows = build_ablation_tables(ARTIFACTS)
    main_rows = build_main_ablation_rows(tradeoff_rows)

    main_fields = [
        "dataset", "model", "role", "module_target", "selected_alpha",
        "selection_rule", "ndcg_retention_pct", "explanation_gain_pct",
        "sweep_ndcg", "explanation_metric_value", "ndcg_scope", "recommended_use",
    ]
    endpoint_fields = [
        "dataset", "model", "role", "module", "optimized_metric", "alpha",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "sweep_protocol", "ndcg_scope",
    ]
    curve_fields = [
        "dataset", "model", "role", "optimized_metric", "alpha",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "ndcg_retention_pct", "optimized_metric_gain_pct", "sweep_protocol", "ndcg_scope",
    ]
    tradeoff_fields = [
        "dataset", "model", "role", "optimized_metric", "alpha", "constraint",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "ndcg_retention_pct", "optimized_metric_gain_pct", "sweep_protocol", "ndcg_scope",
    ]
    provenance_fields = [
        "dataset", "model", "role", "export_status", "accuracy_status",
        "canonical_test_users", "topk_users", "candidate_users", "explanations",
        "pred_path_rows", "accuracy_hr", "accuracy_ndcg", "accuracy_precision",
        "accuracy_recall", "slot_coverage", "sweep_protocol", "ndcg_scope", "result_dir", "paths_dir",
    ]

    write_csv(out_tables / "main_ablation_table_95pct_ndcg.csv", main_rows, main_fields)
    write_csv(out_tables / "endpoint_comparison.csv", endpoint_rows, endpoint_fields)
    write_csv(out_tables / "tradeoff_curves_long.csv", curve_rows, curve_fields)
    write_csv(out_tables / "tradeoff_summary_95pct_ndcg.csv", tradeoff_rows, tradeoff_fields)
    write_csv(out_tables / "provenance_validation.csv", provenance_rows, provenance_fields)

    figure_paths = []
    for dataset_label in ("LastFM", "ML-1M"):
        out_path = out_figures / f"{dataset_label.lower().replace('-', '')}_ndcg_tradeoff.svg"
        render_tradeoff_svg(curve_rows, dataset_label, out_path)
        figure_paths.append(out_path)

    cases = [build_case_for_artifact(artifact, args.case_user_limit) for artifact in ARTIFACTS]
    write_cases(
        cases,
        out_cases / "pgpr_ucpr_path_module_cases.json",
        out_cases / "pgpr_ucpr_path_module_cases.md",
    )

    render_report(out_summary, main_rows, endpoint_rows, tradeoff_rows, provenance_rows, cases, figure_paths)

    print("Generated PGPR/UCPR path-module ablation artifacts:")
    for path in [
        out_tables / "endpoint_comparison.csv",
        out_tables / "main_ablation_table_95pct_ndcg.csv",
        out_tables / "tradeoff_curves_long.csv",
        out_tables / "tradeoff_summary_95pct_ndcg.csv",
        out_tables / "provenance_validation.csv",
        *figure_paths,
        out_cases / "pgpr_ucpr_path_module_cases.json",
        out_cases / "pgpr_ucpr_path_module_cases.md",
        out_summary,
    ]:
        print(f"  {path}")


if __name__ == "__main__":
    main()
