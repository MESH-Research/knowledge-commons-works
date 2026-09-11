# Automated Testing

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-works Github repo. You can (and should) also run the test suite locally.

There are currently three distinct sets of tests that have to be run separately:
(a) python tests run using invenio's fixtures,
(b) javascript tests run separately using jest,
(c) Ghost Inspector tests that run on the deployed site (staging or production).

## Python tests

The python test suite includes (a) unit tests for back end code, (b) tests of ui views and api requests run with a client fixture. It also includes a mypy type-checking step, and it builds the documentation and compiles the translations. To run the unit tests and view/request tests, navigate to the root `knowledge-commons-works` folder and run
```console
bash run-tests.sh -vv
```
Note that you will need to have your local docker service running for these tests to work, since they use the `docker-services-cli` tool to start the required services.

```{warning}
Ensure that you have **stopped** the docker-compose project for your local development instance before running the tests! Otherwise, you will get conflicts with the services that are started by the tests.
```

### Local development vs CI mode

The test runner detects whether it is running in a CI environment (GitHub Actions) or locally:
- **Local**: Runs pytest (and optional Jest with `-J`) inside the `test-runner` container connected to docker-services-cli services for security (prevents malicious dependency code from accessing host credentials)
- **CI**: Uses the current behavior (pytest runs directly on the Actions runner; GitHub Actions provides isolation via ephemeral machines)

The detection is done by checking if the `$CI` environment variable is set. This variable is automatically set by GitHub Actions and can be manually set for local testing of CI mode.

### Running specific tests

To run a specific test file, simply add the relative file path to the command, e.g.,
```console
bash run-tests.sh -vv tests/api/test_user_data_sync.py
```

And to run a specific test function, add the function name to the command, e.g.,
```console
bash run-tests.sh -vv tests/api/test_user_data_sync.py::test_user_data_sync
```
Or use the `-k` flag to run tests whose names contain the specified string, e.g.,
```console
bash run-tests.sh -vv -k "test_user_data_sync"
```

### Options for running tests

In addition to the options listed above, the test runner script provides the following options:

| Option | Short form | Description |
|--------|------------|-------------|
| `--skip-translations` | `-S` | Skip the translation extraction, update, and compilation steps (and Sphinx docs). |
| `--keep-services` | `-K` | Keep the docker-services-cli containers running after the tests are run. |
| `--js` | `-J` | Also run the root Jest suite (`pnpm test`) inside the test-runner before pytest. |
| `--js-only` | | Run only Jest in the test-runner: no docker-services-cli, no translations/docs, no pytest. Extra args are passed to Jest. |
| `--build` | `-B` | Rebuild the test-runner image before running. |

```{note}
Any pytest flags and options can be added to the test runner command and will be passed to pytest. E.g., the `-vv` flag in the examples above is equivalent to running `pytest -vv` and specifies verbose output.
```

### Passing pytest arguments to the test runner

Any pytest arguments can be passed to the script, e.g., to run only tests whose names contain the word "view", and to show verbose output:
```console
bash run-tests.sh -k "view" -vv
```

To run the tests in a specific directory, use the `-d` flag:
```console
bash run-tests.sh -d tests/api
```

To run the tests in a specific file, use the `-f` flag:
```console
bash run-tests.sh -f tests/api/test_view.py
```

By default, the docker containers are stopped after the tests are run. To run the tests and leave the docker containers running, use the upper-case `-K` flag:
```console
bash run-tests.sh -K
```

### Test discovery and doctests

The pytest configuration in `pyproject.toml` tells pytest to look for tests in the `tests` directory as well as in the `site/kcworks` directory (excluding the `dependencies` and `stats_dashboard` subdirectories). If you wish to expand this search, you can do so by adding additional directories to the `tool.pytest.ini_options.testpaths` list in the `pyproject.toml` file.

Pytest will also run any doctests that are found in these directories. This includes any files that end with `.rst` as well as any doctests that are embedded in the docstrings of python files.

### Test configuration

The top-level `conftest.py` file is used to configure the test environment. Most of the tests use an invenio (Flask) app instance that receives all of the configuration variables from the `invenio.cfg` file. Some of these variables are then overridden in the `test_config` dictionary that `conftest.py` passes to the app instance.

The test environment does not use the top-level `.env` file that is used in the development environment. Instead, `run-tests.sh` layers two environment files into the `uv run` invocation that launches pytest:

