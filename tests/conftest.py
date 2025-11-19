# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Top-level pytest configuration for KCWorks tests."""

import importlib
import importlib.util
import os
import shutil
import tempfile
from collections import namedtuple
from pathlib import Path

import jinja2
import pytest
from invenio_app.factory import create_app as _create_app
from invenio_queues import current_queues
from invenio_search.proxies import current_search_client
from jinja2 import PackageLoader

# Imports after logging setup (E402 suppressed - logging must be set up first)
from .fixtures.custom_fields import test_config_fields  # noqa: E402
from .fixtures.frontend import MockManifestLoader  # noqa: E402
from .fixtures.identifiers import test_config_identifiers  # noqa: E402
from .fixtures.saml import test_config_saml  # noqa: E402


def load_config():
    """Load the invenio.cfg file and return a dictionary of its variables.

    This is needed because we can't import the invenio.cfg file directly
    because it's not a Python module.

    Returns:
        dict: Dictionary of configuration variables.

    Raises:
        ValueError: If the configuration file is invalid.
    """
    config_path = Path(__file__).parent.parent / "invenio.cfg"

    spec = importlib.util.spec_from_loader("config", None)
    if spec is None:
        raise ValueError("Failed to load invenio.cfg")
    config = importlib.util.module_from_spec(spec)

    with open(config_path) as f:
        exec(f.read(), config.__dict__)

    # Convert module attributes to a dictionary, excluding private attributes
    return {k: v for k, v in config.__dict__.items() if not k.startswith("_")}


config = load_config()
print("Config loaded successfully")

pytest_plugins = (
    "tests.fixtures.communities",
    "tests.fixtures.community_events",
    "tests.fixtures.custom_fields",
    "tests.fixtures.files",
    "tests.fixtures.fixtures",
    "tests.fixtures.frontend",
    "tests.fixtures.identifiers",
    "tests.fixtures.mail",
    "celery.contrib.pytest",
    "tests.fixtures.records",
    "tests.fixtures.roles",
    "tests.fixtures.search_provisioning",
    "tests.fixtures.stats",
    "tests.fixtures.users",
    "tests.fixtures.vocabularies.affiliations",
    "tests.fixtures.vocabularies.community_types",
    "tests.fixtures.vocabularies.date_types",
    "tests.fixtures.vocabularies.descriptions",
    "tests.fixtures.vocabularies.funding_and_awards",
    "tests.fixtures.vocabularies.languages",
    "tests.fixtures.vocabularies.licenses",
    "tests.fixtures.vocabularies.resource_types",
    "tests.fixtures.vocabularies.roles",
    "tests.fixtures.vocabularies.subjects",
    "tests.fixtures.vocabularies.title_types",
    "tests.pytest_plugins.pytest_live_status",
)


def _(x):
    """Identity function for string extraction.

    Returns:
        Any: The input value unchanged.
    """
    return x


test_config = {
    **config,
    "RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS": test_config_identifiers[
        "RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"
    ],
    "RDM_PERSISTENT_IDENTIFIER_PROVIDERS": test_config_identifiers[
        "RDM_PERSISTENT_IDENTIFIER_PROVIDERS"
    ],
    **test_config_fields,
    # **test_config_stats,  # Now getting directly from invenio.cfg
    **test_config_saml,
    "SQLALCHEMY_DATABASE_URI": (
        "postgresql+psycopg2://kcworks:kcworks@localhost:5432/kcworks"
    ),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SEARCH_INDEX_PREFIX": "",  # TODO: Search index prefix triggers errors
    "POSTGRES_USER": "kcworks",
    "POSTGRES_PASSWORD": "kcworks",
    "POSTGRES_DB": "kcworks",
    "WTF_CSRF_ENABLED": False,
    "WTF_CSRF_METHODS": [],
    "RATELIMIT_ENABLED": False,
    "APP_DEFAULT_SECURE_HEADERS": {
        "content_security_policy": {"default-src": []},
        "force_https": False,
    },
    "BROKER_URL": "amqp://guest:guest@localhost:5672//",
    # "CELERY_CACHE_BACKEND": "memory",
    # "CELERY_RESULT_BACKEND": "cache",
    "CELERY_TASK_ALWAYS_EAGER": False,
    "CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS": True,
    "CELERY_LOGLEVEL": "DEBUG",
    #  'DEBUG_TB_ENABLED': False,
    "INVENIO_INSTANCE_PATH": "/opt/invenio/var/instance",
    "MAIL_SUPPRESS_SEND": False,
    "MAIL_SERVER": "smtp.sparkpostmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.getenv("SPARKPOST_USERNAME"),
    "MAIL_PASSWORD": os.getenv("SPARKPOST_API_KEY"),
    "MAIL_DEFAULT_SENDER": os.getenv("INVENIO_ADMIN_EMAIL"),
    #  'OAUTH2_CACHE_TYPE': 'simple',
    #  'OAUTHLIB_INSECURE_TRANSPORT': True,
    "SECRET_KEY": "test-secret-key",
    "SECURITY_PASSWORD_SALT": "test-secret-key",
    "WEBPACKEXT_MANIFEST_LOADER": MockManifestLoader,
    "TESTING": True,
    "DEBUG": True,
    "COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED": True,
    "COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED": True,
}

