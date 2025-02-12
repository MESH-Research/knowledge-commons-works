from collections import namedtuple
import os
from pathlib import Path
import importlib
from invenio_app.factory import create_app as create_ui_api
from invenio_queues import current_queues
from invenio_search.proxies import current_search_client
import jinja2
from marshmallow import Schema, fields
import pytest

from .fixtures.identifiers import test_config_identifiers
from .fixtures.custom_fields import test_config_fields
from .fixtures.stats import test_config_stats
from .fixtures.saml import test_config_saml
from .fixtures.frontend import MockManifestLoader
from kcworks import invenio_config

var = "invenio_config"
package = importlib.import_module(var)
# This code is not importing variables from ./invenio_config.py because:
# 1. It's using importlib to dynamically import a module named "invenio_config"
# 2. It's creating a dictionary from all attributes of that module
# 3. The local ./invenio_config.py file is not being referenced

# Or if we want to create a dictionary of all variables:

config = {k: v for k, v in invenio_config.__dict__.items() if not k.startswith("_")}

pytest_plugins = (
    "celery.contrib.pytest",
    "tests.fixtures.files",
    "tests.fixtures.communities",
    "tests.fixtures.custom_fields",
    "tests.fixtures.records",
    "tests.fixtures.roles",
    "tests.fixtures.search_provisioning",
    "tests.fixtures.stats",
    "tests.fixtures.users",
    "tests.fixtures.vocabularies.affiliations",
    "tests.fixtures.vocabularies.community_types",
    "tests.fixtures.vocabularies.date_types",
    "tests.fixtures.vocabularies.descriptions",
    "tests.fixtures.vocabularies.languages",
    "tests.fixtures.vocabularies.licenses",
    "tests.fixtures.vocabularies.resource_types",
    "tests.fixtures.vocabularies.roles",
    "tests.fixtures.vocabularies.subjects",
)


def _(x):
    """Identity function for string extraction."""
    return x


test_config = {
    **config,
    **test_config_identifiers,
    **test_config_fields,
    **test_config_stats,
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
    "APP_THEME": "semantic-ui",
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
    "RATELIMIT_ENABLED": False,
    "SECRET_KEY": "test-secret-key",
    "SECURITY_PASSWORD_SALT": "test-secret-key",
    "WEBPACKEXT_MANIFEST_LOADER": MockManifestLoader,
    "TESTING": True,
    "DEBUG": True,
}

parent_path = Path(__file__).parent
log_folder_path = parent_path / "test_logs"
log_file_path = log_folder_path / "invenio.log"
if not log_file_path.exists():
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_path.touch()

test_config["LOGGING_FS_LEVEL"] = "DEBUG"
test_config["LOGGING_FS_LOGFILE"] = str(log_file_path)
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


class CustomUserProfileSchema(Schema):
    """The default user profile schema."""

    full_name = fields.String()
    affiliations = fields.String()
    name_parts = fields.String()
    identifier_email = fields.String()
    identifier_orcid = fields.String()
    identifier_kc_username = fields.String()
    unread_notifications = fields.String()


test_config["ACCOUNTS_USER_PROFILE_SCHEMA"] = CustomUserProfileSchema()

# @pytest.fixture(scope="module")

# @pytest.fixture(scope="module")
# def extra_entry_points() -> dict:
#     return {
#         # 'invenio_db.models': [
#         #     'mock_module = mock_module.models',
#         # ]
#     }


@pytest.fixture(scope="session")
def celery_config(celery_config):
    celery_config["logfile"] = str(log_folder_path / "celery.log")
    celery_config["loglevel"] = "DEBUG"
    celery_config["task_always_eager"] = True
    celery_config["cache_backend"] = "memory"
    celery_config["result_backend"] = "cache"
    celery_config["task_eager_propagates_exceptions"] = True

    return celery_config


@pytest.fixture(scope="session")
def celery_enable_logging():
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


# This is a namedtuple that holds all the fixtures we're likely to need
# in a single test.
RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "location",
        "cache",
        "affiliations_v",
        # "awards_v",
        "community_type_v",
        "contributors_role_v",
        "creators_role_v",
        "date_type_v",
        "description_type_v",
        # "funders_v",
        "language_v",
        "licenses_v",
        # "relation_type_v",
        "resource_type_v",
        "subject_v",
        # "title_type_v",
        "create_communities_custom_fields",
        "create_records_custom_fields",
    ],
)


# This fixture allows us to pass each test a list of commonly used fixtures
# with a single name.
@pytest.fixture(scope="function")
def running_app(
    app,
    location,
    cache,
    affiliations_v,
    # awards_v,
    community_type_v,
    contributors_role_v,
    creators_role_v,
    date_type_v,
    description_type_v,
    # funders_v,
    language_v,
    licenses_v,
    # relation_type_v,
    resource_type_v,
    subject_v,
    # title_type_v,
    create_communities_custom_fields,
    create_records_custom_fields,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(
        app,
        location,
        cache,
        affiliations_v,
        # awards_v,
        community_type_v,
        contributors_role_v,
        creators_role_v,
        date_type_v,
        description_type_v,
        # funders_v,
        language_v,
        licenses_v,
        # relation_type_v,
        resource_type_v,
        subject_v,
        # title_type_v,
        create_communities_custom_fields,
        create_records_custom_fields,
    )


# @pytest.fixture(scope="function")
# def search_clear(search_clear):
#     """Clear search indices after test finishes (function scope)."""
#     #     # current_search_client.indices.delete(index="*")
#     #     # current_search_client.indices.delete_template("*")
#     #     # list(current_search.create())
#     #     # list(current_search.put_templates())
#     yield search_clear

#     from invenio_vocabularies.records.api import Vocabulary

#     Vocabulary.index.refresh()
#     # current_search_client.indices.delete(index="*")

#     # current_search_client.indices.delete_template("*")


@pytest.fixture(scope="module")
def template_loader():
    """Fixture providing overloaded and custom templates to test app."""

    def load_tempates(app):
        site_path = (
            Path(__file__).parent.parent / "kcworks" / "templates" / "semantic-ui"
        )
        root_path = Path(__file__).parent.parent.parent / "templates"
        for path in (
            site_path,
            root_path,
        ):
            assert path.exists()
        custom_loader = jinja2.ChoiceLoader(
            [
                app.jinja_loader,
                jinja2.FileSystemLoader([str(site_path), str(root_path)]),
            ]
        )
        app.jinja_loader = custom_loader
        app.jinja_env.loader = custom_loader

    return load_tempates


# Here we're setting up the module-scoped app fixture.
@pytest.fixture(scope="module")
def app(
    app,
    app_config,
    database,
    search,
    affiliations_v,
    # awards_v,
    community_type_v,
    contributors_role_v,
    creators_role_v,
    date_type_v,
    description_type_v,
    # funders_v,
    language_v,
    licenses_v,
    # relation_type_v,
    resource_type_v,
    subject_v,
    # title_type_v,
    template_loader,
    admin_roles,
):
    """This fixture provides an app with the typically needed fixtures."""
    current_queues.declare()
    template_loader(app)
    yield app


@pytest.fixture(scope="module")
def app_config(app_config) -> dict:
    for k, v in test_config.items():
        app_config[k] = v
    return app_config


@pytest.fixture(scope="module")
def create_app():
    return create_ui_api
