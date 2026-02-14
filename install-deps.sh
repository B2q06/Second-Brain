#!/usr/bin/env bash
set -euo pipefail

# install-deps.sh — Idempotent bootstrap for dev machines
# Supports: macOS (brew), Arch Linux (pacman), Debian/Ubuntu (apt)

REQUIRED_NODE=18
REQUIRED_PYTHON=11  # 3.11+

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[info]${NC}  $*"; }
ok()    { echo -e "${GREEN}[ok]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
fail()  { echo -e "${RED}[fail]${NC}  $*"; }

summary=()
add_summary() { summary+=("$1"); }

# ── 1. Detect OS & Package Manager ─────────────────────────────────────────
detect_os() {
  if [[ "$OSTYPE" == darwin* ]]; then
    OS="macos"
    PKG="brew"
  elif command -v pacman &>/dev/null; then
    OS="arch"
    PKG="pacman"
  elif command -v apt &>/dev/null; then
    OS="debian"
    PKG="apt"
  else
    fail "Unsupported OS. Need macOS, Arch Linux, or Debian/Ubuntu."
    exit 1
  fi
  ok "Detected: $OS ($PKG)"
}

# ── 2. Ensure Homebrew (macOS only) ────────────────────────────────────────
ensure_brew() {
  [[ "$OS" != "macos" ]] && return 0
  if command -v brew &>/dev/null; then
    ok "Homebrew installed"
  else
    info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for Apple Silicon
    if [[ -f /opt/homebrew/bin/brew ]]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    add_summary "Installed Homebrew"
  fi
}

# ── 3. Ensure Node.js >= 18 ────────────────────────────────────────────────
ensure_node() {
  if command -v node &>/dev/null; then
    local ver
    ver=$(node -v | sed 's/v//' | cut -d. -f1)
    if (( ver >= REQUIRED_NODE )); then
      ok "Node.js $(node -v)"
      return 0
    fi
    warn "Node.js $(node -v) is too old (need >= $REQUIRED_NODE)"
  fi

  info "Installing Node.js..."
  case "$PKG" in
    brew)   brew install node ;;
    pacman) sudo pacman -S --needed --noconfirm nodejs npm ;;
    apt)    sudo apt update && sudo apt install -y nodejs npm ;;
  esac

  if command -v node &>/dev/null; then
    ok "Installed Node.js $(node -v)"
    add_summary "Installed Node.js $(node -v)"
  else
    fail "Node.js installation failed. Install manually or use nvm."
    return 1
  fi
}

# ── 4. Ensure Python >= 3.11 ───────────────────────────────────────────────
ensure_python() {
  local py=""
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
      local minor
      minor=$("$cmd" -c 'import sys; print(sys.version_info.minor)')
      local major
      major=$("$cmd" -c 'import sys; print(sys.version_info.major)')
      if (( major == 3 && minor >= REQUIRED_PYTHON )); then
        py="$cmd"
        break
      fi
    fi
  done

  if [[ -n "$py" ]]; then
    ok "Python $($py --version)"
    return 0
  fi

  info "Installing Python >= 3.$REQUIRED_PYTHON..."
  case "$PKG" in
    brew)   brew install python ;;
    pacman) sudo pacman -S --needed --noconfirm python python-pip ;;
    apt)    sudo apt update && sudo apt install -y python3 python3-pip python3-venv ;;
  esac

  if python3 -c "import sys; exit(0 if sys.version_info >= (3,$REQUIRED_PYTHON) else 1)" 2>/dev/null; then
    ok "Installed Python $(python3 --version)"
    add_summary "Installed Python $(python3 --version)"
  else
    fail "Python >= 3.$REQUIRED_PYTHON not available. Install manually or use pyenv."
    return 1
  fi
}

# ── 5. Ensure Claude Code CLI ──────────────────────────────────────────────
ensure_claude() {
  if command -v claude &>/dev/null; then
    ok "Claude Code CLI installed"
  else
    info "Installing Claude Code CLI..."
    npm i -g @anthropic-ai/claude-code
    ok "Installed Claude Code CLI"
    add_summary "Installed Claude Code CLI"
  fi
}

