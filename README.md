# Knowledge Commons Repository

This is the source code for the Knowledge Commons Repository, based on InvenioRDM.

## Copyright

Copyright 2023 MESH Research. Released under the MIT license. (See the included LICENSE.txt file.)

## Installation for Development

These instructions allow you to run the Knowledge Commons Repository for local development. The app source files are copied onto your system, and the Invenio python modules are installed locally. Most of the other services used by the app, however, are run from docker containers.

The installation requirements below are drawn in part from https://inveniordm.docs.cern.ch/install/requirements/.

## Clone the knowledge-commons-repository Code

Using GIT, clone this repository. You should then have a folder called `knowledge-commons-repository` (unless you chose to name it something else) on your local computer.

## Add .env file

Private environment variables (like security keys) should never be committed to version control or a repository. You must create your own .env.private file and place it at the root level of the knowledge-commons-repository folder. Any configuration variables to be picked up by Invenio should have the prefix "INVENIO_" added to the beginning of the variable name. Environment variables for other services (e.g., for pgadmin) should not.

This file should contain at least the following variables, substituting appropriate values after each = sign:

INVENIO_SECRET_KEY=CHANGE_ME
INVENIO_SECURITY_LOGIN_SALT='..put a long random value here..'
INVENIO_CSRF_SECRET_SALT='..put a long random value here..'
INVENIO_DATACITE_PASSWORD=myothersecurepassword
PGADMIN_DEFAULT_EMAIL=myemail@somedomain.edu
PGADMIN_DEFAULT_PASSWORD=myverysecurepassword
POSTGRES_USER=knowledge-commons-repository
POSTGRES_PASSWORD=knowledge-commons-repository
POSTGRES_DB=knowledge-commons-repository

Random values for the INVENIO_SECRET_KEY can be generated in a terminal by running
```console
python -c 'import secrets; print(secrets.token_hex())'
```

## Customize .env.local file

This repository does include a file of local environment variables that are
not secret but should be customized for each installation. These are separated out from the main invenio.cfg file, which contains values that
are fixed for all instances of the Knowledge Commons Repository.

## Install Python and Required Python Tools

### Ensure some version of python is installed

Most operating systems (especially MacOS and Linux) will already have a version of Python installed. You can proceed directly to the next step.

### Install pyenv and pipenv

First install the **pyenv** tool to manage python versions, and the **pipenv** tool to manage virtual environments. (There are other tools to use for virtual environment management, but InvenioRDM is built to work with pipenv.)

Instructions for Linux, MacOS, and Windows can be found here: https://www.newline.co/courses/create-a-serverless-slackbot-with-aws-lambda-and-python/installing-python-3-and-pyenv-on-macos-windows-and-linux

### Install and enable the proper python version

Invenio's command line tools require a specific python version to work reliably. Currently this is python 3.9.16.  At the command line, first install this python version using pyenv:
```console
pyenv install 3.9.16
```
Note: It is important to use cpython. Invenio does not support other python interpreters (like pypy) and advises against using anaconda python in particular for running the RDM application.

Just because this python version is installed does not guarantee it will be used. Next, navigate to the directory where you cloned the source code, and set the correct python version to be used locally:

```console
cd ~/path/to/directory/knowledge-commons-repository
pyenv local 3.9.16
```

### Install the Invenio command line tool

From the same directory Use pip to install the **invenio-cli** python package. (Do not use pipenv yet or create a virtual environment.)

```console
pip install invenio-cli
```

## Install Docker 20.10.10+ and Docker-compose 1.17.0+


### Linux

If you are using Ubuntu, follow the steps for installing Docker and Docker-compose explained here: https://linux.how2shout.com/install-and-configure-docker-compose-on-ubuntu-22-04-lts-jammy/


You must then create a `docker` group and add the current user to it (so that you can run docker commands without sudo). This is *required* for the invenio-cli scripts to work, and it must be done for the *same user* that will run the cli commands:

```console
sudo usermod --append --groups docker $USER
```

You will likely want to configure Docker to start on system boot with systemd.

### MacOS

If you are using MacOS, follow the steps for installing Docker desktop explained here: https://docs.docker.com/desktop/install/mac-install/

You will then need to ensure Docker has enough memory to run all the InvenioRDM containers. In the Docker Desktop app,

