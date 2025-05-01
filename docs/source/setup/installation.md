# Installation

## Quickstart

These instructions allow you to run Knowledge Commons Works for local development. The app source files are copied onto your system, but the Flask application and other services (database, search, etc.) are run in Docker containers. The application is served to your browser by an nginx web server running in a separate container.

First you will need to have the correct versions of Docker (20.10.10+ with Docker Compose 1.17.0+) and Python (3.12.0+). You will also need to have Python's `uv` package manager installed (see [the uv docs](https://docs.astral.sh/uv/getting-started/installation/) for details). If you are going to run frontend development tests you will also need to have Node.js (20+) and npm (10.9.0+) installed.

From there, installation involves these steps. Each one is further explained below, but here is a quick reference:

### 1. Clone the git repository

- From your command line, navigate to the parent folder where you want the cloned repository code to live
- Clone the knowledge-commons-works repository with `git clone git@github.com:MESH-Research/knowledge-commons-works.git && git submodule update --init`

```{note}
Do not use the `--recurse-submodules` option when cloning the repository or the `--recursive` option when initializing the submodules. This will clone redundant copies of the inter-dependent submodules.
```

### 2. Create your configuration files

- `cd knowledge-commons-works`
- Create and configure the `.env` file in this folder as described {ref}`here <setting-up-configuration-files>`
- Create the `.invenio.private` file with the following contents:

```shell
[cli]
services_setup = True
instance_path = /opt/invenio/var/instance
```

### 3. Start the docker-compose project

- `docker-compose --file docker-compose.yml up -d`

### 4. Initialize the database and other services, and build asset files

- enter the `web-ui` container by running `docker exec -it kcworks-ui bash`

```{note}
The container name may be different depending on your local docker setup. You can find the correct name by running `docker ps`
```

- run the script to set up the instance services and build static assets `bash ./scripts/setup-services.sh`

```{note}
Some of the commands in this script may take a while to run. Patience is required! The `invenio rdm-records fixtures` command in particular may take up to an hour to complete during which time it provides no feedback. Don't despair! It is working.
```

### 5. Create your own admin user

- enter the `web-ui` container by running `docker exec -it kcworks-ui bash`

```{note}
The container name may be different depending on your local docker setup. You can find the correct name by running `docker ps`
```

- run the commands:

```shell
invenio users create <email> --password <password>
invenio users activate <email>
invenio access allow administration-access user <email>
```

### 6. View the application

- The Knowledge Commons Works app is now running at `https://localhost`
- The REST API is running at `https://localhost/api`
- pgAdmin is running at `https://localhost/pgadmin`
- OpenSearch Dashboards is running at `https://localhost:5601`

This setup will allow you to make changes to the core Knowledge Commons Works codebase and see those changes reflected in the running application.

## Full local development setup

You will need to take some further steps if you want to
    - Make and test changes to the various invenio modules that are included as git submodules.
    - View and insert debugging statements into the code of the various core Invenio packages installed into the python environment.
To do this, you will need to do the following:

1. Ensure the required git submodules are cloned by running the following commands in the `knowledge-commons-works` folder:
    ```shell
    git submodule update --init
    ```
    This will clone the following repositories:
    ```shell
    main git@github.com:MESH-Research/invenio-record-importer-kcworks.git
    main git@github.com:MESH-Research/invenio-group-collections-kcworks.git
    main git@github.com:MESH-Research/invenio-modular-deposit-form.git
    main git@github.com:MESH-Research/invenio-modular-detail-page.git
    main git@github.com:MESH-Research/invenio-remote-api-provisioner.git
    main git@github.com:MESH-Research/invenio-remote-user-data-kcworks.git
    local-working git@github.com:MESH-Research/invenio-communities.git
    local-working git@github.com:MESH-Research/invenio-rdm-records.git
    local-working git@github.com:MESH-Research/invenio-records-resources.git
    local-working git@github.com:MESH-Research/invenio-vocabularies.git
    ```
    These cloned repositories should then appear under the `knowledge-commons-works/site/kcworks/dependencies` folder.
2. Install the python packages required by Knowldge Commons Works locally by running `uv sync --all-extras` in the `knowledge-commons-works` folder.
3. When you start up the docker compose project, add an additional project file to the command:
    - `docker-compose --file docker-compose.yml --file docker-compose.dev.yml up -d`
