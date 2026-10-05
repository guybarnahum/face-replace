#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
VENV_PYTHON="$VENV_DIR/bin/python"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "error: $PYTHON not found" >&2
  exit 1
fi

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"error: Python 3.11+ required, found {sys.version.split()[0]}")
PY

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating virtual environment: $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo "Reusing virtual environment: $VENV_DIR"
fi

echo "Updating packaging tools..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

echo "Installing face-replace and development dependencies..."
"$VENV_PYTHON" -m pip install -e '.[dev]'

echo
echo "Setup complete."
echo "Activate with: source $VENV_DIR/bin/activate"
echo "Then run:      face-replace --help"
