# Knowledge Commons Repository

The Knowledge Commons Repository is a collaborative tool for storing and sharing academic research. It is part of the Knowledge Commons and is built using InvenioRDM.

## Copyright

Copyright 2023 MESH Research. Released under the MIT license. (See the included LICENSE.txt file.)

## Installation for Development

These instructions allow you to run the Knowledge Commons Repository for local development. The app source files are copied onto your system, and the Invenio python modules and required Node.js packages are installed locally. The other services used by the application are run from docker containers.

First you will need to have the correct versions of Docker (20.10.10+ with Docker Compose 1.17.0+), Python (3.9.16 with pipenv), and Node.js (16.19.1 with npm and nvm) installed on your system.

From there installation involves these steps and commands:

1. `git clone git@github.com:MESH-Research/knowledge-commons-repository.git`
2. `cd knowledge-commons-repository`
3. create and configure the .env file in this folder
4. `pip install invenio-cli`
5. `invenio-cli install`
6. `docker-compose up -d`
7. `invenio-cli services setup`
8. `bash kcr-startup.sh`

You can then create an admin user. From the command line, run
```console
pipenv run invenio users create <email> --password <password>
pipenv run invenio users activate <email>
pipenv run invenio access allow administration-access user <email>
```

The application instance and its services can be started and stopped using single  commands:
```console
bash kcr-startup.sh
```
```console
bash kcr-shutdown.sh
```

