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
| `--skip-translations` | `-S` | Skip the translation extraction, update, and compilation steps. |
| `--keep-services` | `-K` | Keep the docker-services-cli containers running after the tests are run. |

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

The test environment does not use the top-level `.env` file that is used in the development environment. Where environment variables are needed, these are provided in a dedicated environment file `tests/.env` that is used to configure the test environment in the test runner script `run-tests.sh`.

### Pytest fixtures

The `conftest.py` file loads a number of custom fixture files from the `tests/fixtures` directory. Note that any additional custom fixture files must be added to this list. They cannot be loaded automatically based on the `pyproject.toml` pytest configuration because the `tests` directory is not inside the `site` directory, which is the package build context for `kcworks`.

### Additional actions included in the test runner

The test runner includes additional actions that are not part of the pytest framework. These include:

- Building the documentation with Sphinx


## Javascript tests

Pytest does not directly test custom javascript files or React components. In order to test these, navigate to the root `knowledge-commons-works` folder and run
```console
bash run-js-tests.sh
```
These tests are run using the jest test runner, configured in the packages.json file in the root knowledge-commons-works folder.

This is equivalent to running
```console
npm run test
```

Note that these tests run using a local npm configuration in the knowledge-commons-works folder. Any packages that are normally available to InvenioRDM must be added to the local package.json configuration and will be installed in the local node_modules folder. Since this folder is not included in GIT version control, before you run the javascript tests you must ensure the required packages are installed locally by running

```console
npm install
```

## Ghost Inspector tests

The Ghost Inspector tests are run on the deployed site (staging or production). They run on a regular schedule and are used to ensure that the site is working as expected.

```{note}
At present, Ghost Inspector tests are not run automatically when a pull request is merged into the `staging` or `production` branches. This should be implemented in the future once deployment to the respective servers is fully automated.
```