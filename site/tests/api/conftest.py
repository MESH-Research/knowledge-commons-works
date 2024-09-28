# ### tests/api/confest.py ###
# API tests goes in tests/api/ folder.
# from pprint import pprint
import pytest

# from invenio_app.factory import create_api

# from pytest_invenio.fixtures import UserFixture, database, db


# @pytest.fixture(scope='module')
# def create_app():
#     return create_api


@pytest.fixture(scope="function")
def headers(running_app):
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/vnd.inveniordm.v1+json",
    }
