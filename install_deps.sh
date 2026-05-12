#!/usr/bin/env bash
# Developer setup — installs the package in editable mode with test dependencies.
set -euo pipefail

g="\033[1;32m"
r="\033[1;31m"
b="\033[1;34m"
w="\033[0m"

info() { echo -e "${b}[>]${w} $*"; }
ok()   { echo -e "${g}[✔]${w} $*"; }
die()  { echo -e "${r}[✘]${w} $*" >&2; exit 1; }

# --- uv check / install --------------------------------------------------------
if ! command -v uv &>/dev/null; then
  info "uv not found -- installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv $(uv --version)"

# --- Python check --------------------------------------------------------------
PY_VER=$(uv run python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PY_VER"

# --- Sync all dependencies (including dev) -------------------------------------
info "Installing dependencies from uv.lock..."
uv sync --dev
ok "Dependencies installed"

# --- Verify entry points -------------------------------------------------------
info "Verifying entry points..."
uv run eagleosint --help > /dev/null && ok "eagleosint CLI works"
uv run e4gl --help > /dev/null && ok "e4gl alias works"

# --- Run tests ------------------------------------------------------------------
info "Running test suite..."
uv run pytest -v --tb=short
ok "All tests passed"

echo ""
ok "Dev setup complete. Run commands with: uv run eagleosint"
ok "Or activate the venv: source .venv/bin/activate"
