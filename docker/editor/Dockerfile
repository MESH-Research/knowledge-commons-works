# Personal editor image: stable floor only. Mutable CLIs seed into the
# persistent home volume on first boot (see entrypoint.sh).
#
# Image (rebuild rarely):
#   - OS + zsh/tmux/git/rg/fd/fzf + build tools
#   - Neovim (pinned)
#   - Node + Corepack/pnpm (bootstrap only)
#   - zoxide
#
# Home volume (update anytime):
#   - pi, pi-acp, tree-sitter-cli via pnpm → ~/.local/share/pnpm
#   - go, gh, lazygit, yazi → ~/.local
#   - monotasker/{nvconfig,tmux-config,zsh-config}, Mason/lazy, ~/.pi
#
# User: dev (uid/gid 1000). No sudo.
#
# Build::
#
#   docker build -t kcworks-editor:latest -f docker/editor/Dockerfile docker/editor

FROM node:24-bookworm-slim

ARG TARGETARCH
ARG NVIM_VERSION=v0.12.5
ARG PNPM_VERSION=12.9.1

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    HOME=/home/dev \
    EDITOR=nvim \
    VISUAL=nvim \
    SHELL=/bin/zsh \
    TERM=xterm-256color \
    NVM_DIR=/home/dev/.nvm \
    NODE_SHIM_VERSION=v24.9.0 \
    PNPM_VERSION=${PNPM_VERSION} \
    # Prefer home-volume tools when present
    PNPM_HOME=/home/dev/.local/share/pnpm \
    PATH=/home/dev/.local/share/pnpm:/home/dev/.local/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LMS_HOST=host.docker.internal \
    LMS_PORT=1234 \
    DEBIAN_FRONTEND=noninteractive \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

# ── packages ──────────────────────────────────────────────────────────────
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        fd-find \
        fzf \
        git \
        gnupg \
        gzip \
        jq \
        less \
        locales \
        make \
        openssh-client \
        openssl \
        pkg-config \
        procps \
        python3 \
        python3-pip \
        python3-venv \
        ripgrep \
        tar \
        tmux \
        unzip \
        wget \
        xz-utils \
        zsh \
        libsqlite3-0 \
        libssl3 \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && ln -sf "$(command -v fdfind)" /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

# ── pnpm via Corepack
RUN corepack enable

# Official node image already ships uid/gid 1000 as `node`.
RUN usermod -l dev -d /home/dev -m node \
    && groupmod -n dev node \
    && chsh -s /bin/zsh dev \
    && mkdir -p /home/dev \
    && chown -R dev:dev /home/dev

# ── Neovim (stable floor; bump NVIM_VERSION + rebuild to upgrade) ─────────
RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) nvim_arch=x86_64 ;; \
      arm64) nvim_arch=arm64 ;; \
      *) echo "unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL \
      "https://github.com/neovim/neovim/releases/download/${NVIM_VERSION}/nvim-linux-${nvim_arch}.tar.gz" \
      | tar -xz -C /opt; \
    ln -sf "/opt/nvim-linux-${nvim_arch}/bin/nvim" /usr/local/bin/nvim; \
    nvim --version | head -n 1

# ── zoxide ────────────────────────────────────────────────────────────────
RUN curl -fsSL "https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh" \
      | bash -s -- --bin-dir /usr/local/bin \
    && zoxide --version

COPY entrypoint.sh /usr/local/bin/editor-entrypoint.sh
RUN chmod 0755 /usr/local/bin/editor-entrypoint.sh

USER dev

# ── pnpm bootstrap; global packages land in the home volume ─
RUN corepack prepare "pnpm@${PNPM_VERSION}" --activate \
    && pnpm --version

# Seed into editor-home on first empty volume mount so the agents overlay can
# bind-mount S.gpg-agent here without Docker creating a root-owned parent.
RUN mkdir -m 700 -p /home/dev/.gnupg

WORKDIR /opt/invenio/src

ENTRYPOINT ["/usr/local/bin/editor-entrypoint.sh"]
CMD ["sleep", "infinity"]