# ── 6. Install Node dependencies ──────────────────────────────────────────
install_node_deps() {
  local project_root="$1"
  local count=0
  while IFS= read -r -d '' pkg; do
    local dir
    dir=$(dirname "$pkg")
    if [[ ! -d "$dir/node_modules" ]] || [[ "$pkg" -nt "$dir/node_modules" ]]; then
      info "npm install in $dir"
      (cd "$dir" && npm install)
      count=$((count + 1))
    else
      ok "node_modules up-to-date: $dir"
    fi
  done < <(find "$project_root" -name package.json \
    -not -path "*/node_modules/*" \
    -not -path "*/.venv/*" \
    -not -path "*/_archive/*" \
    -print0)

  if (( count > 0 )); then
    add_summary "Ran npm install in $count directories"
  fi
}

# ── 7. Install Python dependencies ────────────────────────────────────────
install_python_deps() {
  local project_root="$1"
  local count=0
  while IFS= read -r -d '' req; do
    local dir
    dir=$(dirname "$req")
    local venv="$dir/.venv"
    if [[ ! -d "$venv" ]]; then
      info "Creating venv in $dir"
      python3 -m venv "$venv"
    fi
    info "pip install -r $req"
    "$venv/bin/pip" install -q -r "$req"
    count=$((count + 1))
  done < <(find "$project_root" -name requirements.txt \
    -not -path "*/.venv/*" \
    -not -path "*/_archive/*" \
    -print0)

  if (( count > 0 )); then
    add_summary "Installed Python deps in $count directories"
  fi
}

# ── 8. Ensure BMAD global harness ─────────────────────────────────────────
ensure_bmad_harness() {
  if [[ -d "$HOME/.claude/skills/bmad" ]]; then
    ok "BMAD harness already installed"
    return 0
  fi

  info "Installing BMAD harness..."
  local harness_dir="$HOME/.bmad-harness"
  if [[ ! -d "$harness_dir" ]]; then
    git clone https://github.com/aj-geddes/claude-code-bmad-skills.git "$harness_dir"
  fi

  if [[ -f "$harness_dir/install-v6.sh" ]]; then
    (cd "$harness_dir" && bash install-v6.sh)
    add_summary "Installed BMAD harness"
  else
    warn "BMAD install script not found at $harness_dir/install-v6.sh"
    warn "You may need to install BMAD manually"
  fi
}

# ── 9. Verify project BMAD setup ──────────────────────────────────────────
verify_project_bmad() {
  local project_root="$1"
  local ok_count=0 warn_count=0

  if [[ -d "$project_root/_bmad" ]]; then
    ok "_bmad/ exists"
    ok_count=$((ok_count + 1))
  else
    warn "_bmad/ not found — run BMAD master agent to initialize"
    warn_count=$((warn_count + 1))
  fi

  if [[ -d "$project_root/.claude/commands/bmad" ]]; then
    ok ".claude/commands/bmad/ exists"
    ok_count=$((ok_count + 1))
  else
    warn ".claude/commands/bmad/ not found — run BMAD master agent to initialize"
    warn_count=$((warn_count + 1))
  fi

  if (( warn_count > 0 )); then
    add_summary "BMAD project setup: $warn_count items need attention"
  fi
}

# ── 10. Print summary ─────────────────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${BLUE}━━━ Summary ━━━${NC}"
  if (( ${#summary[@]} == 0 )); then
    ok "Everything was already set up!"
  else
    for line in "${summary[@]}"; do
      echo -e "  ${GREEN}✓${NC} $line"
    done
  fi
  echo ""
}

# ── Main ───────────────────────────────────────────────────────────────────
main() {
  local project_root
  project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  echo -e "${BLUE}━━━ install-deps.sh ━━━${NC}"
  echo "Project: $project_root"
  echo ""

  detect_os
  ensure_brew
  ensure_node
  ensure_python
  ensure_claude
  install_node_deps "$project_root"
  install_python_deps "$project_root"
  ensure_bmad_harness
  verify_project_bmad "$project_root"
  print_summary
}

main "$@"
