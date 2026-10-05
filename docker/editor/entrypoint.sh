#!/usr/bin/env bash
# Seed the persistent editor home volume, then exec the container command.
#
# First empty home:
#   - Install mutable CLIs into ~/.local (pnpm globals, go, gh, lazygit, yazi)
#   - Clone monotasker configs; install oh-my-zsh / tpm as needed
#   - Recreate NVM-shaped shims for avante.nvim / nvconfig
#
# Updates later:
#   EDITOR_CONFIG_PULL=1   — ff-only pull config repos
#   EDITOR_TOOLS_UPDATE=1   — reinstall/refresh mutable CLIs
set -euo pipefail

log() { printf 'editor: %s\n' "$*" >&2; }

# Defaults (override via compose/env)
: "${NODE_SHIM_VERSION:=v24.9.0}"
: "${NVM_DIR:=$HOME/.nvm}"
: "${PNPM_HOME:=$HOME/.local/share/pnpm}"
: "${GO_VERSION:=1.24.7}"
: "${GH_VERSION:=2.101.0}"
: "${LAZYGIT_VERSION:=0.64.1}"
: "${YAZI_VERSION:=26.9.1}"

export PNPM_HOME
export PATH="$PNPM_HOME:$HOME/.local/bin:$PATH"

arch_triple() {
  local arch
  arch="$(uname -m)"
  case "$arch" in
    x86_64 | amd64) printf '%s\n' "x86_64" ;;
    aarch64 | arm64) printf '%s\n' "arm64" ;;
    *)
      log "unsupported arch: $arch"
      return 1
      ;;
  esac
}

yazi_arch() {
  case "$(arch_triple)" in
    x86_64) printf '%s\n' "x86_64" ;;
    arm64) printf '%s\n' "aarch64" ;;
  esac
}

go_arch() {
  case "$(arch_triple)" in
    x86_64) printf '%s\n' "amd64" ;;
    arm64) printf '%s\n' "arm64" ;;
  esac
}

# gh release tarballs use amd64/arm64 (same as Go).
gh_arch() { go_arch; }

ensure_dirs() {
  mkdir -p \
    "$HOME/.local/bin" \
    "$HOME/.local/share" \
    "$HOME/.config" \
    "$HOME/.pi/agent" \
    "$HOME/.ssh" \
    "$PNPM_HOME"
}

ensure_nvm_shims() {
  local shim_bin="$NVM_DIR/versions/node/$NODE_SHIM_VERSION/bin"
  mkdir -p "$shim_bin"
  # Prefer home-volume bins when present, else image PATH.
  ln -sfn "$(command -v node)" "$shim_bin/node"
  ln -sfn "$(command -v npm)" "$shim_bin/npm"
  ln -sfn "$(command -v npx)" "$shim_bin/npx"
  ln -sfn "$(command -v pnpm)" "$shim_bin/pnpm"
  if command -v pi >/dev/null 2>&1; then
    ln -sfn "$(command -v pi)" "$shim_bin/pi"
  fi
  if command -v pi-acp >/dev/null 2>&1; then
    ln -sfn "$(command -v pi-acp)" "$shim_bin/pi-acp"
  fi
  if command -v tree-sitter >/dev/null 2>&1; then
    ln -sfn "$(command -v tree-sitter)" "$shim_bin/tree-sitter"
  fi
}

ensure_pnpm_globals() {
  local stamp="$HOME/.local/share/editor-tools/pnpm-globals.stamp"
  if [[ -f "$stamp" && "${EDITOR_TOOLS_UPDATE:-0}" != "1" ]] \
    && command -v pi >/dev/null 2>&1 \
    && command -v pi-acp >/dev/null 2>&1; then
    return 0
  fi

  log "installing pnpm globals into $PNPM_HOME (pi, pi-acp, tree-sitter-cli)"
  mkdir -p "$(dirname "$stamp")"
  # Corepack provides pnpm from the image; packages + shims land in the volume.
  pnpm add -g \
    @earendil-works/pi-coding-agent \
    pi-acp \
    tree-sitter-cli
  date -u +%Y-%m-%dT%H:%M:%SZ >"$stamp"
  pi --version || true
}

