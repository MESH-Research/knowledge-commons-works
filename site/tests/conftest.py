from collections import namedtuple
import os
from pathlib import Path
from invenio_app.factory import create_app as create_ui_api
from invenio_queues import current_queues

from .fixtures.identifiers import test_config_identifiers
from .fixtures.custom_fields import test_config_fields
from .fixtures.stats import test_config_stats
from .fixtures.saml import test_config_saml

# from pytest_invenio.fixtures import base_client, db, UserFixture
import pytest
import importlib

var = "invenio_config"
package = importlib.import_module(var)
config = {k: v for k, v in package.__dict__.items()}

pytest_plugins = [
    "celery.contrib.pytest",
    "tests.fixtures.communities",
    "tests.fixtures.custom_fields",
    "tests.fixtures.records",
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
    "tests.helpers.sample_records.basic",
]


def _(x):
    """Identity function for string extraction."""
    return x


test_config = {**config}

test_config = {
    **test_config_identifiers,
    **test_config_fields,
    **test_config_stats,
    **test_config_saml,
    "SQLALCHEMY_DATABASE_URI": (
        "postgresql+psycopg2://kcworks:kcworks@localhost:5432/kcworks"
    ),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SEARCH_INDEX_PREFIX": "",
    "POSTGRES_USER": "kcworks",
    "POSTGRES_PASSWORD": "kcworks",
    "POSTGRES_DB": "kcworks",
    "INVENIO_WTF_CSRF_ENABLED": False,
    "INVENIO_WTF_CSRF_METHODS": [],
    "APP_DEFAULT_SECURE_HEADERS": {
        "content_security_policy": {"default-src": []},
        "force_https": False,
    },
    # "BROKER_URL": "amqp://guest:guest@localhost:5672//",
    "CELERY_CACHE_BACKEND": "memory",
    "CELERY_RESULT_BACKEND": "cache",
    "CELERY_TASK_ALWAYS_EAGER": True,
    "CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS": True,
    #  'DEBUG_TB_ENABLED': False,
    "INVENIO_INSTANCE_PATH": "/opt/invenio/var/instance",
    "MAIL_SUPPRESS_SEND": True,
    #  'OAUTH2_CACHE_TYPE': 'simple',
    #  'OAUTHLIB_INSECURE_TRANSPORT': True,
    "RATELIMIT_ENABLED": False,
    "SECRET_KEY": "test-secret-key",
    "SECURITY_PASSWORD_SALT": "test-secret-key",
    "TESTING": True,
}

parent_path = Path(__file__).parent
log_folder_path = parent_path / "test_logs"
log_file_path = log_folder_path / "invenio.log"
if not log_file_path.exists():
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_path.touch()

test_config["FLASK_DEBUG"] = True
test_config["LOGGING_FS_LEVEL"] = "DEBUG"
test_config["INVENIO_LOGGING_FS_LEVEL"] = "DEBUG"
test_config["LOGGING_FS_LOGFILE"] = str(log_file_path)

# enable DataCite DOI provider
test_config["DATACITE_ENABLED"] = True
test_config["DATACITE_USERNAME"] = "INVALID"
test_config["DATACITE_PASSWORD"] = "INVALID"
test_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
test_config["DATACITE_PREFIX"] = "10.17613"
test_config["DATACITE_TEST_MODE"] = True
# ...but fake it

test_config["SITE_API_URL"] = os.environ.get(
    "INVENIO_SITE_API_URL", "https://127.0.0.1:5000"
)
test_config["SITE_UI_URL"] = os.environ.get(
    "INVENIO_SITE_UI_URL", "https://127.0.0.1:5000"
)


# @pytest.fixture(scope="module")
# def extra_entry_points() -> dict:
#     return {
#         # 'invenio_db.models': [
#         #     'mock_module = mock_module.models',
#         # ]
#     }


# This is a namedtuple that holds all the fixtures we're likely to need
# in a single test.
RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "superuser_identity",
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
    superuser_identity,
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
        superuser_identity,
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
):
    """This fixture provides an app with the typically needed fixtures."""
    current_queues.declare()
    yield app


@pytest.fixture(scope="module")
def app_config(app_config) -> dict:
    for k, v in test_config.items():
        app_config[k] = v
    return app_config


@pytest.fixture(scope="module")
def create_app():
    return create_ui_api
