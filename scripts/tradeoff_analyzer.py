"""
Trade-off Analyzer: Recommendation Quality vs Explanation Quality
=================================================================
Reads the xrecsys alpha-sweep result CSVs for two models (VRKG4Rec and PGPR)
and plots the Pareto frontier curve: NDCG vs LIR/ETD/SEP as α varies.

Usage (from eval_framework/ root):
    conda run -n eval_frame python scripts/tradeoff_analyzer.py \
        --dataset lastfm \
        --models VRKG4Rec=xrecsys/results/lastfm/agent_topk=10-12-1 \
                 PGPR=xrecsys/results/lastfm/agent_topk=25-50-1 \
        --exp-metric LIR \
        --out scripts/figures

Produces:
    figures/tradeoff_<dataset>_<exp_metric>.png  — Pareto frontier
    figures/tradeoff_<dataset>_<exp_metric>.csv  — underlying data table
"""

import argparse
import os
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

OPT_FILE = {
    'LIR': 'LIRopt_moving_alpha_avg.csv',
    'SEP': 'SEPopt_moving_alpha_avg.csv',
    'ETD': 'ETDopt_moving_alpha_avg.csv',
}

METRIC_DISPLAY = {
    'ndcg': 'NDCG@10',
    'hr':   'HR@10',
    'LIR':  'LIR',
    'SEP':  'SEP',
    'ETD':  'ETD',
}


def load_model_results(result_dir: Path, exp_metric: str) -> pd.DataFrame:
    """
    Load the alpha-sweep CSV for a given model directory and explanation metric.
    Returns a DataFrame with columns: [alpha, ndcg, hr, LIR/SEP/ETD]  (Overall group only).
    """
    csv_path = result_dir / OPT_FILE[exp_metric]
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Result file not found: {csv_path}\n"
            f"Run xrecsys/main.py --eval_baseline True for this model first."
        )
    df = pd.read_csv(csv_path)
    overall = df[df['group'] == 'Overall'].copy()

    # Pivot: rows=alpha, cols=metric
    pivot = overall.pivot_table(index='alpha', columns='metric', values='data', aggfunc='first')
    pivot = pivot.reset_index()

    # Add baseline (alpha=0 row already present, but let's make sure col names are clean)
    pivot.columns.name = None

    # metric names in CSV are mixed-case (e.g. 'LIR', 'SEP', 'ETD', 'ndcg', 'hr')
    # find the actual column name for the explanation metric (case-insensitive)
    exp_col_actual = next(
        (c for c in pivot.columns if c.lower() == exp_metric.lower()), None
    )
    keep = ['alpha', 'ndcg', 'hr']
    if exp_col_actual:
        keep.append(exp_col_actual)
    available = [c for c in keep if c in pivot.columns]
    result = pivot[available].sort_values('alpha').reset_index(drop=True)
    # Normalise exp metric column name to the requested case for consistency
    if exp_col_actual and exp_col_actual != exp_metric:
        result = result.rename(columns={exp_col_actual: exp_metric})
    return result


def load_baseline(result_dir: Path) -> dict:
    """Load alpha=0 baseline values from baseline_avg.csv."""
    csv_path = result_dir / 'baseline_avg.csv'
    if not csv_path.exists():
        return {}
    df = pd.read_csv(csv_path)
    overall = df[(df['group'] == 'Overall') & (df['alpha'] == 0)]
    return dict(zip(overall['metric'], overall['data']))


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLORS = ['#2196F3', '#F44336', '#4CAF50', '#FF9800', '#9C27B0']
MARKERS = ['o', 's', '^', 'D', 'v']


