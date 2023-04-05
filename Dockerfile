# Dockerfile that builds a fully functional image of your app.
#
# This image installs all Python dependencies for your application. It's based
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

COPY site ./site
COPY Pipfile Pipfile.lock ./
# TODO: add PIPENV_VENV_IN_PROJECT=1 to command below to put virtual
# environment in ./.venv/ rather than installing in container's system py?
RUN pipenv install --deploy --system

# TODO: maybe restore for production?
# These files and directories will be mounted directly in dev docker-compose
# since the mounts override these points. Copied files to be used in production.
# COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
# COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
# COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
# COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
# COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/
# This is copying whole app directory into /opt/invenio/src in container
# since WORKDIR is set to that folder in base image
COPY ./ .

# TODO: maybe restore for production?
# RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/ && \
#     cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/ && \
#     invenio collect --verbose  && \
#     invenio webpack buildall
# RUN cp -r /opt/invenio/src/static/. ${INVENIO_INSTANCE_PATH}/static/ && \
#     cp -r /opt/invenio/src/assets/. ${INVENIO_INSTANCE_PATH}/assets/
    # && \
    # invenio collect --verbose  && \
    # invenio webpack buildall

ENTRYPOINT [ "bash", "-c"]
