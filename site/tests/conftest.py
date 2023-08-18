from collections import namedtuple
from flask_security import login_user, logout_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access, system_identity
from invenio_accounts.testutils import login_user_via_session
from invenio_administration.permissions import administration_access_action
from invenio_app.factory import create_ui, create_app
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from pprint import pprint
from pytest_invenio.fixtures import base_client, db, UserFixture
import pytest
# pytest_invenio provides these fixtures (among others):
#   pytest_invenio.fixtures.app(base_app, search, database)
#   pytest_invenio.fixtures.app_config(db_uri, broker_uri, celery_config_ext)
#   pytest_invenio.fixtures.appctx(base_app)
#   pytest_invenio.fixtures.base_app(create_app, app_config, request, default_handler)
#   pytest_invenio.fixtures.base_client(base_app)
#   pytest_invenio.fixtures.browser(request)
#   pytest_invenio.fixtures.cli_runner(base_app)
#   pytest_invenio.fixtures.db(database)
#   pytest_invenio.fixtures.default_handler()
#   pytest_invenio.fixtures.entry_points(extra_entry_points

test_config = {

    'SQLALCHEMY_DATABASE_URI': "postgresql+psycopg2://knowledge-commons-repository:knowledge-commons-repository@localhost/knowledge-commons-repository-test",
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'INVENIO_WTF_CSRF_ENABLED': False,
    'INVENIO_WTF_CSRF_METHODS': [],
    'THEME_FRONTPAGE_TITLE': "Knowledge Commons Repository",
    'APP_DEFAULT_SECURE_HEADERS':
        {'content_security_policy': {'default-src': []},
                                     'force_https': False},
    'APP_THEME': ['semantic-ui'],
    'BROKER_URL': 'amqp://guest:guest@localhost:5672//',
    'CELERY_CACHE_BACKEND': 'memory',
    'CELERY_RESULT_BACKEND': 'cache',
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS': True,
#  'DEBUG_TB_ENABLED': False,
    # 'INVENIO_INSTANCE_PATH': '/opt/invenio/var/instance',
#  'MAIL_SUPPRESS_SEND': True,
#  'OAUTH2_CACHE_TYPE': 'simple',
#  'OAUTHLIB_INSECURE_TRANSPORT': True,
    'RATELIMIT_ENABLED': False,
    'SECRET_KEY': 'test-secret-key',
    'SECURITY_PASSWORD_SALT': 'test-secret-key',
    'TESTING': True,
}
#  'THEME_ICONS': {'bootstrap3': {'*': 'fa fa-{} fa-fw',
#                                 'codepen': 'fa fa-codepen fa-fw',
#                                 'cogs': 'fa fa-cogs fa-fw',
#                                 'key': 'fa fa-key fa-fw',
#                                 'link': 'fa fa-link fa-fw',
#                                 'shield': 'fa fa-shield fa-fw',
#                                 'user': 'fa fa-user fa-fw'},
#                  'semantic-ui': {'*': '{} icon',
#                                  'codepen': 'codepen icon',
#                                  'cogs': 'cogs icon',
#                                  'key': 'key icon',
#                                  'link': 'linkify icon',
#                                  'shield': 'shield alternate icon',
#                                  'user': 'user icon'}},

# ### tests/conftest.py ###
# Common application configuration goes here
@pytest.fixture(scope='module')
def app_config(app_config) -> dict:
    # app_config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///testing.db"
    for k, v in test_config.items():
        app_config[k] = v
    # print('*******')
    # pprint(app_config)
    return app_config

@pytest.fixture(scope="module")
def extra_entry_points() -> dict:
    return {
        # 'invenio_db.models': [
        #     'mock_module = mock_module.models',
        # ]
    }

@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )


    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab



# *** db fixture built into pytest-invenio ***
# *** but needed to fix call to _make_scoped_session()??? ***
# @pytest.fixture(scope="function")
# def db(database):
#     """Creates a new database session for a test.

#     Scope: function

#     You must use this fixture if your test connects to the database. The
#     fixture will set a save point and rollback all changes performed during
#     the test (this is much faster than recreating the entire database).
#     """
#     import sqlalchemy as sa

#     connection = database.engine.connect()
#     transaction = connection.begin()

#     options = dict(bind=connection, binds={})
#     session = database._make_scoped_session(options=options)

#     session.begin_nested()

#     # `session` is actually a scoped_session. For the `after_transaction_end`
#     # event, we need a session instance to listen for, hence the `session()`
#     # call.
#     @sa.event.listens_for(session(), "after_transaction_end")
#     def restart_savepoint(sess, trans):
#         if trans.nested and not trans._parent.nested:
#             session.expire_all()
#             session.begin_nested()

#     old_session = database.session
#     database.session = session

#     yield database

