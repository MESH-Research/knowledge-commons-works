# Dockerfile that builds a fully functional image of Knowledge Commons Works
#
# This image installs all Python dependencies for Knowledge Commons Works.
# It's based
# on Almalinux (https://github.com/inveniosoftware/docker-invenio)
# and includes Pip, Pipenv, Node.js, NPM and some few standard libraries
# Invenio usually needs.
#
# Note: It is important to keep the commands in this file in sync with your
# bootstrap script located in ./scripts/bootstrap.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/src/.venv \
    VIRTUAL_ENV=/opt/invenio/src/.venv \
    PATH="/opt/invenio/src/.venv/bin:${PATH}"

# Create instance path and set working directory
RUN mkdir -p ${INVENIO_INSTANCE_PATH} && \
    mkdir -p /opt/invenio/src
WORKDIR /opt/invenio/src

# Install prerequisites and set up locales
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    libxml2 \
    libxml2-dev \
    libxmlsec1 \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libxmlsec1-gnutls \
    xmlsec1 \
    libssl-dev \
    libltdl-dev \
    libpq-dev \
    libpcre3-dev \
    locales \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    libffi-dev \
    uuid-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Configure npm to install packages locally
RUN npm config set prefix '/opt/invenio/src/node_modules' && \
    npm config set global false

# Copy all source files needed for dependencies and webpack
COPY . .

# Install python dependencies in virtual environment
RUN uv venv && \
    . .venv/bin/activate && \
    # First install lxml and xmlsec with system libxml2
    # Then install the rest of the dependencies without reinstall
    uv sync --frozen --compile-bytecode && \
    export CFLAGS="-Wno-error=incompatible-pointer-types" && \
    uv pip install --reinstall --no-binary=lxml --no-binary=xmlsec "lxml==5.2.1" "xmlsec==1.3.14" && \
    uv clean

RUN echo "[cli]" >> .invenio.private && \
    echo "services_setup=False" >> .invenio.private && \
    echo "instance_path=/opt/invenio/var/instance" >> .invenio.private

# Copy required files to instance path
RUN cp ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini && \
    cp ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini && \
    cp ./docker/startup_*.sh ${INVENIO_INSTANCE_PATH}/ && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_*.sh && \
    cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg && \
    cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates && \
    cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data

# Install local dependencies
RUN . .venv/bin/activate && \
    uv pip install --editable . && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-modular-deposit-form && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-group-collections-kcworks && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-modular-detail-page && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-record-importer-kcworks && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-remote-api-provisioner && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-remote-user-data-kcworks && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-communities && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-rdm-records && \
    uv pip install --editable ./site/kcworks/dependencies/invenio-records-resources

# Build assets
RUN . .venv/bin/activate && \
    invenio collect --verbose && \
    invenio webpack clean create && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/ && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/{custom_fields,search} && \
    invenio webpack install && \
    invenio shell /opt/invenio/src/scripts/symlink_assets.py && \
    invenio webpack build

ENTRYPOINT ["/bin/bash", "-c"]
