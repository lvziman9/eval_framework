#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
FRAMEWORK="${FRAMEWORK:-/usr1/home/s125mdg43_08/rep-path-reasoning-recsys}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
CANONICAL_ROOT="$RUN_ROOT/amazon_book_kgat_v1"
UCPR_VIEW="$CANONICAL_ROOT/model_views/ucpr/preprocessed/ucpr"
UCPR_MAPS="$CANONICAL_ROOT/model_views/ucpr/preprocessed"
RUNTIME="${UCPR_AMAZON_RUNTIME:-$RUN_ROOT/ucpr_amazon_book_kgat_runtime_formal}"
RUNTIME_DATA="$RUNTIME/data/amazon_book_kgat_v1/preprocessed/ucpr"
LABELS_DIR="$CANONICAL_ROOT/labels"
REP_PY="${REP_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/rep/bin/python}"
EVAL_PY="${EVAL_PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
PHYSICAL_GPU="${1:-${UCPR_GPU:-0}}"

TRANSE_EPOCHS="${UCPR_TRANSE_EPOCHS:-30}"
TRANSE_EMBED_SIZE="${UCPR_TRANSE_EMBED_SIZE:-100}"
TRANSE_BATCH_SIZE="${UCPR_TRANSE_BATCH_SIZE:-512}"
TRANSE_NEG_SAMPLES="${UCPR_TRANSE_NEG_SAMPLES:-5}"
TRANSE_RUN_NAME="${UCPR_TRANSE_RUN_NAME:-train_transe_model_amazon_formal_e${TRANSE_EPOCHS}_d${TRANSE_EMBED_SIZE}_b${TRANSE_BATCH_SIZE}_n${TRANSE_NEG_SAMPLES}}"

POLICY_EPOCHS="${UCPR_POLICY_EPOCHS:-40}"
POLICY_BATCH_SIZE="${UCPR_POLICY_BATCH_SIZE:-16}"
POLICY_RUN_NAME="${UCPR_POLICY_RUN_NAME:-train_agent_amazon_formal_e${POLICY_EPOCHS}_b${POLICY_BATCH_SIZE}_d${TRANSE_EMBED_SIZE}}"

FORMAL_TOPK_TEXT="${UCPR_FORMAL_TOPK:-25 5 1}"
read -r -a FORMAL_TOPK <<< "$FORMAL_TOPK_TEXT"
if [ "${#FORMAL_TOPK[@]}" -ne 3 ]; then
  echo "UCPR_FORMAL_TOPK must contain exactly three integers, got: $FORMAL_TOPK_TEXT" >&2
  exit 2
fi
BEAM_TAG="${FORMAL_TOPK[0]}-${FORMAL_TOPK[1]}-${FORMAL_TOPK[2]}"
BEAM_BATCH_SIZE="${UCPR_BEAM_BATCH_SIZE:-4}"
AGENT_TOPK_TAG="${UCPR_AGENT_TOPK_TAG:-${BEAM_TAG}-ucpr-amazon-formal-e${POLICY_EPOCHS}}"
UCPR_RUN_INFERENCE="${UCPR_RUN_INFERENCE:-0}"
UCPR_USE_STREAMING_EXPORT="${UCPR_USE_STREAMING_EXPORT:-1}"

STATUS_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_formal_pipeline_status.json"
PREPROCESS_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_preprocess_validation.json"
TRANSE_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_transe_formal_status.json"
POLICY_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_policy_formal_status.json"
INFERENCE_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_inference_formal_status.json"
STREAMING_EXPORT_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_streaming_export_formal.json"
EXPORT_SUMMARY_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_export_validation.json"
ACCURACY_JSON="$RUN_ROOT/ucpr_amazon_book_kgat_accuracy.json"
RAW_PATHS="$RUNTIME_DATA/tmp/policy_paths_epoch${POLICY_EPOCHS}_${BEAM_TAG}.pkl"
PRED_PKL="$RUNTIME/results/amazon_book_kgat_v1/ucpr/pred_paths.pkl"
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
    "physical_gpu": "$PHYSICAL_GPU",
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
    },
    "export": {
        "run_inference": "$UCPR_RUN_INFERENCE",
        "beam_topk": [int("$FORMAL_TOPK_TEXT".split()[0]), int("$FORMAL_TOPK_TEXT".split()[1]), int("$FORMAL_TOPK_TEXT".split()[2])],
        "beam_batch_size": int("$BEAM_BATCH_SIZE"),
        "agent_topk_tag": "$AGENT_TOPK_TAG",
        "raw_paths": "$RAW_PATHS",
        "pred_pkl": "$PRED_PKL",
        "paths_dir": "$PATHS_DIR",
        "streaming_export": "$STREAMING_EXPORT_JSON",
        "streaming_export_enabled": "$UCPR_USE_STREAMING_EXPORT",
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
  write_status "FAILED" "line_${line}" "UCPR Amazon formal pipeline failed"
}
trap 'on_error "$LINENO"' ERR