ensure_go() {
  local prefix="$HOME/.local/go"
  local stamp="$HOME/.local/share/editor-tools/go-${GO_VERSION}.stamp"
  if [[ -x "$prefix/bin/go" && -f "$stamp" && "${EDITOR_TOOLS_UPDATE:-0}" != "1" ]]; then
    ln -sfn "$prefix/bin/go" "$HOME/.local/bin/go"
    ln -sfn "$prefix/bin/gofmt" "$HOME/.local/bin/gofmt"
    return 0
  fi

  log "installing go ${GO_VERSION} → $prefix"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL "https://dl.google.com/go/go${GO_VERSION}.linux-$(go_arch).tar.gz" \
    | tar -xz -C "$tmp"
  rm -rf "$prefix"
  mv "$tmp/go" "$prefix"
  rm -rf "$tmp"
  mkdir -p "$(dirname "$stamp")"
  date -u +%Y-%m-%dT%H:%M:%SZ >"$stamp"
  ln -sfn "$prefix/bin/go" "$HOME/.local/bin/go"
  ln -sfn "$prefix/bin/gofmt" "$HOME/.local/bin/gofmt"
  go version
}

ensure_gh() {
  local bin="$HOME/.local/bin/gh"
  local stamp="$HOME/.local/share/editor-tools/gh-${GH_VERSION}.stamp"
  if [[ -x "$bin" && -f "$stamp" && "${EDITOR_TOOLS_UPDATE:-0}" != "1" ]]; then
    return 0
  fi

  log "installing gh ${GH_VERSION}"
  local tmp arch
  arch="$(gh_arch)"
  tmp="$(mktemp -d)"
  curl -fsSL \
    "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${arch}.tar.gz" \
    | tar -xz -C "$tmp"
  install -m 0755 "$tmp/gh_${GH_VERSION}_linux_${arch}/bin/gh" "$bin"
  rm -rf "$tmp"
  mkdir -p "$(dirname "$stamp")"
  date -u +%Y-%m-%dT%H:%M:%SZ >"$stamp"
  gh --version | head -n 1
}

ensure_lazygit() {
  local bin="$HOME/.local/bin/lazygit"
  local stamp="$HOME/.local/share/editor-tools/lazygit-${LAZYGIT_VERSION}.stamp"
  if [[ -x "$bin" && -f "$stamp" && "${EDITOR_TOOLS_UPDATE:-0}" != "1" ]]; then
    return 0
  fi

  log "installing lazygit ${LAZYGIT_VERSION}"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL \
    "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_$(arch_triple).tar.gz" \
    | tar -xz -C "$tmp" lazygit
  install -m 0755 "$tmp/lazygit" "$bin"
  rm -rf "$tmp"
  mkdir -p "$(dirname "$stamp")"
  date -u +%Y-%m-%dT%H:%M:%SZ >"$stamp"
  lazygit --version | head -n 1
}

ensure_yazi() {
  local bin="$HOME/.local/bin/yazi"
  local stamp="$HOME/.local/share/editor-tools/yazi-${YAZI_VERSION}.stamp"
  if [[ -x "$bin" && -f "$stamp" && "${EDITOR_TOOLS_UPDATE:-0}" != "1" ]]; then
    return 0
  fi

  log "installing yazi ${YAZI_VERSION}"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL \
    "https://github.com/sxyazi/yazi/releases/download/v${YAZI_VERSION}/yazi-$(yazi_arch)-unknown-linux-gnu.zip" \
    -o "$tmp/yazi.zip"
  unzip -q "$tmp/yazi.zip" -d "$tmp"
  install -m 0755 "$tmp"/yazi-*/yazi "$bin"
  if [[ -f "$tmp"/yazi-*/ya ]]; then
    install -m 0755 "$tmp"/yazi-*/ya "$HOME/.local/bin/ya"
  fi
  rm -rf "$tmp"
  mkdir -p "$(dirname "$stamp")"
  date -u +%Y-%m-%dT%H:%M:%SZ >"$stamp"
  yazi --version
}

ensure_mutable_tools() {
  ensure_pnpm_globals
  ensure_go
  ensure_gh
  ensure_lazygit
  ensure_yazi
}

