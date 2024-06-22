# Knowledge Commons Works

Knowledge Commons Works is a collaborative tool for storing and sharing academic research. It is part of Knowledge Commons and is built on an instance of the InvenioRDM repository system.

## Copyright

Copyright 2023-24 Mesh Research. Released under the MIT license. (See the included LICENSE.txt file.)

## Installation for Development

### Quickstart

These instructions allow you to run Knowledge Commons Works for local development. The app source files are copied onto your system, but the Flask application and other services (database, search, etc.) are run in Docker containers. The application is served to your browser by an nginx web server running in a separate container.

First you will need to have the correct versions of Docker (20.10.10+ with Docker Compose 1.17.0+) and Python (3.9.16 with pipenv).

From there, installation involves these steps. Each one is further explained below, but here is a quick reference:

1. Clone the git repository
   1. From your command line, navigate to the parent folder where you want the cloned repository code to live
   2. Clone the knowledge-commons-works repository with `git clone --recurse-submodules git@github.com:MESH-Research/knowledge-commons-works.git`
2. Create your configuration files
   - `cd knowledge-commons-works`
   - Create and configure the `.env` file in this folder as described [here](#add-and-configure-an-env-file)
   - Create the `.invenio.private` file with the following contents:
     ```shell
     [cli]
     services_setup = True
     instance_path = /opt/invenio/var/instance
     ```
3. Start the docker-compose project
   - `docker-compose up -d`
4. Initialize the database and other services, and build asset files
   - enter the `web-ui` container by running `docker compose exec web-ui /bin/bash`
     - _note_: The container name may be different depending on your local docker setup. You can find the correct name by running `docker ps`
   - run the script to set up the instance services and build static assets `bash ./scripts/setup-services.sh`
     - _note_: Some of the commands in this script may take a while to run. Patience is required! The `invenio rdm-records fixtures` command in particular may take up to an hour to complete during which time it provides no feedback. Don't despair! It is working.
5. Create your own admin user
   - enter the `web-ui` container by running `docker compose exec web-ui /bin/bash`
   - run the commands:
     - `invenio users create <email> --password <password>`
     - `invenio users activate <email>`
     - `invenio access allow administration-access user <email>`
6. View the application
   - The Knowledge Commons Works app is now running at `https://kcworks.localtest.me`
   - The REST API is running at `https://kcworks.localtest.me/api`
   - OpenSearch Dashboards is running at `https://opensearch.localtest.me`
   - PGAdmin is running at `https://pgadmin.localtest.me`
   - Traefik's Dashboard is running at `https://traefik.localtest.me`

Further optional steps to allow local debugging or development of the python packages in the Invenio framework and the custom packages created for Knowledge Commons Works:

\*\*NOTE: These instructions have likely changed, but have not been updated yet. Coming soon....

1. In the same parent directory that holds your cloned `knowledge-commons-works` folder, clone the following additional repositories: - `git@github.com:MESH-Research/invenio-record-importer.git` - `git@github.com:MESH-Research/invenio-communities:/opt/invenio/invenio-communities.git` - `git@github.com:MESH-Research/invenio-groups:/opt/invenio/invenio-groups.git` - `git@github.com:MESH-Research/invenio-modular-deposit-form:/opt/invenio/invenio-modular-deposit-form.git` - `git@github.com:MESH-Research/invenio-modular-detail-page:/opt/invenio/invenio-modular-detail-page.git` - `git@github.com:MESH-Research/invenio-rdm-records:/opt/invenio/invenio-rdm-records.git` - `git@github.com:MESH-Research/invenio-records-resources:/opt/invenio/invenio-records-resources.git` - `git@github.com:MESH-Research/invenio-remote-api-provisioner:/opt/invenio/invenio-remote-api-provisioner.git` - `git@github.com:MESH-Research/invenio-remote-user-data:/opt/invenio/invenio-remote-user-data.git`
   The folders holding the cloned code from these repositories should then be direct siblings of your `knowledge-commons-works` folder.
2. Install the invenio-cli tool locally (`pip install invenio-cli`)
3. Install the python packages required by Knowldge Commons Works locally by running `pipenv install` in the `knowledge-commons-works` folder.
   - NOTE: This assumes that you have already cloned the git repositories as described in step 1. If you have not, you will need to do so before running `pipenv install`.
4. When you start up the docker compose project, add an additional project file to the command: - `docker-compose  --file docker-compose.dev.local.yml up -d`
This will mount a variety of local package folders as bind mounts in your running containers. This will allow you to make changes to the python code in the cloned repositories and see those changes reflected in the running Knowledge Commons Works instance.
<!-- Further optional steps to allow fully local development if desired:

    1. Install the invenio-cli tool (`pip install invenio-cli`)
    2. Run `invenio-cli install` locally
    3. With docker running, run `docker-compose up -d`
    4. `invenio-cli services setup --force`
    5.  `bash kcr-startup.sh` -->

### Controlling the Flask application

The application instance and its services can be started and stopped by starting and stopping the docker-compose project:

```shell
docker-compose  up -d
```

```shell
docker-compose  stop
```

> [!Caution]
> Do not use the `docker-compose down` command unless you want the containers to be destroyed. This will destroy all data in your database and all OpenSearch indexes. YOU DO NOT WANT TO DO THIS!

If you need to restart the main Flask application (e.g., after making configuration changes) you can do so either by stopping and restarting the docker-compose project or by running the following command inside the `web-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_ui.pid
```

Similarly, the REST API can be restarted by running the following command inside the `web-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_api.pid
```

But these commands should not be necessary in normal operation.

## Updating the instance with changes

### Changes to html template files

Changes to html template files will be visible immediately in the running Knowledge Commons Works instance. You simply need to refresh the page in your browser.

If you add a new template file (including overriding an existing template file), you will need to collect the new file into the central templates folder and restart the uwsgi processes. This can be done by running the following command inside the `web-ui` container:

```shell
invenio collect -v
uwsgi --reload /tmp/uwsgi_ui.pid
```

Then refresh your browser.

### Changes to invenio.cfg

Changes to the invenio.cfg file will only take effect after the instance uwsgi processes are restarted. This can be done by running the following command inside the `web-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_ui.pid
```

### Changes to theme (CSS) and javascript files

#### The basic build process (slow)

Invenio employs a build process for css and javascript files. Changes to these files will not be visible in the running Knowledge Commons Works instance until the build process is run. This can be done by running the following command inside the `web-ui` container:

```shell
bash ./scripts/build-assets.sh
```

#### Rebuilding changed files on the fly (fast but limited)

The problem is that this build process takes a long time to run, especially in the containers. For most tasks, you can instead run the following command to watch for changes to the files and automatically rebuild them:

```shell
invenio webpack run start
```

The file watching will continue until you stop it with CTRL-C. It will continue to occupy the terminal window where you started it. This means that you can see it respond and begin integrating changed files when it finds them. You can also see there any error or warning output from the build process--very helpful for debugging.

### Adding new files or requirements

The watch command will only pick up changes to files that already existed during the last Webpack build. If you add a new javascript or css (less) file, you need to again run the regular build script to include it in the build process.

### Adding new node.js packages to be included

Normally, the node.js packages to be included in a project are listed in that project's package.json file. In the case of InvenioRDM, the package.json file is created dynamically by InvenioRDM each time the build process runs. So you cannot directly modify the package.json file in your instance folder. Instead, you must add the package to the package.json file in the InvenioRDM module that requires it. Unless you are creating a new stand-alone extension, this will mean adding the package to the `webpack.py` file in the `knowledge-commons-works/sites/kcworks` folder.

There you will find a `WebpackThemeBundle` object that defines your bundle of js and style files along with their dependencies. If I wanted to add the `geopattern` package to the project, I would add it to the `dependencies` dictionary in the `WebpackThemeBundle` object like this:

```python

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "custom_pdf_viewer_js": "./js/invenio_custom_pdf_viewer"
                "/pdfjs.js",
            },
            dependencies={
                "geopattern": "^1.2.3",
            },
            aliases={
                /* ... */
            },
        ),
    },
)
```

If you add a new node.js package to the project, you will then need to run the build script inside the `web-ui` container to install it:

```shell
bash ./scripts/build-assets.sh
```

### Changes to static files

Changes to static files like images will require running the collect command to copy them to the central static folder. This can be done by running the following command inside the `web-ui` container:

```shell
invenio collect -v
```

You will then need to restart the uwsgi processes as described above.

### Changes to python code in the `site` folder

Changes to python code in the `site` folder should (like changes to template files) take effect immediately in the running Knowledge Commons Works instance. You simply need to refresh the page in your browser.

#### Adding new entry points

Sometimes you will need to add new entry points to inform the Flask application about additional code you have provided. This is done via the `setup.py` file in the `site` folder. Once you have added the entry point declaration, you will need to re-install the `kcworks` package in the `web-ui` container. This can be done by running the following command inside the `web-ui` container:

```shell
cd /opt/invenio/src/site
pip install -e .
uwsgi --reload /tmp/uwsgi_ui.pid
```

If you have added js, css, or static files along with the entry point code, you will also need to run the collect and webpack build commands as described above.

### Changes to external python modules (including Invenio modules)

Changes to other python modules (including Invenio modules) will require rebuilding the main knowledge-commons-works container. Additions to the python requirements should be added to the `Pipfile` in the knowledge-commons-works folder and committed to the Github repository. You should then request that the kcworks container be rebuilt.

In the meantime, required python packages can be installed directly in the `web-ui` container. Enter the container and then install the required package using pipenv:

```shell
pipenv install <package-name>
```

### Digging deeper

What follows is a step-by-step walk through this process.

> [!Note]
> These instructions do not support installation under Windows. Windows users should emulate a Linux environment using WSL2.

## Updating an Instance with Upstream Changes

If changes have been made to the upstream Knowledge Commons Works repository and the kcworks container, you will need to update your local instance to reflect those changes. This process involves pulling the changes from the upstream repository, pulling the latest version of the kcworks docker image, restarting the docker-compose project with recreated containers, and rebuilding the asset files.

1. First, to pull the changes from the upstream git repository, execute the following commands from the root knowledge-commons-works folder:

```shell
git pull origin main
```

2. Then, to pull the latest version of the kcworks docker image, execute the following command:

```shell
docker pull monotasker/kcworks:latest
```

3. Next, to restart the docker-compose project with recreated containers, execute the following commands:

```shell
docker-compose --file <your-docker-compose-file-name> stop
docker-compose --file <your-docker-compose-file-name> up -d --build --force-recreate
```

If you are running a development instance, you will use the `docker-compose.yml` file. If you are running a staging or production instance, you will use the `docker-compose.staging.yml` or `docker-compose.production.yml` files respectively.

4. Clean up leftover containers and images:

```shell
docker system prune -a
```

> [!Caution]
> Make sure that you run this `prune` command _while the containers are running._ If you run it while the containers are stopped, you will delete the containers and images that you need to run the application, as well as volumes with stored data.

6. Rebuild the asset files with the following command:

```shell
docker exec -it kcworks-ui bash
bash ./scripts/build-assets.sh
```

7. Restart the docker-compose project once more without rebuilding the containers:

```shell
docker-compose --file <your-docker-compose-file-name> stop
docker-compose --file <your-docker-compose-file-name> up -d
```

8. Then refresh your browser to see the changes.

## Install Python and Required Python Tools

### Ensure some version of python is installed

Most operating systems (especially MacOS and Linux) will already have a version of Python installed. You can proceed directly to the next step.

### Install pyenv and pipenv

First install the **pyenv** tool to manage python versions, and the **pipenv** tool to manage virtual environments. (There are other tools to use for virtual environment management, but InvenioRDM is built to work with pipenv.)

Instructions for Linux, MacOS, and Windows can be found here: https://www.newline.co/courses/create-a-serverless-slackbot-with-aws-lambda-and-python/installing-python-3-and-pyenv-on-macos-windows-and-linux

### Install and enable Python 3.9.16

Invenio's command line tools require a specific python version to work reliably. Currently this is python 3.9.16. At the command line, first install this python version using pyenv:

```console
pyenv install 3.9.16
```

Note: It is important to use cpython. Invenio does not support other python interpreters (like pypy) and advises against using anaconda python in particular for running the RDM application.

Just because this python version is installed does not guarantee it will be used. Next, navigate to the directory where you cloned the source code, and set the correct python version to be used locally:

```console
cd ~/path/to/directory/knowledge-commons-works
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

You must then create a `docker` group and add the current user to it (so that you can run docker commands without sudo). This is _required_ for the invenio-cli scripts to work, and it must be done for the _same user_ that will run the cli commands:

```console
sudo usermod --append --groups docker $USER
```

You will likely want to configure Docker to start on system boot with systemd.

### MacOS

If you are using MacOS, follow the steps for installing Docker desktop explained here: https://docs.docker.com/desktop/install/mac-install/

You will then need to ensure Docker has enough memory to run all the InvenioRDM containers. In the Docker Desktop app,

- click settings cog icon (top bar near right)
- set the memory slider under the "Resources" tab manually to at least 6-8GB

Note: The environment variable recommended in the InvenioRDM documentation for MacOS 11 Big Sur is _not_ necessary for newer MacOS versions.

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

## Add and Configure an .env File

Private environment variables (like security keys) should never be committed to version control or a repository. You must create your own file called `.env` and place it at the root level of the knowledge-commons-works folder. This is a plain text file of key value pairs, with one pair per line, following the pattern `MY_VARIABLE_NAME_IN_CAPS="my value"`. Any configuration variables to be picked up by Invenio should have the prefix "INVENIO\_" added to the beginning of the variable name. Environment variables for other services (e.g., for pgadmin) should not. (These prefixes are already present in the following standard variables.)

### Standardized environment variables

This file must include the following variables with these values:

```env
FLASK_DEBUG=1
INVENIO_DATACITE_USERNAME=MSU.CORE
INVENIO_INSTANCE_PATH=/opt/invenio/var/instance
INVENIO_CSRF_SECRET_SALT='..put a long random value here..'
INVENIO_LOGGING_CONSOLE_LEVEL=NOTSET
INVENIO_SEARCH_DOMAIN='search:9200'
INVENIO_SECRET_KEY=CHANGE_ME
INVENIO_SECURITY_LOGIN_SALT='..put a long random value here..'
INVENIO_SITE_UI_URL="https://localhost"
INVENIO_SITE_API_URL="https://localhost/api"
INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://kcworks:kcworks@localhost/kcworks"
POSTGRES_USER=kcworks
POSTGRES_PASSWORD=kcworks
POSTGRES_DB=kcworks
PYTHON_LOCAL_GIT_PACKAGES_PATH=/opt/invenio
REDIS_DOMAIN='cache:6379'
TESTING_SERVER_DOMAIN=localhost
```

Random values for secrets like INVENIO_SECRET_KEY can be generated in a terminal by running

```console
python -c 'import secrets; print(secrets.token_hex())'
```

For most local development environments your INVENIO_SITE_UI_URL and INVENIO_SITE_API_URL will be "https://localhost" and "https://localhost/api" respectively.

The INVENIO_INSTANCE_PATH should be set to the full path of the instance directory where InvenioRDM will store its compiled files. Since KC Works runs inside containers, this is normally a standard folder inside the container file systems (/opt/invenio/var/instance). If you were to run InvenioRDM with the python/uwsgi processes installed on your local machine, this would be a folder inside your local virtual environment folder. For example, on MacOS this might be ~/.local/share/virtualenvs/{virtual env name}/var/instance/.

Likewise, the PYTHON_LOCAL_GIT_PACKAGES_PATH is the parent directory that holds cloned packages that aren't available via pip or that have been forked by us. This is normally /opt/invenio/src inside the containers for the uwsgi aplications. But if you are running the python processes locally, this would be the folder where you cloned the git repositories for the forked Invenio modules and the extra KC Works modules.

If you are going to use pgAdmin to manage the database, you will also need to add the following variables with the appropriate values for your local development environment:

```env
PGADMIN_DEFAULT_EMAIL=myemail@somedomain.edu
PGADMIN_DEFAULT_PASSWORD=myverysecurepassword
```

### Additional environment variables with sensitive information

Additionally, you should add the following variables with the appropriate values obtained from the Commons administrators:

```env
COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators
```

You will also need to enter the following variable with a dummy value and then replace it with the actual value after the instance is set up. Once you have an administrative user, you can generate a token for that user in the KC Works admin ui and enter it here:

```env
API_TOKEN=myapitoken
```

### Additional required environment variables with paths on your local file system

The next variable refers to a path on your local file system. If you are not installing and running python packages locally, you can simply set this to the folder where you cloned the KCWorks code. Otherwise, it should be the path to the InvenioRDM instance folder in the `site-packages` directory of your virtual environment:

```env
INVENIO_LOCAL_INSTANCE_PATH=/path/to/local/virtual/environment/var/instance
```

### Optional environment variables for migration tools and local development

If you are going to be using the KC Works migration tools, you will also need:

```env
MIGRATION_API_TOKEN=myapitoken
MIGRATION_SERVER_DOMAIN='host.docker.internal'
MIGRATION_SERVER_PROTOCOL='https'
MIGRATION_SERVER_DATA_DIR='/opt/invenio/var/import_data'
MIGRATION_SERVER_LOCAL_DATA_DIR='/path/to/local/import_data'
```

If you are going to be working with the Invenio modules locally, you will also need:

```env
PYTHON_LOCAL_SITE_PACKAGES_PATH=/path/to/local/virtual/environment/lib/python3.9/site-packages
PYTHON_LOCAL_GIT_PACKAGES_PATH=/path/to/local/git/packages
```

## Install the Invenio Python Modules

Navigate to the root knowledge-commons-works folder. Then run the installation script:

```console
cd ~/path/to/directory/knowledge-commons-works
invenio-cli install
```

Note: This installation step will take several minutes.

This stage

- creates and initializes a Python virtual environment using pipenv
- locks the python package requirements
- updates InvenioRDM's internal instance_path variable to match your local installation
  - this is _not_ the folder where you cloned the GIT project, but rather a separate folder where InvenioRDM will place the compiled files used to actually run the application.
  - normally the instance folder is inside the folder for your new virtual environment. On MacOS this will often be ~/.local/share/virtualenvs/{virtual env name}/var/instance/
- installs the Invenio python packages (with pipenv)
  - these packages are again installed under your virtual environment folder. On MacOS this is often ~/.local/share/virtualenvs/{virtual env name}/lib/python3.9/site-packages/. You will find several modules installed here with names that start with "invenio\_".
- installs the `kcworks` Python package (with pipenv)
  - alongside the Invenio packages you will also find a `kcworks` package containing any custom extensions to InvenioRDM defined in your `knowledge-commons-works/sites/` folder
- installs required python dependencies (with pipenv)
- symlinks invenio.cfg, templates/, app_data/ to your instance folder
- finds and collects static files into {instance_folder}/static/
  - static files (like images) are scattered throughout the various Invenio python modules and your local knowledge-commons-works folder. They must be copied to a central location accessible to the web server.
- finds js and less/scss/css files and builds them in {instance_folder}/assets
  - again, this gathers and combines js and style files from all of the Invenio python modules and your local kcworks instance. It also gathers a master list of node.js package requirements from these modules.
  - this build process uses Webpack and is configured in {instance_folder}/assets/webpack.config.js
  - js requirements are installed by npm as node.js modules in the {instance_folder}/assets/node_modules folder
  - note, though, that you _cannot_ directly modify the package.json, webpack.config.js files in your instance folder. This is because these files are created dynamically by InvenioRDM each time the build process runs.

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

### Create and initialize the database, search indexes, and task queue

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

Note: If for some reason you need to run this step again, you will need to add the `--force` flag to the `docker-compose` command. This tells Invenio to destroy any existing redis cache, database, index, and task queue before recreating them all. Just be aware that performing this setup again with `--force` will **destroy all data in your database and all OpenSearch indexes**.

## Start the uwsgi applications and celery worker

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

- The Knowledge Commons Works app (https://localhost)
- The Knowledge Commons Works REST api (https://localhost/api)
- pgAdmin for database management (https://localhost/pgadmin)
- Opensearch Dashboards for managing search (https://localhost:5601)

### Controlling the Application Services

Once Knowledge Commons Works is installed, you can manage its services from the command line. **Note: Unless otherwise specified, the commands below must be run from the root knowledge-commons-works folder.**

### Startup and shutdown scripts

The bash script kcr-startup.sh will start - the containerized services (if not running) - the celery worker - the two uwsgi processes
It will also ensure that you have a .env file and copy your set your INVENIO_INSTANCE_PATH variable in that file to your local instance folder, matching the instance_path variable in your .invenio.private file.

Simply navigate to the root knowledge-commons-works folder and run

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

## Developing Knowledge Commons Works

### Branching and committing

In general, all members of the development team should commit their work to the `main` branch on a daily basis. It is a good idea to create your own local `working` branch to use for your own development. This allows you to commit changes while work is unfinished without breaking the `main` branch for others. Normally, though, at least once a day you should merge your `working` branch with `main` and push your changes to Github. Only create a new feature branch to push to Github if your work (a) requires leaving things broken that others might rely on, and (b) will take more than a day to complete. This should, though, be regarded as an unusual, temporary measure. You should inform the rest of the development team when the new feature branch is created, and plan to merge it with `main` as soon as possible.

### Making changes to template files

Changes made to jinja template files will be visible immediately in the running Knowledge Commons Works instance.

### Making changes to theme (CSS) and javascript files

#### Building js and css assets

Unlike python and config files, the less and javascript files you customize must go through a build process before they will be visible in the running Knowledge Commons Works instance. The Invenio platform provides a convenient cli script for collecting all of these assets (both standard and your customized files) and running webpack to build them.

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

<!-- or, without using invenio's cli, navigate to your local kcworks folder and run the npm watch service using a separate node.js container:
```console
docker run --rm -it -u 1000:1000 -v $PWD/assets:/opt/invenio/var/instance/assets -v $PWD/static:/opt/invenio/var/instance/static/ -w /opt/invenio/var/instance/assets node:19 sh -c "NODE_OPTIONS=--openssl-legacy-provider npm run start"
``` -->

That will watch for changes and automatically rebuild whatever assets are necessary as you go. You will need to run this command in its own terminal, since it will continue to feed output to the terminal until you stop watching the files.

#### Adding new js or css files

The `watch` command will only pick up changes to files that already existed during the last Webpack build. If you add a new javascript or css (less) file, you need to again run

```console
invenio-cli assets build
```

<!-- or, without using invenio's cli, navigate to your local kcworks folder and run the build operation using a separate node.js container:
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

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-works Github repo. You can (and should) also run the test suite locally.

There are currently two distinct sets of tests that have to be run separately: python tests run using invenio's fixtures, and javascript tests run separately using jest.

### Python tests

The python test suite includes (a) unit tests for back end code, (b) tests of ui views and api requests run with a client fixture, (c) user interaction tests run with selenium webdriver. To run the unit tests and view/request tests, navigate to the root knowledge-commons-works folder and run

```console
pipenv run pytest
```

By default the selenium browser interaction tests are not run. To include these, run pytest with the E2E environment variable set to "yes":

```console
pipenv run E2E=yes pytest
```

Running the selenium tests also requires that you have the Selenium Client and Chrome Webdriver installed locally.

### Javascript tests

Pytest does not directly test custom javascript files or React components. In order to test these, navigate to the root knowledge-commons-works folder and run

```console
npm run test
```

These tests are run using the jest test runner, configured in the packages.json file in the root knowledge-commons-works folder.

Note that these tests run using a local npm configuration in the knowledge-commons-works folder. Any packages that are normally available to InvenioRDM must be added to the local package.json configuration and will be installed in the local node_modules folder. Since this folder is not included in GIT version control, before you run the javascript tests you must ensure the required packages are installed locally by running

```console
npm install
```

## InvenioRDM Documentation

The Knowledge Commons Works is built as an instance of InvenioRDM. The InvenioRDM Documentation, including customization and development information, can be found at https://inveniordm.docs.cern.ch/.
