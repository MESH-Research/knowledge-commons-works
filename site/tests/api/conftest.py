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
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        # "accept": "application/vnd.inveniordm.v1+json",
    }


@pytest.fixture(scope="function")
def headers_same_origin(headers, app_config):
    """Headers with Referrer-Policy and Referer set to the same origin."""
    headers["Referrer-Policy"] = "origin"
    headers["Referer"] = f"{app_config['SITE_UI_URL']}/"
    return headers
