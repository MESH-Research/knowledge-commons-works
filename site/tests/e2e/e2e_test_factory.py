from flask import url_for
from pprint import pprint
import pytest


def test_sample_e2e():
    assert True


@pytest.mark.skip(reason="Not implemented")
def test_frontpage_e2e(running_app, live_server, browser):
    # pprint(dir(base_client))
    # pprint(dir(base_app))
    running_app.logger.info("test_frontpage_e2e")
    running_app.logger.info(running_app.config.keys())
    response = browser.get(url_for("index", _external=True))
    response = browser.get("/")
    pprint(dir(response))
    assert True
