# from pytest_invenio.fixtures import app, app_config, appctx, base_client, base_app
from flask import url_for
from pprint import pprint
import sys

def test_sample():
    assert True

def test_frontpage(base_client, base_app):
    # pprint(dir(base_client))
    # pprint(dir(base_app))
    response = base_client.get('/')
    pprint(response.response)
    assert response.status_code == 200
    assert b'<span>Hello world</span>' in response.data
    assert True