- click settings cog icon (top bar near right)
- set the memory slider under the "Resources" tab manually to at least 6-8GB

Note: The environment variable recommended in the InvenioRDM documentation for MacOS 11 Big Sur is *not* necessary for newer MacOS versions.

### Fixing docker-compose "not found" error

With the release of compose v2, the command syntax changed from `docker-compose` to `docker compose` (a command followed by a sub-command instead of one hyphenated command). This will break the invenio-cli scripts, which use the `docker-compose` command and you will receive an error asking you to install the "docker-compose" package.

The solution on Linux systems is to install Docker Compose standalone, which uses the old `docker-compose` syntax:

```console
sudo curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
suod chmod +x /usr/local/bin/docker-compose
```

See further https://docs.docker.com/compose/install/other/

### Docker log rotation

Regardless of your operating system, you should set up log rotation for containers to keep the size of logging files from getting out of control. Either set your default logging driver to "local" (which rotates log files automatically) or set logging configuration if you use the "json-file" logging driver. See https://docs.docker.com/config/containers/logging/configure/

### Note about docker contexts

Make sure to always use the same Docker context to run all of the containers for InvenioRDM. See further, https://docs.docker.com/engine/context/working-with-contexts/

## Install Node.js and NVM

Currently InvenioRDM (v. 11) requires Node.js version 16.19.1. The best way to install and manage Node.js versions is using the nvm version manager.
???

### Activate the correct Node.js version

Navigate to the root knowledge-commons-repository folder and activate the required Node.js version:
```console
cd ~/path/to/directory/knowledge-commons-repository
nvm use 16.19.1
```

## Install the Invenio Modules Locally

Navigate to the root knowledge-commons-repository folder. Then run the installation script:
```console
cd ~/path/to/directory/knowledge-commons-repository
invenio-cli install
```
Note: This installation step will take a long time (at least several minutes). It is installing several python packages and building quite a bit of js and css!

This stage
- locks the python package requirements and installs all the Invenio python packages, along with all of the other python dependencies.
- ???

## Build and Configure the Containerized Services

### Build the containers for the services

This step does several things:

- builds several images
    - web server image (frontend)
        - based on nginx, using ./docker/nginx/Dockerfile
    - remote images for other services
        - mq, search, db, cache, pgadmin, opensearch-dashboards, worker
- starts all containers
- destroys redis cache, database, index, and queue (if --force flag is True [not default])
- creates database and table structure
- creates Invenio admin role and assigns it superuser access
- begins indexing
- creates invenio fixtures
- inserts demo data into database (if --no-demo-data is False [default])

You can perform the build using invenio-cli:

```console
invenio-cli services setup
```

Or you can run the commands that invenio-cli uses under the hood:

```console
pipenv lock
docker-compose build
```

### Start the containers

```console
docker-compose up -d
```

### Set up the services

This stage is generally only performed once after building (or rebuilding) the main knowledge-commons-repository image. It does several things:


Note: This setup step takes much less time than the build step, but can still take a few minutes.

You can perform the setup using invenio-cli:

```console
invenio-cli containers setup
```

## Create an admin user

From the command line, enter a command line inside one of the main app containers:
```console
docker exec -it knowledge-commons-repository-web-ui-1 bash
```
From inside the container, run these commands to create and activate the admin user:
```console
invenio users create <email> --password <password>
invenio users activate <email>
```
If you want this user to have access to the administration panel in Invenio, you also need to run
```console
invenio access allow administration-access user <email>
```
After this you will still be in the container's bash prompt. To leave the container (without killing your ssh session when you're doing this remotely) simply press ctrl-P followed by ctrl-Q.

## Use the application!

