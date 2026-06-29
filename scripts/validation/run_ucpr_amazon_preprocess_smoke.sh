#!/usr/bin/env bash
set -euo pipefail

ROOT="/usr1/home/s125mdg43_08/eval_framework"
FRAMEWORK="${UCPR_FRAMEWORK:-/usr1/home/s125mdg43_08/rep-path-reasoning-recsys}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
UCPR_VIEW="$CANONICAL_ROOT/model_views/ucpr/preprocessed/ucpr"
UCPR_MAPS="$CANONICAL_ROOT/model_views/ucpr/preprocessed"
RUNTIME="${UCPR_AMAZON_RUNTIME:-$RUN_ROOT/ucpr_amazon_book_kgat_runtime_smoke}"
RUNTIME_DATA="$RUNTIME/data/amazon_book_kgat_v1/preprocessed/ucpr"
SUMMARY_JSON="$CANONICAL_ROOT/model_views/ucpr/ucpr_runtime_preprocess_smoke.json"
REP_PY="${REP_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/rep/bin/python}"

echo "[$(date '+%F %T')] UCPR Amazon preprocess smoke start"
echo "runtime=$RUNTIME"
echo "ucpr_view=$UCPR_VIEW"

if [[ ! -d "$RUNTIME/models/UCPR" ]]; then
  mkdir -p "$RUNTIME/models"
  cp -a "$FRAMEWORK/models/UCPR" "$RUNTIME/models/UCPR"
  cp "$FRAMEWORK/models/__init__.py" "$RUNTIME/models/__init__.py"
  cp "$FRAMEWORK/models/utils.py" "$RUNTIME/models/utils.py"
fi

if [[ ! -d "$RUNTIME_DATA" ]]; then
  mkdir -p "$(dirname "$RUNTIME_DATA")"
  cp -a "$UCPR_VIEW" "$RUNTIME_DATA"
fi
mkdir -p "$RUNTIME/results"

"$REP_PY" "$ROOT/scripts/model_patches/patch_ucpr_cli_topk.py" \
  --runtime-root "$RUNTIME"
"$REP_PY" "$ROOT/scripts/model_patches/patch_ucpr_amazon_runtime.py" \
  --runtime-root "$RUNTIME"

export PYTHONPATH="$RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
cd "$RUNTIME/models/UCPR"

echo "[$(date '+%F %T')] UCPR Amazon preprocess.py start"
"$REP_PY" preprocess.py --dataset amazon_book_kgat_v1
echo "[$(date '+%F %T')] UCPR Amazon preprocess.py done"

cd "$ROOT"
"$REP_PY" "$ROOT/scripts/validation/validate_ucpr_preprocess_smoke.py" \
  --runtime-root "$RUNTIME" \
  --canonical-root "$CANONICAL_ROOT" \
  --view-root "$UCPR_MAPS" \
  --dataset amazon_book_kgat_v1 \
  --summary-json "$SUMMARY_JSON"

echo "[$(date '+%F %T')] UCPR Amazon preprocess smoke done: $SUMMARY_JSON"
