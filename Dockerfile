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
# Copy in forked packages to be installed from local
# COPY ./invenio-communities/ /opt/invenio/src/invenio-communities/
RUN git clone https://github.com/MESH-Research/invenio-communities.git /opt/invenio/invenio-communities
# COPY ./invenio-rdm-records/ /opt/invenio/src/invenio-rdm-records/
RUN git clone https://github.com/MESH-Research/invenio-rdm-records.git /opt/invenio/invenio-rdm-records
RUN git clone https://github.com/MESH-Research/invenio-group-collections.git /opt/invenio/invenio-group-collections/
RUN git clone https://github.com/MESH-Research/invenio-modular-deposit-form.git /opt/invenio/invenio-modular-deposit-form/
RUN git clone https://github.com/MESH-Research/invenio-modular-detail-page.git /opt/invenio/invenio-modular-detail-page/
RUN git clone https://github.com/MESH-Research/invenio-record-importer.git /opt/invenio/invenio-record-importer/
RUN git clone https://github.com/MESH-Research/invenio-records-resources.git /opt/invenio/invenio-records-resources/
RUN git clone https://github.com/MESH-Research/invenio-remote-api-provisioner.git /opt/invenio/invenio-remote-api-provisioner/
RUN git clone https://github.com/MESH-Research/invenio-remote-user-data.git /opt/invenio/invenio-remote-user-data/
# Install python requirements with pipenv in container

# NOTE: turned off --deploy for dev
RUN pipenv install --system
RUN pip install invenio-cli
# FIXME: temporary workaround for python-xmlsec regression in uwsgi
RUN pip uninstall lxml xmlsec -y
RUN pip install --no-binary lxml xmlsec --no-cache-dir

RUN echo "[cli]" >> .invenio.private
RUN echo "services_setup=False" >> .invenio.private
RUN echo "instance_path=/opt/invenio/var/instance" >> .invenio.private


# Copying whole app directory into /opt/invenio/src
# (WORKDIR is set to that folder in base image)
COPY ./ .
ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance
ENV INVENIO_SITE_UI_URL=https://localhost
ENV INVENIO_SITE_API_URL=https://localhost
ENV MIGRATION_SERVER_DOMAIN=localhost
ENV MIGRATION_SERVER_PROTOCOL=http
ENV MIGRATION_API_TOKEN=changeme

RUN cp -r ./docker/uwsgi/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini
RUN cp -r ./docker/uwsgi/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini
RUN cp ./invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg
RUN cp -r ./templates ${INVENIO_INSTANCE_PATH}/templates
RUN cp -r ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data

RUN invenio collect --verbose
RUN invenio webpack clean create
RUN mkdir -p ${INVENIO_INSTANCE_PATH}/assets/less
RUN cp ./assets/less/theme.config ${INVENIO_INSTANCE_PATH}/assets/less/theme.config
RUN mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/custom_fields
RUN mkdir -p ${INVENIO_INSTANCE_PATH}/assets/templates/search
RUN invenio webpack install
RUN invenio shell ./scripts/symlink_assets.py
RUN invenio webpack build

ENTRYPOINT ["bash", "-c"]
