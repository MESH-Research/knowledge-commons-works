# from pytest_invenio.fixtures import app, app_config, appctx, base_client, base_app
from flask import url_for
from pprint import pprint
import sys

def test_sample():
    assert True

def test_frontpage(base_client, base_app):
    pprint(dir(base_client))
    pprint(dir(base_app))
    # resp = base_client.get('/')
    # print(resp)
    assert True