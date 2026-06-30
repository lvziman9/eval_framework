#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
PGPR_VIEW="$CANONICAL_ROOT/model_views/pgpr/amazon_book_kgat_v1"
RUNTIME="${PGPR_RUNTIME:-$RUN_ROOT/pgpr_amazon_book_kgat_runtime_formal}"
PGPR_PY="${PGPR_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/pgpr_env/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
PHYSICAL_GPU="${1:-${PGPR_GPU:-}}"

TRANSE_EPOCHS="${PGPR_TRANSE_EPOCHS:-30}"
TRANSE_EMBED_SIZE="${PGPR_TRANSE_EMBED_SIZE:-300}"
TRANSE_BATCH_SIZE="${PGPR_TRANSE_BATCH_SIZE:-2048}"
TRANSE_NEG_SAMPLES="${PGPR_TRANSE_NEG_SAMPLES:-5}"
TRANSE_RUN_NAME="${PGPR_TRANSE_RUN_NAME:-train_transe_model_amazon_formal_e${TRANSE_EPOCHS}_d${TRANSE_EMBED_SIZE}_b${TRANSE_BATCH_SIZE}_n${TRANSE_NEG_SAMPLES}}"

POLICY_EPOCHS="${PGPR_POLICY_EPOCHS:-50}"
POLICY_BATCH_SIZE="${PGPR_POLICY_BATCH_SIZE:-8192}"
POLICY_MAX_ACTS="${PGPR_POLICY_MAX_ACTS:-250}"
POLICY_EXPECTED_STATE_DIM="$((TRANSE_EMBED_SIZE * 4))"
POLICY_HIDDEN_TEXT="${PGPR_POLICY_HIDDEN:-512 256}"
read -r -a POLICY_HIDDEN <<< "$POLICY_HIDDEN_TEXT"
if [ "${#POLICY_HIDDEN[@]}" -ne 2 ]; then
  echo "PGPR_POLICY_HIDDEN must contain exactly two integers, got: $POLICY_HIDDEN_TEXT" >&2
  exit 2
fi
POLICY_RUN_NAME="${PGPR_POLICY_RUN_NAME:-train_agent_amazon_formal_e${POLICY_EPOCHS}_a${POLICY_MAX_ACTS}_h${POLICY_HIDDEN[0]}-${POLICY_HIDDEN[1]}}"

FORMAL_TOPK_TEXT="${PGPR_FORMAL_TOPK:-10 12 1}"
read -r -a FORMAL_TOPK <<< "$FORMAL_TOPK_TEXT"
if [ "${#FORMAL_TOPK[@]}" -ne 3 ]; then
  echo "PGPR_FORMAL_TOPK must contain exactly three integers, got: $FORMAL_TOPK_TEXT" >&2
  exit 2
fi
INFERENCE_BATCH_SIZE="${PGPR_INFERENCE_BATCH_SIZE:-256}"
AGENT_TOPK_TAG="${PGPR_AGENT_TOPK_TAG:-pgpr-amazon-formal-e${POLICY_EPOCHS}_a${POLICY_MAX_ACTS}_beam${FORMAL_TOPK[0]}-${FORMAL_TOPK[1]}-${FORMAL_TOPK[2]}}"
PGPR_USE_STREAMING_EXPORT="${PGPR_USE_STREAMING_EXPORT:-1}"

STATUS_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_formal_pipeline_status.json"
PREPROCESS_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_preprocess_validation.json"
TRANSE_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_transe_formal_validation.json"
POLICY_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_policy_formal_validation.json"
INFERENCE_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_policy_inference_formal.json"
STREAMING_EXPORT_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_streaming_export_formal.json"
PATHS_PKL="$RUN_ROOT/pgpr_amazon_book_kgat_policy_paths_${AGENT_TOPK_TAG}.pkl"
EXPORT_SUMMARY_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_export_validation.json"
ACCURACY_JSON="$RUN_ROOT/pgpr_amazon_book_kgat_accuracy.json"
PATHS_DIR="$ROOT/xrecsys/paths/amazon_book_kgat_v1/agent_topk=$AGENT_TOPK_TAG"

