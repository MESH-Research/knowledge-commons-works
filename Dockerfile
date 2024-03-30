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
RUN dnf install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel -y
# Copy over directory for kcr instance Python package
COPY site ./site

COPY Pipfile Pipfile.lock ./
# Copy in forked packages to be installed from local
# COPY ./invenio-communities/ /opt/invenio/src/invenio-communities/
RUN git clone https://github.com/MESH-Research/invenio-communities.git /opt/invenio/invenio-communities
# COPY ./invenio-rdm-records/ /opt/invenio/src/invenio-rdm-records/
RUN git clone https://github.com/MESH-Research/invenio-rdm-records.git /opt/invenio/invenio-rdm-records
RUN git clone https://github.com/MESH-Research/invenio-groups.git /opt/invenio/invenio-groups/
RUN git clone https://github.com/MESH-Research/invenio-modular-deposit-form.git /opt/invenio/invenio-modular-deposit-form/
RUN git clone https://github.com/MESH-Research/invenio-modular-detail-page.git /opt/invenio/invenio-modular-detail-page/
RUN git clone https://github.com/MESH-Research/invenio-record-importer.git /opt/invenio/invenio-record-importer/
RUN git clone https://github.com/MESH-Research/invenio-records-resources.git /opt/invenio/invenio-records-resources/
RUN git clone https://github.com/MESH-Research/invenio-remote-api-provisioner.git /opt/invenio/invenio-remote-api-provisioner/
RUN git clone https://github.com/MESH-Research/invenio-remote-user-data.git /opt/invenio/invenio-remote-user-data/
# Install python requirements with pipenv in container
RUN pipenv install --deploy --system

# copy local instance files to instance directory /opt/invenio/var/instance
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/
# Copying whole app directory into /opt/invenio/src
# (WORKDIR is set to that folder in base image)
COPY ./ .

# Copy local static files and css/js assets
RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/ && \
    cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/
# Symlink for dev build
# FIXME: This symlink will only work for containerized development
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/less/knowledge-commons-repository ./site/knowledge_commons_repository/assets/semantic-ui/less/knowledge_commons_repository
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/less/invenio_app_rdm /usr/local/lib/python3.9/site-packages/invenio_app_rdm/theme/assets/semantic-ui/less/invenio_app_rdm
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/less/invenio_theme /usr/local/lib/python3.9/site-packages/invenio_app_rdm/theme/assets/semantic-ui/less/invenio_theme
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/less/theme.config ./assets/less/theme.config
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/less/site/globals/* ./assets/less/site/globals/
RUN ln -s ${INVENIO_INSTANCE_PATH}/assets/js/invenio_app_rdm /usr/local/lib/python3.9/site-packages/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm


# Build assets
RUN invenio collect --verbose  && \
    invenio webpack buildall

ENTRYPOINT ["bash", "-c"]