#     session.remove()
#     transaction.rollback()
#     connection.close()
#     database.session = old_session
# dir(database)
# ['Model',
#  'Query',
#  'Table',
#  '__class__',
#  '__delattr__',
#  '__dict__',
#  '__dir__',
#  '__doc__',
#  '__eq__',
#  '__format__',
#  '__ge__',
#  '__getattr__',
#  '__getattribute__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__init_subclass__',
#  '__le__',
#  '__lt__',
#  '__module__',
#  '__ne__',
#  '__new__',
#  '__reduce__',
#  '__reduce_ex__',
#  '__repr__',
#  '__setattr__',
#  '__sizeof__',
#  '__str__',
#  '__subclasshook__',
#  '__weakref__',
#  '_add_models_to_shell',
#  '_app_engines',
#  '_apply_driver_defaults',
#  '_call_for_binds',
#  '_engine_options',
#  '_make_declarative_base',
#  '_make_engine',
#  '_make_metadata',
#  '_make_scoped_session',
#  '_make_session_factory',
#  '_make_table_class',
#  '_relation',
#  '_set_rel_query',
#  '_teardown_commit',
#  '_teardown_session',
#  '_user_resources_hooks_registered',
#  'apply_driver_hacks',
#  'create_all',
#  'drop_all',
#  'dynamic_loader',
#  'engine',
#  'engines',
#  'first_or_404',
#  'get_binds',
#  'get_engine',
#  'get_or_404',
#  'get_tables_for_bind',
#  'init_app',
#  'metadata',
#  'metadatas',
#  'one_or_404',
#  'paginate',
#  'reflect',
#  'relationship',
#  'session']


# @pytest.fixture()
# def users(UserFixture, app, db):
#     user1 = UserFixture(
#         email="scottia4@msu.edu",
#         password="password",
#     )
#     user1.create(app, db)
#     user2 = UserFixture(
#         email="info@invenio.org",
#         password="password",
#     )
#     user2.create(app, db)
#     return [user1, user2]

@pytest.fixture()
def users(UserFixture, app, db) -> list:
    """Create example user."""
    # user1 = UserFixture(
    #     email="scottia4@msu.edu",
    #     password="password"
    # )
    # user1.create(app, db)
    # user2 = UserFixture(
    #     email="scottianw@gmail.com",
    #     password="password"
    # )
    # user2.create(app, db)
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="ser-testalot@inveniosoftware.org",
            password=hash_password("beetlesmasher"),
            active=True,
        )

    db.session.commit()
    return [user1, user2]

# dir(user)
# ['__class__',
#  '__delattr__',
#  '__dict__',
#  '__dir__',
#  '__doc__',
#  '__eq__',
#  '__format__',
#  '__ge__',
#  '__getattribute__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__init_subclass__',
#  '__le__',
#  '__lt__',
#  '__module__',
#  '__ne__',
#  '__new__',
#  '__reduce__',
#  '__reduce_ex__',
#  '__repr__',
#  '__setattr__',
#  '__sizeof__',
#  '__str__',
#  '__subclasshook__',
#  '__weakref__',
#  '_active',
#  '_app',
#  '_client',
#  '_confirmed',
#  '_email',
#  '_identity',
#  '_login',
#  '_logout',
#  '_password',
#  '_preferences',
#  '_user',
#  '_user_profile',
#  '_username',
#  'api_login',
#  'api_logout',
#  'app_login',
#  'app_logout',
#  'create',
#  'email',
#  'get_id',
#  'id',
#  'identity',
#  'is_active',
#  'login',
#  'logout',
#  'password',
#  'refresh',
#  'user',
#  'username']

@pytest.fixture()
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="administration-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=administration_access_action, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "administration-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture()
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity



@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    # user = users[0].user
    # pprint('^^^^^^^')
    # pprint(user.__class__())
    # pprint(dir(user))
    login_user(user)
    login_user_via_session(client, email=user.email)
    return client


RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "superuser_identity",
        "location",
        "cache",
        "resource_type_v",
        # "subject_v",
        # "languages_v",
        # "affiliations_v",
        # "title_type_v",
        # "description_type_v",
        # "date_type_v",
        # "contributors_role_v",
        # "relation_type_v",
        # "licenses_v",
        # "funders_v",
        # "awards_v",
    ],
)


@pytest.fixture
def running_app(
    app,
    superuser_identity,
    location,
    cache,
    resource_type_v,
    # subject_v,
    # languages_v,
    # affiliations_v,
    # title_type_v,
    # description_type_v,
    # date_type_v,
    # contributors_role_v,
    # relation_type_v,
    # licenses_v,
    # funders_v,
    # awards_v,
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
        resource_type_v,
        # subject_v,
        # languages_v,
        # affiliations_v,
        # title_type_v,
        # description_type_v,
        # date_type_v,
        # contributors_role_v,
        # relation_type_v,
        # licenses_v,
        # funders_v,
        # awards_v,
    )
