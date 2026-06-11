"""
run_eval.py — Unified evaluation entry point for eval_framework
================================================================

Workflow
--------
  1. (Optional) Run adapter: convert model pkl → xrecsys CSV format
  2. Run xrecsys main.py --eval_baseline True
  3. Print summary of results

Usage
-----
  # Full pipeline: convert PGPR output + evaluate
  python run_eval.py \\
      --model pgpr \\
      --dataset ml1m \\
      --pkl xrecsys/models/PGPR/tmp/ml1m/train_agent/policy_paths_epoch50.pkl \\
      --topk 10

  # Skip conversion (CSVs already exist), evaluate only
  python run_eval.py \\
      --model pgpr \\
      --dataset ml1m \\
      --topk 10 \\
      --skip-convert

  # Evaluate with a specific agent_topk tag (e.g., pre-downloaded 25-50-1)
  python run_eval.py \\
      --model pgpr \\
      --dataset ml1m \\
      --agent-topk-tag 25-50-1 \\
      --skip-convert

Environment
-----------
  Run inside:  conda activate eval_frame
  Working dir: eval_framework/   (the repo root, parent of xrecsys/)
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).parent.resolve()
XRECSYS_DIR  = REPO_ROOT / 'xrecsys'
ADAPTERS_DIR = REPO_ROOT / 'adapters'

SUPPORTED_MODELS   = ('pgpr', 'vrkg4rec')
SUPPORTED_DATASETS = ('ml1m', 'lastfm')


# ── helpers ────────────────────────────────────────────────────────────────────

def _agent_topk_tag(topk: int) -> str:
    return f"{topk}-{topk + 2}-1"


def run_adapter(model: str, pkl: str, dataset: str, topk: int, tag: str) -> None:
    """Import and call the appropriate adapter's convert() function."""
    sys.path.insert(0, str(ADAPTERS_DIR))

    if model == 'pgpr':
        from pgpr_adapter import convert
    elif model == 'vrkg4rec':
        from vrkg4rec_adapter import convert
    else:
        raise ValueError(f"Unknown model '{model}'. Supported: {SUPPORTED_MODELS}")

    convert(
        pkl_path=pkl,
        dataset=dataset,
        xrecsys_dir=str(XRECSYS_DIR),
        topk=topk,
        agent_topk_tag=tag,
    )


def run_xrecsys_eval(dataset: str, tag: str, log_file: Path = None) -> int:
    """
    Call xrecsys/main.py --eval_baseline True via subprocess.

    Returns the process exit code.
    """
    cmd = [
        sys.executable,
        str(XRECSYS_DIR / 'main.py'),
        '--dataset',       dataset,
        '--agent_topk',    tag,
        '--eval_baseline', 'True',
    ]

    print(f"\n{'='*60}")
    print(f"Running xrecsys evaluation")
    print(f"  dataset      : {dataset}")
    print(f"  agent_topk   : {tag}")
    print(f"  working dir  : {XRECSYS_DIR}")
    if log_file:
        print(f"  log file     : {log_file}")
    print(f"{'='*60}\n")

    kwargs = dict(cwd=str(XRECSYS_DIR))
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w') as lf:
            result = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, **kwargs)
    else:
        result = subprocess.run(cmd, **kwargs)

    return result.returncode


def print_results(dataset: str, tag: str) -> None:
    """Print the baseline.txt summary if it exists."""
    baseline = XRECSYS_DIR / 'log' / dataset / f'agent_topk={tag}' / 'baseline.txt'
    if baseline.exists():
        print(f"\n{'='*60}")
        print(f"Results — {dataset} / agent_topk={tag}")
        print(f"{'='*60}")
        print(baseline.read_text())
    else:
        print(f"\n[warn] baseline.txt not found at {baseline}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Convert model output and/or run xrecsys evaluation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('--model',           required=True,
                   choices=SUPPORTED_MODELS, help='Model name')
    p.add_argument('--dataset',         required=True,
                   choices=SUPPORTED_DATASETS, help='Dataset name')
    p.add_argument('--pkl',             default=None,
                   help='Path to model output pkl (required unless --skip-convert)')
    p.add_argument('--topk',            type=int, default=10,
                   help='Top-K items per user (default: 10)')
    p.add_argument('--agent-topk-tag',  default=None,
                   help='xrecsys agent_topk folder tag, e.g. 25-50-1 '
                        '(inferred from --topk if omitted)')
    p.add_argument('--skip-convert',    action='store_true',
                   help='Skip adapter conversion (assume CSVs already exist)')
    p.add_argument('--skip-eval',       action='store_true',
                   help='Run adapter only, skip xrecsys evaluation')
    p.add_argument('--log-file',        default=None,
                   help='Redirect xrecsys stdout/stderr to this file '
                        '(default: print to console)')
    return p.parse_args()


def main():
    args = parse_args()

    tag = args.agent_topk_tag or _agent_topk_tag(args.topk)

    # ── Adapter (conversion) ──────────────────────────────────────────────────
    if not args.skip_convert:
        if not args.pkl:
            print("[error] --pkl is required unless --skip-convert is set.", file=sys.stderr)
            sys.exit(1)
        print(f"\n[1/2] Running {args.model} adapter for {args.dataset} ...")
        run_adapter(
            model=args.model,
            pkl=args.pkl,
            dataset=args.dataset,
            topk=args.topk,
            tag=tag,
        )
    else:
        print(f"\n[1/2] Skipping adapter conversion (--skip-convert).")

    if args.skip_eval:
        print("[2/2] Skipping evaluation (--skip-eval).")
        return

    # ── Evaluation ────────────────────────────────────────────────────────────
    print(f"\n[2/2] Running xrecsys evaluation ...")
    log_file = Path(args.log_file) if args.log_file else None
    rc = run_xrecsys_eval(dataset=args.dataset, tag=tag, log_file=log_file)

    if rc != 0:
        print(f"\n[error] xrecsys exited with code {rc}", file=sys.stderr)
        sys.exit(rc)

    print_results(args.dataset, tag)


if __name__ == '__main__':
    main()
