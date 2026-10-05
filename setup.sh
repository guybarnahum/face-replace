#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
TOOLS_DIR="$ROOT/.tools"
UV="$TOOLS_DIR/uv"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

TOTAL_STEPS=5
STEP=0
TTY=0
[[ -t 1 && "${TERM:-dumb}" != "dumb" ]] && TTY=1

if (( TTY )) && [[ -z "${NO_COLOR:-}" ]]; then
  DIM=$'\033[2m'
  GREEN=$'\033[32m'
  RED=$'\033[31m'
  CYAN=$'\033[36m'
  RESET=$'\033[0m'
else
  DIM=""
  GREEN=""
  RED=""
  CYAN=""
  RESET=""
fi

SPINNER=( "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏" )

run_step() {
  local label="$1"
  shift
  STEP=$((STEP + 1))

  local log
  log="$(mktemp)"
  local rc=0

  if (( TTY )); then
    "$@" >"$log" 2>&1 &
    local pid=$!
    local i=0

    while kill -0 "$pid" 2>/dev/null; do
      printf "\r\033[2K  %s[%d/%d]%s %s%s%s %s" \
        "$DIM" "$STEP" "$TOTAL_STEPS" "$RESET" \
        "$CYAN" "${SPINNER[$i]}" "$RESET" "$label"
      i=$(( (i + 1) % ${#SPINNER[@]} ))
      sleep 0.08
    done

    if wait "$pid"; then
      printf "\r\033[2K  %s[%d/%d]%s %s✓%s %s\n" \
        "$DIM" "$STEP" "$TOTAL_STEPS" "$RESET" "$GREEN" "$RESET" "$label"
    else
      rc=$?
      printf "\r\033[2K  %s[%d/%d]%s %s✗%s %s\n" \
        "$DIM" "$STEP" "$TOTAL_STEPS" "$RESET" "$RED" "$RESET" "$label" >&2
    fi
  else
    printf "[%d/%d] %s... " "$STEP" "$TOTAL_STEPS" "$label"
    if "$@" >"$log" 2>&1; then
      printf "done\n"
    else
      rc=$?
      printf "failed\n" >&2
    fi
  fi

  if (( rc != 0 )); then
    echo >&2
    echo "Setup failed during: $label" >&2
    echo "Last output:" >&2
    tail -n 40 "$log" >&2
    rm -f "$log"
    exit "$rc"
  fi

  rm -f "$log"
}

bootstrap_uv() {
  if [[ -x "$UV" ]]; then
    return 0
  fi

  command -v curl >/dev/null 2>&1 || {
    echo "curl is required to bootstrap uv" >&2
    return 1
  }

  mkdir -p "$TOOLS_DIR"
  curl -LsSf https://astral.sh/uv/install.sh |
    env UV_INSTALL_DIR="$TOOLS_DIR" UV_NO_MODIFY_PATH=1 sh

  [[ -x "$UV" ]]
}

prepare_venv() {
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    if "$VENV_DIR/bin/python" - <<PY
import sys
raise SystemExit(0 if sys.version_info[:2] == tuple(map(int, "$PYTHON_VERSION".split("."))) else 1)
PY
    then
      return 0
    fi

    rm -rf "$VENV_DIR"
  fi

  "$UV" venv --python "$PYTHON_VERSION" "$VENV_DIR"
}

verify_install() {
  "$VENV_DIR/bin/python" - <<'PY'
import face_replace
print(face_replace.__name__)
PY
  "$VENV_DIR/bin/face-replace" --help >/dev/null
}

echo
echo "face-replace setup"
echo "──────────────────"

run_step "Bootstrap uv" bootstrap_uv
run_step "Provision CPython $PYTHON_VERSION" "$UV" python install "$PYTHON_VERSION"
run_step "Prepare virtual environment" prepare_venv
run_step "Install project dependencies" "$UV" pip install --python "$VENV_DIR/bin/python" -e '.[dev]'
run_step "Verify CLI" verify_install

echo
printf "%s✓ Setup complete%s\n" "$GREEN" "$RESET"
echo "  Python: $("$VENV_DIR/bin/python" --version 2>&1)"
echo "  Venv:   $ROOT/$VENV_DIR"
echo
echo "Activate with:"
echo "  source $VENV_DIR/bin/activate"
