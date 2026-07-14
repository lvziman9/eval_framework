from __future__ import annotations

from pathlib import Path
import shutil

import cairosvg
from graphviz import Digraph
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


ROOT = Path("/home/lvzi/eval_framework")
SOURCE_PACKAGE = ROOT / "paper/full_dissertation_draft/figure_table_final_production_v1"
OUT = ROOT / "paper/full_dissertation_draft/figure_table_final_production_v2"
SVG_DIR = OUT / "figures/svg"
PNG_DIR = OUT / "figures/png"

MODELS = ["PGPR", "UCPR", "CAFE", "TPRec", "KGGLM", "PEARLM"]
DATASETS = ["LastFM", "ML-1M"]
OBJECTIVES = ["LIR", "SEP", "ETD"]

# Okabe-Ito palette with redundant marker and line-style encoding.
MODEL_COLORS = {
    "PGPR": "#0072B2",
    "UCPR": "#D55E00",
    "CAFE": "#009E73",
    "TPRec": "#CC79A7",
    "KGGLM": "#222222",
    "PEARLM": "#E69F00",
}
MODEL_MARKERS = {
    "PGPR": "o",
    "UCPR": "s",
    "CAFE": "^",
    "TPRec": "D",
    "KGGLM": "P",
    "PEARLM": "X",
}
MODEL_LINESTYLES = {
    "PGPR": "-",
    "UCPR": "--",
    "CAFE": "-.",
    "TPRec": ":",
    "KGGLM": (0, (5, 1)),
    "PEARLM": (0, (3, 1, 1, 1)),
}
OBJECTIVE_COLORS = {
    "LIR": "#0072B2",
    "SEP": "#D55E00",
    "ETD": "#009E73",
}

INK = "#202124"
MID = "#5F6368"
GRID = "#DADCE0"
BLUE_FILL = "#EAF3F8"
AMBER_FILL = "#FFF4DF"
GREEN_FILL = "#EAF4EF"
GRAY_FILL = "#F5F6F7"


def configure_matplotlib() -> None:
    plt.style.use("default")
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "axes.titlesize": 8.5,
            "axes.titleweight": "bold",
            "axes.edgecolor": INK,
            "axes.linewidth": 0.8,
            "axes.facecolor": "white",
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "xtick.color": INK,
            "ytick.color": INK,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.7,
            "ytick.major.width": 0.7,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "legend.fontsize": 7.2,
            "legend.frameon": False,
            "lines.linewidth": 1.35,
            "lines.markersize": 4.0,
            "savefig.facecolor": "white",
            "savefig.edgecolor": "white",
            "savefig.transparent": False,
            "svg.fonttype": "none",
            "figure.dpi": 120,
        }
    )


def prepare_output() -> None:
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    source = SOURCE_PACKAGE / "FULL_DISSERTATION_FIGURE_TABLE_READY_V2.md"
    target = OUT / "FULL_DISSERTATION_FIGURE_TABLE_READY_V3.md"
    shutil.copyfile(source, target)


