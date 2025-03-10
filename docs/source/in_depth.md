# In-depth Installation Instructions (NEEDS UPDATING)

## Install Python and Required Python Tools

### Ensure some version of python is installed

Most operating systems (especially MacOS and Linux) will already have a version of Python installed. You can proceed directly to the next step.

### Install pyenv and pipenv

First install the **pyenv** tool to manage python versions, and the **pipenv** tool to manage virtual environments. (There are other tools to use for virtual environment management, but InvenioRDM is built to work with pipenv.)

Instructions for Linux, MacOS, and Windows can be found here: https://www.newline.co/courses/create-a-serverless-slackbot-with-aws-lambda-and-python/installing-python-3-and-pyenv-on-macos-windows-and-linux

### Install and enable Python 3.9.16

Invenio's command line tools require a specific python version to work reliably. Currently this is python 3.9.16.  At the command line, first install this python version using pyenv:
```console
pyenv install 3.9.16
```
Note: It is important to use cpython. Invenio does not support other python interpreters (like pypy) and advises against using anaconda python in particular for running the RDM application.

Just because this python version is installed does not guarantee it will be used. Next, navigate to the directory where you cloned the source code, and set the correct python version to be used locally:

```console
cd ~/path/to/directory/knowledge-commons-works
pyenv local 3.9.16
```

#### Install the invenio-cli command line tool

From the same directory Use pip to install the **invenio-cli** python package. (Do not use pipenv yet or create a virtual environment.)

```console
pip install invenio-cli
```

## Install Docker 20.10.10+ and Docker-compose 1.17.0+

### Linux

If you are using Ubuntu Linux, follow the steps for installing Docker and Docker-compose explained here: https://linux.how2shout.com/install-and-configure-docker-compose-on-ubuntu-22-04-lts-jammy/

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

One solution on Linux systems is to install Docker Compose standalone, which uses the old `docker-compose` syntax:

