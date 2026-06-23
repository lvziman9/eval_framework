#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
DATASET="${1:?usage: run_canonical_xrecsys_protocol.sh <ml1m|lastfm> <path_agent_tag> <labels_dir> [result_tag]}"
AGENT_TAG="${2:?missing path agent tag}"
LABELS_DIR="${3:?missing labels directory}"
RESULT_TAG="${4:-${AGENT_TAG}-canonical-all-users}"
EVAL_PY="/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python"
RESULT_DIR="$ROOT/xrecsys/results/$DATASET/agent_topk=$RESULT_TAG"

cd "$ROOT/xrecsys"
"$EVAL_PY" main.py \
  --dataset "$DATASET" \
  --agent_topk "$AGENT_TAG" \
  --result_tag "$RESULT_TAG" \
  --labels_dir "$LABELS_DIR" \
  --rec_eval_protocol canonical-all-users \
  --eval_baseline True \
  --only_baseline

for OPT in LIRopt SEPopt ETDopt; do
  "$EVAL_PY" main.py \
    --dataset "$DATASET" \
    --agent_topk "$AGENT_TAG" \
    --result_tag "$RESULT_TAG" \
    --labels_dir "$LABELS_DIR" \
    --rec_eval_protocol canonical-all-users \
    --opt "$OPT" \
    --resume-moving-alpha
done

"$EVAL_PY" "$ROOT/scripts/validation/validate_xrecsys_sweeps.py" \
  --results-dir "$RESULT_DIR" \
  --summary-json "$RESULT_DIR/sweeps_validation.json"

touch "$RESULT_DIR/canonical_protocol.complete"
echo "canonical xrecsys protocol complete: $RESULT_DIR"