def save_mpl(fig: mpl.figure.Figure, basename: str) -> None:
    svg_path = SVG_DIR / f"{basename}.svg"
    png_path = PNG_DIR / f"{basename}.png"
    fig.savefig(svg_path, format="svg", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png_path, format="png", dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def style_axis(ax: mpl.axes.Axes, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis=grid_axis, color=GRID, linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)


def panel_title(ax: mpl.axes.Axes, letter: str, dataset: str) -> None:
    ax.set_title(f"({letter}) {dataset}", loc="left", pad=7)


def padded_limits(values: np.ndarray, lower_zero: bool = False, fraction: float = 0.06) -> tuple[float, float]:
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    span = high - low
    if span == 0:
        span = max(abs(high), 1.0) * 0.1
    lo = low - fraction * span
    hi = high + fraction * span
    if lower_zero and low >= 0:
        lo = max(0.0, lo)
    return lo, hi


def status_matrix() -> pd.DataFrame:
    return pd.read_csv(ROOT / "reports/tables/canonical_native_path_status_matrix.csv")


def sweep_path(dataset: str, objective: str) -> Path:
    if dataset == "LastFM":
        folder = "canonical_lastfm_native_paths_v4_six_model"
        filename = f"tradeoff_lastfm_{objective}_ndcg_models.csv"
    else:
        folder = "canonical_ml1m_native_paths_v2"
        filename = f"tradeoff_ml1m_{objective}_ndcg_models.csv"
    return ROOT / "reports/figures/tradeoff" / folder / filename


def graph_defaults(graph: Digraph, rankdir: str = "TB") -> None:
    graph.attr(
        rankdir=rankdir,
        bgcolor="white",
        fontname="DejaVu Sans",
        fontsize="9",
        color=INK,
        pad="0.08",
        nodesep="0.26",
        ranksep="0.38",
        splines="polyline",
        outputorder="edgesfirst",
    )
    graph.attr(
        "node",
        shape="box",
        style="filled",
        fillcolor="white",
        color=INK,
        fontcolor=INK,
        fontname="DejaVu Sans",
        fontsize="8.5",
        penwidth="1.0",
        margin="0.12,0.08",
    )
    graph.attr(
        "edge",
        color=INK,
        fontcolor=INK,
        fontname="DejaVu Sans",
        fontsize="7.5",
        penwidth="1.0",
        arrowsize="0.65",
    )


def render_graph(graph: Digraph, basename: str, output_width: int = 3600) -> None:
    graph.format = "svg"
    rendered = Path(graph.render(filename=basename, directory=SVG_DIR, cleanup=True))
    expected = SVG_DIR / f"{basename}.svg"
    if rendered != expected:
        rendered.replace(expected)
    cairosvg.svg2png(
        url=str(expected),
        write_to=str(PNG_DIR / f"{basename}.png"),
        output_width=output_width,
        background_color="white",
    )


def figure_3_1() -> None:
    g = Digraph("framework_overview")
    graph_defaults(g, "TB")
    g.attr(ratio="compress")

    with g.subgraph(name="cluster_pipeline") as c:
        c.attr(label="Canonical evaluation pipeline", color=GRID, penwidth="0.8", style="rounded")
        c.node("canonical", "Canonical dataset truth\nusers, items, splits, labels", fillcolor=BLUE_FILL)
        c.node("views", "Model-specific execution views")
        c.node("execution", "Native model execution\nor imported outputs")
        c.node("contract", "Native-path export contract", fillcolor=BLUE_FILL)
        with c.subgraph() as rank:
            rank.attr(rank="same")
            rank.node("canonical")
            rank.node("views")
            rank.node("execution")
            rank.node("contract")
        c.edge("canonical", "views")
        c.edge("views", "execution")
        c.edge("execution", "contract")

    with g.subgraph() as files:
        files.attr(rank="same")
        files.node("topk", "uid_topk.csv", fillcolor=GRAY_FILL)
        files.node("paths", "pred_paths.csv", fillcolor=GRAY_FILL)
        files.node("explanations", "uid_pid_explanation.csv", fillcolor=GRAY_FILL)
    g.edge("contract", "topk")
    g.edge("contract", "paths")
    g.edge("contract", "explanations")

    g.node("validation", "Validation gate", shape="diamond", fillcolor=BLUE_FILL)
    g.edge("topk", "validation")
    g.edge("paths", "validation")
    g.edge("explanations", "validation")

    with g.subgraph() as decisions:
        decisions.attr(rank="same")
        decisions.node("reportable", "PASS\nReportable model-dataset row", fillcolor=GREEN_FILL, color="#2F6F55")
        decisions.node("boundary", "BLOCKED / PARTIAL\nBoundary record", fillcolor=AMBER_FILL, color="#9A6500")
    g.edge("validation", "reportable", label="PASS", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("validation", "boundary", label="BLOCKED / PARTIAL", color="#9A6500", fontcolor="#9A6500")

    with g.subgraph() as outputs:
        outputs.attr(rank="same")
        outputs.node("strict", "Strict accuracy\nHR@10, NDCG@10,\nPrecision@10, Recall@10")
        outputs.node("endpoints", "Explanation endpoints\nLIR, SEP, ETD")
        outputs.node("sweeps", "Objective-specific\nalpha-sweep trajectories")
        outputs.node("ablation", "PGPR/UCPR\nablation evidence")
        outputs.node("chapter5", "Chapter 5\nboundary analysis", fillcolor=AMBER_FILL, color="#9A6500")
    for output in ["strict", "endpoints", "sweeps", "ablation"]:
        g.edge("reportable", output)
    g.edge("boundary", "chapter5", color="#9A6500")
    render_graph(g, "figure_3_1_framework_overview_final")


def figure_3_2() -> None:
    g = Digraph("evidence_streams")
    graph_defaults(g, "TB")
    g.attr(newrank="true", ranksep="0.32")

    with g.subgraph(name="cluster_strict") as c:
        c.attr(label="Strict accuracy stream", color="#7AA7BF", penwidth="0.9", style="rounded")
        c.node("s1", "Validated baseline\nrecommendation output", fillcolor=BLUE_FILL)
        c.node("s2", "HR@10, NDCG@10,\nPrecision@10, Recall@10")
        c.node("s3", "Chapter 4\nstrict comparison", fillcolor=BLUE_FILL)
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("s1")
            row.node("s2")
            row.node("s3")
        c.edge("s1", "s2")
        c.edge("s2", "s3")

    with g.subgraph(name="cluster_sweep") as c:
        c.attr(label="Objective-specific alpha-sweep stream", color="#7AA7BF", penwidth="0.9", style="rounded")
        c.node("a1", "alpha=0\nranking-oriented baseline")
        c.node("a2", "alpha in [0, 1]\nobjective-specific re-ranking")
        c.node("a3", "LIR, SEP, or ETD\npaired with sweep NDCG")
        c.node("a4", "Chapter 4\ntrade-off trajectories", fillcolor=BLUE_FILL)
        with c.subgraph() as row:
            row.attr(rank="same")
            for node in ["a1", "a2", "a3", "a4"]:
                row.node(node)
        c.edge("a1", "a2")
        c.edge("a2", "a3")
        c.edge("a3", "a4")

    with g.subgraph(name="cluster_ablation") as c:
        c.attr(label="Registered ablation stream", color="#B08A4D", penwidth="0.9", style="rounded")
        c.node("b1", "Frozen original\ntop-k item set", fillcolor=AMBER_FILL)
        c.node("b2", "PGPR/UCPR only\nobjective-specific control")
        c.node("b3", "Baseline preservation\nand NDCG retention", fillcolor=AMBER_FILL)
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("b1")
            row.node("b2")
            row.node("b3")
        c.edge("b1", "b2")
        c.edge("b2", "b3")

    g.edge("s1", "a1", style="invis", weight="20")
    g.edge("a1", "b1", style="invis", weight="20")
    g.node("separation", "Sweep NDCG is not strict NDCG@10; ablation remains a separate evidence stream.", shape="note", fillcolor=GRAY_FILL, color=MID)
    g.edge("b2", "separation", style="dashed", color=MID, arrowhead="none")
    render_graph(g, "figure_3_2_alpha_sweep_design_final")


def figure_3_3() -> None:
    g = Digraph("validation_gate")
    graph_defaults(g, "TB")
    g.attr(ranksep="0.38")
    g.node("input", "Export package for model m on dataset d", fillcolor=BLUE_FILL)
    g.node(
        "integrity",
        "Export integrity gate\ncoverage - duplicates - leakage - canonical IDs",
        shape="diamond",
        fillcolor="white",
        width="3.5",
    )
    g.node(
        "fidelity",
        "Path fidelity gate\nendpoints - top-k alignment - candidate consistency",
        shape="diamond",
        fillcolor="white",
        width="3.8",
    )
    g.node(
        "sanity",
        "Metric sanity gate\nfinite values - valid score ranges",
        shape="diamond",
        fillcolor="white",
        width="3.2",
    )
    g.node("pass", "PASS\nReportable evidence row", fillcolor=GREEN_FILL, color="#2F6F55")
    g.node("block", "BLOCKED or PARTIAL\nEvidence record, not a performance result", fillcolor=AMBER_FILL, color="#9A6500")
    with g.subgraph() as outcomes:
        outcomes.attr(rank="same")
        outcomes.node("pass")
        outcomes.node("block")
    g.edge("input", "integrity")
    g.edge("integrity", "fidelity", label="PASS", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("fidelity", "sanity", label="PASS", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("sanity", "pass", label="PASS", color="#2F6F55", fontcolor="#2F6F55")
    for node in ["integrity", "fidelity", "sanity"]:
        g.edge(node, "block", label="FAIL", color="#9A6500", fontcolor="#9A6500")
    render_graph(g, "figure_3_3_validation_gate_flow_final", output_width=3200)


def figure_4_1() -> None:
    frame = status_matrix()
    frame = frame[frame["dataset"].isin(DATASETS)].copy()
    frame["model"] = pd.Categorical(frame["model"], MODELS, ordered=True)
    frame = frame.sort_values(["dataset", "model"])

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.05), sharey=True)
    ymax = float(frame["ndcg_at_10"].max()) * 1.18
    x = np.arange(len(MODELS))
    for index, (ax, dataset) in enumerate(zip(axes, DATASETS)):
        data = frame[frame["dataset"] == dataset].set_index("model").reindex(MODELS)
        values = data["ndcg_at_10"].to_numpy(float)
        bars = ax.bar(
            x,
            values,
            width=0.68,
            color=[MODEL_COLORS[model] for model in MODELS],
            edgecolor=INK,
            linewidth=0.55,
        )
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + ymax * 0.018,
                f"{value:.4f}",
                ha="center",
                va="bottom",
                fontsize=6.4,
            )
        ax.set_xticks(x, MODELS)
        ax.set_ylim(0, ymax)
        ax.yaxis.set_major_locator(MaxNLocator(5))
        panel_title(ax, "a" if index == 0 else "b", dataset)
        style_axis(ax)
        ax.set_xlabel("Model")
    axes[0].set_ylabel("Strict NDCG@10")
    fig.subplots_adjust(left=0.09, right=0.995, bottom=0.17, top=0.90, wspace=0.16)
    save_mpl(fig, "figure_4_1_strict_ndcg_comparison_final")


def figure_4_2() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 5.15))
    x = np.arange(len(MODELS))
    letters = iter("abcdef")
    endpoint_handles = [
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor="white", markeredgecolor=INK, label="alpha=0"),
        Line2D([0], [0], marker="s", linestyle="none", markerfacecolor="#0072B2", markeredgecolor="#0072B2", label="alpha=1"),
    ]
    for row, dataset in enumerate(DATASETS):
        for column, objective in enumerate(OBJECTIVES):
            ax = axes[row, column]
            data = pd.read_csv(sweep_path(dataset, objective))
            zeros = data[np.isclose(data["alpha"], 0)].set_index("model").reindex(MODELS)[objective].to_numpy(float)
            ones = data[np.isclose(data["alpha"], 1)].set_index("model").reindex(MODELS)[objective].to_numpy(float)
            for xpos, start, end in zip(x, zeros, ones):
                ax.plot([xpos, xpos], [start, end], color="#9AA0A6", linewidth=1.0, zorder=1)
            ax.scatter(x, zeros, s=20, facecolor="white", edgecolor=INK, linewidth=0.9, marker="o", zorder=3)
            ax.scatter(x, ones, s=20, facecolor="#0072B2", edgecolor="#0072B2", linewidth=0.8, marker="s", zorder=3)
            values = np.concatenate([zeros, ones])
            ax.set_ylim(*padded_limits(values, lower_zero=True, fraction=0.09))
            ax.yaxis.set_major_locator(MaxNLocator(4))
            ax.set_xticks(x, MODELS, rotation=25, ha="right")
            ax.set_ylabel(objective)
            panel_title(ax, next(letters), f"{dataset} - {objective}")
            style_axis(ax)
    fig.legend(handles=endpoint_handles, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.995), columnspacing=2.0)
    fig.subplots_adjust(left=0.075, right=0.995, bottom=0.10, top=0.91, wspace=0.30, hspace=0.43)
    save_mpl(fig, "figure_4_2_explanation_endpoint_summary_final")


