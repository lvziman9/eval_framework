#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
DATASET="${1:?usage: run_canonical_kgglm_pipeline.sh <canonical_ml1m_v1|canonical_lastfm_v1|canonical_amazon_book_kgat_v1> [physical_gpu]}"
PHYSICAL_GPU="${2:-}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
DATA_ROOT="$RUN_ROOT/hopwise_data"
OUT_ROOT="$RUN_ROOT/kgglm_formal/$DATASET"
PRETRAIN_CHECKPOINT_ROOT="$OUT_ROOT/pretrain_checkpoints"
FINETUNE_CHECKPOINT_ROOT="$OUT_ROOT/finetune_checkpoints"
EXPORT_CHECKPOINT_ROOT="$OUT_ROOT/export_checkpoints"
RAW_PATH="$OUT_ROOT/kgglm_paths.pkl"
SHARD_DIR="$OUT_ROOT/path_shards"
PY="/usr1/home/s125mdg43_08/miniconda3/envs/hopwise/bin/python"
EVAL_PY="/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python"

# The authors' official recommendation table reports three generic-path
# pretraining epochs and two recommendation-specific finetuning epochs.
PRETRAIN_EPOCHS="${PRETRAIN_EPOCHS:-3}"
FINETUNE_EPOCHS="${FINETUNE_EPOCHS:-2}"
EMBEDDING_SIZE="${EMBEDDING_SIZE:-768}"
NUM_HEADS="${NUM_HEADS:-12}"
NUM_LAYERS="${NUM_LAYERS:-6}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-256}"
WARMUP_STEPS="${WARMUP_STEPS:-250}"
PATHS_PER_USER="${PATHS_PER_USER:-25}"
NUM_BEAMS="${NUM_BEAMS:-25}"

case "$DATASET" in
  canonical_ml1m_v1)
    CANONICAL_DATASET="ml1m"
    LABELS_DIR="$RUN_ROOT/ml1m_v1/labels"
    EXPORT_BATCH_SIZE="${EXPORT_BATCH_SIZE:-32}"
    RUN_XRECSYS=1
    ;;
  canonical_lastfm_v1)
    CANONICAL_DATASET="lastfm"
    LABELS_DIR="$ROOT/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/labels"
    EXPORT_BATCH_SIZE="${EXPORT_BATCH_SIZE:-32}"
    RUN_XRECSYS=1
    ;;
  canonical_amazon_book_kgat_v1)
    CANONICAL_DATASET="amazon_book_kgat_v1"
    LABELS_DIR="$RUN_ROOT/amazon_book_kgat_v1/labels"
    EXPORT_BATCH_SIZE="${EXPORT_BATCH_SIZE:-16}"
    RUN_XRECSYS=0
    ;;
  *)
    echo "unsupported canonical KGGLM dataset: $DATASET" >&2
    exit 2
    ;;
esac

AGENT_TAG="kgglm-canonical-p${PRETRAIN_EPOCHS}-f${FINETUNE_EPOCHS}-h${EMBEDDING_SIZE}-l${NUM_LAYERS}-b${NUM_BEAMS}"
PATHS_DIR="$ROOT/xrecsys/paths/$CANONICAL_DATASET/agent_topk=$AGENT_TAG"
CANONICAL_RESULT_TAG="${AGENT_TAG}-canonical-all-users"
CANONICAL_RESULT_DIR="$ROOT/xrecsys/results/$CANONICAL_DATASET/agent_topk=$CANONICAL_RESULT_TAG"
GPU_ID=""
if [[ -n "$PHYSICAL_GPU" ]]; then
  export CUDA_DEVICE_ORDER=PCI_BUS_ID
  export CUDA_VISIBLE_DEVICES="$PHYSICAL_GPU"
  GPU_ID="$PHYSICAL_GPU"
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="/usr1/home/s125mdg43_08/hopwise:$ROOT"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1

mkdir -p \
  "$PRETRAIN_CHECKPOINT_ROOT" \
  "$FINETUNE_CHECKPOINT_ROOT" \
  "$EXPORT_CHECKPOINT_ROOT" \
  "$SHARD_DIR"
cd "$ROOT"

echo "[$(date '+%F %T')] KGGLM canonical formal pipeline start"
echo "dataset=$DATASET physical_gpu=${PHYSICAL_GPU:-CPU} agent_tag=$AGENT_TAG"

