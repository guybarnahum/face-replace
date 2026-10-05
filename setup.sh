#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
TOOLS_DIR="$ROOT/.tools"
UV="$TOOLS_DIR/uv"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

TOTAL_STEPS=6
STEP=0
TTY=0
[[ -t 1 && "${TERM:-dumb}" != "dumb" ]] && TTY=1

if (( TTY )) && [[ -z "${NO_COLOR:-}" ]]; then
  DIM=$'\033[2m'; GREEN=$'\033[32m'; RED=$'\033[31m'
  CYAN=$'\033[36m'; RESET=$'\033[0m'
else
  DIM=""; GREEN=""; RED=""; CYAN=""; RESET=""
fi

SPINNER=( "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏" )

run_step() {
  local label="$1"; shift
  STEP=$((STEP + 1))
  local log; log="$(mktemp)"
  local rc=0

  if (( TTY )); then
    "$@" >"$log" 2>&1 &
    local pid=$! i=0
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
    if "$@" >"$log" 2>&1; then printf "done\n"; else rc=$?; printf "failed\n" >&2; fi
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
  [[ -x "$UV" ]] && return 0
  command -v curl >/dev/null 2>&1 || { echo "curl is required to bootstrap uv" >&2; return 1; }
  mkdir -p "$TOOLS_DIR"
  curl -LsSf https://astral.sh/uv/install.sh |
    env UV_INSTALL_DIR="$TOOLS_DIR" UV_NO_MODIFY_PATH=1 sh
  [[ -x "$UV" ]]
}

prepare_venv() {
  if [[ -x "$VENV_DIR/bin/python" ]] &&
     "$VENV_DIR/bin/python" -c "import sys; raise SystemExit(sys.version_info[:2] != tuple(map(int, '$PYTHON_VERSION'.split('.'))))"; then
    return 0
  fi
  rm -rf "$VENV_DIR"
  "$UV" venv --python "$PYTHON_VERSION" "$VENV_DIR"
}

install_provider() {
  local provider
  provider="$("$VENV_DIR/bin/python" - <<'PY'
from face_replace.config import load_config
print(load_config().runtime.provider)
PY
)"

  case "$provider" in
    insightface)
      "$UV" pip install --python "$VENV_DIR/bin/python" -e '.[provider-insightface]'
      "$UV" pip install --python "$VENV_DIR/bin/python" --no-deps 'insightface==2.0'
      ;;
    *)
      echo "unsupported provider in config.yaml: $provider" >&2
      return 1
      ;;
  esac
}

verify_install() {
  "$VENV_DIR/bin/python" - <<'PY'
import onnxruntime as ort
from face_replace.config import load_config
from face_replace.runtime import create_engine

assert "CUDAExecutionProvider" in ort.get_available_providers()
config = load_config()
engine = create_engine(config.runtime)
print(f"{config.runtime.provider}/{config.runtime.model}: {type(engine).__name__}")
PY
  "$VENV_DIR/bin/face-replace" --help >/dev/null
}

echo
echo "face-replace setup"
echo "──────────────────"

run_step "Bootstrap uv" bootstrap_uv
run_step "Provision CPython $PYTHON_VERSION" "$UV" python install "$PYTHON_VERSION"
run_step "Prepare virtual environment" prepare_venv
run_step "Install core dependencies" "$UV" pip install --python "$VENV_DIR/bin/python" -e '.[dev]'
run_step "Install configured provider" install_provider
run_step "Verify CUDA runtime" verify_install

echo
printf "%s✓ Setup complete%s\n" "$GREEN" "$RESET"
echo "  Python: $("$VENV_DIR/bin/python" --version 2>&1)"
echo "  Venv:   $ROOT/$VENV_DIR"
echo
echo "Activate with:"
echo "  source $VENV_DIR/bin/activate"