def tradeoff_figure(objective: str, number: int) -> None:
    frames = {dataset: pd.read_csv(sweep_path(dataset, objective)) for dataset in DATASETS}
    all_y = np.concatenate([frame["ndcg"].to_numpy(float) for frame in frames.values()])
    y_limits = padded_limits(all_y, lower_zero=True, fraction=0.07)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), sharey=True)
    legend_handles = []
    for panel, (ax, dataset) in enumerate(zip(axes, DATASETS)):
        frame = frames[dataset]
        for model in MODELS:
            data = frame[frame["model"] == model].sort_values("alpha")
            marker_indices = sorted(set([0, 5, 10, 15, len(data) - 1]))
            line, = ax.plot(
                data[objective],
                data["ndcg"],
                color=MODEL_COLORS[model],
                linestyle=MODEL_LINESTYLES[model],
                marker=MODEL_MARKERS[model],
                markevery=marker_indices,
                markerfacecolor="white" if model not in {"KGGLM", "PEARLM"} else MODEL_COLORS[model],
                markeredgecolor=MODEL_COLORS[model],
                markeredgewidth=0.8,
                label=model,
            )
            if panel == 0:
                legend_handles.append(line)
        x_values = frame[objective].to_numpy(float)
        ax.set_xlim(*padded_limits(x_values, lower_zero=True, fraction=0.06))
        ax.set_ylim(*y_limits)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.set_xlabel(f"Implemented {objective} score")
        panel_title(ax, "a" if panel == 0 else "b", dataset)
        style_axis(ax)
    axes[0].set_ylabel("Sweep NDCG")
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=6,
        bbox_to_anchor=(0.5, 0.995),
        handlelength=2.0,
        columnspacing=1.15,
    )
    fig.subplots_adjust(left=0.085, right=0.995, bottom=0.17, top=0.84, wspace=0.12)
    save_mpl(fig, f"figure_4_{number}_{objective.lower()}_tradeoff_final")


