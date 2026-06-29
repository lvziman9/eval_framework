#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
RUNTIME="$RUN_ROOT/pgpr_amazon_book_kgat_runtime_smoke"
PGPR_PY="${PGPR_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"

EPOCH="${PGPR_POLICY_EPOCHS:-1}"
MAX_ACTS="${PGPR_POLICY_MAX_ACTS:-250}"
RUN_NAME="${PGPR_POLICY_RUN_NAME:-train_agent_amazon_smoke_e${EPOCH}_a${MAX_ACTS}_h32-16}"
NUM_USERS="${PGPR_EXPORT_SMOKE_USERS:-8}"
AGENT_TOPK="${PGPR_EXPORT_SMOKE_TAG:-pgpr-amazon-smoke-e${EPOCH}_a${MAX_ACTS}_${NUM_USERS}users}"
SUMMARY_JSON="$CANONICAL_ROOT/model_views/pgpr/pgpr_policy_inference_smoke.json"
PATHS_PKL="$CANONICAL_ROOT/model_views/pgpr/pgpr_policy_inference_smoke_paths.pkl"
EXPORT_SUMMARY_JSON="$CANONICAL_ROOT/model_views/pgpr/pgpr_export_smoke_validation.json"
PATHS_DIR="$ROOT/xrecsys/paths/amazon_book_kgat_v1/agent_topk=$AGENT_TOPK"

echo "[$(date '+%F %T')] PGPR Amazon export smoke start"
echo "run_name=$RUN_NAME epoch=$EPOCH max_acts=$MAX_ACTS users=$NUM_USERS tag=$AGENT_TOPK"

"$PGPR_PY" "$ROOT/scripts/validation/run_pgpr_policy_inference_smoke.py" \
  --runtime-root "$RUNTIME" \
  --dataset amazon_book_kgat_v1 \
  --run-name "$RUN_NAME" \
  --epoch "$EPOCH" \
  --summary-json "$SUMMARY_JSON" \
  --max-acts "$MAX_ACTS" \
  --num-users "$NUM_USERS" \
  --topk 5 5 1 \
  --paths-pkl "$PATHS_PKL"

"$PGPR_PY" "$ROOT/adapters/pgpr_adapter.py" \
  --pkl "$PATHS_PKL" \
  --embedding-pkl "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl" \
  --dataset amazon_book_kgat_v1 \
  --xrecsys-dir "$ROOT/xrecsys" \
  --topk 10 \
  --agent-topk-tag "$AGENT_TOPK" \
  --labels-dir "$CANONICAL_ROOT/labels"

"$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_export.py" \
  --paths-dir "$PATHS_DIR" \
  --labels-dir "$CANONICAL_ROOT/labels" \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --summary-json "$EXPORT_SUMMARY_JSON"

echo "[$(date '+%F %T')] PGPR Amazon export smoke PASS"
