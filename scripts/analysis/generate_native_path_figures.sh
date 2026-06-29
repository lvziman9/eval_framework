#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(git rev-parse --show-toplevel)}"
PY="${PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
DATASET="${1:?usage: generate_native_path_figures.sh <lastfm|ml1m>}"

export MPLCONFIGDIR="${MPLCONFIGDIR:-$ROOT/.cache/matplotlib}"
mkdir -p "$MPLCONFIGDIR"

if [[ "$DATASET" == "lastfm" ]]; then
  OUT="$ROOT/reports/figures/tradeoff/canonical_lastfm_native_paths_v4_six_model"
  MODELS=(
    "PGPR=$ROOT/xrecsys/results/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score"
    "UCPR=$ROOT/xrecsys/results/lastfm/agent_topk=25-50-1-ucpr-canonical-matched"
    "CAFE=$ROOT/xrecsys/results/lastfm/agent_topk=cafe-canonical-lastfm"
    "TPRec=$ROOT/xrecsys/results/lastfm/agent_topk=tprec-canonical-e50-25-50-1"
    "KGGLM=$ROOT/xrecsys/results/lastfm/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users"
    "PEARLM=$ROOT/xrecsys/results/lastfm/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users"
  )
elif [[ "$DATASET" == "ml1m" ]]; then
  OUT="$ROOT/reports/figures/tradeoff/canonical_ml1m_native_paths_v2"
  MODELS=(
    "PGPR=$ROOT/xrecsys/results/ml1m/agent_topk=25-50-1-pgpr-canonical-ml1m-canonical-all-users"
    "UCPR=$ROOT/xrecsys/results/ml1m/agent_topk=25-50-1-ucpr-canonical-ml1m-canonical-all-users"
    "CAFE=$ROOT/xrecsys/results/ml1m/agent_topk=cafe-canonical-ml1m-canonical-all-users"
    "TPRec=$ROOT/xrecsys/results/ml1m/agent_topk=tprec-canonical-e50-25-50-1-canonical-all-users"
    "KGGLM=$ROOT/xrecsys/results/ml1m/agent_topk=kgglm-canonical-p3-f2-h768-l6-b25-canonical-all-users"
    "PEARLM=$ROOT/xrecsys/results/ml1m/agent_topk=pearlm-canonical-bestval10-e50-h768-l6-b25-canonical-all-users"
  )
else
  echo "Unsupported dataset: $DATASET" >&2
  exit 2
fi

mkdir -p "$OUT"
for METRIC in LIR SEP ETD; do
  "$PY" "$ROOT/scripts/analysis/tradeoff_analyzer.py" \
    --dataset "$DATASET" \
    --models "${MODELS[@]}" \
    --exp-metric "$METRIC" \
    --out "$OUT"
done

echo "Generated $DATASET native-path figures in $OUT"