def figure_5_1() -> None:
    path = ROOT / "reports/tables/ablation/pgpr_ucpr_path_module/tradeoff_curves_long.csv"
    frame = pd.read_csv(path)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35))

    objective_handles = [
        Line2D([0], [0], color=OBJECTIVE_COLORS[objective], linewidth=1.5, label=objective)
        for objective in OBJECTIVES
    ]
    model_handles = [
        Line2D(
            [0],
            [0],
            color=INK,
            linestyle="-" if model == "PGPR" else "--",
            marker="o" if model == "PGPR" else "s",
            markerfacecolor="white",
            markeredgecolor=INK,
            label=model,
        )
        for model in ["PGPR", "UCPR"]
    ]

    for panel, (ax, dataset) in enumerate(zip(axes, DATASETS)):
        subset = frame[frame["dataset"] == dataset]
        for objective in OBJECTIVES:
            for model in ["PGPR", "UCPR"]:
                data = subset[(subset["optimized_metric"] == objective) & (subset["model"] == model)].sort_values("alpha")
                marker_indices = sorted(set([0, 5, 10, 15, len(data) - 1]))
                ax.plot(
                    data["optimized_metric_gain_pct"],
                    data["ndcg_retention_pct"],
                    color=OBJECTIVE_COLORS[objective],
                    linestyle="-" if model == "PGPR" else "--",
                    marker="o" if model == "PGPR" else "s",
                    markevery=marker_indices,
                    markerfacecolor="white",
                    markeredgecolor=OBJECTIVE_COLORS[objective],
                    markeredgewidth=0.8,
                )
        x_values = subset["optimized_metric_gain_pct"].to_numpy(float)
        y_values = subset["ndcg_retention_pct"].to_numpy(float)
        ax.set_xlim(*padded_limits(x_values, lower_zero=False, fraction=0.06))
        low, high = padded_limits(y_values, lower_zero=False, fraction=0.08)
        low = min(low, 94.4)
        ax.set_ylim(low, high)
        ax.axhline(95, color=MID, linewidth=0.9, linestyle=(0, (4, 3)))
        ax.text(0.985, 95, "95% threshold", transform=ax.get_yaxis_transform(), ha="right", va="bottom", color=MID, fontsize=6.8)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.set_xlabel("Optimized explanation gain (%)")
        ax.set_ylabel("NDCG@10 retention (%)")
        panel_title(ax, "a" if panel == 0 else "b", dataset)
        style_axis(ax)
    legend_one = fig.legend(
        handles=objective_handles,
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.34, 0.995),
        title="Objective",
        title_fontsize=7.2,
        columnspacing=1.2,
    )
    fig.add_artist(legend_one)
    fig.legend(
        handles=model_handles,
        loc="upper center",
        ncol=2,
        bbox_to_anchor=(0.77, 0.995),
        title="Model",
        title_fontsize=7.2,
        columnspacing=1.2,
    )
    fig.subplots_adjust(left=0.085, right=0.995, bottom=0.17, top=0.82, wspace=0.22)
    save_mpl(fig, "figure_5_1_pgpr_ucpr_ablation_final")


