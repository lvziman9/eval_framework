#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
DATASET="${1:?usage: run_canonical_tprec_pipeline.sh <canonical_ml1m_v1|canonical_lastfm_v1|canonical_amazon_book_kgat_v1> [physical_gpu]}"
PHYSICAL_GPU="${2:-}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
DATA_ROOT="$RUN_ROOT/hopwise_data"
OUT_ROOT="$RUN_ROOT/tprec_formal/$DATASET"
CHECKPOINT_DIR="$OUT_ROOT/checkpoints"
PY="/usr1/home/s125mdg43_08/miniconda3/envs/hopwise/bin/python"
EVAL_PY="/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python"

TRANSE_EPOCHS="${TRANSE_EPOCHS:-50}"
PRETRAIN_EPOCHS="${PRETRAIN_EPOCHS:-5}"
POLICY_EPOCHS="${POLICY_EPOCHS:-50}"
BEAM_FIRST="${BEAM_FIRST:-25}"
BEAM_SECOND="${BEAM_SECOND:-50}"
BEAM_THIRD="${BEAM_THIRD:-1}"

case "$DATASET" in
  canonical_ml1m_v1)
    CANONICAL_DATASET="ml1m"
    LABELS_DIR="$RUN_ROOT/ml1m_v1/labels"
    TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-2048}"
    EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-8}"
    ;;
  canonical_lastfm_v1)
    CANONICAL_DATASET="lastfm"
    LABELS_DIR="$ROOT/runs/debug_compare/2026-04-14_canonical_dataset/lastfm_v1/labels"
    TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-4096}"
    EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-4}"
    ;;
  canonical_amazon_book_kgat_v1)
    CANONICAL_DATASET="amazon_book_kgat_v1"
    LABELS_DIR="$RUN_ROOT/amazon_book_kgat_v1/labels"
    TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-2048}"
    EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-4}"
    "$EVAL_PY" "$ROOT/scripts/validation/audit_tprec_amazon_timestamp_semantics.py" \
      --summary-json "$RUN_ROOT/amazon_book_kgat_v1/model_views/tprec/tprec_timestamp_semantics_audit.json"
    if [[ "${TPREC_ALLOW_TIMESTAMPLESS_AMAZON:-0}" != "1" ]]; then
      echo "Amazon TPRec formal run blocked: canonical_amazon_book_kgat_v1 timestamps are sentinel -1." >&2
      echo "Set TPREC_ALLOW_TIMESTAMPLESS_AMAZON=1 only for an explicitly documented non-temporal ablation, not for formal TPRec reporting." >&2
      exit 3
    fi
    ;;
  *)
    echo "unsupported canonical TPRec dataset: $DATASET" >&2
    exit 2
    ;;
esac

AGENT_TAG="tprec-canonical-e${POLICY_EPOCHS}-${BEAM_FIRST}-${BEAM_SECOND}-${BEAM_THIRD}"
RAW_PATH="$OUT_ROOT/tprec_paths.pkl"
PATH_SHARD_DIR="$OUT_ROOT/path_shards"
PATHS_DIR="$ROOT/xrecsys/paths/$CANONICAL_DATASET/agent_topk=$AGENT_TAG"
GPU_ID=""
if [[ -n "$PHYSICAL_GPU" ]]; then
  export CUDA_DEVICE_ORDER=PCI_BUS_ID
  export CUDA_VISIBLE_DEVICES="$PHYSICAL_GPU"
  # Hopwise/RecBole Config rewrites CUDA_VISIBLE_DEVICES from gpu_id during
  # initialization, so pass the physical id instead of the post-mask ordinal.
  GPU_ID="$PHYSICAL_GPU"
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="/usr1/home/s125mdg43_08/hopwise:$ROOT"
export PYTHONUNBUFFERED=1

mkdir -p "$CHECKPOINT_DIR"
cd "$ROOT"

checkpoint_from_json() {
  "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["checkpoint"])' "$1"
}

echo "[$(date '+%F %T')] TPRec canonical pipeline start"
echo "dataset=$DATASET physical_gpu=${PHYSICAL_GPU:-CPU} agent_tag=$AGENT_TAG"

