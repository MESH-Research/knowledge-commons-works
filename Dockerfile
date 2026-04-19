# Dockerfile that builds a fully functional image of Knowledge Commons Works.
#
# Uses a two-stage build:
#   builder  – full toolchain (uv, Node, pnpm, gcc, *-dev libs) to compile
#              Python extensions and build webpack assets.
#   runtime  – minimal Debian Bookworm image with only shared runtime libs;
#              no compilers, no Node, no pnpm, no uv in the final image.
#
# Note: Keep commands in sync with ./scripts/bootstrap.

# ── Stage 1: builder ──────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/src/.venv \
    VIRTUAL_ENV=/opt/invenio/src/.venv \
    PATH="/opt/invenio/src/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNODONTWRITEBYTECODE=1 \
    PYTHONWARNINGS=ignore::DeprecationWarning,ignore::SyntaxWarning

RUN mkdir -p /opt/invenio/var/instance && \
    mkdir -p /opt/invenio/src
WORKDIR /opt/invenio/src

# Build tools, compile-time libs, Node.js — none of these land in the runtime image.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    libltdl-dev \
    libpq-dev \
    libpcre3-dev \
    locales \
    libpcre3 \
    libffi-dev \
    uuid-dev \
    wget \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# pnpm via Corepack. invenio webpack install uses PNPMPackage (WEBPACKEXT_NPM_PKG_CLS).
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@10.32.1 --activate

COPY . .

# Install Python dependencies.
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --frozen --compile-bytecode && \
    export CFLAGS="-Wno-error=incompatible-pointer-types" && \
    uv pip install --reinstall --no-binary=lxml "lxml==5.2.1" && \
    uv clean

RUN echo "[cli]" >> .invenio.private && \
    echo "services_setup=False" >> .invenio.private && \
    echo "instance_path=/opt/invenio/var/instance" >> .invenio.private

# Copy required files to instance path.
RUN cp ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini && \
    cp ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini && \
    cp ./docker/startup_*.sh ${INVENIO_INSTANCE_PATH}/ && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_*.sh && \
    cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg && \
    cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates && \
    cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data

# Build frontend assets. Node/pnpm are present here but won't be in the runtime image.
# `invenio webpack ...` here routes through the rspack project + PNPMPackage that
# invenio.cfg selects via WEBPACKEXT_PROJECT and WEBPACKEXT_NPM_PKG_CLS — see the
# explanatory comment in scripts/build-assets.sh for details.
RUN . .venv/bin/activate && \
    uv pip install -e ./site/kcworks/dependencies/invenio-stats-dashboard && \
    invenio collect --verbose && \
    invenio webpack clean create && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/ && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/{custom_fields,search} && \
    invenio webpack install && \
    invenio shell /opt/invenio/src/scripts/symlink_assets.py && \
    invenio webpack build


# ── Stage 2: runtime ──────────────────────────────────────────────────────
# python:3.12-slim-bookworm shares the same Python path (/usr/local/bin/python3.12)
# as the builder base, so venv symlinks resolve correctly after the COPY.
FROM python:3.12-slim-bookworm AS runtime

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/src/.venv \
    VIRTUAL_ENV=/opt/invenio/src/.venv \
    PATH="/opt/invenio/src/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNODONTWRITEBYTECODE=1 \
    PYTHONWARNINGS=ignore::DeprecationWarning,ignore::SyntaxWarning \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

# Runtime shared libs only — no *-dev packages, no compilers, no Node.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libpq5 \
    libpcre3 \
    libssl3 \
    libffi8 \
    libcairo2 \
    locales \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --system --no-create-home --home-dir /opt/invenio \
        --shell /usr/sbin/nologin invenio

# Copy the entire built tree (venv, source, instance path) from the builder.
# The source tree must be present because all local packages are editable installs.
COPY --from=builder --chown=invenio:invenio /opt/invenio /opt/invenio

WORKDIR /opt/invenio/src
USER invenio

ENTRYPOINT ["/bin/bash", "-c"]
