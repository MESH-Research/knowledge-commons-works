# Knowledge Commons Repository

This is the source code for the Knowledge Commons Repository, based on InvenioRDM.

## Copyright

Copyright 2023 MESH Research. Released under the MIT license. (See the included LICENSE.txt file.)

## Installation for Development

These instructions allow you to run the Knowledge Commons Repository in a set of docker containers without installing any of the services locally. The app source files are copied onto your system, though, and changes to those files will take effect without rebuilding the docker images.

Currently, the images *will* have to be rebuilt if you change any of the python package requirements. The images will also have to be rebuilt if you want to change the javascript or css (less) files, requiring that webpack build them again.

The installation requirements below are drawn in part from https://inveniordm.docs.cern.ch/install/requirements/.

### Clone the knowledge-commons-repository code

Using GIT, clone this repository. You should then have a folder called `knowledge-commons-repository` (unless you chose to name it something else) on your local computer.

### Install python and python tools

#### Ensure some version of python is installed

Most operating systems (especially MacOS and Linux) will already have a version of Python installed. You can proceed directly to the next step.

#### Install pyenv and pipenv

First install the **pyenv** tool to manage python versions, and the **pipenv** tool to manage virtual environments. (There are other tools to use for virtual environment management, but InvenioRDM is built to work with pipenv.)

