#!/usr/bin/env bash
set -euo pipefail
# Launcher script to start yt-dlp GUI using the project's virtualenv Python.
# Behavior:
# 1) If a previous GUI was started via this script, stop it (uses run_gui.pid). Falls back to pgrep.
# 2) Run a quick Python compilation (compileall) to catch syntax errors.
# 3) Start the GUI and write PID to run_gui.pid; logs appended to run_gui.log.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/run_gui.pid"
LOGFILE="$DIR/run_gui.log"

# Activate venv if present
if [ -f "$DIR/.venv/bin/activate" ]; then
  # shellcheck disable=SC1090
  . "$DIR/.venv/bin/activate"
fi

# Prefer the venv python, fall back to system python3/python
if [ -x "$DIR/.venv/bin/python" ]; then
  PY="$DIR/.venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi

echo "[run_gui] Using Python: $PY" | tee -a "$LOGFILE"

# If PID file exists, try to stop the old process gracefully
if [ -f "$PIDFILE" ]; then
  OLD_PID="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "[run_gui] Stopping previous GUI process $OLD_PID" | tee -a "$LOGFILE"
    kill "$OLD_PID" 2>/dev/null || true
    # wait up to 10s for graceful exit
    for i in $(seq 1 20); do
      if ! kill -0 "$OLD_PID" 2>/dev/null; then
        break
      fi
      sleep 0.5
    done
    if kill -0 "$OLD_PID" 2>/dev/null; then
      echo "[run_gui] Force killing $OLD_PID" | tee -a "$LOGFILE"
      kill -9 "$OLD_PID" 2>/dev/null || true
    fi
  else
    echo "[run_gui] No live process for PID in $PIDFILE, removing stale PID file" | tee -a "$LOGFILE"
  fi
  rm -f "$PIDFILE"
fi

# Fallback: try to find any running copies of the script and stop them
if command -v pgrep >/dev/null 2>&1; then
  PIDS="$(pgrep -f "yt-dlp-gui.py" || true)"
  for pid in $PIDS; do
    # skip empty and this shell (though this is run before starting)
    if [ -z "$pid" ] || [ "$pid" -eq "$$" ] 2>/dev/null; then
      continue
    fi
    echo "[run_gui] Stopping previous GUI process (pgrep) $pid" | tee -a "$LOGFILE"
    kill "$pid" 2>/dev/null || true
  done
fi

# Recompile python files to catch syntax errors before launching
echo "[run_gui] Compiling Python files (compileall) ..." | tee -a "$LOGFILE"
if ! "$PY" -m compileall -q "$DIR" 2>>"$LOGFILE"; then
  echo "[run_gui] Compilation failed; aborting. See $LOGFILE" | tee -a "$LOGFILE"
  exit 1
fi

echo "[run_gui] Starting yt-dlp GUI with: $PY" | tee -a "$LOGFILE"
# write this process PID so subsequent runs can stop it
echo "$$" > "$PIDFILE"

exec "$PY" "$DIR/yt-dlp-gui.py" "$@" >>"$LOGFILE" 2>&1
