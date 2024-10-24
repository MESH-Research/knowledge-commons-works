# Knowledge Commons Works

Knowledge Commons Works is a collaborative tool for storing and sharing academic research. It is part of Knowledge Commons and is built on an instance of the InvenioRDM repository system.

## Copyright

Copyright 2023-24 Mesh Research. Released under the MIT license. (See the included LICENSE.txt file.)

## Installation for Development


### Quickstart

These instructions allow you to run Knowledge Commons Works for local development. The app source files are copied onto your system, but the Flask application and other services (database, search, etc.) are run in Docker containers. The application is served to your browser by an nginx web server running in a separate container.

First you will need to have the correct versions of Docker (20.10.10+ with Docker Compose 1.17.0+) and Python (3.12.0+ with pipenv).

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
    - `docker-compose --file docker-compose.yml up -d`
4. Initialize the database and other services, and build asset files
    - enter the `web-ui` container by running `docker exec -it kcworks-ui bash`
        - *note*: The container name may be different depending on your local docker setup. You can find the correct name by running `docker ps`
    - run the script to set up the instance services and build static assets `bash ./scripts/setup-services.sh`
        - *note*: Some of the commands in this script may take a while to run. Patience is required! The `invenio rdm-records fixtures` command in particular may take up to an hour to complete during which time it provides no feedback. Don't despair! It is working.
5. Create your own admin user
    - enter the `web-ui` container by running `docker exec -it kcworks-ui bash`
    - run the commands:
        - `invenio users create <email> --password <password>`
        - `invenio users activate <email>`
        - `invenio access allow administration-access user <email>`
6. View the application
    - The Knowledge Commons Works app is now running at `https://localhost`
    - The REST API is running at `https://localhost/api`
    - pgAdmin is running at `https://localhost/pgadmin`
    - OpenSearch Dashboards is running at `https://localhost:5601`

This setup will allow you to make changes to the core Knowledge Commons Works codebase and see those changes reflected in the running application.

### Full local development setup

You will need to take some further steps if you want to
    - Make and test changes to the various invenio modules that are included as git submodules.
    - View and insert debugging statements into the code of the various core Invenio packages installed into the python environment.
To do this, you will need to do the following:

1. In the same parent directory that holds your cloned `knowledge-commons-works` folder, clone the following additional repositories:
    ```shell
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-record-importer-kcworks.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-groups.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-modular-deposit-form.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-modular-detail-page.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-remote-api-provisioner.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-remote-user-data-kcworks.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-communities.git
    git clone --single-branch -b main git@github.com:MESH-Research/invenio-rdm-records.git
    git clone --single-branch -b local-working git@github.com:MESH-Research/invenio-records-resources.git
    git clone --single-branch -b local-working git@github.com:MESH-Research/invenio-vocabularies.git
    ```
    The folders holding the cloned code from these repositories should then be direct siblings of your `knowledge-commons-works` folder.
2. Install the python packages required by Knowldge Commons Works locally by running `pipenv install` in the `knowledge-commons-works` folder.
3. When you start up the docker compose project, add an additional project file to the command:
    - `docker-compose --file docker-compose.yml --file docker-compose.dev.yml up -d`
This will mount a variety of local package folders as bind mounts in your running containers. This will allow you to make changes to the python code in the cloned repositories and see those changes reflected in the running Knowledge Commons Works instance.

### Controlling the KCWorks (Flask) application

The application instance and its services can be started and stopped by starting and stopping the docker-compose project:

```shell
docker-compose --file docker-compose.yml up -d
```
```shell
docker-compose --file docker-compose.yml stop
```

> [!Caution]
> Do not use the `docker-compose down` command unless you want the containers to be destroyed. This will destroy all data in your database and all OpenSearch indices. YOU DO NOT WANT TO DO THIS!

If you need to restart the main Flask application (e.g., after making configuration changes) you can do so either by stopping and restarting the docker-compose project or by running the following command inside the `kcworks-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_ui.pid
```

Similarly, the REST API can be restarted by running the following command inside the `web-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_api.pid
```
But these commands should not be necessary in normal operation.

## KCWorks Customizations to InvenioRDM

### Template Customizations

#### Page templates