def figure_5_2() -> None:
    frame = status_matrix()
    datasets = ["LastFM", "ML-1M", "Amazon-Book KGAT"]
    values: list[list[str]] = []
    for dataset in datasets:
        row = []
        subset = frame[frame["dataset"] == dataset].set_index("model")
        for model in MODELS:
            record = subset.loc[model]
            row.append("PASS" if record["export_validation"] == "PASS" else "BLOCKED / N/A")
        values.append(row)

    fig, ax = plt.subplots(figsize=(7.2, 2.45))
    for row, dataset in enumerate(datasets):
        for column, model in enumerate(MODELS):
            status = values[row][column]
            passed = status == "PASS"
            rect = Rectangle(
                (column + 0.03, row + 0.04),
                0.94,
                0.92,
                facecolor=GREEN_FILL if passed else AMBER_FILL,
                edgecolor="#2F6F55" if passed else "#9A6500",
                linewidth=0.85,
                hatch=None if passed else "////",
            )
            ax.add_patch(rect)
            ax.text(
                column + 0.5,
                row + 0.5,
                status,
                ha="center",
                va="center",
                fontsize=7.2 if passed else 6.5,
                fontweight="bold",
                color=INK,
            )
    ax.set_xlim(0, len(MODELS))
    ax.set_ylim(len(datasets), 0)
    ax.set_xticks(np.arange(len(MODELS)) + 0.5, MODELS)
    ax.set_yticks(np.arange(len(datasets)) + 0.5, datasets)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False, left=False, length=0, pad=6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    handles = [
        Patch(facecolor=GREEN_FILL, edgecolor="#2F6F55", label="PASS"),
        Patch(facecolor=AMBER_FILL, edgecolor="#9A6500", hatch="////", label="BLOCKED / N/A"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.01), handlelength=1.8)
    fig.subplots_adjust(left=0.20, right=0.995, bottom=0.20, top=0.80)
    save_mpl(fig, "figure_5_2_experiment_status_matrix_final")


