# Developing KCWorks

## Version Numbering

KCWorks uses semantic versioning (https://semver.org/). When a new release is made, the version number should be incremented in the following files:

- `README.md`
- `docs/source/README.md`
- `docs/source/conf.py`
- `site/pyproject.toml`
- `site/kcworks/__init__.py`

While in beta, the version number should be followed by a numbered `-beta` suffix: e.g., `0.3.3-beta6`. This suffix should be updated continuously (without starting over again for minor releases) until version 1.0.0 is reached and KCWorks leaves beta.

Bug fixes and other changes that do not introduce new features (including changes to documentation, build processes, etc.) should be considered `patch` releases.

New features should be considered `minor` releases.

## Version Control

### Git Branching Strategy

KCWorks employs a modified version of the Gitlab Flow branching strategy for version control. The repository has four persistent branches:

- `main` is the default branch and is the reference point for active development. It will usually not be ready for production deployment.
- `staging` is the branch that is deployed to the staging server. It is created from the `main` branch when changes are ready to be tested. No commits should be made directly to the `staging` branch except to merge changes from `main`.
- `production` is the branch that is deployed to the development server. It is created from the `staging` branch when changes are ready to be deployed to the production server. No commits should be made directly to the `production` branch except to merge changes from `staging`.
- `gh_pages` is the branch that is used to generate the static documentation site for KCWorks on Github Pages. This branch is automatically updated from the `main` branch.

#### Daily Development Workflow

When a developer needs to make changes to the codebase, they should create a new temporary working branch from the `main` branch. This branch should be named descriptively, such as `feature/new-feature` or `fix/fix-issue`. Work in progress should be committed to this working branch until the developer is ready to merge the changes into the `main` branch.

Changes should be merged back into `main` as often as possible, and the temporary branches deleted. These merges should be performed when a developer is ready to deploy the changes to the staging server for testing. This should generally be done *after* the appropriate tests have been written and are passing. Merges should also represent a single completed change (feature or fix). Developers should, though, think in terms of small, incremental changes and merge often.

Merging to `main` should be done via pull request, and the merge only accepted if the newly added tests are present and passing. This ensures that the `main` branch is always in a deployable state and ready for incoming merges by other developers. Merges should be performed using the squash merge strategy (the equivalent of `git merge --squash <branch>`). This combines all of the incoming changes into a single commit, making the commit history cleaner and easier to read.

No commits should be made directly to the `staging` or `production` branches. All changes should be made to the `main` branch and then merged into `staging` and `production` via pull requests. This is especially important because changes pushed to `staging` and `production` branches will automatically trigger rebuilding of the stanging or production containers and the deployment of the updated containers to the respective servers.

### Commit strategy

Developers should make frequent commits to their working branch. These may be as small and granular as the developer wishes since many incremental commits allow easy rollback to specific points in the development history. Such commits should be given descriptive names and commit messages that would allow quick identification of the changes. These commits will be squashed into a single commit when merged into `main`.

Commits to the `main` branch should each represent a single completed change (feature or fix). We try to avoid `wip` commits in order to keep the commit history readable. So all of the changes for a single feature or fix should be squashed into a single commit when merged from a temporary working branch into `main`.

Commits to the `main` branch should be named with the `feature` or `fix` prefix and one or more labels for the aspect of the codebase that the changes address. For example, `feature(upload-form): add a new upload form` or `fix(record-page): fix the problem with the record page`. In general, maintenance changes should be considered `fix` commits unless they are part of a larger feature or add new functionality.

### Tagging Releases

Whenever the KCWorks version number changes, that commit should be tagged with the new version number. This can be done by running the following command:

```shell
git tag -a <version-number> -m "Release <version-number>"
```
We do not create branches for each numbered release.

### Git Submodules

KCWorks uses git submodules to manage dependencies. The submodules are located in the `site/kcworks/dependencies` folder. The submodules are cloned from the upstream repositories when the KCWorks instance is first created. They are updated from the upstream repositories when the KCWorks instance is updated.

Note that in some cases there are inter-dependencies between these submodules. For example, the `invenio-record-importer-kcworks` submodule has its own dependency on the `invenio-group-collections-kcworks` submodule. When cloning the KCWorks repository, you **should not use the `--recurse-submodules` option** because this will clone redundant copies of these inter-dependent submodules. Instead, you should clone the KCWorks repository and then initialize the submodules in a separate step with `git submodule update --init`. Likewise, when updating the KCWorks submodules, you should use the `git submodule update --remote` command **without the `--recursive` option**.



## Updating the running KCWorks instance with development changes

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
Or you can restart the docker-compose project, which will also restart the uwsgi processes.

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

> [!Note]
> The watch command will only pick up changes to files that already existed during the last Webpack build. If you add
> - a new javascript file
> - a new css (less) file
> - a new node.js package requirement
> then you need to again run the basic (slow) build script to include it in the build process.
> After that you can run `invenio webpack run start` again to pick up changes on the fly.

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

You will then need to restart the uwsgi processes or restart the docker-compose project as described above.

### Changes to python code in the `site` folder

Changes to python code in the `site` folder should (like changes to template files) take effect immediately in the running Knowledge Commons Works instance. You simply need to refresh the page in your browser.

#### Adding new entry points

Sometimes you will need to add new entry points to inform the Flask application about additional code you have provided. This is done via the `setup.py` file in the `site` folder. Once you have added the entry point declaration, you will need to re-install the `kcworks` package in the `kcworks-ui`, `kcworks-api`, and `kcworks-worker` container. This can be done by running the following command inside the each container:

```shell
cd /opt/invenio/src/site
pip install -e .
uwsgi --reload /tmp/uwsgi_ui.pid
```

If you have added js, css, or static files along with the entry point code, you will also need to run the collect and webpack build commands as described above and restart the docker-compose project.

Note that entry point changes may be overridden if you pull a more recent version of the kcworks docker image and restart the docker-compose project. Ultimately the entry point changes will have to be added to a new version of the kcworks docker image.

### Changes to external python modules (including Invenio modules)

Changes to other python modules (including Invenio modules) will require rebuilding the main kcworks container. Additions to the python requirements should be added to the `Pipfile` in the kcworks folder and committed to the Github repository. You should then request that the kcworks container be rebuilt with the additions.

In the meantime, required python packages can be installed directly in the `kcworks-ui`, `kcworks-api`, and `kcworks-worker` containers. Enter each container and then install the required package pip (not pipenv):

```shell
pip install <package-name>
```

## Digging deeper

What follows is a step-by-step walk through this process.

> [!Note]
> These instructions do not support installation under Windows. Windows users should emulate a Linux environment using WSL2.

## Updating an Instance with Upstream Changes

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

## Running automated tests (NEEDS UPDATING)

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
