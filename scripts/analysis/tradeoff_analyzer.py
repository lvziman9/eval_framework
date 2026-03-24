"""
Trade-off Analyzer: Recommendation Quality vs Explanation Quality
=================================================================
Reads xrecsys alpha-sweep result CSVs and plots alpha-induced tradeoff curves.

Two intended report modes:
1. Single-model, multi-rec-metric comparison (implemented here).
2. Multi-model, single-rec-metric comparison (kept as a documented TODO).

Usage (from eval_framework/ root):
    conda run -n eval_frame python scripts/analysis/tradeoff_analyzer.py \
        --dataset lastfm \
        --models PGPR=xrecsys/results/lastfm/agent_topk=25-50-1 \
        --exp-metric SEP \
        --rec-metrics ndcg hr precision recall \
        --out reports/figures/tradeoff
"""

import argparse
from pathlib import Path
from typing import List

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D


OPT_FILE = {
    'LIR': 'LIRopt_moving_alpha_avg.csv',
    'SEP': 'SEPopt_moving_alpha_avg.csv',
    'ETD': 'ETDopt_moving_alpha_avg.csv',
}

METRIC_DISPLAY = {
    'ndcg': 'NDCG@10',
    'hr': 'HR@10',
    'precision': 'Precision@10',
    'recall': 'Recall@10',
    'LIR': 'LIR',
    'SEP': 'SEP',
    'ETD': 'ETD',
}

REC_METRIC_CHOICES = ['ndcg', 'hr', 'precision', 'recall']
METRIC_COLORS = {
    'ndcg': '#1565C0',
    'hr': '#C62828',
    'precision': '#2E7D32',
    'recall': '#EF6C00',
}
ALPHA0_MARKER = 'o'
ALPHA1_MARKER = 'X'
EXP_LINESTYLE = (0, (6, 2))
REC_LINESTYLE = '-'


def load_model_results(result_dir: Path, exp_metric: str) -> pd.DataFrame:
    csv_path = result_dir / OPT_FILE[exp_metric]
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Result file not found: {csv_path}\n"
            f"Run xrecsys/main.py --eval_baseline True for this model first."
        )

    df = pd.read_csv(csv_path)
    overall = df[df['group'] == 'Overall'].copy()
    pivot = overall.pivot_table(index='alpha', columns='metric', values='data', aggfunc='first')
    pivot = pivot.reset_index()
    pivot.columns.name = None

    exp_col_actual = next((c for c in pivot.columns if c.lower() == exp_metric.lower()), None)
    keep = ['alpha', 'ndcg', 'hr', 'precision', 'recall']
    if exp_col_actual:
        keep.append(exp_col_actual)
    available = [c for c in keep if c in pivot.columns]
    result = pivot[available].sort_values('alpha').reset_index(drop=True)
    if exp_col_actual and exp_col_actual != exp_metric:
        result = result.rename(columns={exp_col_actual: exp_metric})
    return result


def load_baseline(result_dir: Path) -> dict:
    csv_path = result_dir / 'baseline_avg.csv'
    if not csv_path.exists():
        return {}
    df = pd.read_csv(csv_path)
    overall = df[(df['group'] == 'Overall') & (df['alpha'] == 0)]
    return dict(zip(overall['metric'], overall['data']))


def _available_rec_metrics(models_data: dict, requested: List[str]) -> List[str]:
    available = []
    for metric in requested:
        if any(metric in df.columns for df in models_data.values()):
            available.append(metric)
    return available


def _annotate_alpha_endpoints(ax, x_values, y_values):
    ax.scatter(
        x_values.iloc[0], y_values.iloc[0],
        color='#212121', marker=ALPHA0_MARKER, s=70,
        edgecolor='white', linewidth=0.9, zorder=5,
    )
    ax.scatter(
        x_values.iloc[-1], y_values.iloc[-1],
        color='#212121', marker=ALPHA1_MARKER, s=80,
        edgecolor='white', linewidth=0.9, zorder=5,
    )
    ax.annotate('α=0', (x_values.iloc[0], y_values.iloc[0]), textcoords='offset points',
                xytext=(-18, 8), fontsize=8, color='#212121')
    ax.annotate('α=1', (x_values.iloc[-1], y_values.iloc[-1]), textcoords='offset points',
                xytext=(6, -14), fontsize=8, color='#212121')