def figure_5_3() -> None:
    g = Digraph("amazon_boundary")
    graph_defaults(g, "TB")
    g.attr(ranksep="0.42")
    g.node("row", "Amazon-Book KGAT model row", fillcolor=BLUE_FILL)
    g.node("export", "Native-path export complete?", shape="diamond", width="2.8")
    g.node("validation", "Validation gates pass?", shape="diamond", width="2.8")
    g.node("sweep", "Complete explanation sweep available?", shape="diamond", width="3.3")
    g.node("blocked", "Boundary case\nBLOCKED / N/A", fillcolor=AMBER_FILL, color="#9A6500")
    g.node("partial", "Partial evidence only\nNo complete sweep protocol", fillcolor=AMBER_FILL, color="#9A6500")
    g.node("eligible", "Eligible for main-style analysis", fillcolor=GREEN_FILL, color="#2F6F55")
    g.node("discussion", "Boundary discussion\nNo blocked-row ranking", fillcolor=GRAY_FILL, color=MID)
    g.edge("row", "export")
    g.edge("export", "validation", label="YES", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("validation", "sweep", label="YES", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("export", "blocked", label="NO", color="#9A6500", fontcolor="#9A6500")
    g.edge("validation", "blocked", label="NO", color="#9A6500", fontcolor="#9A6500")
    g.edge("sweep", "partial", label="NO", color="#9A6500", fontcolor="#9A6500")
    g.edge("sweep", "eligible", label="YES", color="#2F6F55", fontcolor="#2F6F55")
    g.edge("blocked", "discussion")
    g.edge("partial", "discussion")
    render_graph(g, "figure_5_3_amazon_boundary_flow_final", output_width=3200)


def main() -> None:
    configure_matplotlib()
    prepare_output()
    figure_3_1()
    figure_3_2()
    figure_3_3()
    figure_4_1()
    figure_4_2()
    tradeoff_figure("LIR", 3)
    tradeoff_figure("SEP", 4)
    tradeoff_figure("ETD", 5)
    figure_5_1()
    figure_5_2()
    figure_5_3()
    print(f"Generated {len(list(SVG_DIR.glob('*.svg')))} SVG and {len(list(PNG_DIR.glob('*.png')))} PNG figures in {OUT}")


if __name__ == "__main__":
    main()
