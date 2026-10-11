# Dockerfile that builds a fully functional image of Knowledge Commons Works.
#
# Uses a multi-stage build:
#   dev-workspace - full toolchain (uv, Node, pnpm, gcc, *-dev libs) to compile
#                   Python extensions and build webpack assets. But these assets are
#                   *not* included in this image itself. This stage also copies a 
#                   bootstrap script that will pull the actual application code 
#                   and run the setup in a set of shared volumes for the dev environment.
#   builder     – full toolchain (uv, Node, pnpm, gcc, *-dev libs) to compile
#                 Python extensions and build webpack assets. No test extras.
#   test-runner – builder + optional-dependencies.tests (pytest, …) + root
#                 ``pnpm install`` for Jest; not copied into runtime.
#   runtime     – minimal Debian Bookworm image with only shared runtime libs;
#                 no compilers, no Node, no pnpm, no uv, no test extras.
#
# Note: Keep commands in sync with ./scripts/bootstrap.

# ── Stage 0: dev workspace ────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS dev-workspace

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost/api \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/src/.venv \
    VIRTUAL_ENV=/opt/invenio/src/.venv \
    PATH="/opt/invenio/src/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONWARNINGS=ignore::DeprecationWarning,ignore::SyntaxWarning

# Build tools, compile-time libs, Node.js — none of these land in the runtime image.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    gnupg \
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
    openssh-client \
    openssl \
    gosu \
    socat \
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

RUN groupadd --gid 1000 invenio \
    && useradd --uid 1000 --gid 1000 \
        --home-dir /opt/invenio \
        --create-home \
        --shell /bin/bash \
        invenio

# pnpm is installed via Corepack; `invenio webpack install` uses PNPMPackage (WEBPACKEXT_NPM_PKG_CLS).
# Corepack enable must run as root
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable 

WORKDIR /opt/invenio
USER invenio
# Corepack prepare must run with same user as assets build command
# Must match root package.json packageManager (Corepack form: sha512.<hex>,
# not npm integrity sha512-<base64>).
RUN corepack prepare pnpm@12.9.1+sha512.06b055fff5cd20dc12781de173ced3310ce0951bf2ec620211a16045d5444d5c93a663210764ef29a653a610459ba0368f0e74f84d80c54723cf95aae7bc0d6d --activate
# Placeholders so fresh named volumes seed as uid 1000 (not root) and
# non-empty. Bootstrap removes src's keep file before git clone.
RUN mkdir -p /opt/invenio/var/instance && \
    mkdir -p /opt/invenio/var/import_data && \
    mkdir -p /opt/invenio/src && \
    touch /opt/invenio/src/.kcworks-volume \
          /opt/invenio/var/instance/.kcworks-volume \
          /opt/invenio/var/import_data/.kcworks-volume && \
    # So agents overlay can bind-mount S.gpg-agent without Docker creating a
    # root-owned parent (see docker-compose.dev.agents.yml).
    mkdir -m 700 -p /opt/invenio/.gnupg

COPY --chown=invenio:invenio ./docker/workspace_bootstrap.sh /opt/invenio/workspace_bootstrap.sh
RUN chmod 0700 /opt/invenio/workspace_bootstrap.sh

# Entrypoint runs as root (socat proxy for SSH agent), then drops to invenio.
USER root
COPY ./docker/workspace_entrypoint.sh /opt/invenio/workspace_entrypoint.sh
RUN chmod 0755 /opt/invenio/workspace_entrypoint.sh

# Keep the workspace up; bootstrap on demand as invenio::
#   docker exec -u invenio -it <project>-workspace /opt/invenio/workspace_bootstrap.sh
ENTRYPOINT ["/opt/invenio/workspace_entrypoint.sh"]
CMD ["sleep", "infinity"]

# ── Stage 1: builder ──────────────────────────────────────────────────────
FROM dev-workspace AS builder

WORKDIR /opt/invenio/src
USER invenio

COPY --chown=invenio:invenio . .

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
# Translations: keep the project catalog under src/ and symlink instance ->
# src (same as invenio-cli translations compile). Compile happens below with
# the asset build so .mo files exist before the runtime stage COPY.
RUN cp ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini && \
    cp ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini && \
    cp ./docker/startup_*.sh ${INVENIO_INSTANCE_PATH}/ && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_*.sh && \
    cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg && \
    cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates && \
    cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data && \
    ln -sfn /opt/invenio/src/translations ${INVENIO_INSTANCE_PATH}/translations

# Build frontend assets. Node/pnpm are present here but won't be in the runtime image.
# `invenio webpack ...` here routes through the rspack project + PNPMPackage that
# invenio.cfg selects via WEBPACKEXT_PROJECT and WEBPACKEXT_NPM_PKG_CLS — see the
# explanatory comment in scripts/build/build-assets.sh for details.
RUN . .venv/bin/activate && \
    uv pip install -e ./site/kcworks/dependencies/invenio-stats-dashboard && \
    pybabel compile -d /opt/invenio/src/translations && \
    pybabel compile -d /opt/invenio/src/site/kcworks/translations && \
    invenio collect --verbose && \
    invenio webpack clean create && \
    python /opt/invenio/src/scripts/build/patch-webpack-assets-pnpm-allow-builds.py && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/ && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/{custom_fields,search} && \
    invenio webpack install && \
    invenio shell /opt/invenio/src/scripts/build/symlink_assets.py && \
    invenio webpack build

ENTRYPOINT []

# ── Stage 1b: test-runner ─────────────────────────────────────────────────
# Extends builder with test extras only. docker-compose.test.yml targets this
# stage. Runtime still COPY --from=builder, so these packages never ship in
# the deployed image.
FROM builder AS test-runner

RUN . .venv/bin/activate && \
    uv sync --frozen --extra tests --compile-bytecode && \
    uv clean

# Root Jest suite deps (package.json / pnpm-lock.yaml from COPY). All root
# deps live under ``devDependencies``; force development so they are not
# skipped. Webpack's install lives under instance assets, not this tree.
RUN NODE_ENV=development pnpm install --frozen-lockfile \
    && test -x node_modules/.bin/jest

# ── Stage 2: runtime ──────────────────────────────────────────────────────
# python:3.12-slim-bookworm shares the same Python path (/usr/local/bin/python3.12)
# as the builder base, so venv symlinks resolve correctly after the COPY.
FROM python:3.12-slim-bookworm AS runtime

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost/api \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/src/.venv \
    VIRTUAL_ENV=/opt/invenio/src/.venv \
    PATH="/opt/invenio/src/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
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

RUN groupadd --gid 1000 invenio \
    && useradd --uid 1000 --gid 1000 \
        --no-create-home \
        --shell /usr/sbin/nologin \
        invenio

# Copy the entire built tree (venv, source, instance path) from the builder.
# The source tree must be present because all local packages are editable installs.
COPY --from=builder --chown=invenio:invenio /opt/invenio /opt/invenio

WORKDIR /opt/invenio/src
USER invenio

ENTRYPOINT ["/bin/bash", "-c"]