This will mount a variety of local package folders as bind mounts in your running containers. This will allow you to make changes to the python code, both in the cloned repositories and in the `knowledge-commons-works/.venv` virtual environment, and see those changes reflected in the running Knowledge Commons Works instance.

## Controlling the KCWorks (Flask) application

The application instance and its services can be started and stopped by starting and stopping the docker-compose project:

```shell
docker-compose --file docker-compose.yml up -d
```
```shell
docker-compose --file docker-compose.yml stop
```

```{caution}
Do not use the `docker-compose down` command unless you want the containers to be destroyed. This will destroy all data in your database and all OpenSearch indices. YOU DO NOT WANT TO DO THIS!
```

If you need to restart the main Flask application (e.g., after making configuration changes) you can do so either by stopping and restarting the docker-compose project or by running the following command inside the `kcworks-ui` container:

```shell
uwsgi --reload /tmp/uwsgi_ui.pid
```

Similarly, the REST API can be restarted by running the following command inside the `kcworks-api` container:

```shell
uwsgi --reload /tmp/uwsgi_api.pid
```
But these commands should not be necessary in normal operation.

## Setting up configuration files

### Configuring your `.env` file

The `.env` file is used to configure the Knowledge Commons Works application. It is a standard python environment file that is used to set the environment variables for the application.

These are the minimal variables that you need to set in your `.env` file to get the application running:

```shell
FLASK_DEBUG=1
INVENIO_INSTANCE_PATH=/opt/invenio/var/instance
INVENIO_LOGGING_CONSOLE=True
INVENIO_LOGGING_CONSOLE_LEVEL=DEBUG
INVENIO_RECORD_IMPORTER_LOCAL_DATA_DIR=/
INVENIO_RECORD_IMPORTER_DATA_DIR=/opt/invenio/var/import_data
INVENIO_SEARCH_DOMAIN='search:9200'
INVENIO_SITE_UI_URL="https://localhost"
INVENIO_SITE_API_URL="https://localhost/api"
REDIS_DOMAIN='cache:6379'
INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://kcworks:PASSWORDHERE@db/kcworks" # DON'T FORGET TO CHANGE THE PASSWORD HERE
POSTGRES_USER=kcworks
POSTGRES_DB=kcworks
INVENIO_CSRF_SECRET_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
INVENIO_SECURITY_LOGIN_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
INVENIO_SECRET_KEY='SECRET_KEY_VERY_SECRET'
COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators - just leave as is
API_TOKEN=myapitoken # just leave as is
INVENIO_LOCAL_SITE_PATH=/local/path/to/cloned/repository/knowledge-commons-works/site # set this to `site` under the base directory of your cloned repository
INVENIO_LOCAL_DEPENDENCIES_PATH=/local/path/to/cloned/repository/knowledge-commons-works/site/kcworks/dependencies # set this to `site/kcworks/dependencies` under the base directory of your cloned repository
PYTHON_LOCAL_SITE_PACKAGES_PATH=/local/path/to/cloned/repository/knowledge-commons-works/.venv/lib/python3.12/site-packages # you need this for dev
POSTGRES_PASSWORD=PASSWORDHERE
PGADMIN_DEFAULT_EMAIL=your.email@example.com
PGADMIN_DEFAULT_PASSWORD=PASSWORDHERE
INVENIO_LOCAL_INSTANCE_PATH=/opt/invenio/var/instance
```

```{note}
Don't forget to change the `PASSWORDHERE` values to the actual passwords you use for your admin user and pgAdmin. This includes replacing `PASSWORDHERE` in the `INVENIO_SQLALCHEMY_DATABASE_URI` variable.
```

#### Generating random secrets

Random values for secrets like INVENIO_SECRET_KEY can be generated in a terminal by running

```shell
python -c 'import secrets; print(secrets.token_hex())'
```

#### Generating an API token

Once you are up and running, you will need to replace the dummy `API_TOKEN` variable in your `.env` file with a genuine oAuth token that identifies you when you make API requests from your local instance. You can generate a token for yourself in the KC Works admin ui and enter it as the value of the `API_TOKEN` variable.

### Configuring your `.invenio.private` file

The `.invenio.private` file is used to configure the Knowledge Commons Works application. It is a standard python environment file that is used to set the environment variables for the application.

Here is a list of the variables that you need to set in your `.invenio.private` file:

```shell
[cli]
services_setup = True
instance_path = /opt/invenio/var/instance
```