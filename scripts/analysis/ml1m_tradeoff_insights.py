#!/usr/bin/env python3
"""Generate ML-1M tradeoff exploration tables and figures.

This script intentionally separates two evidence tracks:

1. legacy_four_model: the completed four-model historical xrecsys comparison
   curves already rendered under reports/figures/tradeoff/canonical_ml1m_native_paths.
2. canonical_language_models: canonical-all-users curves that currently exist
   for PEARLM and KGGLM.

The two tracks should not be merged into one paper table without rerunning all
models under the same protocol.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
LEGACY_DIR = ROOT / "reports" / "figures" / "tradeoff" / "canonical_ml1m_native_paths"
OUT_FIG = ROOT / "reports" / "figures" / "tradeoff" / "ml1m_tradeoff_insights"
OUT_TAB = ROOT / "reports" / "tables" / "tradeoff_insights"

OBJECTIVES = ("LIR", "SEP", "ETD")
REC_METRICS = ("ndcg", "hr", "precision", "recall")

CANONICAL_LM_DIRS = {
    "KGGLM": ROOT
    / "xrecsys"
    / "results"
    / "ml1m"
    / "agent_topk=kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users",
    "PEARLM": ROOT
    / "xrecsys"
    / "results"
    / "ml1m"
    / "agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users",
}

ACCURACY_JSONS = {
    "PGPR": ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion" / "pgpr_ml1m_accuracy.json",
    "UCPR": ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion" / "ucpr_ml1m_accuracy.json",
    "CAFE": ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion" / "cafe_ml1m_accuracy.json",
    "TPRec": ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "tprec_formal"
    / "canonical_ml1m_v1"
    / "accuracy.json",
    "KGGLM": ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "kgglm_formal"
    / "canonical_ml1m_v1"
    / "accuracy.json",
    "PEARLM": ROOT
    / "runs"
    / "debug_compare"
    / "2026-06-20_native_path_expansion"
    / "pearlm_formal_bestval10"
    / "canonical_ml1m_v1"
    / "accuracy.json",
}

MODEL_FAMILY = {
    "PGPR": "RL path search",
    "UCPR": "User-centric RL path search",
    "CAFE": "Coarse-to-fine neural-symbolic",
    "TPRec": "Time-aware RL path search",
    "KGGLM": "Two-stage path language model",
    "PEARLM": "KG-constrained path language model",
}


def ensure_dirs() -> None:
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    OUT_TAB.mkdir(parents=True, exist_ok=True)


def load_legacy_curve(objective: str, rec_metric: str) -> pd.DataFrame:
    path = LEGACY_DIR / f"tradeoff_ml1m_{objective}_{rec_metric}_models.csv"
    df = pd.read_csv(path)
    df["objective"] = objective
    df["rec_metric"] = rec_metric
    df["protocol"] = "legacy_four_model"
    df = df.rename(columns={objective: "explainability", rec_metric: "rec_value"})
    return df[["protocol", "model", "objective", "rec_metric", "alpha", "rec_value", "explainability"]]


def load_legacy_all() -> pd.DataFrame:
    frames = []
    for objective in OBJECTIVES:
        for metric in REC_METRICS:
            frames.append(load_legacy_curve(objective, metric))
    return pd.concat(frames, ignore_index=True)


def _endpoint_summary(curves: pd.DataFrame, rec_metric: str = "ndcg") -> pd.DataFrame:
    rows = []
    subset = curves[curves["rec_metric"] == rec_metric]
    for (protocol, model, objective), g in subset.groupby(["protocol", "model", "objective"]):
        g = g.sort_values("alpha").copy()
        base = g[g["alpha"].round(10) == 0.0].iloc[0]
        end = g[g["alpha"].round(10) == 1.0].iloc[-1]
        best_rec = g.loc[g["rec_value"].idxmax()]
        max_exp = g.loc[g["explainability"].idxmax()]
        base_rec = float(base["rec_value"])
        base_exp = float(base["explainability"])
        end_rec = float(end["rec_value"])
        end_exp = float(end["explainability"])
        rows.append(
            {
                "protocol": protocol,
                "model": model,
                "family": MODEL_FAMILY.get(model, ""),
                "objective": objective,
                "rec_metric": rec_metric,
                "alpha0_rec": base_rec,
                "alpha1_rec": end_rec,
                "delta_rec": end_rec - base_rec,
                "relative_rec_change": (end_rec / base_rec - 1.0) if base_rec else float("nan"),
                "alpha0_explainability": base_exp,
                "alpha1_explainability": end_exp,
                "delta_explainability": end_exp - base_exp,
                "relative_explainability_change": (end_exp / base_exp - 1.0) if base_exp else float("nan"),
                "best_rec_alpha": float(best_rec["alpha"]),
                "best_rec_value": float(best_rec["rec_value"]),
                "best_exp_alpha": float(max_exp["alpha"]),
                "best_exp_value": float(max_exp["explainability"]),
                "explanation_monotonic_increases": int((g["explainability"].diff().fillna(0) >= -1e-12).all()),
                "rec_monotonic_nonincreasing": int((g["rec_value"].diff().fillna(0) <= 1e-12).all()),
            }
        )
    return pd.DataFrame(rows)


def _threshold_summary(curves: pd.DataFrame, rec_metric: str = "ndcg") -> pd.DataFrame:
    rows = []
    subset = curves[curves["rec_metric"] == rec_metric]
    for (protocol, model, objective), g in subset.groupby(["protocol", "model", "objective"]):
        g = g.sort_values("alpha").copy()
        base = g[g["alpha"].round(10) == 0.0].iloc[0]
        base_rec = float(base["rec_value"])
        base_exp = float(base["explainability"])
        for retention in (0.99, 0.95, 0.90):
            feasible = g[g["rec_value"] >= base_rec * retention]
            if feasible.empty:
                best = None
            else:
                best = feasible.loc[feasible["explainability"].idxmax()]
            rows.append(
                {
                    "protocol": protocol,
                    "model": model,
                    "family": MODEL_FAMILY.get(model, ""),
                    "objective": objective,
                    "rec_metric": rec_metric,
                    "retention_threshold": retention,
                    "base_rec": base_rec,
                    "base_explainability": base_exp,
                    "best_alpha": float(best["alpha"]) if best is not None else float("nan"),
                    "best_rec": float(best["rec_value"]) if best is not None else float("nan"),
                    "best_explainability": float(best["explainability"]) if best is not None else float("nan"),
                    "gain": (float(best["explainability"]) - base_exp) if best is not None else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def load_canonical_lm_curves() -> pd.DataFrame:
    rows = []
    for model, directory in CANONICAL_LM_DIRS.items():
        if not directory.exists():
            continue
        for objective in OBJECTIVES:
            path = directory / f"{objective}opt_moving_alpha_avg.csv"
            if not path.exists():
                continue
            raw = pd.read_csv(path)
            raw = raw[raw["group"] == "Overall"]
            pivot = raw.pivot_table(index="alpha", columns="metric", values="data", aggfunc="first").reset_index()
            for _, row in pivot.iterrows():
                if "ndcg" not in row or objective not in row:
                    continue
                rows.append(
                    {
                        "protocol": "canonical_all_users_language_models",
                        "model": model,
                        "objective": objective,
                        "rec_metric": "ndcg",
                        "alpha": float(row["alpha"]),
                        "rec_value": float(row["ndcg"]),
                        "explainability": float(row[objective]),
                    }
                )
    return pd.DataFrame(rows)


def load_canonical_lm_baseline_mismatch() -> pd.DataFrame:
    rows = []
    for model, directory in CANONICAL_LM_DIRS.items():
        baseline_path = directory / "baseline_avg.csv"
        if not baseline_path.exists():
            continue
        baseline_raw = pd.read_csv(baseline_path)
        baseline = baseline_raw[(baseline_raw["group"] == "Overall") & (baseline_raw["alpha"] == 0)]
        base_metrics = baseline.set_index("metric")["data"].to_dict()
        for objective in OBJECTIVES:
            opt_path = directory / f"{objective}opt_moving_alpha_avg.csv"
            if not opt_path.exists():
                continue
            opt = pd.read_csv(opt_path)
            opt0 = opt[(opt["group"] == "Overall") & (opt["alpha"] == 0)]
            opt_metrics = opt0.set_index("metric")["data"].to_dict()
            rows.append(
                {
                    "model": model,
                    "objective": objective,
                    "baseline_ndcg": base_metrics.get("ndcg"),
                    "opt_alpha0_ndcg": opt_metrics.get("ndcg"),
                    "delta_ndcg": opt_metrics.get("ndcg") - base_metrics.get("ndcg"),
                    "baseline_precision": base_metrics.get("precision"),
                    "opt_alpha0_precision": opt_metrics.get("precision"),
                    "delta_precision": opt_metrics.get("precision") - base_metrics.get("precision"),
                }
            )
    return pd.DataFrame(rows)


def load_accuracy_coverage() -> pd.DataFrame:
    rows = []
    for model, path in ACCURACY_JSONS.items():
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        metrics = payload["metrics"]
        coverage = payload["recommendation_coverage"]
        rows.append(
            {
                "model": model,
                "family": MODEL_FAMILY.get(model, ""),
                "users": payload.get("users"),
                "hr": metrics.get("hr"),
                "ndcg": metrics.get("ndcg"),
                "precision": metrics.get("precision"),
                "recall": metrics.get("recall"),
                "slot_coverage": coverage.get("slot_coverage"),
                "empty_users": coverage.get("empty_users"),
                "short_users": coverage.get("short_users"),
                "mean_items": coverage.get("mean_items"),
                "exact_k_users": coverage.get("exact_k_users"),
            }
        )
    return pd.DataFrame(rows)


def plot_normalized_tradeoff(curves: pd.DataFrame, out_path: Path, title: str) -> None:
    df = curves[curves["rec_metric"] == "ndcg"].copy()
    models = list(df["model"].drop_duplicates())
    colors = dict(zip(models, plt.cm.tab10.colors[: len(models)]))
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for ax, objective in zip(axes, OBJECTIVES):
        part = df[df["objective"] == objective]
        for model, g in part.groupby("model"):
            g = g.sort_values("alpha")
            base = g[g["alpha"].round(10) == 0.0].iloc[0]
            end = g[g["alpha"].round(10) == 1.0].iloc[-1]
            denom = float(end["explainability"] - base["explainability"])
            if abs(denom) < 1e-12:
                x = g["alpha"]
                xlabel = "alpha (no explanation movement)"
            else:
                x = (g["explainability"] - float(base["explainability"])) / denom
                xlabel = "normalized explanation gain"
            y = g["rec_value"] / float(base["rec_value"])
            ax.plot(x, y, marker="o", linewidth=2, markersize=3.8, label=model, color=colors[model])
        ax.axhline(1.0, color="#666666", linewidth=0.8, linestyle="--")
        ax.axhline(0.95, color="#999999", linewidth=0.8, linestyle=":")
        ax.set_title(objective)
        ax.set_xlabel(xlabel)
        ax.grid(True, linewidth=0.3, alpha=0.5)
    axes[0].set_ylabel("NDCG retention vs alpha=0")
    axes[-1].legend(loc="best", fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_endpoint_delta(summary: pd.DataFrame, out_path: Path, title: str) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    models = list(summary["model"].drop_duplicates())
    colors = dict(zip(models, plt.cm.tab10.colors[: len(models)]))
    for ax, objective in zip(axes, OBJECTIVES):
        part = summary[summary["objective"] == objective]
        for _, row in part.iterrows():
            ax.scatter(
                row["delta_explainability"],
                row["relative_rec_change"] * 100,
                s=70,
                color=colors[row["model"]],
                label=row["model"],
            )
            ax.annotate(row["model"], (row["delta_explainability"], row["relative_rec_change"] * 100), fontsize=8)
        ax.axhline(0.0, color="#666666", linewidth=0.8)
        ax.axhline(-5.0, color="#999999", linewidth=0.8, linestyle=":")
        ax.set_title(objective)
        ax.set_xlabel("explanation gain at alpha=1")
        ax.grid(True, linewidth=0.3, alpha=0.5)
    axes[0].set_ylabel("NDCG change at alpha=1 (%)")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_threshold_bars(thresholds: pd.DataFrame, out_path: Path, title: str, retention: float = 0.95) -> None:
    part = thresholds[thresholds["retention_threshold"] == retention].copy()
    models = sorted(part["model"].drop_duplicates())
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=False)
    for ax, objective in zip(axes, OBJECTIVES):
        g = part[part["objective"] == objective].set_index("model").reindex(models)
        ax.bar(models, g["gain"], color="#4C78A8")
        for idx, model in enumerate(models):
            val = g.loc[model, "gain"]
            alpha = g.loc[model, "best_alpha"]
            ax.text(idx, val, f"a={alpha:.2g}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
        ax.set_title(objective)
        ax.set_xlabel("model")
        ax.tick_params(axis="x", labelrotation=30)
        ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    axes[0].set_ylabel(f"explanation gain with NDCG retention >= {retention:.0%}")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_accuracy_coverage(df: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.2))
    colors = plt.cm.tab10.colors
    for idx, row in df.iterrows():
        ax.scatter(row["slot_coverage"], row["ndcg"], s=90, color=colors[idx % len(colors)])
        ax.annotate(row["model"], (row["slot_coverage"], row["ndcg"]), fontsize=9, xytext=(5, 4), textcoords="offset points")
    ax.set_xlabel("slot coverage")
    ax.set_ylabel("standard canonical NDCG@10")
    ax.set_title("ML-1M native-path coverage and accuracy")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main() -> None:
    ensure_dirs()

    legacy = load_legacy_all()
    legacy.to_csv(OUT_TAB / "ml1m_legacy_four_model_curves_long.csv", index=False)
    legacy_summary = _endpoint_summary(legacy)
    legacy_thresholds = _threshold_summary(legacy)
    legacy_summary.to_csv(OUT_TAB / "ml1m_legacy_four_model_ndcg_tradeoff_summary.csv", index=False)
    legacy_thresholds.to_csv(OUT_TAB / "ml1m_legacy_four_model_ndcg_threshold_summary.csv", index=False)

    plot_normalized_tradeoff(
        legacy,
        OUT_FIG / "legacy_four_model_normalized_ndcg_tradeoff.png",
        "ML-1M historical protocol: normalized NDCG-explainability tradeoff",
    )
    plot_endpoint_delta(
        legacy_summary,
        OUT_FIG / "legacy_four_model_endpoint_delta.png",
        "ML-1M historical protocol: endpoint tradeoff",
    )
    plot_threshold_bars(
        legacy_thresholds,
        OUT_FIG / "legacy_four_model_expl_gain_at_95pct_ndcg.png",
        "ML-1M historical protocol: explanation gain under <=5% NDCG loss",
    )

    canonical_lm = load_canonical_lm_curves()
    if not canonical_lm.empty:
        canonical_lm.to_csv(OUT_TAB / "ml1m_canonical_language_model_curves_long.csv", index=False)
        canonical_lm_summary = _endpoint_summary(canonical_lm)
        canonical_lm_summary.to_csv(OUT_TAB / "ml1m_canonical_language_model_ndcg_tradeoff_summary.csv", index=False)
        plot_normalized_tradeoff(
            canonical_lm,
            OUT_FIG / "canonical_language_model_normalized_ndcg_tradeoff.png",
            "ML-1M canonical-all-users: PEARLM/KGGLM normalized tradeoff",
        )
        plot_endpoint_delta(
            canonical_lm_summary,
            OUT_FIG / "canonical_language_model_endpoint_delta.png",
            "ML-1M canonical-all-users: PEARLM/KGGLM endpoint tradeoff",
        )

    mismatch = load_canonical_lm_baseline_mismatch()
    mismatch.to_csv(OUT_TAB / "ml1m_canonical_language_model_alpha0_mismatch_audit.csv", index=False)

    accuracy = load_accuracy_coverage()
    accuracy.to_csv(OUT_TAB / "ml1m_standard_accuracy_coverage.csv", index=False)
    plot_accuracy_coverage(accuracy, OUT_FIG / "ml1m_standard_accuracy_vs_coverage.png")

    print(f"Wrote figures to {OUT_FIG}")
    print(f"Wrote tables to {OUT_TAB}")


if __name__ == "__main__":
    main()
