# from pytest_invenio.fixtures import app, app_config, appctx, base_client, base_app
from flask import url_for
from pprint import pprint
import sys

def test_sample_e2e():
    assert True

def test_frontpage_e2e(live_server, browser):
    # pprint(dir(base_client))
    # pprint(dir(base_app))
    response = browser.get(url_for('index', _external=True))
    response = browser.get('/')
    pprint(dir(response))
    assert True

