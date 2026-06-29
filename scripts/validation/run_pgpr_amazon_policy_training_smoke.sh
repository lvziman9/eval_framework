#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
RUNTIME="$RUN_ROOT/pgpr_amazon_book_kgat_runtime_smoke"
PGPR_PY="${PGPR_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
PHYSICAL_GPU="${1:-}"

EPOCHS="${PGPR_POLICY_EPOCHS:-1}"
BATCH_SIZE="${PGPR_POLICY_BATCH_SIZE:-8192}"
MAX_ACTS="${PGPR_POLICY_MAX_ACTS:-250}"
RUN_NAME="${PGPR_POLICY_RUN_NAME:-train_agent_amazon_smoke_e${EPOCHS}_a${MAX_ACTS}_h32-16}"
SUMMARY_JSON="$CANONICAL_ROOT/model_views/pgpr/pgpr_policy_training_smoke.json"

echo "[$(date '+%F %T')] PGPR Amazon policy training smoke start"
echo "epochs=$EPOCHS batch_size=$BATCH_SIZE max_acts=$MAX_ACTS gpu=${PHYSICAL_GPU:-CPU}"

"$PGPR_PY" "$ROOT/scripts/model_patches/patch_pgpr_runtime.py" \
  --runtime-root "$RUNTIME"
"$PGPR_PY" "$ROOT/scripts/model_patches/patch_pgpr_amazon_runtime.py" \
  --runtime-root "$RUNTIME"

export PYTHONPATH="$RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
cd "$RUNTIME/models/PGPR"
"$PGPR_PY" train_agent.py \
  --dataset amazon_book_kgat_v1 \
  --name "$RUN_NAME" \
  --gpu "$PHYSICAL_GPU" \
  --epochs "$EPOCHS" \
  --batch_size "$BATCH_SIZE" \
  --max_acts "$MAX_ACTS" \
  --max_path_len 3 \
  --state_history 1 \
  --hidden 32 16 \
  --act_dropout 0.0

cd "$ROOT"
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_policy_training_smoke.py" \
  --runtime-root "$RUNTIME" \
  --dataset amazon_book_kgat_v1 \
  --run-name "$RUN_NAME" \
  --epoch "$EPOCHS" \
  --expected-state-dim 64 \
  --expected-act-dim "$((MAX_ACTS + 1))" \
  --summary-json "$SUMMARY_JSON"

echo "[$(date '+%F %T')] PGPR Amazon policy training smoke PASS"
