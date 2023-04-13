from invenio_app.factory import create_ui
from pytest_invenio.fixtures import base_client
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

# ### tests/conftest.py ###
# Common application configuration goes here
@pytest.fixture(scope='module')
def app_config(app_config):
    app_config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://knowledge-commons-repository:knowledge-commons-repository@db/knowledge-commons-repository"
    app_config['INVENIO_INSTANCE_PATH'] = "/opt/invenio/var/instance"
    return app_config
