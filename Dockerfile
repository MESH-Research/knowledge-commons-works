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

# TODO: Add env variables below?
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONFAULTHANDLER 1

# Install prerequisites for building xmlsec Python package
# also adds ps command for debugging
RUN dnf install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel procps -y
# Copy over directory for kcr instance Python package
COPY site ./site

COPY Pipfile Pipfile.lock ./

RUN git clone https://github.com/MESH-Research/invenio-communities.git /opt/invenio/invenio-communities && \
    git clone https://github.com/MESH-Research/invenio-rdm-records.git /opt/invenio/invenio-rdm-records && \
    git clone -b local-working --single-branch https://github.com/MESH-Research/invenio-vocabularies.git /opt/invenio/invenio-vocabularies && \
    git clone https://github.com/MESH-Research/invenio-group-collections.git /opt/invenio/invenio-group-collections/ && \
    git clone https://github.com/MESH-Research/invenio-modular-deposit-form.git /opt/invenio/invenio-modular-deposit-form/ && \
    git clone https://github.com/MESH-Research/invenio-modular-detail-page.git /opt/invenio/invenio-modular-detail-page/ && \
    git clone https://github.com/MESH-Research/invenio-record-importer.git /opt/invenio/invenio-record-importer/ && \
    git clone https://github.com/MESH-Research/invenio-records-resources.git /opt/invenio/invenio-records-resources/ && \
    git clone https://github.com/MESH-Research/invenio-remote-api-provisioner.git /opt/invenio/invenio-remote-api-provisioner/ && \
    git clone https://github.com/MESH-Research/invenio-remote-user-data.git /opt/invenio/invenio-remote-user-data/

# NOTE: turned off --deploy for dev
RUN pipenv install --system

RUN echo "[cli]" >> .invenio.private && \
    echo "services_setup=False" >> .invenio.private && \
    echo "instance_path=/opt/invenio/var/instance" >> .invenio.private

# Copying whole app directory into /opt/invenio/src
# (WORKDIR is set to that folder in base image)
COPY ./ .
ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    INVENIO_SITE_UI_URL=https://localhost \
    INVENIO_SITE_API_URL=https://localhost \
    MIGRATION_SERVER_DOMAIN=localhost \
    MIGRATION_SERVER_PROTOCOL=http \
    MIGRATION_API_TOKEN=changeme

RUN cp -r ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini && \
    cp -r ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini && \
    cp -r ./docker/startup_ui.sh ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    cp -r ./docker/startup_api.sh ${INVENIO_INSTANCE_PATH}/startup_api.sh && \
    cp -r ./docker/startup_worker.sh ${INVENIO_INSTANCE_PATH}/startup_worker.sh && \
    cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg && \
    cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates && \
    cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data
RUN chmod +x ${INVENIO_INSTANCE_PATH}/startup_ui.sh && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_api.sh && \
    chmod +x ${INVENIO_INSTANCE_PATH}/startup_worker.sh

RUN invenio collect --verbose && invenio webpack clean create && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less && \
    cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/theme.config && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/custom_fields && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/search && \
    invenio webpack install && \
    invenio shell ./scripts/symlink_assets.py && \
    invenio webpack build

ENTRYPOINT ["bash", "-c"]