What follows is a step-by-step walk through this process. Note that these instructions do not support installation under Windows. Windows users should emulate a Linux environment using WSL2.

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
cd ~/path/to/directory/knowledge-commons-repository
pyenv local 3.9.16
```

### Install the invenio-cli command line tool

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
suod chmod +x /usr/local/bin/docker-compose
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
You may have other Node versions installed as well, so before a session working with Knowledge Commons Repository it's a good idea to make sure you're using the correct version. On MacOS and Linux you can check
from the command line with
```console
which node
```
## Clone the knowledge-commons-repository Code

Using GIT, clone this repository. You should then have a folder called `knowledge-commons-repository` (unless you chose to name it something else) on your local computer.

## Add and Configure an .env File

Private environment variables (like security keys) should never be committed to version control or a repository. You must create your own .env.private file and place it at the root level of the knowledge-commons-repository folder. Any configuration variables to be picked up by Invenio should have the prefix "INVENIO_" added to the beginning of the variable name. Environment variables for other services (e.g., for pgadmin) should not.

This file should contain at least the following variables, substituting appropriate values after each = sign:

INVENIO_SITE_UI_URL = "https://myhostname"
INVENIO_SITE_API_URL = "https://myhostname/api"
INVENIO_SECRET_KEY=CHANGE_ME
INVENIO_SECURITY_LOGIN_SALT='..put a long random value here..'
INVENIO_CSRF_SECRET_SALT='..put a long random value here..'
PGADMIN_DEFAULT_EMAIL=myemail@somedomain.edu
PGADMIN_DEFAULT_PASSWORD=myverysecurepassword
POSTGRES_USER=knowledge-commons-repository
POSTGRES_PASSWORD=knowledge-commons-repository
POSTGRES_DB=knowledge-commons-repository
INVENIO_DATACITE_USERNAME=MSU.CORE
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword
INVENIO_INSTANCE_PATH=/full/path/to/my/instance/directory

Random values for the INVENIO_SECRET_KEY can be generated in a terminal by running
```console
python -c 'import secrets; print(secrets.token_hex())'
```

Another variable, INVENIO_INSTANCE_PATH, will be added automatically by the kcr-startup.sh script later on.

## Install the Invenio Python Modules

Navigate to the root knowledge-commons-repository folder. Then run the installation script:
```console
cd ~/path/to/directory/knowledge-commons-repository
invenio-cli install
```
Note: This installation step will take several minutes.

This stage
- creates and initializes a Python virtual environment using pipenv
- locks the python package requirements
- updates InvenioRDM's internal instance_path variable to match your local installation
    - this is *not* the folder where you cloned the GIT project, but rather a separate folder where InvenioRDM will place the compiled files used to actually run the application.
    - normally the instance folder is inside the folder for your new virtual environment. On MacOS this will often be ~/.local/share/virtualenvs/{virtual env name}/var/instance/
- installs the Invenio python packages (with pipenv)
    - these packages are again installed under your virtual environment folder. On MacOS this is often ~/.local/share/virtualenvs/{virtual env name}/lib/python3.9/site-packages/. You will find several modules installed here with names that start with "invenio_".
- installs the knowledge-commons-repository Python package (with pipenv)
    - alongside the Invenio packages you will also find a knowledge-commons-repository package containing any custom extensions to InvenioRDM defined in your `knowledge-commons-repository/sites/` folder
- installs required python dependencies (with pipenv)
- symlinks invenio.cfg, templates/, app_data/ to your instance folder
- finds and collects static files into {instance_folder}/static/
    - static files (like images) are scattered throughout the various Invenio python modules and your local knowledge-commons-repository folder. They must be copied to a central location accessible to the web server.
- finds js and less/scss/css files and builds them in {instance_folder}/assets
    - again, this gathers and combines js and style files from all of the Invenio python modules and your local knowledge-commons-repository instance. It also gathers a master list of node.js package requirements from these modules.
    - this build process uses Webpack and is configured in {instance_folder}/assets/webpack.config.js
    - js requirements are installed by npm as node.js modules in the {instance_folder}/assets/node_modules folder
    - note, though, that you *cannot* directly modify the package.json, webpack.config.js files in your instance folder. This is because these files are created dynamically by InvenioRDM each time the build process runs.

## Build and Configure the Containerized Services

### Build and start the containers

Make sure you are in the root knowledge-commons-repository folder and then run
```console
docker-compose up -d
```
This step will
- build the docker image for the nginx web server (frontend) using ./docker/nginx/Dockerfile
- pull remote images for other services: mq, search, db, cache, pgadmin, opensearch-dashboards
- start containers from all of these images and mounts local files or folders into the containers as required in the docker-compose.yml and docker-services.yml files

### Create and initialize the database, search indexes, and task queue

Again, from the root knowledge-commons-repository folder, run this command:
```console
invenio-cli services setup
```

This step will
- create the postgresql database and table structure
- create Invenio admin role and assigns it superuser access
- begin indexing with OpenSearch
- create Invenio fixtures
- insert demo data into the database (unless you add the --no-demo-data flag)

Note: If for some reason you need to run this step again, you will need to add the `--force` flag to the `docker-compose` command. This tells Invenio to destroy any existing redis cache, database, index, and task queue before recreating them all. Just be aware that performing this setup again with `--force` will **destroy all data in your database and all OpenSearch indexes**.

## Start the uwsgi applications and celery worker

Finally, you need to start the actual applications. Knowledge Commons Repository is actually run as two separate applications: one providing an html user interface, and one providing a REST api and serving JSON responses. Each application is served to the nginx web server by its own uwsgi process. The nginx server begins automatically when the `frontend` docker container starts, but the uwsgi applications run on your local machine and need to be started directly.

These applications are also supported by a Celery worker process. This is a task queue that (with the help of the RabbitMQ docker container) frees up the python applications from being blocked by long-running tasks like indexing. The celery worker also runs on your local machine and must be started directly.

If you want to quickly start all of these processes in the background (as daemons), you can run the kcr-startup.sh script in the root knowledge-commons-repository directory:
```console
bash kcr-startup.sh
```
The processes will output request and error logging to files in the `logs` folder of your knowledge-commons-repository folder.

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


## Create an admin user

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
- The Knowledge Commons Repository app (https://localhost)
- The Knowledge Commons Repository REST api (https://localhost/api)
- pgAdmin for database management (https://localhost/pgadmin)
- Opensearch Dashboards for managing search (https://localhost:5601)

### Controlling the Application Services

Once Knowledge Commons Repository is installed, you can manage its services from the command line. **Note: Unless otherwise specified, the commands below must be run from the root knowledge-commons-repository folder.**

### Startup and shutdown scripts

The bash script kcr-startup.sh will start
    - the containerized services (if not running)
    - the celery worker
    - the two uwsgi processes
It will also ensure that you have a .env file and copy your set your INVENIO_INSTANCE_PATH variable in that file to your local instance folder, matching the instance_path variable in your .invenio.private file.

Simply navigate to the root knowledge-commons-repository folder and run
```console
bash ./kcr-startup.sh
```

To stop the processes and containerized services, simply run
```console
bash ./kcr-shutdown.sh
```

### Controlling just the containerized services (postgresql, RabbitMQ, redis, pgAdmin, OpenSearch, opensearch dashboards, nginx)

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

Activity and error logging for the two uwsgi processes are written to date-stamped files in the knowledge-commons-repository/logs/ folder. To watch the live logging output from one of these processes, open a new terminal in your knowledge-commons-repository folder and run
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
- nginx: knowledge-commons-repository-frontend-1
- RabbitMQ: knowledge-commons-repository-mq-1
- PostgreSQL: knowledge-commons-repository-db-1
- OpenSearch: knowledge-commons-repository-search-1
- Redis: knowledge-commons-repository-cache-1
- OpenSearch Dashboards: knowledge-commons-repository-opensearch-dashboards-1
- pgAdmin: knowledge-commons-repository-pgadmin-1

### Controlling containerized nginx server

The frontend container is configured so that the configuration files in docker/nginx/ are bind mounted. This means that changes to those config files can be seen in the running container and enabled without rebuilding the container. To reload the nginx configuration, first **enter the frontend container**:
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
Alternately, you can rebuild and restart the frontend container by running
```console
docker-compose up -d --build frontend
```

## Developing the Knowledge Commons Repository

### Branching and committing

In general, all members of the development team should commit their work to the `main` branch on a daily basis. It is a good idea to create your own local `working` branch to use for your own development. This allows you to commit changes while work is unfinished without breaking the `main` branch for others. Normally, though, at least once a day you should merge your `working` branch with `main` and push your changes to Github. Only create a new feature branch to push to Github if your work (a) requires leaving things broken that others might rely on, and (b) will take more than a day to complete. This should, though, be regarded as an unusual, temporary measure. You should inform the rest of the development team when the new feature branch is created, and plan to merge it with `main` as soon as possible.

### Making changes to template files

Changes made to jinja template files will be visible immediately in the running Knowledge Commons Repository instance.

### Making changes to theme (CSS) and javascript files

#### Building js and css assets

Unlike python and config files, the less and javascript files you customize must go through a build process before they will be visible in the running Knowledge Commons Repository instance. The Invenio platform provides a convenient cli script for collecting all of these assets (both standard and your customized files) and running webpack to build them.
```console
invenio-cli assets build
```
This command will copy all files from the `src` folder to the application
instance folder project, download the npm packages and run Webpack to build our assets.

Behind the scenes it is running the following lower-level commands:
```console
pipenv run invenio collect -v
pipenv run invenio webpack buildall
```

Alternately, you can perform each of these steps separately:
```console
invenio webpack create  # Copy all sources to the working directory
invenio webpack install # Run npm install and download all dependencies
invenio webpack build # Run npm run build.
```

**Note:** Before you run these build commands, ensure that you have activated the correct Node.js version using nvm:
```console
nvm use 16.19.1
```
Otherwise you are likely to have errors during the build process.

#### Watching for changes to existing files

**Note: File watching is currently broken in InvenioRDM v.11. This is a known issue which will hopefully be fixed soon.**

In development, if you want to avoid having to build these files after every change, you can instead run
```console
invenio-cli assets watch
```
or
```console
pipenv run invenio webpack run start
```
<!-- or, without using invenio's cli, navigate to your local knowledge-commons-repository folder and run the npm watch service using a separate node.js container:
```console
docker run --rm -it -u 1000:1000 -v $PWD/assets:/opt/invenio/var/instance/assets -v $PWD/static:/opt/invenio/var/instance/static/ -w /opt/invenio/var/instance/assets node:19 sh -c "NODE_OPTIONS=--openssl-legacy-provider npm run start"
``` -->
That will watch for changes and automatically rebuild whatever assets are necessary as you go. You will need to run this command in its own terminal, since it will continue to feed output to the terminal until you stop watching the files.

#### Adding new js or css files

The `watch` command will only pick up changes to files that already existed during the last Webpack build. If you add a new javascript or css (less) file, you need to again run
```console
invenio-cli assets build
```
<!-- or, without using invenio's cli, navigate to your local knowledge-commons-repository folder and run the build operation using a separate node.js container:
```console
docker run --rm -it -u 1000:1000 -v $PWD/assets:/opt/invenio/var/instance/assets -v $PWD/static:/opt/invenio/var/instance/static/ -w /opt/invenio/var/instance/assets node:19 sh -c "npm ci &&  NODE_OPTIONS=--openssl-legacy-provider npm run build"
``` -->
Then start the `watch` command again.

### Making changes to static files

Because of Flask's decentralized structure, Static files like images must be collected into a central directory. After making changes to static files run
```console
invenio collect -v
```

### Running automated tests

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-repository Github repo. You can (and should) also run the test suite locally.

There are currently two distinct sets of tests that have to be run separately: python tests run using invenio's fixtures, and javascript tests run separately using jest.

### Python tests

The python test suite includes (a) unit tests for back end code, (b) tests of ui views and api requests run with a client fixture, (c) user interaction tests run with selenium webdriver. To run the unit tests and view/request tests, navigate to the root knowledge-commons-repository folder and run
```console
pipenv run pytest
```
By default the selenium browser interaction tests are not run. To include these, run pytest with the E2E environment variable set to "yes":
```console
pipenv run E2E=yes pytest
```
Running the selenium tests also requires that you have the Selenium Client and Chrome Webdriver installed locally.

### Javascript tests

Pytest does not directly test custom javascript files or React components. In order to test these, navigate to the root knowledge-commons-repository folder and run
```console
npm run test
```
These tests are run using the jest test runner, configured in the packages.json file in the root knowledge-commons-repository folder.

Note that these tests run using a local npm configuration in the knowledge-commons-repository folder. Any packages that are normally available to InvenioRDM must be added to the local package.json configuration and will be installed in the local node_modules folder. Since this folder is not included in GIT version control, before you run the javascript tests you must ensure the required packages are installed locally by running
```console
npm install
```

## InvenioRDM Documentation

The Knowledge Commons Repository is built as an instance of InvenioRDM. The InvenioRDM Documentation, including customization and development information, can be found at https://inveniordm.docs.cern.ch/.