def _make_single_model_legends(fig, rec_metrics, exp_metric):
    handles = [
        Line2D([0], [0], color=METRIC_COLORS[m], lw=2.5, label=f"{METRIC_DISPLAY[m]} curve")
        for m in rec_metrics
    ]
    handles.extend([
        Line2D([0], [0], color='#616161', lw=2.5, linestyle=EXP_LINESTYLE,
               label=f'{METRIC_DISPLAY[exp_metric]} Δ% (gray dashed)'),
        Line2D([0], [0], marker=ALPHA0_MARKER, color='none', markerfacecolor='#212121',
               markeredgecolor='white', markersize=8, label='α = 0 endpoint'),
        Line2D([0], [0], marker=ALPHA1_MARKER, color='none', markerfacecolor='#212121',
               markeredgecolor='white', markersize=8, label='α = 1 endpoint'),
    ])
    fig.legend(handles=handles, loc='upper center', ncol=min(4, len(handles)),
               bbox_to_anchor=(0.5, 0.965), frameon=False, title='Legend')


def plot_single_model_tradeoff(model_name: str, df: pd.DataFrame, exp_metric: str, rec_metrics: List[str], dataset: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    exp_col = exp_metric
    rec_metrics = [m for m in rec_metrics if m in df.columns]
    if not rec_metrics:
        raise ValueError('No requested recommendation metrics are available in the loaded result file.')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.8))
    fig.suptitle(
        f'{model_name}: Alpha-Sweep Tradeoff vs {exp_metric}  (dataset={dataset})',
        fontsize=15,
        fontweight='bold',
        y=0.995,
    )

    ax_abs, ax_rel = axes

    for idx, rec_metric in enumerate(rec_metrics):
        color = METRIC_COLORS.get(rec_metric, list(METRIC_COLORS.values())[idx % len(METRIC_COLORS)])
        ax_abs.plot(df[exp_col], df[rec_metric], color=color, linewidth=2.5, label=METRIC_DISPLAY[rec_metric])
        _annotate_alpha_endpoints(ax_abs, df[exp_col], df[rec_metric])

        rec0 = df[rec_metric].iloc[0]
        rec_delta = (df[rec_metric] - rec0) / (abs(rec0) + 1e-9) * 100
        ax_rel.plot(df['alpha'], rec_delta, color=color, linewidth=2.5, label=METRIC_DISPLAY[rec_metric])

    exp0 = df[exp_col].iloc[0]
    exp_delta = (df[exp_col] - exp0) / (abs(exp0) + 1e-9) * 100
    ax_rel.plot(df['alpha'], exp_delta, color='#616161', linewidth=2.5, linestyle=EXP_LINESTYLE,
                label=f'{METRIC_DISPLAY[exp_metric]} Δ%')
    _annotate_alpha_endpoints(ax_rel, df['alpha'], exp_delta)

    ax_abs.set_xlabel(METRIC_DISPLAY.get(exp_metric, exp_metric), fontsize=11)
    ax_abs.set_ylabel('Recommendation metric value', fontsize=11)
    ax_abs.set_title('Tradeoff curves across recommendation metrics', fontsize=11)
    ax_abs.grid(True, alpha=0.25)

    ax_rel.axhline(0, color='gray', linewidth=0.9, linestyle=':')
    ax_rel.set_xlabel('α  (weight on explanation metric)', fontsize=11)
    ax_rel.set_ylabel('Relative change from α=0 (%)', fontsize=11)
    ax_rel.set_title('Relative change vs alpha', fontsize=11)
    ax_rel.grid(True, alpha=0.25)
    ax_rel.xaxis.set_major_locator(mticker.MultipleLocator(0.1))

    _make_single_model_legends(fig, rec_metrics, exp_metric)

    plt.tight_layout(rect=[0.03, 0.06, 0.97, 0.88])
    out_path = out_dir / f'tradeoff_{dataset}_{model_name}_{exp_metric}.png'
    plt.savefig(out_path, dpi=170, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out_path}')