Instructions for Linux, MacOS, and Windows can be found here: [https://www.newline.co/courses/create-a-serverless-slackbot-with-aws-lambda-and-python/installing-python-3-and-pyenv-on-macos-windows-and-linux]

#### Install and enable the proper python version

Invenio's command line tools require a specific python version to work reliably. Currently this is python 3.9.16.  At the command line, first install this python version using pyenv:
```
pyenv install 3.9.16
```
Note: It is important to use cpython. Invenio does not support other python interpreters (like pypy) and advises against using anaconda python in particular for running the RDM application.

Just because this python version is installed does not guarantee it will be used. Next, navigate to the directory where you cloned the source code, and set the correct python version to be used locally:

```
cd ~/path/to/directory/knowledge-commons-repository
pyenv local 3.9.16
```

#### Install the Invenio command line tool

From the same directory Use pip to install the **invenio-cli** python package. (Do not use pipenv yet or create a virtual environment.)

```
pip install invenio-cli
```

### install docker 20.10.10+ and docker-compose 1.17.0+


#### Linux

If you are using Ubuntu, follow the steps for installing Docker and Docker-compose explained here: [https://linux.how2shout.com/install-and-configure-docker-compose-on-ubuntu-22-04-lts-jammy/]

You must then create a `docker` group and add the current user to it (so that you can run docker commands without sudo). This is *required* for the invenio-cli scripts to work, and it must be done for the *same user* that will run the cli commands:

```
sudo usermod --append --groups docker $USER
```

You will likely want to configure Docker to start on system boot with systemd.

#### MacOS

If you are using MacOS, follow the steps for installing Docker desktop explained here: [https://docs.docker.com/desktop/install/mac-install/]

You will then need to ensure Docker has enough memory to run all the InvenioRDM containers. In the Docker Desktop app,

- click settings cog icon (top bar near right)
- set the memory slider under the "Resources" tab manually to at least 6-8GB

Note: The environment variable recommended in the InvenioRDM documentation for MacOS 11 Big Sur is *not* necessary for newer MacOS versions.

#### Docker log rotation

Regardless of your operating system, you should set up log rotation for containers to keep the size of logging files from getting out of control. Either set your default logging driver to "local" (which rotates log files automatically) or set logging configuration if you use the "json-file" logging driver. See https://docs.docker.com/config/containers/logging/configure/

#### Note about docker contexts

Make sure to always use the same Docker context to run all of the containers for InvenioRDM. See further, [https://docs.docker.com/engine/context/working-with-contexts/]

## Build and Configure the Containers

### Build the containers for the app and services

This step does several things:

- locks the python package requirements
- builds several images
    - base app image (knowledge-commons-repository)
        - using ./Dockerfile
        - installs python dependencies
        - builds javascript and css (less) assets using webpack
    - the two images to actually run the app (web-ui and web-api)
        - both based on the base knowledge-commons-repository image
    - web server image (frontend)
        - based on nginx, using ./docker/nginx/Dockerfile
- pulls remote images for other services
    - mq, search, db, cache, pgadmin, opensearch-dashboards, worker
- starts all containers
    - creates and mounts volumes for persisting and sharing data
    - mounts application source and config files in web-ui and web-api containers

Note: This build step will take a long time (at least several minutes). It is installing several python packages and building quite a bit of js and css!

You can perform the build using invenio-cli:

```
invenio-cli containers build
```

Or you can run the commands that invenio-cli uses under the hood:

```
pipenv lock
docker-compose --file docker-compose.full.yml build
```

### Set up the services

This stage is generally only performed once after building (or rebuilding) the main knowledge-commons-repository image. It does several things:

- checks that all containers are running
- destroys redis cache, database, index, and queue (if --force flag is True [not default])
- creates database and table structure
- creates Invenio admin role and assigns it superuser access
- begins indexing
- creates invenio fixtures
- inserts demo data into database (if --no-demo-data is False [default])

Note: This setup step takes much less time than the build step, but can still take a few minutes.

You can perform the setup using invenio-cli:

```
invenio-cli containers build
```

### Create an admin user

From the command line run

```
pipenv run invenio users create <email> --password <password>
pipenv run invenio users activate <email>
```

### Use the application!

You should now be able to access the following:
- The Knowledge Commons Repository app (https://localhost)
- The Knowledge Commons Repository REST api (https://localhost/api)
- pgAdmin for database management (https://localhost:5050)
- Opensearch Dashboards for managing search (https://localhost:5601)

### Control the containerized services

#### Start the containers

With the invenio cli:
```
invenio-cli containers start
```

or directly with docker commands:
```
docker-compose --file docker-compose.full.yml up -d
```

#### Stop the containers

With the invenio cli:
```
invenio-cli containers stop
```

or directly with docker commands:
```
docker-compose --file docker-compose.full.yml stop
```

#### View container logging output

The logging output (and stdout) can be viewed with Docker Desktop using its convenient ui. It can also be viewed from the command line using:

```
docker logs <image-name> -f
```

The names of the various images are:
- knowledge-commons-repository-web-ui-1
- knowledge-commons-repository-web-api-1
- knowledge-commons-repository-frontend-1
- knowledge-commons-repository-mq-1
- knowledge-commons-repository-db-1
- knowledge-commons-repository-search-1
- knowledge-commons-repository-cache-1
- knowledge-commons-repository-opensearch-dashboards-1
- knowledge-commons-repository-pgadmin-1
- knowledge-commons-repository-worker-1


## DEPRECATED

**Note**: The instructions below are the default README for InvenioRDM. They
are not usable as they stand for building the Knowledge Commons Repository
instance. Updated installation instructions will follow.**

Run the following commands in order to start the InvenioRDM instance:

```console
invenio-cli containers start --lock --build --setup
```

The above command first builds the application docker image and afterwards
starts the application and related services (database, opensearch, Redis
and RabbitMQ). The build and boot process will take some time to complete,
especially the first time as docker images have to be downloaded during the
process.

Once running, visit https://127.0.0.1 in your browser.

**Note**: The server is using a self-signed SSL certificate, so your browser
will issue a warning that you will have to by-pass.

## Overview

Following is an overview of the generated files and folders:

| Name | Description |
|---|---|
| ``Dockerfile`` | Dockerfile used to build your application image. |
| ``Pipfile`` | Python requirements installed via [pipenv](https://pipenv.pypa.io) |
| ``Pipfile.lock`` | Locked requirements (generated on first install). |
| ``app_data`` | Application data such as vocabularies. |
| ``assets`` | Web assets (CSS, JavaScript, LESS, JSX templates) used in the Webpack build. |
| ``docker`` | Example configuration for NGINX and uWSGI. |
| ``docker-compose.full.yml`` | Example of a full infrastructure stack. |
| ``docker-compose.yml`` | Backend services needed for local development. |
| ``docker-services.yml`` | Common services for the Docker Compose files. |
| ``invenio.cfg`` | The Invenio application configuration. |
| ``logs`` | Log files. |
| ``static`` | Static files that need to be served as-is (e.g. images). |
| ``templates`` | Folder for your Jinja templates. |
| ``.invenio`` | Common file used by Invenio-CLI to be version controlled. |
| ``.invenio.private`` | Private file used by Invenio-CLI *not* to be version controlled. |

## Documentation

To learn how to configure, customize, deploy and much more, visit
the [InvenioRDM Documentation](https://inveniordm.docs.cern.ch/).
