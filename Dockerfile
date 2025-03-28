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

FROM ghcr.io/astral-sh/uv:python3.12-alpine

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    PATH="/opt/invenio/src/.venv/bin:${PATH}"

# Create instance path and set working directory
RUN mkdir -p ${INVENIO_INSTANCE_PATH}
RUN mkdir -p /opt/invenio/src
WORKDIR /opt/invenio/src

# Install prerequisites for building xmlsec Python package
# also adds ps command for debugging
RUN apk update && apk add python3 py3-setuptools nodejs npm gcc musl-dev linux-headers python3-dev cairo git procps postgresql-dev bash curl && \
    apk add --no-cache libxml2 libxml2-dev xmlsec xmlsec-dev libressl libltdl && \
    ln -s /usr/bin/node /usr/local/bin/node && \
    ln -s /usr/bin/npm /usr/local/bin/npm

# Copy over directory for kcr instance Python package
COPY site ./site

# Install python dependencies system-wide
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen && \
    uv clean

RUN echo "[cli]" >> .invenio.private && \
    echo "services_setup=False" >> .invenio.private && \
    echo "instance_path=/opt/invenio/var/instance" >> .invenio.private

# Copying whole app directory into /opt/invenio/src, the working directory
COPY ./ .

# Copy required files to instance path
RUN mkdir -p ${INVENIO_INSTANCE_PATH} && \
    cp ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini && \
    cp ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini && \
    cp ./docker/startup_ui.sh ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    cp ./docker/startup_api.sh ${INVENIO_INSTANCE_PATH}/startup_api.sh && \
    cp ./docker/startup_worker.sh ${INVENIO_INSTANCE_PATH}/startup_worker.sh && \
    cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg && \
    cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates && \
    cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_api.sh && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_worker.sh && \
    ls -l ${INVENIO_INSTANCE_PATH}/startup_*.sh && \
    test -f ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    test -f ${INVENIO_INSTANCE_PATH}/startup_api.sh && \
    test -x ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    test -x ${INVENIO_INSTANCE_PATH}/startup_api.sh

# Install uwsgi from source for Alpine compatibility
RUN apk add --no-cache build-base && \
    cd /tmp && \
    curl -O https://github.com/unbit/uwsgi/archive/refs/tags/2.0.23.tar.gz && \
    tar xf 2.0.23.tar.gz && \
    cd uwsgi-2.0.23 && \
    python3 uwsgiconfig.py --build && \
    python3 setup.py install && \
    cd / && \
    rm -rf /tmp/uwsgi-2.0.23 /tmp/2.0.23.tar.gz && \
    apk del build-base

RUN uv pip install --break-system-packages --editable . && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-modular-deposit-form && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-group-collections-kcworks && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-modular-detail-page && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-record-importer-kcworks && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-remote-api-provisioner && \
    uv pip install --break-system-packages --editable ./site/kcworks/dependencies/invenio-remote-user-data-kcworks

RUN invenio collect --verbose && invenio webpack clean create && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/theme.config && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/custom_fields && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/search && \
    invenio webpack install && \
    # symlinking of assets has to be run from src directory
    cd /opt/invenio/src && \
    invenio shell /opt/invenio/src/scripts/symlink_assets.py && \
    invenio webpack build

# Set working directory to instance path for startup scripts
# WORKDIR ${INVENIO_INSTANCE_PATH}

ENTRYPOINT ["/bin/bash", "-c"]