def save_table(model_name: str, df: pd.DataFrame, exp_metric: str, dataset: str, out_dir: Path):
    out_path = out_dir / f'tradeoff_{dataset}_{model_name}_{exp_metric}.csv'
    df.to_csv(out_path, index=False, float_format='%.4f')
    print(f'  Saved: {out_path}')

    print(f"\n{'='*80}")
    print(f'  α-sweep summary  |  model={model_name}  |  dataset={dataset}  |  opt={exp_metric}')
    print(f"{'='*80}")
    metric_cols = [c for c in ['ndcg', 'hr', 'precision', 'recall', exp_metric] if c in df.columns]
    header = '  ' + '  '.join([f'{x:>10}' for x in ['alpha'] + metric_cols])
    print(header)
    for _, row in df.iterrows():
        values = [f"{row['alpha']:>10.2f}"]
        for metric in metric_cols:
            values.append(f"{row[metric]:>10.4f}")
        print('  ' + '  '.join(values))
    print()


def main():
    parser = argparse.ArgumentParser(description='Plot alpha-sweep tradeoff curves')
    parser.add_argument('--dataset', default='lastfm', help='Dataset name (default: lastfm)')
    parser.add_argument('--models', nargs='+', required=True, metavar='NAME=PATH',
                        help='Model result dirs, e.g. PGPR=xrecsys/results/lastfm/agent_topk=25-50-1')
    parser.add_argument('--exp-metric', default='LIR', choices=['LIR', 'SEP', 'ETD'],
                        help='Explanation metric to visualise (default: LIR)')
    parser.add_argument('--rec-metrics', nargs='+', default=REC_METRIC_CHOICES, choices=REC_METRIC_CHOICES,
                        help='Recommendation metrics to include (default: ndcg hr precision recall)')
    parser.add_argument('--out', default='reports/figures/tradeoff',
                        help='Output directory for figures (default: reports/figures/tradeoff)')
    args = parser.parse_args()

    model_dirs = {}
    for entry in args.models:
        if '=' not in entry:
            parser.error(f'--models entries must be NAME=PATH, got: {entry}')
        name, path = entry.split('=', 1)
        model_dirs[name] = Path(path)

    if len(model_dirs) != 1:
        raise ValueError(
            'This refined report version currently supports the single-model, multi-metric mode only. '
            'Use one NAME=PATH pair for now; the multi-model comparison remains a documented TODO.'
        )

    model_name, result_dir = next(iter(model_dirs.items()))
    out_dir = Path(args.out)

    print(f'\nLoading results for model={model_name}, exp_metric={args.exp_metric} ...')
    df = load_model_results(result_dir, args.exp_metric)
    baseline = load_baseline(result_dir)
    if baseline:
        available_baselines = []
        for metric in ['ndcg', 'hr', 'precision', 'recall', args.exp_metric]:
            metric_value = baseline.get(metric, baseline.get(metric.lower(), None))
            if metric_value is not None:
                available_baselines.append(f'{metric}={metric_value:.4f}')
        if available_baselines:
            print('  baseline ' + '  '.join(available_baselines))

    print('\nPlotting single-model multi-metric tradeoff figure ...')
    plot_single_model_tradeoff(model_name, df, args.exp_metric, args.rec_metrics, args.dataset, out_dir)
    save_table(model_name, df, args.exp_metric, args.dataset, out_dir)


if __name__ == '__main__':
    main()
