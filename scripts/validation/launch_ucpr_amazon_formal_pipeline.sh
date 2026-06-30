#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
LOG_FILE="${UCPR_FORMAL_LOG:-$RUN_ROOT/ucpr_amazon_book_kgat_formal_pipeline.log}"
PID_FILE="${UCPR_FORMAL_PID:-$RUN_ROOT/ucpr_amazon_book_kgat_formal_pipeline.pid}"
TMUX_SESSION="${UCPR_FORMAL_TMUX_SESSION:-ucpr_amazon_formal}"
TMUX_CMD_FILE="$RUN_ROOT/ucpr_amazon_book_kgat_formal_pipeline.tmux.sh"
GPU_ARG="${1:-${UCPR_GPU:-0}}"

mkdir -p "$RUN_ROOT"

if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$TMUX_SESSION" >/dev/null 2>&1; then
  echo "UCPR Amazon formal pipeline tmux session already exists: $TMUX_SESSION"
  echo "log=$LOG_FILE"
  echo "attach=tmux attach -t $TMUX_SESSION"
  exit 0
fi

if [ -f "$PID_FILE" ]; then
  existing_pid="$(tr -d '[:space:]' < "$PID_FILE")"
  if [ -n "$existing_pid" ] && ps -p "$existing_pid" >/dev/null 2>&1; then
    echo "UCPR Amazon formal pipeline is already running: pid=$existing_pid"
    echo "log=$LOG_FILE"
    exit 0
  fi
fi

cd "$ROOT"
export UCPR_FORMAL_TOPK="${UCPR_FORMAL_TOPK:-25 5 1}"
export UCPR_BEAM_BATCH_SIZE="${UCPR_BEAM_BATCH_SIZE:-4}"
export UCPR_RUN_INFERENCE="${UCPR_RUN_INFERENCE:-0}"
export UCPR_USE_STREAMING_EXPORT="${UCPR_USE_STREAMING_EXPORT:-1}"

if command -v tmux >/dev/null 2>&1; then
  cat > "$TMUX_CMD_FILE" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$ROOT"
export UCPR_FORMAL_TOPK="$UCPR_FORMAL_TOPK"
export UCPR_BEAM_BATCH_SIZE="$UCPR_BEAM_BATCH_SIZE"
export UCPR_RUN_INFERENCE="$UCPR_RUN_INFERENCE"
export UCPR_USE_STREAMING_EXPORT="$UCPR_USE_STREAMING_EXPORT"
exec bash "$ROOT/scripts/validation/run_ucpr_amazon_formal_pipeline.sh" "$GPU_ARG" > "$LOG_FILE" 2>&1
EOF
  chmod +x "$TMUX_CMD_FILE"
  tmux new-session -d -s "$TMUX_SESSION" "$TMUX_CMD_FILE"
  pid="$(tmux display-message -p -t "$TMUX_SESSION" '#{pane_pid}')"
  echo "$pid" > "$PID_FILE"
  launch_mode="tmux:$TMUX_SESSION"
else
  nohup bash "$ROOT/scripts/validation/run_ucpr_amazon_formal_pipeline.sh" "$GPU_ARG" \
    > "$LOG_FILE" 2>&1 &
  pid="$!"
  echo "$pid" > "$PID_FILE"
  launch_mode="nohup"
fi

echo "UCPR Amazon formal pipeline launched"
echo "mode=$launch_mode"
echo "pid=$pid"
echo "log=$LOG_FILE"
echo "pid_file=$PID_FILE"
echo "tmux_session=$TMUX_SESSION"
echo "physical_gpu=$GPU_ARG"
echo "topk=$UCPR_FORMAL_TOPK"
echo "beam_batch_size=$UCPR_BEAM_BATCH_SIZE"
echo "run_inference=$UCPR_RUN_INFERENCE"
echo "streaming_export=$UCPR_USE_STREAMING_EXPORT"