#### Email templates

Custom email templates are located in `site/kcworks/templates/semantic-ui/invenio_notifications`. These override the default templates provided by InvenioRDM, and include both html and plaintext versions of each email, as well has markdown templates for other notification backends.

Additional email templates are added for KCWorks-specific email types.

- `user-first-record.create.jinja`: sent to KCWorks moderators when a user has created their first record.
- `user-first-record.publish.jinja`: sent to KCWorks moderators when a user's first record is published.

### Record Detail Page Customizations

#### Modular Framework (invenio-modular-detail-page)

#### Overrides in the KCWorks Package (kcworks/site)

### Deposit Form Customizations

#### Modular Framework (invenio-modular-deposit-form)

#### Overrides in the KCWorks Package (kcworks/site)

### Collections

#### Collections for KC Groups (invenio-group-collections-kcworks)

### Notifications

#### In-app notifications

A user's unread notifications are tracked in the user's profile record.

#### Content moderation notifications

##### User-first-record notifications

Emails are sent to the KCWorks moderators when a user creates their first draft and publishes their first record. This is implemented using
- a custom service component for the RDMRecord service (kcworks.services.notifications.services.FirstRecordCreatedNotificationService) that runs during draft creation and publication and
    - checks whether the user has any other drafts or published records.
    - if not, adds a NotificationOp to the unit of work for the record operation to emit a notification of the type "user-first-record.create" or "user-first-record.publish".
- two custom notification builder classes (kcworks.services.notifications.builders.FirstRecordPublishedNotificationBuilder and kcworks.services.notifications.builders.FirstRecordCreatedNotificationBuilder) that build the notifications.
    - these builders define the notification recipients using a custom ModeratorRoleRecipient generator (kcworks.services.notifications.generators.ModeratorRoleRecipient) and sends the notification to all users with the role defined in the NOTIFICATIONS_MODERATOR_ROLE config variable.
    - they also define the notification backends to be used for sending the notification. In this case, a custom EmailBackend (kcworks.services.notifications.backends.EmailBackend) that sends email via the Flask-Mail extension.
- custom email templates for the notifications, located at `site/kcworks/templates/semantic-ui/invenio_notifications/`.

### Integrations with KC

#### User Data Sync (invenio-remote-user-data-kcworks)

User data is synced uni-directionally from KC to KCWorks. A user's data is synced with KC when
1. the user's SAML authentication info is first saved in KCWorks
2. the user logs into KCWorks
3. a webhook signal is received by KCWorks from KC

#### KC Search Provisioning (invenio-remote-api-provisioner)

#### SAML Authentication

### Metadata Schema Customizations

#### KCWorks Custom Fields (kcworks/site/custom_fields)

### Bulk Record Import (invenio-record-importer-kcworks)

### Forked Core Invenio Modules

#### invenio-communities

#### invenio-rdm-records

#### invenio-records-resources

#### invenio-vocabularies

## KCWorks Configuration of InvenioRDM

## KCWorks Infrastructure

## Developing KCWorks

### Updating the running KCWorks instance with development changes

#### Changes to html template files

Changes to html template files will be visible immediately in the running Knowledge Commons Works instance. You simply need to refresh the page in your browser.

If you add a new template file (including overriding an existing template file), you will need to collect the new file into the central templates folder and restart the uwsgi processes. This can be done by running the following command inside the `web-ui` container:

```shell
invenio collect -v
uwsgi --reload /tmp/uwsgi_ui.pid
```
Then refresh your browser.

#### Changes to invenio.cfg

Changes to the invenio.cfg file will only take effect after the instance uwsgi processes are restarted. This can be done by running the following command inside the `web-ui` container:
```shell
uwsgi --reload /tmp/uwsgi_ui.pid
```
Or you can restart the docker-compose project, which will also restart the uwsgi processes.

#### Changes to theme (CSS) and javascript files

##### The basic build process (slow)

Invenio employs a build process for css and javascript files. Changes to these files will not be visible in the running Knowledge Commons Works instance until the build process is run. This can be done by running the following command inside the `web-ui` container:

```shell
bash ./scripts/build-assets.sh
```

##### Rebuilding changed files on the fly (fast but limited)

