# Automated Testing

Automated tests (unit tests and integration tests) are run every time a commit is pushed to the knowledge-commons-works Github repo. You can (and should) also run the test suite locally.

There are currently three distinct sets of tests that have to be run separately:
(a) python tests run using invenio's fixtures,
(b) javascript tests run separately using jest,
(c) Ghost Inspector tests that run on the deployed site (staging or production).

## Python tests

The python test suite includes (a) unit tests for back end code, (b) tests of ui views and api requests run with a client fixture. To run the unit tests and view/request tests, navigate to the root `knowledge-commons-works/site` folder and run
```console
bash run_tests.sh
```
Note that you will need to have your local docker service running for these tests to work, since they use the `docker-services-cli` tool to start the required services.

> [!Note]
> Ensure that you have stopped the docker-compose project for your local development instance before running the tests! Otherwise, you will get conflicts with the services that are started by the tests.

## Javascript tests

Pytest does not directly test custom javascript files or React components. In order to test these, navigate to the root knowledge-commons-works folder and run
```console
npm run test
```
These tests are run using the jest test runner, configured in the packages.json file in the root knowledge-commons-works folder.

Note that these tests run using a local npm configuration in the knowledge-commons-works folder. Any packages that are normally available to InvenioRDM must be added to the local package.json configuration and will be installed in the local node_modules folder. Since this folder is not included in GIT version control, before you run the javascript tests you must ensure the required packages are installed locally by running
```console
npm install
```

## Ghost Inspector tests

The Ghost Inspector tests are run on the deployed site (staging or production). They run on a regular schedule and are used to ensure that the site is working as expected.

> [!Note]
> At present, Ghost Inspector tests are not run automatically when a pull request is merged into the `staging` or `production` branches. This should be implemented in the future once deployment to the respective servers is fully automated.