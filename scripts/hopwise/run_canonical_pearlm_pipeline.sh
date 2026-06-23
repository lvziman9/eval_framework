#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
DATASET="${1:?usage: run_canonical_pearlm_pipeline.sh <canonical_ml1m_v1|canonical_lastfm_v1|canonical_amazon_book_kgat_v1> [physical_gpu]}"
PHYSICAL_GPU="${2:-}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
DATA_ROOT="$RUN_ROOT/hopwise_data"
OUT_ROOT="$RUN_ROOT/pearlm_formal_bestval10/$DATASET"
CHECKPOINT_ROOT="$OUT_ROOT/checkpoints"
EXPORT_CHECKPOINT_ROOT="$OUT_ROOT/export_checkpoints"
RAW_PATH="$OUT_ROOT/pearlm_paths.pkl"
SHARD_DIR="$OUT_ROOT/path_shards"
PY="/usr1/home/s125mdg43_08/miniconda3/envs/hopwise/bin/python"
EVAL_PY="/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python"

EPOCHS="${EPOCHS:-50}"
EMBEDDING_SIZE="${EMBEDDING_SIZE:-768}"
NUM_HEADS="${NUM_HEADS:-12}"
NUM_LAYERS="${NUM_LAYERS:-6}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-64}"
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
    echo "unsupported canonical PEARLM dataset: $DATASET" >&2
    exit 2
    ;;
esac

AGENT_TAG="pearlm-canonical-bestval10-e${EPOCHS}-h${EMBEDDING_SIZE}-l${NUM_LAYERS}-b${NUM_BEAMS}"
PATHS_DIR="$ROOT/xrecsys/paths/$CANONICAL_DATASET/agent_topk=$AGENT_TAG"
CANONICAL_RESULT_TAG="${AGENT_TAG}-canonical-all-users"
CANONICAL_RESULT_DIR="$ROOT/xrecsys/results/$CANONICAL_DATASET/agent_topk=$CANONICAL_RESULT_TAG"
GPU_ID=""
if [[ -n "$PHYSICAL_GPU" ]]; then
  export CUDA_DEVICE_ORDER=PCI_BUS_ID
  export CUDA_VISIBLE_DEVICES="$PHYSICAL_GPU"
  # Hopwise rewrites CUDA_VISIBLE_DEVICES from gpu_id during Config setup.
  GPU_ID="$PHYSICAL_GPU"
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="/usr1/home/s125mdg43_08/hopwise:$ROOT"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1

mkdir -p "$CHECKPOINT_ROOT" "$EXPORT_CHECKPOINT_ROOT" "$SHARD_DIR"
cd "$ROOT"

echo "[$(date '+%F %T')] PEARLM canonical formal pipeline start"
echo "dataset=$DATASET physical_gpu=${PHYSICAL_GPU:-CPU} agent_tag=$AGENT_TAG"

if [[ ! -f "$OUT_ROOT/train.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_native_path.py \
    --model PEARLM \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_ROOT" \
    --output "$OUT_ROOT/train.json" \
    --gpu-id "$GPU_ID" \
    --epochs "$EPOCHS" \
    --embedding-size "$EMBEDDING_SIZE" \
    --num-heads "$NUM_HEADS" \
    --num-layers "$NUM_LAYERS" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --warmup-steps "$WARMUP_STEPS" \
    --eval-step 5 \
    --stopping-step 5 \
    --validation-paths-per-user 10 \
    --validation-num-beams 10 \
    --select-best-validation \
    --experiment-kind "formal canonical native-path baseline" \
    --skip-test-evaluation
  touch "$OUT_ROOT/train.complete"
fi

CHECKPOINT="$(
  find "$CHECKPOINT_ROOT" -mindepth 1 -maxdepth 1 -type d \
    -exec test -f '{}/model.safetensors' ';' -printf '%T@ %p\n' |
    sort -nr |
    sed -n '1s/^[^ ]* //p'
)"
test -n "$CHECKPOINT"
test -f "$CHECKPOINT/model.safetensors"
echo "checkpoint=$CHECKPOINT"

if [[ ! -f "$OUT_ROOT/paths.complete" ]]; then
  "$PY" scripts/hopwise/export_native_paths.py \
    --model PEARLM \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint "$CHECKPOINT" \
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
echo "[$(date '+%F %T')] PEARLM canonical formal pipeline complete"