1. `tests/.env` (when present) holds non-secret defaults — URLs, public identifiers, and any per-developer overrides. This file is checked in only as a placeholder; values are managed locally.
2. A dynamically generated `/tmp/kcworks-tests-secrets.env` (mode `600`, removed immediately after container starts) holds secrets fetched from AWS Secrets Manager. This file is loaded **after** `tests/.env`, so its values override any matching keys in `tests/.env`.

The secret file is produced by `scripts/kcworks_test_secrets.sh`, which mirrors the production-style flow used by `kcworks-startup.sh`. By default it pulls a small, defined slice of keys from the `staging/kcworks` secret:

- `SPARKPOST_USERNAME`
- `SPARKPOST_API_KEY`
- `INVENIO_ADMIN_EMAIL`

The defaults can be overridden without editing the script:

- `KCWORKS_TEST_SM_SECRET_ID` (or `--secret-id`): override the AWS Secrets Manager secret id.
- `KCWORKS_TEST_SM_KEYS` (or `--keys`): comma-separated list of keys to pull from the secret.
- `--region`: forwarded to `aws` for cross-region secrets.
- `--allow-missing`: warn instead of failing when a listed key is absent from the secret.
- `KCWORKS_TEST_SM_DISABLE=1`: skip the AWS lookup entirely; rely on `tests/.env` (used in CI, where secrets come from GitHub Actions secrets).

Run `./scripts/kcworks_test_secrets.sh --help` for the full contract. The helper requires the `aws` CLI to be configured on the host and the project venv at `.venv/bin/python`.

```{note}
On CI the workflow sets `KCWORKS_TEST_SM_DISABLE=1` and injects the same keys via the `Run tests` step's `env:` block from GitHub Actions secrets. No AWS credentials are needed (or used) in CI.
```

### Containerized test runner for local development

In local mode, pytest (and optional Jest) runs inside a container (`test-runner`) that:
- Connects to the docker-services-cli network (`docker_services_cli_default`) when pytest needs those services
- Mounts site/deps/tests (and assets/Jest config when needed) from the host
- Loads secrets via a Compose service secret for the pytest path

The temp file containing AWS secrets is:
1. Created by `kcworks_test_secrets.sh`
2. Mounted into the container for its lifetime
3. Deleted after the container finishes (cleanup trap handles interrupts)

### Pytest fixtures

The `conftest.py` file loads a number of custom fixture files from the `tests/fixtures` directory. Note that any additional custom fixture files must be added to this list. They cannot be loaded automatically based on the `pyproject.toml` pytest configuration because the `tests` directory is not inside the `site` directory, which is the package build context for `kcworks`.

### Additional actions included in the test runner

The test runner includes additional actions that are not part of the pytest framework. These include:

- Building the documentation with Sphinx
- Extracting translations from python files


## Javascript tests

Pytest does not directly test custom javascript files or React components. Those use Jest.

**Local:** one entrypoint runs every registered suite inside the `test-runner` container:

```console
bash run-tests.sh --js-only
```

Or include JS before pytest:

```console
bash run-tests.sh -J -vv
```

`bash run-js-tests.sh` locally forwards to `./run-tests.sh --js-only`. Suites are defined in `scripts/run-js-suites.sh` (root first, then dependency packages that have their own Jest harness). Each suite uses its own `package.json` / `pnpm` / `jest.config.js`. The root Jest config ignores `site/kcworks/dependencies/` so those tests are not double-run under the root installer.

**CI:** `run-js-tests.sh` runs `scripts/run-js-suites.sh` on the Actions runner (host `pnpm`).

Extra arguments are passed through to each suite’s Jest, e.g.:

```console
bash run-tests.sh --js-only -- test_utils.js
```

Rebuild the test-runner image after root `package.json` / lockfile changes (`-B`). Package-suite installs run in-container onto the editable dep mounts when `KCWORKS_JS_SUITE_INSTALL=1` (default).

Dependency packages that still have `*.test.js` files but are **not** listed in `scripts/run-js-suites.sh` are not executed until they get a package-local Jest setup and are added to that list. Current package suites: `invenio-stats-dashboard`, `invenio-modular-deposit-form`, `invenio-modular-detail-page` (detail-page may report zero tests until UI tests are added).

Jest configs use `verbose: false` by default (file-level results, not per-test PASS lines). For per-test output: `pnpm test -- --verbose`.

## Ghost Inspector tests

The Ghost Inspector tests are run on the deployed site (staging or production). They run on a regular schedule and are used to ensure that the site is working as expected.

```{note}
At present, Ghost Inspector tests are not run automatically when a pull request is merged into the `staging` or `production` branches. This should be implemented in the future once deployment to the respective servers is fully automated.
```