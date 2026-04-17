# Installation

## Quickstart

These instructions allow you to run Knowledge Commons Works for local development. The app source files are copied onto your system, but the Flask application and other services (database, search, etc.) are run in Docker containers. The application is served to your browser by an nginx web server running in a separate container.

First you will need to have the correct versions of Docker (20.10.10+ with Docker Compose 1.17.0+) and Python (3.12.0+). You will also need to have Python's `uv` package manager installed (see [the uv docs](https://docs.astral.sh/uv/getting-started/installation/) for details). If you are going to run **frontend / JavaScript tests** against the root `package.json`, install **Node.js (20+)** and enable **Corepack** (bundled with Node) once per Node install: `corepack enable`. The repo uses **[pnpm](https://pnpm.io/)**; the exact version is set in **`package.json`** as **`packageManager`**. Install dependencies with **`pnpm install`** from the repository root (see `pnpm-lock.yaml`).

From there, installation involves these steps. Each one is further explained below, but here is a quick reference:

### 1. Clone the git repository

- From your command line, navigate to the parent folder where you want the cloned repository code to live
- Clone the knowledge-commons-works repository with

```shell
git clone git@github.com:MESH-Research/knowledge-commons-works.git
cd knowledge-commons-works
git submodule update --init
```

```{note}
Do not use the `--recurse-submodules` option when cloning the repository or the `--recursive` option when initializing the submodules. This will clone redundant copies of the inter-dependent submodules.
```

### 2. Create your configuration files