parent_path = Path(__file__).parent
log_folder_path = parent_path / "test_logs"
log_file_path = log_folder_path / "invenio.log"
if not log_file_path.exists():
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_path.touch()

test_config["LOGGING_FS_LEVEL"] = "DEBUG"
test_config["LOGGING_FS_LOGFILE"] = str(log_file_path)
test_config["LOGGING_CONSOLE_LEVEL"] = "DEBUG"
test_config["CELERY_LOGFILE"] = str(log_folder_path / "celery.log")
test_config["RECORD_IMPORTER_DATA_DIR"] = str(
    parent_path / "helpers" / "sample_import_data"
)
test_config["RECORD_IMPORTER_LOGS_LOCATION"] = log_folder_path

# enable DataCite DOI provider
test_config["DATACITE_ENABLED"] = True
test_config["DATACITE_USERNAME"] = "INVALID"
test_config["DATACITE_PASSWORD"] = "INVALID"
test_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
test_config["DATACITE_PREFIX"] = "10.17613"
test_config["DATACITE_TEST_MODE"] = True
# ...but fake it

test_config["SITE_API_URL"] = os.environ.get(
    "INVENIO_SITE_API_URL", "https://127.0.0.1:5000/api"
)
test_config["SITE_UI_URL"] = os.environ.get(
    "INVENIO_SITE_UI_URL", "https://127.0.0.1:5000"
)


@pytest.fixture(scope="module")
def extra_entry_points() -> dict:
    """Extra entry points fixture for KCWorks.

    Returns:
        dict: Dictionary of extra entry points.
    """
    return {
        # "invenio_base.api_apps": ["kcworks = kcworks.ext:KCWorks"],
        # "invenio_base.apps": ["kcworks = kcworks.ext:KCWorks"],
        # "invenio_base.api_blueprints": [
        #     "kcworks = kcworks.views.views:create_api_blueprint"
        # ],
        # "invenio_base.blueprints": ["kcworks = kcworks.views.views:create_blueprint"],
    }


@pytest.fixture(scope="session")
def celery_config(celery_config):
    """Celery config fixture for KCWorks.

    Returns:
        dict: Celery configuration dictionary.
    """
    celery_config["logfile"] = str(log_folder_path / "celery.log")
    celery_config["loglevel"] = "DEBUG"
    celery_config["task_always_eager"] = True
    celery_config["cache_backend"] = "memory"
    celery_config["result_backend"] = "cache"
    celery_config["task_eager_propagates_exceptions"] = True

    return celery_config


@pytest.fixture(scope="session")
def celery_enable_logging():
    """Celery enable logging fixture for KCWorks.

    Returns:
        bool: True to enable Celery logging.
    """
    return True


# @pytest.fixture(scope="session")
# def flask_celery_app(celery_config):
#     app = Celery("invenio_app.celery")
#     app.config_from_object(celery_config)
#     return app


# @pytest.fixture(scope="session")
# def flask_celery_worker(flask_celery_app):
#     with start_worker(flask_celery_app, perform_ping_check=False) as worker:
#         yield worker


@pytest.yield_fixture(scope="module")
def location(database):
    """Creates a simple default location for a test.

    Use this fixture if your test requires a `files location <https://invenio-
    files-rest.readthedocs.io/en/latest/api.html#invenio_files_rest.models.
    Location>`_. The location will be a default location with the name
    ``pytest-location``.

    Yields:
        Location: The created test location.
    """
    from invenio_files_rest.models import Location

    uri = tempfile.mkdtemp()
    location_obj = Location(name="pytest-location", uri=uri, default=True)

    database.session.add(location_obj)
    database.session.commit()

    yield location_obj

    # TODO: Submit PR to pytest-invenio to fix the below line in the stock fixture
    shutil.rmtree(uri)


# This is a namedtuple that holds all the fixtures we're likely to need
# in a single test.
RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "location",
        "cache",
        "affiliations_v",
        "awards_v",
        "community_type_v",
        "contributors_role_v",
        "creators_role_v",
        "date_type_v",
        "description_type_v",
        "funders_v",
        "language_v",
        "licenses_v",
        # "relation_type_v",
        "resource_type_v",
        "subject_v",
        "title_type_v",
        "create_communities_custom_fields",
        "create_records_custom_fields",
    ],
)