The problem is that this build process takes a long time to run, especially in the containers. For most tasks, you can instead run the following command to watch for changes to the files and automatically rebuild them:

```shell
invenio webpack run start
```

The file watching will continue until you stop it with CTRL-C. It will continue to occupy the terminal window where you started it. This means that you can see it respond and begin integrating changed files when it finds them. You can also see there any error or warning output from the build process--very helpful for debugging.

> [!Note]
> The watch command will only pick up changes to files that already existed during the last Webpack build. If you add
> - a new javascript file
> - a new css (less) file
> - a new node.js package requirement
> then you need to again run the basic (slow) build script to include it in the build process.
> After that you can run `invenio webpack run start` again to pick up changes on the fly.

#### Adding new node.js packages to be included

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

#### Changes to static files

Changes to static files like images will require running the collect command to copy them to the central static folder. This can be done by running the following command inside the `web-ui` container:

```shell
invenio collect -v
```

You will then need to restart the uwsgi processes or restart the docker-compose project as described above.


#### Changes to python code in the `site` folder

Changes to python code in the `site` folder should (like changes to template files) take effect immediately in the running Knowledge Commons Works instance. You simply need to refresh the page in your browser.

##### Adding new entry points

Sometimes you will need to add new entry points to inform the Flask application about additional code you have provided. This is done via the `setup.py` file in the `site` folder. Once you have added the entry point declaration, you will need to re-install the `kcworks` package in the `kcworks-ui`, `kcworks-api`, and `kcworks-worker` container. This can be done by running the following command inside the each container:

```shell
cd /opt/invenio/src/site
pip install -e .
uwsgi --reload /tmp/uwsgi_ui.pid
```

If you have added js, css, or static files along with the entry point code, you will also need to run the collect and webpack build commands as described above and restart the docker-compose project.

Note that entry point changes may be overridden if you pull a more recent version of the kcworks docker image and restart the docker-compose project. Ultimately the entry point changes will have to be added to a new version of the kcworks docker image.

#### Changes to external python modules (including Invenio modules)

Changes to other python modules (including Invenio modules) will require rebuilding the main kcworks container. Additions to the python requirements should be added to the `Pipfile` in the kcworks folder and committed to the Github repository. You should then request that the kcworks container be rebuilt with the additions.

In the meantime, required python packages can be installed directly in the `kcworks-ui`, `kcworks-api`, and `kcworks-worker` containers. Enter each container and then install the required package pip (not pipenv):

```shell
pip install <package-name>
```

### Digging deeper

What follows is a step-by-step walk through this process.

> [!Note]
> These instructions do not support installation under Windows. Windows users should emulate a Linux environment using WSL2.

### Updating an Instance with Upstream Changes

If changes have been made to the upstream Knowledge Commons Works repository and the kcworks container, you will need to update your local instance to reflect those changes. This process involves pulling the changes from the upstream repository, pulling the latest version of the kcworks docker image, restarting the docker-compose project with recreated containers, and rebuilding the asset files.

1. First, from the root knowledge-commons-works folder, pull the changes from the upstream git repository:

```shell
git pull origin main
```

2. Then pull the latest version of the kcworks docker image:

```shell
docker pull monotasker/kcworks:latest
```

3. Next, restart the docker-compose project with recreated containers:

```shell
docker-compose --file docker-compose.yml stop
docker-compose --file docker-compose.yml up -d --build --force-recreate
```

4. Clean up leftover containers and images:

```shell
docker system prune -a
```

> [!Caution]
> Make sure that you run this `prune` command *while the containers are running.* If you run it while the containers are stopped, you will delete the containers and images that you need to run the application, as well as volumes with stored data.

6. Rebuild the asset files with the following command:

```shell
docker exec -it kcworks-ui bash
bash ./scripts/build-assets.sh
```

7. Then refresh your browser to see the changes.

### Running automated tests (NEEDS UPDATING)

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-works Github repo. You can (and should) also run the test suite locally.

There are currently two distinct sets of tests that have to be run separately: python tests run using invenio's fixtures, and javascript tests run separately using jest.

#### Python tests

