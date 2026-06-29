#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
PGPR_VIEW="$CANONICAL_ROOT/model_views/pgpr/amazon_book_kgat_v1"
RUNTIME="$RUN_ROOT/pgpr_amazon_book_kgat_runtime_smoke"
PGPR_PY="${PGPR_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
SUMMARY_JSON="$CANONICAL_ROOT/model_views/pgpr/pgpr_runtime_preprocess_smoke.json"

echo "[$(date '+%F %T')] PGPR Amazon preprocess smoke start"

mkdir -p "$RUNTIME/models/PGPR" "$RUNTIME/datasets/amazon_book_kgat_v1"
cp "$ROOT/xrecsys/models/PGPR/"*.py "$RUNTIME/models/PGPR/"
cp "$ROOT/xrecsys/models/PGPR/README.md" "$RUNTIME/models/PGPR/"
cp "$ROOT/xrecsys/models/PGPR/LICENSE" "$RUNTIME/models/PGPR/"
cp -a "$PGPR_VIEW/." "$RUNTIME/datasets/amazon_book_kgat_v1/"

"$PGPR_PY" "$ROOT/scripts/model_patches/patch_pgpr_runtime.py" \
  --runtime-root "$RUNTIME"
"$PGPR_PY" "$ROOT/scripts/model_patches/patch_pgpr_amazon_runtime.py" \
  --runtime-root "$RUNTIME"

export PYTHONPATH="$RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
cd "$RUNTIME/models/PGPR"
"$PGPR_PY" preprocess.py --dataset amazon_book_kgat_v1

cd "$ROOT"
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_preprocess_smoke.py" \
  --dataset amazon_book_kgat_v1 \
  --canonical-labels-dir "$CANONICAL_ROOT/labels" \
  --pgpr-tmp-dir "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1" \
  --summary-json "$SUMMARY_JSON"

echo "[$(date '+%F %T')] PGPR Amazon preprocess smoke PASS"
