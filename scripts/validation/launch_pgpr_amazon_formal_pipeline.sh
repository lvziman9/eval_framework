#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/usr1/home/s125mdg43_08/eval_framework}"
RUN_ROOT="$ROOT/runs/debug_compare/2026-06-20_native_path_expansion"
LOG_FILE="${PGPR_FORMAL_LOG:-$RUN_ROOT/pgpr_amazon_book_kgat_formal_pipeline.log}"
PID_FILE="${PGPR_FORMAL_PID:-$RUN_ROOT/pgpr_amazon_book_kgat_formal_pipeline.pid}"
TMUX_SESSION="${PGPR_FORMAL_TMUX_SESSION:-pgpr_amazon_formal}"
TMUX_CMD_FILE="$RUN_ROOT/pgpr_amazon_book_kgat_formal_pipeline.tmux.sh"
GPU_ARG="${1:-${PGPR_GPU:-}}"

mkdir -p "$RUN_ROOT"

if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$TMUX_SESSION" >/dev/null 2>&1; then
  echo "PGPR Amazon formal pipeline tmux session already exists: $TMUX_SESSION"
  echo "log=$LOG_FILE"
  echo "attach=tmux attach -t $TMUX_SESSION"
  exit 0
fi

if [ -f "$PID_FILE" ]; then
  existing_pid="$(tr -d '[:space:]' < "$PID_FILE")"
  if [ -n "$existing_pid" ] && ps -p "$existing_pid" >/dev/null 2>&1; then
    echo "PGPR Amazon formal pipeline is already running: pid=$existing_pid"
    echo "log=$LOG_FILE"
    exit 0
  fi
fi

cd "$ROOT"
export PGPR_FORMAL_TOPK="${PGPR_FORMAL_TOPK:-10 12 1}"
export PGPR_INFERENCE_BATCH_SIZE="${PGPR_INFERENCE_BATCH_SIZE:-256}"

if command -v tmux >/dev/null 2>&1; then
  cat > "$TMUX_CMD_FILE" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$ROOT"
export PGPR_FORMAL_TOPK="$PGPR_FORMAL_TOPK"
export PGPR_INFERENCE_BATCH_SIZE="$PGPR_INFERENCE_BATCH_SIZE"
exec bash "$ROOT/scripts/validation/run_pgpr_amazon_formal_pipeline.sh" "$GPU_ARG" > "$LOG_FILE" 2>&1
EOF
  chmod +x "$TMUX_CMD_FILE"
  tmux new-session -d -s "$TMUX_SESSION" "$TMUX_CMD_FILE"
  pid="$(tmux display-message -p -t "$TMUX_SESSION" '#{pane_pid}')"
  echo "$pid" > "$PID_FILE"
  launch_mode="tmux:$TMUX_SESSION"
else
  nohup bash "$ROOT/scripts/validation/run_pgpr_amazon_formal_pipeline.sh" "$GPU_ARG" \
    > "$LOG_FILE" 2>&1 &
  pid="$!"
  echo "$pid" > "$PID_FILE"
  launch_mode="nohup"
fi

echo "PGPR Amazon formal pipeline launched"
echo "mode=$launch_mode"
echo "pid=$pid"
echo "log=$LOG_FILE"
echo "pid_file=$PID_FILE"
echo "tmux_session=$TMUX_SESSION"
echo "topk=$PGPR_FORMAL_TOPK"
echo "inference_batch_size=$PGPR_INFERENCE_BATCH_SIZE"