You should now be able to access the following:
- The Knowledge Commons Repository app (https://localhost)
- The Knowledge Commons Repository REST api (https://localhost/api)
- pgAdmin for database management (https://localhost/pgadmin)
- Opensearch Dashboards for managing search (https://localhost:5601)

## Control the containerized services

### Start the containers

With the invenio cli:
```console
invenio-cli containers start
```

or directly with docker commands:
```console
docker-compose --file docker-compose.full.yml up -d
```

### Stop the containers

With the invenio cli:
```console
invenio-cli containers stop
```

or directly with docker commands:
```console
docker-compose --file docker-compose.full.yml stop
```

Note that stopping the containers this way will not destroy the data and configuration which live in docker volumes. Those volumes persist as long as the containers are not destroyed.

### View container logging output

The logging output (and stdout) can be viewed with Docker Desktop using its convenient ui. It can also be viewed from the command line using:

```console
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

### Controlling containerized nginx server

The frontend container is configured so that the configuration files in docker/nginx/ are bind mounted. This means that changes to those config files can be seen in the running container and enabled without rebuilding the container. To reload the nginx configuration, first enter the frontend container:
```console
docker exec -it knowledge-commons-repository-frontend-1 bash
```
Then tell gninx to reload the config files:
```console
nginx -s reload
```
You can also test the nginx config prior to reloading by running
```console
nginx -t
```

## Developing the Knowledge Commons Repository

### Branching and committing

In general, all members of the development team should commit their work to the `main` branch on a daily basis. It is a good idea to create your own local `working` branch to use for your own development. This allows you to commit changes while work is unfinished without breaking the `main` branch for others. Normally, though, at least once a day you should merge your `working` branch with `main` and push your changes to Github. Only create a new feature branch to push to Github if your work (a) requires leaving things broken that others might rely on, and (b) will take more than a day to complete. This should, though, be regarded as an unusual, temporary measure. You should inform the rest of the development team when the new feature branch is created, and plan to merge it with `main` as soon as possible.

### Making changes to template files

Changes made to jinja template files will be visible immediately in the running Knowledge Commons Repsitory instance.

### Making changes to theme (CSS) and javascript files

#### Building js and css assets

Unlike python and config files, the less and javascript files you customize must go through a build process before they will be visible in the running Knowledge Commons Repository instance. The Invenio platform provides a convenient cli script for collecting all of these assets (both standard and your customized files) and running webpack to build them.

First enter the web-ui container:
```console
docker exec -it knowledge-commons-repository-web-ui-1 bash
```
Then run the cli build script from inside the container:
```console
invenio collect -v
invenio webpack buildall
```
This command will copy all files from the `src` folder to the application
instance folder project, download the npm packages and run Webpack to build our assets.

Alternately, you can perform each of these steps separately:
```console
invenio webpack create  # Copy all sources to the working directory
invenio webpack install # Run npm install and download all dependencies
invenio webpack build # Run npm run build.
```
After the first run of the webpack build script, the webpack configuration files can be found in your local instance folder under `assets/build/`.

#### Watching for changes to existing files

In development, if you want to avoid having to build these files after every change, you can instead run (inside the web-ui container):
```console
invenio webpack run start
```
or, without using invenio's cli, navigate to your local knowledge-commons-repository folder and run the npm watch service using a separate node.js container:
```console
docker run --rm -it -u 1000:1000 -v $PWD/assets:/opt/invenio/var/instance/assets -v $PWD/static:/opt/invenio/var/instance/static/ -w /opt/invenio/var/instance/assets node:19 sh -c "NODE_OPTIONS=--openssl-legacy-provider npm run start"
```
That will watch for changes and automatically rebuild whatever assets are necessary as you go. You will need to run this command in its own terminal, since it will continue to feed output to the terminal until you stop watching the files.

#### Adding new js or css files

The `watch` command will only pick up changes to files that already existed during the last Webpack build. If you add a new javascript or css (less) file, you need to again run
```console
invenio-cli assets build
```
or, without using invenio's cli, navigate to your local knowledge-commons-repository folder and run the build operation using a separate node.js container:
```console
docker run --rm -it -u 1000:1000 -v $PWD/assets:/opt/invenio/var/instance/assets -v $PWD/static:/opt/invenio/var/instance/static/ -w /opt/invenio/var/instance/assets node:19 sh -c "npm ci &&  NODE_OPTIONS=--openssl-legacy-provider npm run build"
```

And then start the `watch` command again.

### Making changes to static files

Because of Flask's decentralized structure, Static files like images must be collected into a central directory. After making changes to static files, enter the web-ui container:
```console
docker exec -it knowledge-commons-repository-web-ui-1 bash
```
and then run:
```console
invenio collect -v
```
or
```console
flask collect -v
```

### Running automated tests

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-repository Github repo. You can also run the test suite locally. Again, enter the web-ui


## DEPRECATED (Default README text from InvenioRDM)

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
