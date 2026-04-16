#!/usr/bin/env bash
set -euo pipefail
# Launcher script to start yt-dlp GUI using the project's virtualenv Python.
# If a .venv exists in the repository root, it will be activated/used.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo "Starting yt-dlp GUI with: $PY"
exec "$PY" "$DIR/yt-dlp-gui.py" "$@"