def plot_pareto(models_data: dict, exp_metric: str, dataset: str, out_dir: Path):
    """
    models_data: {model_name: DataFrame}
    exp_metric: 'LIR' | 'SEP' | 'ETD'
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    exp_col = exp_metric  # column name is already normalised to requested case

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f'Trade-off: Recommendation Quality vs {exp_metric}  (dataset={dataset})',
        fontsize=14, fontweight='bold'
    )

    # --- subplot 1: NDCG vs exp_metric (Pareto frontier) ---
    ax1 = axes[0]
    for idx, (name, df) in enumerate(models_data.items()):
        if exp_col not in df.columns or 'ndcg' not in df.columns:
            print(f"  WARNING: {name} missing column '{exp_col}', skipping")
            continue
        color  = COLORS[idx % len(COLORS)]
        marker = MARKERS[idx % len(MARKERS)]
        ax1.plot(df[exp_col], df['ndcg'],
                 color=color, marker=marker, linewidth=2,
                 markersize=6, label=name)
        # Annotate α=0 and α=1 endpoints
        ax1.annotate(f'α=0', (df[exp_col].iloc[0],  df['ndcg'].iloc[0]),
                     textcoords='offset points', xytext=(-15, 5),
                     fontsize=8, color=color)
        ax1.annotate(f'α=1', (df[exp_col].iloc[-1], df['ndcg'].iloc[-1]),
                     textcoords='offset points', xytext=(3, -12),
                     fontsize=8, color=color)

    ax1.set_xlabel(METRIC_DISPLAY.get(exp_metric, exp_metric), fontsize=12)
    ax1.set_ylabel(METRIC_DISPLAY['ndcg'], fontsize=12)
    ax1.set_title('Pareto Frontier', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # --- subplot 2: α sweep lines ---
    ax2 = axes[1]
    for idx, (name, df) in enumerate(models_data.items()):
        color = COLORS[idx % len(COLORS)]
        marker = MARKERS[idx % len(MARKERS)]
        if 'ndcg' in df.columns:
            ndcg0 = df['ndcg'].iloc[0]
            ax2.plot(df['alpha'], (df['ndcg'] - ndcg0) / (ndcg0 + 1e-9) * 100,
                     color=color, marker=marker, linewidth=2, markersize=5,
                     linestyle='-', label=f'{name} NDCG Δ%')
        if exp_col in df.columns:
            exp0 = df[exp_col].iloc[0]
            ax2.plot(df['alpha'], (df[exp_col] - exp0) / (abs(exp0) + 1e-9) * 100,
                     color=color, marker=marker, linewidth=2, markersize=5,
                     linestyle='--', label=f'{name} {exp_metric} Δ%')

    ax2.axhline(0, color='gray', linewidth=0.8, linestyle=':')
    ax2.set_xlabel('α  (weight on explanation metric)', fontsize=12)
    ax2.set_ylabel('Relative change from α=0 (%)', fontsize=12)
    ax2.set_title(f'NDCG (solid) vs {exp_metric} (dashed) as α increases', fontsize=12)
    ax2.legend(fontsize=9, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_locator(mticker.MultipleLocator(0.1))

    plt.tight_layout()
    out_path = out_dir / f'tradeoff_{dataset}_{exp_metric}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out_path}")


def save_table(models_data: dict, exp_metric: str, dataset: str, out_dir: Path):
    """Save combined alpha-sweep table to CSV."""
    exp_col = exp_metric  # column name normalised in load_model_results
    frames = []
    for name, df in models_data.items():
        tmp = df.copy()
        tmp.insert(0, 'model', name)
        frames.append(tmp)
    combined = pd.concat(frames, ignore_index=True)
    out_path = out_dir / f'tradeoff_{dataset}_{exp_metric}.csv'
    combined.to_csv(out_path, index=False, float_format='%.4f')
    print(f"  Saved: {out_path}")

    # Print summary table
    print(f"\n{'='*70}")
    print(f"  α-sweep summary  |  dataset={dataset}  |  opt={exp_metric}")
    print(f"{'='*70}")
    for name, df in models_data.items():
        print(f"\n  [{name}]")
        if exp_col not in df.columns:
            print(f"    (no {exp_col} column)")
            continue
        print(f"  {'alpha':>6}  {'NDCG':>8}  {'HR':>8}  {exp_metric:>8}")
        for _, row in df.iterrows():
            ndcg = f"{row['ndcg']:.4f}" if 'ndcg' in row else '  N/A  '
            hr   = f"{row['hr']:.4f}"   if 'hr'   in row else '  N/A  '
            exp  = f"{row[exp_col]:.4f}"
            print(f"  {row['alpha']:>6.2f}  {ndcg:>8}  {hr:>8}  {exp:>8}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Plot trade-off Pareto frontier for two models')
    parser.add_argument('--dataset',    default='lastfm',
                        help='Dataset name (default: lastfm)')
    parser.add_argument('--models',     nargs='+', required=True,
                        metavar='NAME=PATH',
                        help='Model result dirs, e.g. VRKG4Rec=xrecsys/results/lastfm/agent_topk=10-12-1')
    parser.add_argument('--exp-metric', default='LIR',
                        choices=['LIR', 'SEP', 'ETD'],
                        help='Explanation metric to optimise (default: LIR)')
    parser.add_argument('--out',        default='scripts/figures',
                        help='Output directory for figures (default: scripts/figures)')
    args = parser.parse_args()

    # Parse model name=path pairs
    model_dirs = {}
    for entry in args.models:
        if '=' not in entry:
            parser.error(f"--models entries must be NAME=PATH, got: {entry}")
        name, path = entry.split('=', 1)
        model_dirs[name] = Path(path)

    out_dir = Path(args.out)

    print(f"\nLoading results for exp_metric={args.exp_metric} ...")
    models_data = {}
    for name, result_dir in model_dirs.items():
        print(f"  {name}: {result_dir}")
        try:
            df = load_model_results(result_dir, args.exp_metric)
            models_data[name] = df
            baseline = load_baseline(result_dir)
            if baseline:
                ndcg_val = baseline.get('ndcg', None)
                exp_val  = baseline.get(args.exp_metric, baseline.get(args.exp_metric.lower(), None))
                ndcg_str = f"{ndcg_val:.4f}" if ndcg_val is not None else 'N/A'
                exp_str  = f"{exp_val:.4f}"  if exp_val  is not None else 'N/A'
                print(f"    baseline NDCG={ndcg_str}  {args.exp_metric}={exp_str}")
        except FileNotFoundError as e:
            print(f"  ERROR: {e}")

    if not models_data:
        print("No models loaded. Exiting.")
        return

    print(f"\nPlotting Pareto frontier ...")
    plot_pareto(models_data, args.exp_metric, args.dataset, out_dir)

    save_table(models_data, args.exp_metric, args.dataset, out_dir)


if __name__ == '__main__':
    main()
