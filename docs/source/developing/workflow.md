# Development Workflow

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

```{note}
The watch command will only pick up changes to files that already existed during the last Webpack build. If you add
- a new javascript file
- a new css (less) file
- a new node.js package requirement
then you need to again run the basic (slow) build script to include it in the build process.
After that you can run `invenio webpack run start` again to pick up changes on the fly.
```

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

Changes to python code in the `site` folder should (like changes to template files) take effect immediately in the running Knowledge Commons Works instance, provided that the `build-assets.sh` script has been run since the last updated image was built. You simply need to refresh the page in your browser.

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

```{note}
These instructions do not support installation under Windows. Windows users should emulate a Linux environment using WSL2.
```

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

```{caution}
Make sure that you run this `prune` command *while the containers are running.* If you run it while the containers are stopped, you will delete the containers and images that you need to run the application, as well as volumes with stored data.
```

6. Rebuild the asset files with the following command:

```shell
docker exec -it kcworks-ui bash
bash ./scripts/build-assets.sh
```

7. Then refresh your browser to see the changes.
