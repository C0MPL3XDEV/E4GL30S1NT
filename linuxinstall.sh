#!/usr/bin/env bash
set -euo pipefail

g="\033[1;32m"
r="\033[1;31m"
b="\033[1;34m"
y="\033[1;33m"
w="\033[0m"

info()  { echo -e "${b}[>]${w} $*"; }
ok()    { echo -e "${g}[✔]${w} $*"; }
warn()  { echo -e "${y}[!]${w} $*"; }
die()   { echo -e "${r}[✘]${w} $*" >&2; exit 1; }

echo -e "${b}"
cat <<'EOF'
      .---.        .-----------
     /     \  __  /    ------
    / /     \(  )/    -----
   //////   ' \/ `   ---
  //// / // :    : ---
 // /   /  /`    '--
//          //..\
       ====UU====UU====
           '//||\`
             ''``
  E4GL30S1NT v2.0 — installer
EOF
echo -e "${w}"

# --- 1. Check OS ----------------------------------------------------------------------
if command -v apt-get &>/dev/null; then
  PM="apt"
elif command -v pacman &>/dev/null; then
  PM="pacman"
elif command -v dnf &>/dev/null; then
  PM="dnf"
else
  die "No supported package manager found (apt / pacman / dnf)."
fi
info "Detected package manager: ${g}$PM${w}"

case "$PM" in
  apt)
      PKG_PYTHON="python3 python3-pip python3-venv"
      PKG_LIBS="libxml2 libxslt1.1"
      PKG_TOOLS="curl git"
    ;;
  pacman)
      PKG_PYTHON="python python-pip"
      PKG_LIBS="libxml2 libxslt"
      PKG_TOOLS="curl git"
      ;;
  dnf)
      PKG_PYTHON="python3 python3-pip"
      PKG_LIBS="libxml2 libxslt"
      PKG_TOOLS="curl git"
      ;;
esac


# -- 2. System packages -----------------------------------------------------------------
pkg_install() {
  case "$PM" in
    apt)  sudo apt-get install -y -q $* ;;
    pacman)  sudo pacman -S --noconfirm --needed $* ;;
    dnf)  sudo dnf install -y -q $* ;;
  esac
}

info "Updating package lists..."
case "$PM" in
  apt) sudo apt-get update -q ;;
  pacman) sudo pacman -Sy --noconfirm ;;
  dnf) sudo dnf check-update -q || true ;;
esac

info "Installing system dependencies..."
pkg_install $PKG_PYTHON $PKG_LIBS $PKG_TOOLS

# --- 3. Python version check ----------------------------------------------------------
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ) ]]; then
  die "Python 3.11+ is required. Found: $PY_VER"
fi
ok "Python $PY_VER detected"

# --- 4. Clone or update repo ---------------------------------------------------------
INSTALL_DIR="$HOME/.local/share/eagleosint"

if [[ -d "$INSTALL_DIR/.git" ]]; then
  info "Updating existing installation at $INSTALL_DIR..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  info "Cloning repository to $INSTALL_DIR..."
  git clone https://github.com/C0MPL3XDEV/E4GL30S1NT.git "$INSTALL_DIR"
fi

# --- 5. Virtual Env ------------------------------------------------------------------
VENV_DIR="$INSTALL_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  info "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi
ok "Virtual environment ready"

# --- 6. Install package -------------------------------------------------------------
info "Install eagleosint..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet "$INSTALL_DIR"
ok "Package installed"

# --- 7. Launcher script -------------------------------------------------------------
LAUNCHER="/usr/local/bin/eagleosint"
sudo tee "$LAUNCHER" > /dev/null <<LAUNCHER
#!/usr/bin/env bash
exec "$VENV_DIR/bin/eagleosint" "\$@"
LAUNCHER
sudo chmod +x "$LAUNCHER"

sudo ln -sf "$LAUNCHER" /usr/local/bin/e4gl
ok "Launchers created: eagleosint, e4gl"

# ── 8. Done ───────────────────────────────────────────────────────────────────
echo ""
ok "Installation complete!"
info "Run ${g}eagleosint${w} or ${g}e4gl${w} to start"
info "Run ${g}eagleosint --help${w} to see all subcommands"
info ""
warn "API keys are stored in ~/.config/E4GL30S1NT/config.json"
warn "You will be prompted for them on first use, or set them via:"
info "  ${g}eagleosint settings${w}"