write_status() {
  local status="$1"
  local stage="$2"
  local message="$3"
  "$EVAL_PY" - "$STATUS_JSON" "$status" "$stage" "$message" <<PY
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
summary = {
    "dataset": "amazon_book_kgat_v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "stage": sys.argv[3],
    "message": sys.argv[4],
    "runtime_root": "$RUNTIME",
    "device": "${PHYSICAL_GPU:-CPU}",
    "transe": {
        "run_name": "$TRANSE_RUN_NAME",
        "epochs": int("$TRANSE_EPOCHS"),
        "embed_size": int("$TRANSE_EMBED_SIZE"),
        "batch_size": int("$TRANSE_BATCH_SIZE"),
        "neg_samples": int("$TRANSE_NEG_SAMPLES"),
    },
    "policy": {
        "run_name": "$POLICY_RUN_NAME",
        "epochs": int("$POLICY_EPOCHS"),
        "batch_size": int("$POLICY_BATCH_SIZE"),
        "max_acts": int("$POLICY_MAX_ACTS"),
        "expected_state_dim": int("$POLICY_EXPECTED_STATE_DIM"),
        "hidden": [int("$POLICY_HIDDEN_TEXT".split()[0]), int("$POLICY_HIDDEN_TEXT".split()[1])],
    },
    "export": {
        "beam_topk": [int("$FORMAL_TOPK_TEXT".split()[0]), int("$FORMAL_TOPK_TEXT".split()[1]), int("$FORMAL_TOPK_TEXT".split()[2])],
        "inference_batch_size": int("$INFERENCE_BATCH_SIZE"),
        "agent_topk_tag": "$AGENT_TOPK_TAG",
        "paths_pkl": "$PATHS_PKL",
        "paths_dir": "$PATHS_DIR",
        "streaming_export": "$STREAMING_EXPORT_JSON",
        "streaming_export_enabled": "$PGPR_USE_STREAMING_EXPORT",
        "export_validation": "$EXPORT_SUMMARY_JSON",
        "accuracy": "$ACCURACY_JSON",
    },
}
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
PY
}

on_error() {
  local line="$1"
  write_status "FAILED" "line_${line}" "PGPR Amazon formal pipeline failed"
}
trap 'on_error "$LINENO"' ERR

echo "[$(date '+%F %T')] PGPR Amazon formal pipeline start"
echo "runtime=$RUNTIME"
echo "gpu=${PHYSICAL_GPU:-CPU}"
echo "transe=$TRANSE_RUN_NAME epochs=$TRANSE_EPOCHS embed=$TRANSE_EMBED_SIZE batch=$TRANSE_BATCH_SIZE neg=$TRANSE_NEG_SAMPLES"
echo "policy=$POLICY_RUN_NAME epochs=$POLICY_EPOCHS batch=$POLICY_BATCH_SIZE max_acts=$POLICY_MAX_ACTS hidden=${POLICY_HIDDEN[*]}"
echo "export tag=$AGENT_TOPK_TAG topk=${FORMAL_TOPK[*]} inference_batch=$INFERENCE_BATCH_SIZE streaming=$PGPR_USE_STREAMING_EXPORT"
write_status "RUNNING" "prepare_runtime" "Preparing isolated PGPR Amazon formal runtime"

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

write_status "RUNNING" "preprocess" "Running or validating PGPR Amazon preprocessing"
if [ "${PGPR_FORCE_PREPROCESS:-0}" = "1" ] || [ ! -f "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/dataset.pkl" ] || [ ! -f "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/kg.pkl" ]; then
  cd "$RUNTIME/models/PGPR"
  "$PGPR_PY" preprocess.py --dataset amazon_book_kgat_v1
  cd "$ROOT"
fi
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_preprocess_smoke.py" \
  --dataset amazon_book_kgat_v1 \
  --canonical-labels-dir "$CANONICAL_ROOT/labels" \
  --pgpr-tmp-dir "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1" \
  --summary-json "$PREPROCESS_JSON"

write_status "RUNNING" "transe" "Training or validating formal PGPR Amazon TransE embeddings"
TRANSE_CKPT="$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/$TRANSE_RUN_NAME/transe_model_sd_epoch_${TRANSE_EPOCHS}.ckpt"
if [ "${PGPR_FORCE_TRANSE:-0}" = "1" ] || [ ! -f "$TRANSE_CKPT" ] || [ ! -f "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl" ]; then
  cd "$RUNTIME/models/PGPR"
  "$PGPR_PY" train_transe_model.py \
    --dataset amazon_book_kgat_v1 \
    --name "$TRANSE_RUN_NAME" \
    --gpu "$PHYSICAL_GPU" \
    --epochs "$TRANSE_EPOCHS" \
    --batch_size "$TRANSE_BATCH_SIZE" \
    --embed_size "$TRANSE_EMBED_SIZE" \
    --num_neg_samples "$TRANSE_NEG_SAMPLES" \
    --steps_per_checkpoint 50
  cd "$ROOT"
fi
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_transe_training_smoke.py" \
  --runtime-root "$RUNTIME" \
  --dataset amazon_book_kgat_v1 \
  --run-name "$TRANSE_RUN_NAME" \
  --epoch "$TRANSE_EPOCHS" \
  --expected-embed-size "$TRANSE_EMBED_SIZE" \
  --summary-json "$TRANSE_JSON"