echo "[$(date '+%F %T')] UCPR Amazon formal pipeline start"
echo "runtime=$RUNTIME"
echo "physical_gpu=$PHYSICAL_GPU"
echo "transe=$TRANSE_RUN_NAME epochs=$TRANSE_EPOCHS embed=$TRANSE_EMBED_SIZE batch=$TRANSE_BATCH_SIZE neg=$TRANSE_NEG_SAMPLES"
echo "policy=$POLICY_RUN_NAME epochs=$POLICY_EPOCHS batch=$POLICY_BATCH_SIZE"
echo "export tag=$AGENT_TOPK_TAG topk=${FORMAL_TOPK[*]} beam_batch=$BEAM_BATCH_SIZE run_inference=$UCPR_RUN_INFERENCE streaming=$UCPR_USE_STREAMING_EXPORT"
write_status "RUNNING" "prepare_runtime" "Preparing isolated UCPR Amazon formal runtime"

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

export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES="$PHYSICAL_GPU"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export PYTHONPATH="$RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

cd "$RUNTIME/models/UCPR"

write_status "RUNNING" "preprocess" "Running or validating UCPR Amazon preprocessing"
if [[ "${UCPR_FORCE_PREPROCESS:-0}" = "1" || ! -f "$RUNTIME_DATA/tmp/dataset.pkl" || ! -f "$RUNTIME_DATA/tmp/kg.pkl" ]]; then
  "$REP_PY" preprocess.py --dataset amazon_book_kgat_v1
fi

"$REP_PY" "$ROOT/scripts/validation/validate_ucpr_preprocess_smoke.py" \
  --runtime-root "$RUNTIME" \
  --canonical-root "$CANONICAL_ROOT" \
  --view-root "$UCPR_MAPS" \
  --dataset amazon_book_kgat_v1 \
  --summary-json "$PREPROCESS_JSON"

write_status "RUNNING" "transe" "Training or validating formal UCPR Amazon TransE embeddings"
TRANSE_DIR="$RUNTIME_DATA/tmp/$TRANSE_RUN_NAME"
TRANSE_BEST="$TRANSE_DIR/transe_best_model.ckpt"
TRANSE_EMBED="$RUNTIME_DATA/tmp/transe_embed.pkl"
if [[ "${UCPR_FORCE_TRANSE:-0}" = "1" || ! -f "$TRANSE_BEST" || ! -f "$TRANSE_EMBED" ]]; then
  "$REP_PY" preprocess/train_transe.py \
    --dataset amazon_book_kgat_v1 \
    --name "$TRANSE_RUN_NAME" \
    --gpu "$PHYSICAL_GPU" \
    --epochs "$TRANSE_EPOCHS" \
    --batch_size "$TRANSE_BATCH_SIZE" \
    --embed_size "$TRANSE_EMBED_SIZE" \
    --num_neg_samples "$TRANSE_NEG_SAMPLES"
fi

"$EVAL_PY" - "$TRANSE_JSON" "$TRANSE_BEST" "$TRANSE_EMBED" "$TRANSE_RUN_NAME" <<PY
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

summary = {
    "dataset": "amazon_book_kgat_v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "PASS",
    "run_name": sys.argv[4],
    "transe_best_model": {"path": sys.argv[2], "exists": Path(sys.argv[2]).exists(), "size_bytes": Path(sys.argv[2]).stat().st_size if Path(sys.argv[2]).exists() else 0},
    "transe_embed": {"path": sys.argv[3], "exists": Path(sys.argv[3]).exists(), "size_bytes": Path(sys.argv[3]).stat().st_size if Path(sys.argv[3]).exists() else 0},
}
if not (summary["transe_best_model"]["exists"] and summary["transe_embed"]["exists"]):
    summary["status"] = "FAIL"
Path(sys.argv[1]).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if summary["status"] != "PASS":
    raise SystemExit(1)
PY

write_status "RUNNING" "policy" "Training or validating formal UCPR Amazon policy checkpoint"
POLICY="$RUNTIME_DATA/tmp/policy_model_epoch_${POLICY_EPOCHS}.ckpt"
if [[ "${UCPR_FORCE_POLICY:-0}" = "1" || ! -f "$POLICY" ]]; then
  "$REP_PY" train.py \
    --dataset amazon_book_kgat_v1 \
    --name "$POLICY_RUN_NAME" \
    --gpu 0 \
    --epochs "$POLICY_EPOCHS" \
    --batch_size "$POLICY_BATCH_SIZE" \
    --early_stop_patience 0 \
    --KGE_pretrained 1 \
    --embed_size "$TRANSE_EMBED_SIZE"
fi

"$EVAL_PY" - "$POLICY_JSON" "$POLICY" "$POLICY_RUN_NAME" <<PY
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