```console
sudo curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Another approach is simply to alias the `docker compose` command to `docker-compose` in the configuration file for your command line shell (.bashrc, .zshrc, or whichever config file is used by your shell).

See further https://docs.docker.com/compose/install/other/

### Docker log rotation

Regardless of your operating system, you should set up log rotation for containers to keep the size of logging files from getting out of control. Either set your default logging driver to "local" (which rotates log files automatically) or set logging configuration if you use the "json-file" logging driver. See https://docs.docker.com/config/containers/logging/configure/

### Note about docker contexts

Make sure to always use the same Docker context to run all of the containers for InvenioRDM. See further, https://docs.docker.com/engine/context/working-with-contexts/

## Install Node.js and NVM

Currently InvenioRDM (v. 11) requires Node.js version 16.19.1. The best way to install and manage Node.js versions is using the nvm version manager. You can find instructions here: https://www.freecodecamp.org/news/node-version-manager-nvm-install-guide/

Once nvm is installed, install the required Node.js version and set it as the active version:
```console
nvm install v16.19.1
nvm use 16.19.1
```
You may have other Node versions installed as well, so before a session working with Knowledge Commons Works it's a good idea to make sure you're using the correct version. On MacOS and Linux you can check
from the command line with
```console
which node
```

## Clone the knowledge-commons-works Code

Using GIT, clone this repository. You should then have a folder called `knowledge-commons-works` (unless you chose to name it something else) on your local computer.

(add-and-configure-an-environment-file)=
## Add and Configure an Environment File

### Standardized environment variables

For local development, this file must include the following variables with these values:

```
INVENIO_INSTANCE_PATH=/opt/invenio/var/instance
INVENIO_RECORD_IMPORTER_LOCAL_DATA_DIR=/
INVENIO_RECORD_IMPORTER_DATA_DIR=/opt/invenio/var/import_data
INVENIO_SEARCH_DOMAIN='search:9200'
INVENIO_SITE_UI_URL="https://localhost"
INVENIO_SITE_API_URL="https://localhost/api"
REDIS_DOMAIN='cache:6379'
INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://kcworks:kcworks@db/kcworks"
POSTGRES_USER=kcworks
POSTGRES_DB=kcworks
```

The INVENIO_INSTANCE_PATH should be set to the full path of the instance directory where InvenioRDM will store its compiled files. Since KC Works runs inside containers, this is normally a standard folder inside the container file systems (/opt/invenio/var/instance). If you were to run InvenioRDM with the python/uwsgi processes installed on your local machine, this would be a folder inside your local virtual environment folder. For example, on MacOS this might be ~/.local/share/virtualenvs/{virtual env name}/var/instance/.

### Variables for local credentials

Several variables hold random values used to secure the application, or hold passwords and email addresses supplied by the local developer:

```
INVENIO_CSRF_SECRET_SALT='..put a long random value here..'
INVENIO_SECURITY_LOGIN_SALT='..put a long random value here..'
INVENIO_SECRET_KEY=CHANGE_ME
POSTGRES_PASSWORD=???
PGADMIN_DEFAULT_EMAIL=???
PGADMIN_DEFAULT_PASSWORD=???
```

Random values for secrets like INVENIO_SECRET_KEY can be generated in a terminal by running
```console
python -c 'import secrets; print(secrets.token_hex())'
```
#### Additional environment variables with sensitive information

Additionally, you should add the following variables with the appropriate values obtained from the Commons administrators:

```
COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators
```
You will also need to enter the following variable with a dummy value and then replace it with the actual value after the instance is set up. Once you have an administrative user, you can generate a token for that user in the KC Works admin ui and enter it here:

```
API_TOKEN=myapitoken
```

#### Additional required environment variables with paths on your local file system

The next variables refer to paths on your local file system that are used during local development to provide easy access to the source code of various python packages and KCWorks modules:

```
PYTHON_LOCAL_GIT_PACKAGES_PATH=/path/to/local/git/packages
PYTHON_LOCAL_SITE_PACKAGES_PATH=/path/to/local/virtual/environment/lib/python3.12/site-packages
```

PYTHON_LOCAL_GIT_PACKAGES_PATH is the parent directory that holds cloned packages that aren't available via pip or that have been forked by us. If you are not working with the KCWorks custom modules locally, this can be set to the folder where you cloned the KCWorks code. Otherwise, it should be the path to the parent folder containing the git repositories for the forked Invenio modules and the extra KC Works modules.

PYTHON_LOCAL_SITE_PACKAGES_PATH is the path to the site-packages folder in your local virtual environment. This assumes that you have run `pipenv install --dev --python=3.12` in your KCWorks project folder to install the python packages locally in a virtual environment.

## Install the Invenio Python Modules

Navigate to the root knowledge-commons-works folder and run
```console
pipenv install --dev --python=3.12
```
Note: This installation step will take several minutes.

This stage
- creates and initializes a Python virtual environment using pipenv
- locks the python package requirements
- installs the Invenio python packages (with pipenv)
    - these packages are again installed under your virtual environment folder. On MacOS this is often ~/.local/share/virtualenvs/{virtual env name}/lib/python3.9/site-packages/. You will find several modules installed here with names that start with "invenio_".
- installs the `kcworks` Python package (with pipenv)
    - alongside the Invenio packages you will also find a `kcworks` package containing any custom extensions to InvenioRDM defined in your `knowledge-commons-works/sites/` folder
- installs required python dependencies (with pipenv)

## Build and Configure the Containerized Services

### Build and start the containers

Make sure you are in the root knowledge-commons-works folder and then run
```console
docker-compose up -d
```
This step will
- build the docker image for the nginx web server (frontend) using ./docker/nginx/Dockerfile
- pull remote images for other services: mq, search, db, cache, pgadmin, opensearch-dashboards
- start containers from all of these images and mounts local files or folders into the containers as required in the docker-compose.yml and docker-services.yml files

### Create and initialize the database, search indices, and task queue

Again, from the root knowledge-commons-works folder, run this command:
```console
invenio-cli services setup
```

This step will
- create the postgresql database and table structure
- create Invenio admin role and assigns it superuser access
- begin indexing with OpenSearch
- create Invenio fixtures
- insert demo data into the database (unless you add the --no-demo-data flag)

Note: If for some reason you need to run this step again, you will need to add the `--force` flag to the `docker-compose` command. This tells Invenio to destroy any existing redis cache, database, index, and task queue before recreating them all. Just be aware that performing this setup again with `--force` will **destroy all data in your database and all OpenSearch indices**.

### Start the uwsgi applications and celery worker

Finally, you need to start the actual applications. Knowledge Commons Works is actually run as two separate applications: one providing an html user interface, and one providing a REST api and serving JSON responses. Each application is served to the nginx web server by its own uwsgi process. The nginx server begins automatically when the `frontend` docker container starts, but the uwsgi applications run on your local machine and need to be started directly.

These applications are also supported by a Celery worker process. This is a task queue that (with the help of the RabbitMQ docker container) frees up the python applications from being blocked by long-running tasks like indexing. The celery worker also runs on your local machine and must be started directly.

If you want to quickly start all of these processes in the background (as daemons), you can run the kcr-startup.sh script in the root knowledge-commons-works directory:
```console
bash kcr-startup.sh
```
The processes will output request and error logging to files in the `logs` folder of your knowledge-commons-works folder.

To stop these processes, simply run
```console
bash kcr-shutdown.sh
```

If you would like to view the real time log output of these processes, you can also start them individually in three separate terminals:
```console
pipenv run celery --app invenio_app.celery worker --beat --events --loglevel INFO
```
```console
pipenv run uwsgi docker/uwsgi/uwsgi_ui.ini --pidfile=/tmp/kcr_ui.pid
```
```console
pipenv run uwsgi docker/uwsgi/uwsgi_rest.ini  --pidfile=/tmp/kcr_api.pid
```
These processes can be stopped individually by pressing CTRL-C

### Create an admin user

From the command line, run these commands to create and activate the admin user:
```console
pipenv run invenio users create <email> --password <password>
pipenv run invenio users activate <email>
```
If you want this user to have access to the administration panel in Invenio, you also need to run
```console
pipenv run invenio access allow administration-access user <email>
```

## Use the application!

You should now be able to access the following:
- The Knowledge Commons Works app (https://localhost)
- The Knowledge Commons Works REST api (https://localhost/api)
- pgAdmin for database management (https://localhost/pgadmin)
- Opensearch Dashboards for managing search (https://localhost:5601)

### Controlling the Application Services

Once Knowledge Commons Works is installed, you can manage its services from the command line. **Note: Unless otherwise specified, the commands below must be run from the root knowledge-commons-works folder.**

### Startup and shutdown scripts

The bash script kcr-startup.sh will start
    - the containerized services (if not running)
    - the celery worker
    - the two uwsgi processes
It will also ensure that you have a .env file and copy your set your INVENIO_INSTANCE_PATH variable in that file to your local instance folder, matching the instance_path variable in your .invenio.private file.

Simply navigate to the root knowledge-commons-works folder and run
```console
bash ./kcr-startup.sh
```

To stop the processes and containerized services, simply run
```console
bash ./kcr-shutdown.sh
```

### Controlling just the containerized services

If you want to stop or start just the containerized services (rather than the local processes), you can use the invenio cli:
```console
invenio-cli services start
invenio-cli services stop
```
Or you can control them directly with the docker-compose command:
```console
docker-compose up -d
docker-compose stop
```
Note that stopping the containers this way will not destroy the data and configuration which live in docker volumes. Those volumes persist as long as the containers are not destroyed. **Do not use the `docker-compose down` command unless you want the containers to be destroyed.**

### View logging output for uwsgi processes

Activity and error logging for the two uwsgi processes are written to date-stamped files in the knowledge-commons-works/logs/ folder. To watch the live logging output from one of these processes, open a new terminal in your knowledge-commons-works folder and run
```console
tail -f logs/uwsgi-ui-{date}.log
```
or
```console
tail -f logs/uwsgi-api-{date}.log
```

### View container logging output

The logging output (and stdout) can be viewed with Docker Desktop using its convenient ui. It can also be viewed from the command line using:

```console
docker logs <image-name> -f
```

The names of the various images are:
- nginx: kcworks-frontend-1
- RabbitMQ: kcworks-mq-1
- PostgreSQL: kcworks-db-1
- OpenSearch: kcworks-search-1
- Redis: kcworks-cache-1
- OpenSearch Dashboards: kcworks-opensearch-dashboards-1
- pgAdmin: kcworks-pgadmin-1

### Controlling containerized nginx server

The frontend container is configured so that the configuration files in docker/nginx/ are bind mounted. This means that changes to those config files can be seen in the running container and enabled without rebuilding the container. To reload the nginx configuration, first **enter the frontend container**:
```console
docker exec -it kcworks-frontend-1 bash
```
Then tell gninx to reload the config files:
```console
nginx -s reload
```
You can also test the nginx config prior to reloading by running
```console
nginx -t
```
Alternately, you can rebuild and restart the frontend container by running
```console
docker-compose up -d --build frontend
```