- `cd knowledge-commons-works`
- Create and configure the `.env` file in this folder as described below (["Setting up configuration files"](#setting-up-configuration-files)).
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
invenio access allow administration-moderation user <email>
invenio roles add <email> administration
invenio roles add <email> administration-moderation
```

### 6. View the application

- The Knowledge Commons Works app is now running at `https://localhost` (if you set `KCWORKS_NGINX_HTTPS_HOST_PORT` to something other than `443`, use that port in the URL, e.g. `https://localhost:8443`, and set `INVENIO_SITE_UI_URL` / `INVENIO_SITE_API_URL` to match — see [Host port overrides](#host-port-overrides))
- The REST API is running at the same origin under `/api`
- pgAdmin is proxied at `https://localhost/pgadmin` (direct UI port defaults to host `5050` mapped to the pgAdmin container)
- OpenSearch Dashboards defaults to `http://localhost:5601` unless you override `KCWORKS_OPENSEARCH_DASHBOARDS_HOST_PORT`

This setup will allow you to make changes to the core Knowledge Commons Works codebase and see those changes reflected in the running application.

## Full local development setup

You will need to take some further steps if you want to - Make and test changes to the various invenio modules that are included as git submodules. - View and insert debugging statements into the code of the various core Invenio packages installed into the python environment.
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
3. When you start up the docker compose project, add an additional project file to the command: - `docker-compose --file docker-compose.yml --file docker-compose.dev.yml up -d`
   This will mount a variety of local package folders as bind mounts in your running containers. This will allow you to make changes to the python code, both in the cloned repositories and in the `knowledge-commons-works/.venv` virtual environment, and see those changes reflected in the running Knowledge Commons Works instance.

### Troubleshooting and Workarounds

#### MacOS cairo error

The `invenio-formatter` package relies on `cairoffi` for generating svg badges, which in turn relies on having the `cairo` rendering library accessible on your local machine. _This should only be necessary if you are running tests locally_, since otherwise the library is already installed in the service containers. But you can install this locally with homebrew by running

```shell
brew install cairo
```

On MacOS machines with Apple Silicon chips (all modern macs now) the python library may still not be able to _find_ your Homebrew-installed packages. The workaround for this is to add your homebrew binary directory to your system path. In your `.zshrc` (or other shell environment file) add this line:

```shell
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/cairo/lib:$DYLD_FALLBACK_LIBRARY_PATH"
```

This will allow your terminal system to find any binary files in the `/opt/homebrew/lib` folder, the standard installation location on Apple Silicon Macs.

If that doesn't work, you can add these lines to your `tests/.env` testing environment file:

```
PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
DYLD_LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/cairo/lib:$DYLD_LIBRARY_PATH"
DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/cairo/lib:$DYLD_FALLBACK_LIBRARY_PATH"
```

## Running multiple KCWorks instances on the same machine

You can run several clones (for example `knowledge-commons-works`, `kcworks-next`, and `v13test`) at once if each project uses:

1. A distinct **`KCWORKS_CONTAINERS_BASE_NAME`** in its `.env` so Docker container names do not collide.
2. Distinct **published host ports** for every service that binds to the host (see [Host port overrides](#host-port-overrides)). Compose variable defaults preserve the original single-instance ports when you omit the overrides.

Keep **service** names in `docker-compose.yml` as `web-ui`, `web-api`, `worker`, `cache`, `db`, etc. Only container display names and host ports need to differ per clone.

For `docker-compose.dev.yml`, ensure these point at the correct clone for that project:

- `PYTHON_LOCAL_SITE_PACKAGES_PATH`
- `INVENIO_LOCAL_DEPENDENCIES_PATH`
- `INVENIO_LOCAL_SITE_PATH`
- `INVENIO_LOCAL_INSTANCE_PATH`
- `INVENIO_INSTANCE_PATH`

### Host port overrides

Set these in each clone’s **`.env`** in the repository root (same directory as `docker-compose.yml`). Docker Compose reads this file for `${VAR:-default}` substitution. **Defaults** match the historical ports; omit a variable to keep the default.

| Variable | Default | Container port | Purpose |
|----------|---------|------------------|---------|
| `KCWORKS_NGINX_HTTP_HOST_PORT` | `80` | `80` | HTTP (nginx) |
| `KCWORKS_NGINX_HTTPS_HOST_PORT` | `443` | `443` | HTTPS (nginx) |
| `KCWORKS_REDIS_HOST_PORT` | `6379` | `6379` | Redis (host access / tools) |
| `KCWORKS_POSTGRES_HOST_PORT` | `5432` | `5432` | PostgreSQL |
| `KCWORKS_PGADMIN_HOST_PORT` | `5050` | `80` (pgAdmin listens on 80 in-container) | pgAdmin web UI (host) |
| `KCWORKS_RABBITMQ_AMQP_HOST_PORT` | `5672` | `5672` | AMQP |
| `KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT` | `15672` | `15672` | RabbitMQ management UI |
| `KCWORKS_OPENSEARCH_HTTP_HOST_PORT` | `9200` | `9200` | OpenSearch HTTP |
| `KCWORKS_OPENSEARCH_PERF_ANALYZER_HOST_PORT` | `9600` | `9600` | OpenSearch Performance Analyzer |
| `KCWORKS_OPENSEARCH_DASHBOARDS_HOST_PORT` | `5601` | `5601` | OpenSearch Dashboards |

**Do not change** `REDIS_DOMAIN`, `INVENIO_SEARCH_DOMAIN`, or the host in `INVENIO_SQLALCHEMY_DATABASE_URI` for normal Docker Compose use: apps inside the stack should keep using Docker service names (for example `REDIS_DOMAIN='cache:6379'`, `INVENIO_SEARCH_DOMAIN='search:9200'`, `...@db/kcworks`). Host-port overrides only change how ports are published **to your Mac**, not how containers talk to each other.

If you change nginx HTTPS (or HTTP) host ports, update **`INVENIO_SITE_UI_URL`** and **`INVENIO_SITE_API_URL`** in that clone’s `.env` so the app generates correct links (for example `INVENIO_SITE_UI_URL="https://localhost:8443"` and `INVENIO_SITE_API_URL="https://localhost:8443/api"`).

**Example — second instance (`kcworks-next`)** so it can run alongside defaults on `knowledge-commons-works`:

```shell
KCWORKS_CONTAINERS_BASE_NAME=kcworks-next
KCWORKS_NGINX_HTTP_HOST_PORT=8080
KCWORKS_NGINX_HTTPS_HOST_PORT=8443
KCWORKS_REDIS_HOST_PORT=6380
KCWORKS_POSTGRES_HOST_PORT=5433
KCWORKS_PGADMIN_HOST_PORT=5051
KCWORKS_RABBITMQ_AMQP_HOST_PORT=5673
KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT=15673
KCWORKS_OPENSEARCH_HTTP_HOST_PORT=9201
KCWORKS_OPENSEARCH_PERF_ANALYZER_HOST_PORT=9601
KCWORKS_OPENSEARCH_DASHBOARDS_HOST_PORT=5602
INVENIO_SITE_UI_URL="https://localhost:8443"
INVENIO_SITE_API_URL="https://localhost:8443/api"
```

**Example — third instance (`v13test`)** alongside the above (pick unused ports on your machine):

```shell
KCWORKS_CONTAINERS_BASE_NAME=v13test
KCWORKS_NGINX_HTTP_HOST_PORT=9080
KCWORKS_NGINX_HTTPS_HOST_PORT=9443
KCWORKS_REDIS_HOST_PORT=6381
KCWORKS_POSTGRES_HOST_PORT=5434
KCWORKS_PGADMIN_HOST_PORT=5052
KCWORKS_RABBITMQ_AMQP_HOST_PORT=5674
KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT=15674
KCWORKS_OPENSEARCH_HTTP_HOST_PORT=9202
KCWORKS_OPENSEARCH_PERF_ANALYZER_HOST_PORT=9602
KCWORKS_OPENSEARCH_DASHBOARDS_HOST_PORT=5603
INVENIO_SITE_UI_URL="https://localhost:9443"
INVENIO_SITE_API_URL="https://localhost:9443/api"
```

Leave **one** instance (typically your primary clone) with no `KCWORKS_*_HOST_PORT` lines so it keeps ports `80`, `443`, `6379`, `5432`, and so on.

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

These are the minimal variables that you need to set in your `.env` file to get the application running. For local development you should use the default values for all variables except the ones with comments:

```shell
# Optional: base name for Docker container names (default: kcworks). Set to e.g. kcworks-next when
# running a second instance on the same host to avoid container name conflicts.
# KCWORKS_CONTAINERS_BASE_NAME=kcworks
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
INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://kcworks:PASSWORDHERE@db/kcworks" # THE PASSWORD HERE MUST MATCH THE POSTGRES_PASSWORD BELOW
POSTGRES_USER=kcworks
POSTGRES_DB=kcworks
POSTGRES_PASSWORD=PASSWORDHERE
INVENIO_CSRF_SECRET_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
INVENIO_SECURITY_LOGIN_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
INVENIO_SECRET_KEY='SECRET_KEY_VERY_SECRET'
COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators - just leave as is
API_TOKEN=myapitoken # this can be generated after the instance is running, just leave as is
API_TOKEN_PRODUCTION=myapitokenproduction # for importing test data in local development, this must be obtained from the KCWorks administrators - just leave as is for now
INVENIO_LOCAL_SITE_PATH=/local/path/to/cloned/repository/knowledge-commons-works/site # set this to `site` under the base directory of your cloned repository
INVENIO_LOCAL_DEPENDENCIES_PATH=/local/path/to/cloned/repository/knowledge-commons-works/site/kcworks/dependencies # set this to `site/kcworks/dependencies` under the base directory of your cloned repository
PYTHON_LOCAL_SITE_PACKAGES_PATH=/local/path/to/cloned/repository/knowledge-commons-works/.venv/lib/python3.12/site-packages # you need this for dev
PGADMIN_DEFAULT_EMAIL=your.email@example.com  # change this to your email address
PGADMIN_DEFAULT_PASSWORD=PASSWORDHERE
INVENIO_LOCAL_INSTANCE_PATH=/opt/invenio/var/instance
```

```{note}
Don't forget to change the `PASSWORDHERE` values to the actual passwords you use for your admin user and pgAdmin. This includes replacing `PASSWORDHERE` in the `INVENIO_SQLALCHEMY_DATABASE_URI` variable.
```

#### Running a second instance on the same machine

If you run another copy of KCWorks on the same host (e.g. a second clone for a different branch), set a unique base name in that copy's `.env` so Docker container names do not clash:

```shell
KCWORKS_CONTAINERS_BASE_NAME=kcworks-next
```

Use any distinct value (e.g. `kcworks-next`, `kcworks-dev2`). Container names will become `kcworks-next-ui`, `kcworks-next-db`, and so on.

If **more than one** stack should run **at the same time**, also assign a non-overlapping set of [Host port overrides](#host-port-overrides) in each clone’s `.env` (and matching `INVENIO_SITE_*_URL` values when nginx ports change). Optionally set **`COMPOSE_PROJECT_NAME`** (or `docker compose -p <name>`) per clone so Compose project labels and default network names stay distinct; that is separate from host port binding.

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

## Importing test data

To import test data into your local instance, you can use the `import_test_data` command. This command will import records from the production API and create a Knowledge Commons community if it doesn't exist. The new records will be added to the Knowledge Commons community. From inside the `kcworks-ui` container, run the following command:

```shell
invenio kcworks_records import-test-records <email> <number-of-records>
```

This will import the specified number of records from the production API and add them to the Knowledge Commons community, owned by the user with the specified email address. (The email address must be an existing user in the local instance and must have the "owner" role for the Knowledge Commons community.)