policy = Path(sys.argv[2])
summary = {
    "dataset": "amazon_book_kgat_v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "PASS" if policy.exists() else "FAIL",
    "run_name": sys.argv[3],
    "policy_checkpoint": {
        "path": str(policy),
        "exists": policy.exists(),
        "size_bytes": policy.stat().st_size if policy.exists() else 0,
    },
}
Path(sys.argv[1]).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if summary["status"] != "PASS":
    raise SystemExit(1)
PY

if [[ "$UCPR_RUN_INFERENCE" != "1" ]]; then
  write_status "INFERENCE_DEFERRED" "policy_complete" "UCPR Amazon formal training completed; full-user inference/export intentionally deferred pending memory-safe streaming path"
  echo "[$(date '+%F %T')] UCPR Amazon formal training complete; inference deferred"
  exit 0
fi

write_status "RUNNING" "inference_export" "Running UCPR Amazon full-user inference/export"
if [[ "$UCPR_USE_STREAMING_EXPORT" = "1" ]]; then
  if [[ "${UCPR_FORCE_INFERENCE:-0}" = "1" || ! -f "$PATHS_DIR/pred_paths.csv" || ! -f "$PATHS_DIR/uid_topk.csv" || ! -f "$PATHS_DIR/uid_pid_explanation.csv" ]]; then
    cd "$ROOT"
    "$REP_PY" scripts/validation/export_ucpr_streaming.py \
      --runtime-root "$RUNTIME" \
      --dataset amazon_book_kgat_v1 \
      --run-name "$POLICY_RUN_NAME" \
      --epoch "$POLICY_EPOCHS" \
      --policy-path "$POLICY" \
      --labels-dir "$LABELS_DIR" \
      --user-remap "$UCPR_MAPS/user_remap.tsv" \
      --product-remap "$UCPR_MAPS/product_remap.tsv" \
      --paths-dir "$PATHS_DIR" \
      --summary-json "$STREAMING_EXPORT_JSON" \
      --gpu 0 \
      --embed-size "$TRANSE_EMBED_SIZE" \
      --max-acts 50 \
      --beam-batch-size "$BEAM_BATCH_SIZE" \
      --topk "${FORMAL_TOPK[@]}" \
      --recommendation-topk 10
  fi
else
  if [[ "${UCPR_FORCE_INFERENCE:-0}" = "1" || ! -f "$RAW_PATHS" ]]; then
    "$REP_PY" test.py \
      --dataset amazon_book_kgat_v1 \
      --name "$POLICY_RUN_NAME" \
      --gpu 0 \
      --best_model_epoch "$POLICY_EPOCHS" \
      --policy_path "$POLICY" \
      --topk "${FORMAL_TOPK[@]}" \
      --beam_batch_size "$BEAM_BATCH_SIZE" \
      --run_path True \
      --run_eval False \
      --save_paths False \
      --KGE_pretrained 1 \
      --embed_size "$TRANSE_EMBED_SIZE"
  fi

  if [[ "${UCPR_FORCE_EXPORT:-0}" = "1" || ! -f "$PRED_PKL" ]]; then
    "$REP_PY" test.py \
      --dataset amazon_book_kgat_v1 \
      --name "$POLICY_RUN_NAME" \
      --gpu 0 \
      --best_model_epoch "$POLICY_EPOCHS" \
      --policy_path "$POLICY" \
      --topk "${FORMAL_TOPK[@]}" \
      --beam_batch_size "$BEAM_BATCH_SIZE" \
      --run_path False \
      --run_eval False \
      --save_paths True \
      --KGE_pretrained 1 \
      --embed_size "$TRANSE_EMBED_SIZE"
  fi

  cd "$ROOT"
  "$REP_PY" adapters/ucpr_adapter.py \
    --pred-pkl "$PRED_PKL" \
    --dataset amazon_book_kgat_v1 \
    --xrecsys-dir "$ROOT/xrecsys" \
    --topk 10 \
    --agent-topk-tag "$AGENT_TOPK_TAG" \
    --user-remap "$UCPR_MAPS/user_remap.tsv" \
    --product-remap "$UCPR_MAPS/product_remap.tsv" \
    --labels-dir "$LABELS_DIR"
fi

"$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_export.py" \
  --paths-dir "$PATHS_DIR" \
  --labels-dir "$LABELS_DIR" \
  --dataset amazon_book_kgat_v1 \
  --topk 10 \
  --require-all-test-users \
  --summary-json "$EXPORT_SUMMARY_JSON"

"$EVAL_PY" "$ROOT/scripts/validation/evaluate_uid_topk.py" \
  --uid-topk "$PATHS_DIR/uid_topk.csv" \
  --labels-dir "$LABELS_DIR" \
  --topk 10 \
  --allow-short \
  --summary-json "$ACCURACY_JSON"

write_status "PASS" "complete" "UCPR Amazon formal pipeline completed with strict full-user validation"
echo "[$(date '+%F %T')] UCPR Amazon formal pipeline PASS"