The python test suite includes (a) unit tests for back end code, (b) tests of ui views and api requests run with a client fixture, (c) user interaction tests run with selenium webdriver. To run the unit tests and view/request tests, navigate to the root knowledge-commons-works folder and run
```console
pipenv run pytest
```
By default the selenium browser interaction tests are not run. To include these, run pytest with the E2E environment variable set to "yes":
```console
pipenv run E2E=yes pytest
```
Running the selenium tests also requires that you have the Selenium Client and Chrome Webdriver installed locally.

#### Javascript tests

Pytest does not directly test custom javascript files or React components. In order to test these, navigate to the root knowledge-commons-works folder and run
```console
npm run test
```
These tests are run using the jest test runner, configured in the packages.json file in the root knowledge-commons-works folder.

Note that these tests run using a local npm configuration in the knowledge-commons-works folder. Any packages that are normally available to InvenioRDM must be added to the local package.json configuration and will be installed in the local node_modules folder. Since this folder is not included in GIT version control, before you run the javascript tests you must ensure the required packages are installed locally by running
```console
npm install
```

## In-depth Development Installation Instructions (NEEDS UPDATING)

### Install Python and Required Python Tools

#### Ensure some version of python is installed

Most operating systems (especially MacOS and Linux) will already have a version of Python installed. You can proceed directly to the next step.

#### Install pyenv and pipenv

First install the **pyenv** tool to manage python versions, and the **pipenv** tool to manage virtual environments. (There are other tools to use for virtual environment management, but InvenioRDM is built to work with pipenv.)

Instructions for Linux, MacOS, and Windows can be found here: https://www.newline.co/courses/create-a-serverless-slackbot-with-aws-lambda-and-python/installing-python-3-and-pyenv-on-macos-windows-and-linux

#### Install and enable Python 3.9.16

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

### Install Docker 20.10.10+ and Docker-compose 1.17.0+

#### Linux

If you are using Ubuntu Linux, follow the steps for installing Docker and Docker-compose explained here: https://linux.how2shout.com/install-and-configure-docker-compose-on-ubuntu-22-04-lts-jammy/

You must then create a `docker` group and add the current user to it (so that you can run docker commands without sudo). This is *required* for the invenio-cli scripts to work, and it must be done for the *same user* that will run the cli commands:

```console
sudo usermod --append --groups docker $USER
```

You will likely want to configure Docker to start on system boot with systemd.

#### MacOS

If you are using MacOS, follow the steps for installing Docker desktop explained here: https://docs.docker.com/desktop/install/mac-install/

You will then need to ensure Docker has enough memory to run all the InvenioRDM containers. In the Docker Desktop app,

- click settings cog icon (top bar near right)
- set the memory slider under the "Resources" tab manually to at least 6-8GB

Note: The environment variable recommended in the InvenioRDM documentation for MacOS 11 Big Sur is *not* necessary for newer MacOS versions.

#### Fixing docker-compose "not found" error

With the release of compose v2, the command syntax changed from `docker-compose` to `docker compose` (a command followed by a sub-command instead of one hyphenated command). This will break the invenio-cli scripts, which use the `docker-compose` command and you will receive an error asking you to install the "docker-compose" package.

One solution on Linux systems is to install Docker Compose standalone, which uses the old `docker-compose` syntax:

```console
sudo curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Another approach is simply to alias the `docker compose` command to `docker-compose` in the configuration file for your command line shell (.bashrc, .zshrc, or whichever config file is used by your shell).

See further https://docs.docker.com/compose/install/other/

#### Docker log rotation

Regardless of your operating system, you should set up log rotation for containers to keep the size of logging files from getting out of control. Either set your default logging driver to "local" (which rotates log files automatically) or set logging configuration if you use the "json-file" logging driver. See https://docs.docker.com/config/containers/logging/configure/

#### Note about docker contexts

Make sure to always use the same Docker context to run all of the containers for InvenioRDM. See further, https://docs.docker.com/engine/context/working-with-contexts/

### Install Node.js and NVM

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
### Clone the knowledge-commons-works Code

Using GIT, clone this repository. You should then have a folder called `knowledge-commons-works` (unless you chose to name it something else) on your local computer.

### Add and Configure an .env File

Private environment variables (like security keys) should never be committed to version control or a repository. You must create your own file called `.env` and place it at the root level of the knowledge-commons-works folder. This is a plain text file of key value pairs, with one pair per line, following the pattern `MY_VARIABLE_NAME_IN_CAPS="my value"`. Any configuration variables to be picked up by Invenio should have the prefix "INVENIO_" added to the beginning of the variable name. Environment variables for other services (e.g., for pgadmin) should not. (These prefixes are already present in the following standard variables.)

#### Standardized environment variables

This file must include the following variables with these values:

```env
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