write_status "RUNNING" "policy" "Training or validating formal PGPR Amazon policy checkpoint"
POLICY_CKPT="$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/$POLICY_RUN_NAME/policy_model_epoch_${POLICY_EPOCHS}.ckpt"
if [ "${PGPR_FORCE_POLICY:-0}" = "1" ] || [ ! -f "$POLICY_CKPT" ]; then
  cd "$RUNTIME/models/PGPR"
  "$PGPR_PY" train_agent.py \
    --dataset amazon_book_kgat_v1 \
    --name "$POLICY_RUN_NAME" \
    --gpu "$PHYSICAL_GPU" \
    --epochs "$POLICY_EPOCHS" \
    --batch_size "$POLICY_BATCH_SIZE" \
    --max_acts "$POLICY_MAX_ACTS" \
    --max_path_len 3 \
    --state_history 1 \
    --hidden "${POLICY_HIDDEN[@]}" \
    --act_dropout 0.5
  cd "$ROOT"
fi
"$EVAL_PY" "$ROOT/scripts/validation/validate_pgpr_policy_training_smoke.py" \
  --runtime-root "$RUNTIME" \
  --dataset amazon_book_kgat_v1 \
  --run-name "$POLICY_RUN_NAME" \
  --epoch "$POLICY_EPOCHS" \
  --expected-state-dim "$POLICY_EXPECTED_STATE_DIM" \
  --expected-act-dim "$((POLICY_MAX_ACTS + 1))" \
  --expected-hidden "${POLICY_HIDDEN[@]}" \
  --summary-json "$POLICY_JSON"

write_status "RUNNING" "inference_export" "Running full-user PGPR Amazon inference and strict export validation"
if [ "$PGPR_USE_STREAMING_EXPORT" = "1" ]; then
  if [ "${PGPR_FORCE_INFERENCE:-0}" = "1" ] || [ ! -f "$PATHS_DIR/pred_paths.csv" ] || [ ! -f "$PATHS_DIR/uid_topk.csv" ] || [ ! -f "$PATHS_DIR/uid_pid_explanation.csv" ]; then
    "$PGPR_PY" "$ROOT/scripts/validation/export_pgpr_streaming.py" \
      --runtime-root "$RUNTIME" \
      --dataset amazon_book_kgat_v1 \
      --run-name "$POLICY_RUN_NAME" \
      --epoch "$POLICY_EPOCHS" \
      --embedding-pkl "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl" \
      --labels-dir "$CANONICAL_ROOT/labels" \
      --paths-dir "$PATHS_DIR" \
      --summary-json "$STREAMING_EXPORT_JSON" \
      --max-acts "$POLICY_MAX_ACTS" \
      --beam-batch-size "$INFERENCE_BATCH_SIZE" \
      --hidden "${POLICY_HIDDEN[@]}" \
      --topk "${FORMAL_TOPK[@]}" \
      --recommendation-topk 10
  fi
else
  if [ "${PGPR_FORCE_INFERENCE:-0}" = "1" ] || [ ! -f "$PATHS_PKL" ]; then
    "$PGPR_PY" "$ROOT/scripts/validation/run_pgpr_policy_inference_smoke.py" \
      --runtime-root "$RUNTIME" \
      --dataset amazon_book_kgat_v1 \
      --run-name "$POLICY_RUN_NAME" \
      --epoch "$POLICY_EPOCHS" \
      --summary-json "$INFERENCE_JSON" \
      --max-acts "$POLICY_MAX_ACTS" \
      --num-users 0 \
      --beam-batch-size "$INFERENCE_BATCH_SIZE" \
      --hidden "${POLICY_HIDDEN[@]}" \
      --topk "${FORMAL_TOPK[@]}" \
      --paths-pkl "$PATHS_PKL"
  fi

  "$PGPR_PY" "$ROOT/adapters/pgpr_adapter.py" \
    --pkl "$PATHS_PKL" \
    --embedding-pkl "$RUNTIME/models/PGPR/tmp/amazon_book_kgat_v1/transe_embed.pkl" \
    --dataset amazon_book_kgat_v1 \
    --xrecsys-dir "$ROOT/xrecsys" \
    --topk 10 \
    --agent-topk-tag "$AGENT_TOPK_TAG" \
    --labels-dir "$CANONICAL_ROOT/labels"
fi

"$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_export.py" \
  --paths-dir "$PATHS_DIR" \
  --labels-dir "$CANONICAL_ROOT/labels" \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --require-all-test-users \
  --summary-json "$EXPORT_SUMMARY_JSON"

"$EVAL_PY" "$ROOT/scripts/validation/evaluate_uid_topk.py" \
  --uid-topk "$PATHS_DIR/uid_topk.csv" \
  --labels-dir "$CANONICAL_ROOT/labels" \
  --topk 10 \
  --allow-short \
  --summary-json "$ACCURACY_JSON"

write_status "PASS" "complete" "PGPR Amazon formal pipeline completed with strict full-user validation"
echo "[$(date '+%F %T')] PGPR Amazon formal pipeline PASS"