ensure_nvim_config() {
  local nvim_cfg="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"
  local lua_dir="$nvim_cfg/lua"

  mkdir -p "$nvim_cfg/undodir" "$nvim_cfg/after"

  if [[ ! -f "$nvim_cfg/init.lua" ]]; then
    printf '%s\n' "-- import neovim lua configuration" "" "require('nvconfig');" \
      >"$nvim_cfg/init.lua"
  fi

  if [[ ! -d "$lua_dir/.git" ]]; then
    log "cloning monotasker/nvconfig → $lua_dir"
    rm -rf "$lua_dir"
    git clone --depth 1 https://github.com/monotasker/nvconfig.git "$lua_dir"
  elif [[ "${EDITOR_CONFIG_PULL:-0}" == "1" ]]; then
    log "pulling nvconfig"
    git -C "$lua_dir" pull --ff-only || log "nvconfig pull failed (continuing)"
  fi
}

ensure_tmux_config() {
  local tmux_cfg="${XDG_CONFIG_HOME:-$HOME/.config}/tmux"

  if [[ ! -d "$tmux_cfg/.git" ]]; then
    log "cloning monotasker/tmux-config → $tmux_cfg"
    mkdir -p "$(dirname "$tmux_cfg")"
    rm -rf "$tmux_cfg"
    git clone --depth 1 https://github.com/monotasker/tmux-config.git "$tmux_cfg"
  elif [[ "${EDITOR_CONFIG_PULL:-0}" == "1" ]]; then
    log "pulling tmux-config"
    git -C "$tmux_cfg" pull --ff-only || log "tmux-config pull failed (continuing)"
  fi

  mkdir -p "$tmux_cfg/plugins"
  if [[ ! -f "$tmux_cfg/plugins/nordfox.tmux" ]]; then
    curl -fsSL \
      "https://raw.githubusercontent.com/EdenEast/nightfox.nvim/main/extra/nordfox/nordfox.tmux" \
      -o "$tmux_cfg/plugins/nordfox.tmux"
  fi

  if [[ ! -d "$tmux_cfg/plugins/tpm" ]]; then
    log "cloning tmux plugin manager (tpm)"
    git clone --depth 1 https://github.com/tmux-plugins/tpm.git "$tmux_cfg/plugins/tpm"
  fi

  if [[ ! -f "$HOME/.tmux.conf" ]]; then
    cat >"$HOME/.tmux.conf" <<'EOF'
source-file ~/.config/tmux/tmux.conf
EOF
  fi

  if [[ -x "$tmux_cfg/plugins/tpm/bin/install_plugins" ]] \
    && [[ ! -d "$tmux_cfg/plugins/tmux-sensible" ]]; then
    log "installing tmux plugins via tpm"
    "$tmux_cfg/plugins/tpm/bin/install_plugins" || log "tpm install failed (continuing)"
  fi
}

ensure_zsh_config() {
  local zsh_cfg="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

  if [[ ! -d "$zsh_cfg/.git" ]]; then
    log "cloning monotasker/zsh-config → $zsh_cfg"
    mkdir -p "$(dirname "$zsh_cfg")"
    rm -rf "$zsh_cfg"
    git clone --depth 1 https://github.com/monotasker/zsh-config.git "$zsh_cfg"
  elif [[ "${EDITOR_CONFIG_PULL:-0}" == "1" ]]; then
    log "pulling zsh-config"
    git -C "$zsh_cfg" pull --ff-only || log "zsh-config pull failed (continuing)"
  fi

  if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
    log "installing oh-my-zsh + plugins via zsh-config/install.sh"
    bash "$zsh_cfg/install.sh" --with-omz --with-plugins
  elif [[ ! -e "$HOME/.zshrc" ]] || ! grep -q 'ZSH_CONFIG_DIR\|config/zsh' "$HOME/.zshrc" 2>/dev/null; then
    bash "$zsh_cfg/install.sh"
  fi
}

ensure_pi_defaults() {
  local settings="$HOME/.pi/agent/settings.json"
  mkdir -p "$HOME/.pi/agent"
  if [[ ! -f "$settings" ]]; then
    log "writing default pi agent settings (lmstudio)"
    cat >"$settings" <<EOF
{
  "defaultProvider": "lmstudio",
  "defaultModel": "qwen/qwen3-coder-next",
  "theme": "dark",
  "defaultThinkingLevel": "medium"
}
EOF
  fi
}

ensure_dirs
ensure_mutable_tools
ensure_nvm_shims
ensure_nvim_config
ensure_tmux_config
ensure_zsh_config
ensure_pi_defaults

exec "$@"