#### Variables for local credentials

Several variables hold random values used to secure the application, or hold passwords and email addresses supplied by the local developer:

```env
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

```env
COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators
```
You will also need to enter the following variable with a dummy value and then replace it with the actual value after the instance is set up. Once you have an administrative user, you can generate a token for that user in the KC Works admin ui and enter it here:

```env
API_TOKEN=myapitoken
```

#### Additional required environment variables with paths on your local file system

The next variables refer to paths on your local file system that are used during local development to provide easy access to the source code of various python packages and KCWorks modules:

```env
PYTHON_LOCAL_GIT_PACKAGES_PATH=/path/to/local/git/packages
PYTHON_LOCAL_SITE_PACKAGES_PATH=/path/to/local/virtual/environment/lib/python3.12/site-packages
```

PYTHON_LOCAL_GIT_PACKAGES_PATH is the parent directory that holds cloned packages that aren't available via pip or that have been forked by us. If you are not working with the KCWorks custom modules locally, this can be set to the folder where you cloned the KCWorks code. Otherwise, it should be the path to the parent folder containing the git repositories for the forked Invenio modules and the extra KC Works modules.

PYTHON_LOCAL_SITE_PACKAGES_PATH is the path to the site-packages folder in your local virtual environment. This assumes that you have run `pipenv install --dev --python=3.12` in your KCWorks project folder to install the python packages locally in a virtual environment.

### Install the Invenio Python Modules

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

### Build and Configure the Containerized Services

#### Build and start the containers

Make sure you are in the root knowledge-commons-works folder and then run
```console
docker-compose up -d
```
This step will
- build the docker image for the nginx web server (frontend) using ./docker/nginx/Dockerfile
- pull remote images for other services: mq, search, db, cache, pgadmin, opensearch-dashboards
- start containers from all of these images and mounts local files or folders into the containers as required in the docker-compose.yml and docker-services.yml files

#### Create and initialize the database, search indices, and task queue

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

#### Start the uwsgi applications and celery worker

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


#### Create an admin user

From the command line, run these commands to create and activate the admin user:
```console
pipenv run invenio users create <email> --password <password>
pipenv run invenio users activate <email>
```
If you want this user to have access to the administration panel in Invenio, you also need to run
```console
pipenv run invenio access allow administration-access user <email>
```

### Use the application!

You should now be able to access the following:
- The Knowledge Commons Works app (https://localhost)
- The Knowledge Commons Works REST api (https://localhost/api)
- pgAdmin for database management (https://localhost/pgadmin)
- Opensearch Dashboards for managing search (https://localhost:5601)

#### Controlling the Application Services

Once Knowledge Commons Works is installed, you can manage its services from the command line. **Note: Unless otherwise specified, the commands below must be run from the root knowledge-commons-works folder.**

#### Startup and shutdown scripts

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

#### Controlling just the containerized services (postgresql, RabbitMQ, redis, pgAdmin, OpenSearch, opensearch dashboards, nginx)

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

#### View logging output for uwsgi processes

Activity and error logging for the two uwsgi processes are written to date-stamped files in the knowledge-commons-works/logs/ folder. To watch the live logging output from one of these processes, open a new terminal in your knowledge-commons-works folder and run
```console
tail -f logs/uwsgi-ui-{date}.log
```
or
```console
tail -f logs/uwsgi-api-{date}.log
```

#### View container logging output

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

#### Controlling containerized nginx server

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

## Reference

### InvenioRDM Documentation

The Knowledge Commons Works is built as an instance of InvenioRDM. The InvenioRDM Documentation, including customization and development information, can be found at https://inveniordm.docs.cern.ch/.
