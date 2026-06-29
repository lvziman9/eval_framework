#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
RUNTIME="$RUN_ROOT/pgpr_amazon_book_kgat_runtime_smoke"
PGPR_PY="${PGPR_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
PHYSICAL_GPU="${1:-}"

EPOCHS="${PGPR_TRANSE_EPOCHS:-1}"
EMBED_SIZE="${PGPR_TRANSE_EMBED_SIZE:-16}"
BATCH_SIZE="${PGPR_TRANSE_BATCH_SIZE:-2048}"
NEG_SAMPLES="${PGPR_TRANSE_NEG_SAMPLES:-2}"
RUN_NAME="${PGPR_TRANSE_RUN_NAME:-train_transe_model_amazon_smoke_e${EPOCHS}_d${EMBED_SIZE}}"
SUMMARY_JSON="$CANONICAL_ROOT/model_views/pgpr/pgpr_transe_training_smoke.json"

echo "[$(date '+%F %T')] PGPR Amazon TransE training smoke start"
echo "epochs=$EPOCHS embed_size=$EMBED_SIZE batch_size=$BATCH_SIZE neg_samples=$NEG_SAMPLES gpu=${PHYSICAL_GPU:-CPU}"

"$PGPR_PY" "$ROOT/scripts/model_patches/patch_pgpr_amazon_runtime.py" \
  --runtime-root "$RUNTIME"

export PYTHONPATH="$RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
cd "$RUNTIME/models/PGPR"
"$PGPR_PY" train_transe_model.py \
  --dataset amazon_book_kgat_v1 \
  --name "$RUN_NAME" \
  --gpu "$PHYSICAL_GPU" \
  --epochs "$EPOCHS" \
  --batch_size "$BATCH_SIZE" \
  --embed_size "$EMBED_SIZE" \
  --num_neg_samples "$NEG_SAMPLES" \
  --steps_per_checkpoint 50

cd "$ROOT"
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_transe_training_smoke.py" \
  --runtime-root "$RUNTIME" \
  --dataset amazon_book_kgat_v1 \
  --run-name "$RUN_NAME" \
  --epoch "$EPOCHS" \
  --expected-embed-size "$EMBED_SIZE" \
  --summary-json "$SUMMARY_JSON"

echo "[$(date '+%F %T')] PGPR Amazon TransE training smoke PASS"