if [[ ! -f "$OUT_ROOT/transe.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_tprec.py \
    --stage transe \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --output "$OUT_ROOT/transe.json" \
    --gpu-id "$GPU_ID" \
    --epochs "$TRANSE_EPOCHS" \
    --embedding-size 100 \
    --train-batch-size "$TRAIN_BATCH_SIZE"
  touch "$OUT_ROOT/transe.complete"
fi
TRANSE_CHECKPOINT="$(checkpoint_from_json "$OUT_ROOT/transe.json")"
test -f "$TRANSE_CHECKPOINT"

if [[ ! -f "$OUT_ROOT/transe_embedding_export.complete" ]]; then
  "$PY" scripts/hopwise/export_transe_embeddings.py \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --checkpoint "$TRANSE_CHECKPOINT" \
    --embedding-size 100 \
    --summary-json "$OUT_ROOT/transe_embedding_export.json"
  touch "$OUT_ROOT/transe_embedding_export.complete"
fi

if [[ ! -f "$OUT_ROOT/preflight.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_tprec.py \
    --stage preflight \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --output "$OUT_ROOT/preflight.json" \
    --transe-checkpoint "$TRANSE_CHECKPOINT" \
    --gpu-id "$GPU_ID" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --eval-batch-size "$EVAL_BATCH_SIZE"
  touch "$OUT_ROOT/preflight.complete"
fi

if [[ ! -f "$OUT_ROOT/pretrain.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_tprec.py \
    --stage pretrain \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --output "$OUT_ROOT/pretrain.json" \
    --transe-checkpoint "$TRANSE_CHECKPOINT" \
    --gpu-id "$GPU_ID" \
    --epochs "$PRETRAIN_EPOCHS" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --eval-batch-size "$EVAL_BATCH_SIZE"
  touch "$OUT_ROOT/pretrain.complete"
fi
PRETRAIN_CHECKPOINT="$(checkpoint_from_json "$OUT_ROOT/pretrain.json")"
test -f "$PRETRAIN_CHECKPOINT"

if [[ ! -f "$OUT_ROOT/policy.complete" ]]; then
  "$PY" scripts/hopwise/run_canonical_tprec.py \
    --stage policy \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --output "$OUT_ROOT/policy.json" \
    --pretrained-checkpoint "$PRETRAIN_CHECKPOINT" \
    --gpu-id "$GPU_ID" \
    --epochs "$POLICY_EPOCHS" \
    --train-batch-size "$TRAIN_BATCH_SIZE" \
    --eval-batch-size "$EVAL_BATCH_SIZE" \
    --beam-search-hop "$BEAM_FIRST" "$BEAM_SECOND" "$BEAM_THIRD"
  touch "$OUT_ROOT/policy.complete"
fi
POLICY_CHECKPOINT="$(checkpoint_from_json "$OUT_ROOT/policy.json")"
test -f "$POLICY_CHECKPOINT"

if [[ ! -f "$OUT_ROOT/paths.complete" ]]; then
  "$PY" scripts/hopwise/export_tprec_paths.py \
    --dataset "$DATASET" \
    --data-root "$DATA_ROOT" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --policy-checkpoint "$POLICY_CHECKPOINT" \
    --output "$RAW_PATH" \
    --shard-dir "$PATH_SHARD_DIR" \
    --summary-json "$OUT_ROOT/path_export.json" \
    --gpu-id "$GPU_ID" \
    --batch-size "$EVAL_BATCH_SIZE" \
    --beam-search-hop "$BEAM_FIRST" "$BEAM_SECOND" "$BEAM_THIRD" \
    --verify-determinism
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

cd "$ROOT/xrecsys"
"$EVAL_PY" main.py \
  --dataset "$CANONICAL_DATASET" \
  --agent_topk "$AGENT_TAG" \
  --labels_dir "$LABELS_DIR" \
  --eval_baseline True \
  --only_baseline
for OPT in LIRopt SEPopt ETDopt; do
  "$EVAL_PY" main.py \
    --dataset "$CANONICAL_DATASET" \
    --agent_topk "$AGENT_TAG" \
    --labels_dir "$LABELS_DIR" \
    --opt "$OPT" \
    --resume-moving-alpha
done

"$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_sweeps.py" \
  --results-dir "$ROOT/xrecsys/results/$CANONICAL_DATASET/agent_topk=$AGENT_TAG" \
  --summary-json "$OUT_ROOT/xrecsys_sweeps_validation.json"

touch "$OUT_ROOT/pipeline.complete"
echo "[$(date '+%F %T')] TPRec canonical pipeline complete"