@pytest.fixture(scope="function")
def running_app(
    app,
    location,
    cache,
    affiliations_v,
    awards_v,
    community_type_v,
    contributors_role_v,
    creators_role_v,
    date_type_v,
    description_type_v,
    funders_v,
    language_v,
    licenses_v,
    # relation_type_v,
    resource_type_v,
    subject_v,
    title_type_v,
    create_communities_custom_fields,
    create_records_custom_fields,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.

    Returns:
        RunningApp: The running application instance.
    """
    return RunningApp(
        app,
        location,
        cache,
        affiliations_v,
        awards_v,
        community_type_v,
        contributors_role_v,
        creators_role_v,
        date_type_v,
        description_type_v,
        funders_v,
        language_v,
        licenses_v,
        # relation_type_v,
        resource_type_v,
        subject_v,
        title_type_v,
        create_communities_custom_fields,
        create_records_custom_fields,
    )


@pytest.fixture(scope="function")
def search_clear(search_clear):
    """Clear search indices after test finishes (function scope).

    the search_clear fixture should each time start by running
    ```python
    current_search.create()
    current_search.put_templates()
    ```
    and then clear the indices during the fixture teardown. But
    this doesn't catch the stats indices, so we need to add an
    additional step to delete the stats indices and template manually.
    Otherwise, the stats indices aren't cleared between tests.

    Yields:
        None: Yields control to the test.
    """
    # Clear identity cache before each test to prevent stale community role data
    from invenio_communities.proxies import current_identities_cache

    current_identities_cache.flush()

    yield search_clear

    # Delete stats indices and templates if they exist
    current_search_client.indices.delete("*stats*", ignore=[404])
    current_search_client.indices.delete_template("*stats*", ignore=[404])


@pytest.fixture(scope="module")
def template_loader():
    """Fixture providing overloaded and custom templates to test app.

    Returns:
        Callable: Function to load templates.
    """

    def load_tempates(app):
        """Load templates for the test app."""
        project_root = Path(__file__).parent.parent
        site_path = project_root / "site" / "kcworks" / "templates" / "semantic-ui"
        root_path = project_root / "templates"
        test_helpers_path = (
            Path(__file__).parent / "helpers" / "templates" / "semantic-ui"
        )

        # Local template paths for overrides
        template_paths = []
        for path in (
            test_helpers_path,  # Main project test stubs (highest priority)
            site_path,
            root_path,
        ):
            if path.exists():
                template_paths.append(str(path))
        
        loaders = [jinja2.FileSystemLoader(template_paths)]
        
        package_configs = [
            ("invenio_theme", "templates"),  # This finds macros
            ("invenio_theme", "templates/semantic-ui"),  # This finds page templates
            ("invenio_app_rdm", "theme/templates/semantic-ui"),
            ("invenio_banners", "templates/semantic-ui"),
            ("invenio_communities", "templates/semantic-ui"),
            ("invenio_stats_dashboard", "templates/semantic-ui"),
        ]
        
        for package_name, template_dir in package_configs:
            try:
                loader = PackageLoader(package_name, template_dir)
                loaders.append(loader)
            except (ImportError, ModuleNotFoundError, ValueError) as e:
                app.logger.warning(
                    f"Could not create PackageLoader for {package_name}: {e}"
                )
        
        custom_loader = jinja2.ChoiceLoader(loaders)
        app.jinja_loader = custom_loader
        app.jinja_env.loader = custom_loader
        
    return load_tempates


@pytest.fixture(scope="module")
def app(
    app,
    app_config,
    database,
    search,
    template_loader,
    admin_roles,
):
    """This fixture provides an app with the typically needed basic fixtures.

    This fixture should be used in conjunction with the `running_app`
    fixture to provide a complete app with all the typically needed
    fixtures. This fixture sets up the basic functions like db, search,
    and template loader once per modules. The `running_app` fixture is function
    scoped and initializes all the fixtures that should be reset between tests.

    Yields:
        Flask: The Flask application instance.
    """
    current_queues.declare()
    template_loader(app)
    yield app


@pytest.fixture(scope="module")
def app_config(app_config) -> dict:
    """App config fixture for KCWorks.

    Returns:
        dict: Application configuration dictionary.
    """
    for k, v in test_config.items():
        app_config[k] = v

    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Create the app fixture for KCWorks.

    This initializes the basic Flask app which will then be used
    to set up the `app` fixture with initialized services.

    Returns:
        Callable: Function to create the app.
    """
    return _create_app
