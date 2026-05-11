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

# ── Python check ──────────────────────────────────────────────────────────────
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ) ]]; then
    die "Python 3.11+ required. Found: $PY_VER"
fi
ok "Python $PY_VER"

# ── Virtual environment ───────────────────────────────────────────────────────
if [[ ! -d ".venv" ]]; then
    info "Creating .venv..."
    python3 -m venv .venv
fi

source .venv/bin/activate
info "Virtual environment: $(which python)"

# ── Install in editable mode with dev extras ──────────────────────────────────
info "Installing eagleosint[dev] in editable mode..."
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev]"
ok "Dependencies installed"

# ── Verify entry points ───────────────────────────────────────────────────────
info "Verifying entry points..."
eagleosint --help > /dev/null && ok "eagleosint CLI works"
e4gl --help       > /dev/null && ok "e4gl alias works"

# ── Run tests ─────────────────────────────────────────────────────────────────
info "Running test suite..."
pytest -v --tb=short
ok "All tests passed"

echo ""
ok "Dev setup complete. Activate with: source .venv/bin/activate"