if [[ ! -f "$OUT_ROOT/pretrain.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_native_path.py \
    --model KGGLM \
    --train-stage pretrain \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$PRETRAIN_CHECKPOINT_ROOT" \
    --output "$OUT_ROOT/pretrain.json" \
    --gpu-id "$GPU_ID" \
    --epochs 1 \
    --pretrain-epochs "$PRETRAIN_EPOCHS" \
    --save-step 1 \
    --pretrain-paths 1 \
    --embedding-size "$EMBEDDING_SIZE" \
    --num-heads "$NUM_HEADS" \
    --num-layers "$NUM_LAYERS" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --warmup-steps "$WARMUP_STEPS" \
    --experiment-kind "formal canonical KGGLM generic-path pretraining" \
    --skip-test-evaluation
  touch "$OUT_ROOT/pretrain.complete"
fi

PRETRAIN_CHECKPOINT="$(
  find "$PRETRAIN_CHECKPOINT_ROOT" -type f -name model.safetensors \
    -printf '%T@ %h\n' |
    sort -nr |
    sed -n '1s/^[^ ]* //p'
)"
test -n "$PRETRAIN_CHECKPOINT"
test -f "$PRETRAIN_CHECKPOINT/model.safetensors"
test -f "$PRETRAIN_CHECKPOINT/config.json"
echo "pretrain_checkpoint=$PRETRAIN_CHECKPOINT"

if [[ ! -f "$OUT_ROOT/finetune.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_native_path.py \
    --model KGGLM \
    --train-stage finetune \
    --pre-model-path "$PRETRAIN_CHECKPOINT" \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$FINETUNE_CHECKPOINT_ROOT" \
    --output "$OUT_ROOT/finetune.json" \
    --gpu-id "$GPU_ID" \
    --epochs "$FINETUNE_EPOCHS" \
    --pretrain-epochs "$PRETRAIN_EPOCHS" \
    --embedding-size "$EMBEDDING_SIZE" \
    --num-heads "$NUM_HEADS" \
    --num-layers "$NUM_LAYERS" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --warmup-steps "$WARMUP_STEPS" \
    --eval-step 1 \
    --stopping-step 2 \
    --validation-paths-per-user 10 \
    --validation-num-beams 10 \
    --select-best-validation \
    --experiment-kind "formal canonical KGGLM recommendation-path finetuning" \
    --skip-test-evaluation
  touch "$OUT_ROOT/finetune.complete"
fi

FINETUNE_CHECKPOINT="$(
  find "$FINETUNE_CHECKPOINT_ROOT" -mindepth 1 -maxdepth 4 -type f -name model.safetensors \
    -printf '%T@ %h\n' |
    sort -nr |
    sed -n '1s/^[^ ]* //p'
)"
test -n "$FINETUNE_CHECKPOINT"
test -f "$FINETUNE_CHECKPOINT/model.safetensors"
echo "finetune_checkpoint=$FINETUNE_CHECKPOINT"

if [[ ! -f "$OUT_ROOT/paths.complete" ]]; then
  "$PY" scripts/hopwise/export_native_paths.py \
    --model KGGLM \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint "$FINETUNE_CHECKPOINT" \
    --pre-model-path "$PRETRAIN_CHECKPOINT" \
    --checkpoint-dir "$EXPORT_CHECKPOINT_ROOT" \
    --output "$RAW_PATH" \
    --shard-dir "$SHARD_DIR" \
    --gpu-id "$GPU_ID" \
    --embedding-size "$EMBEDDING_SIZE" \
    --num-heads "$NUM_HEADS" \
    --num-layers "$NUM_LAYERS" \
    --paths-per-user "$PATHS_PER_USER" \
    --num-beams "$NUM_BEAMS" \
    --batch-size "$EXPORT_BATCH_SIZE"
  touch "$OUT_ROOT/paths.complete"
fi

"$EVAL_PY" adapters/hopwise_adapter.py \
  --raw-path "$RAW_PATH" \
  --xrecsys-dir "$ROOT/xrecsys" \
  --labels-dir "$LABELS_DIR" \
  --topk 10 \
  --agent-topk-tag "$AGENT_TAG" \
  --include-all-test-users \
  --summary-json "$OUT_ROOT/adapter.json"

"$EVAL_PY" scripts/validation/validate_xrecsys_export.py \
  --paths-dir "$PATHS_DIR" \
  --labels-dir "$LABELS_DIR" \
  --dataset "$CANONICAL_DATASET" \
  --topk 10 \
  --require-all-test-users \
  --summary-json "$OUT_ROOT/export_validation.json"

"$EVAL_PY" scripts/validation/evaluate_uid_topk.py \
  --uid-topk "$PATHS_DIR/uid_topk.csv" \
  --labels-dir "$LABELS_DIR" \
  --topk 10 \
  --allow-short \
  --summary-json "$OUT_ROOT/accuracy.json"

if [[ "$RUN_XRECSYS" -eq 1 ]]; then
  /bin/bash "$ROOT/scripts/hopwise/run_canonical_xrecsys_protocol.sh" \
    "$CANONICAL_DATASET" \
    "$AGENT_TAG" \
    "$LABELS_DIR" \
    "$CANONICAL_RESULT_TAG"

  "$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_sweeps.py" \
    --results-dir "$CANONICAL_RESULT_DIR" \
    --summary-json "$OUT_ROOT/xrecsys_sweeps_validation.json"
else
  printf '%s\n' \
    'Amazon-book xrecsys explanation sweeps are intentionally not run: timestamps are unavailable and no canonical SEP/ETD denominator has been approved.' \
    > "$OUT_ROOT/xrecsys_not_applicable.txt"
fi

touch "$OUT_ROOT/pipeline.complete"
echo "[$(date '+%F %T')] KGGLM canonical formal pipeline complete"
