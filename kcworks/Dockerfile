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

FROM registry.cern.ch/inveniosoftware/almalinux:1



# Install prerequisites for building xmlsec Python package
# also adds ps command for debugging
RUN dnf install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel procps -y
# Copy over directory for kcr instance Python package

COPY modules/ ${WORKING_DIR}

#Install pipenv deps
#WORKDIR ${WORKING_DIR}/src
COPY app/Pipfile app/Pipfile.lock ./
COPY app/site ./site

RUN pipenv install --system

COPY app/ ./


RUN echo "[cli]" >> .invenio.private && \
    echo "services_setup=False" >> .invenio.private && \
    echo "instance_path=/opt/invenio/var/instance" >> .invenio.private

ENV INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    MIGRATION_SERVER_DOMAIN=localhost \
    MIGRATION_SERVER_PROTOCOL=http \
    MIGRATION_API_TOKEN=changeme


COPY instance/ ${INVENIO_INSTANCE_PATH}

RUN invenio collect --verbose && invenio webpack clean create && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/theme.config && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/custom_fields && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/search && \
    invenio webpack install && \
    invenio shell ./scripts/symlink_assets.py && \
    invenio webpack build

ENTRYPOINT ["bash", "-c"]
