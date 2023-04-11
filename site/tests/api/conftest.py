# ### tests/api/confest.py ###
# API tests goes in tests/api/ folder.
import pytest
from invenio_app.factory import create_api

@pytest.fixture(scope='module')
def create_app():
    return create_api
