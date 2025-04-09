# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Factory for E2E tests."""

from pprint import pprint

import pytest
from flask import url_for


@pytest.mark.skip(reason="Not implemented")
def test_frontpage_e2e(running_app, live_server, browser):
    """Test the frontpage of the application using Selenium."""
    # pprint(dir(base_client))
    # pprint(dir(base_app))
    running_app.logger.info("test_frontpage_e2e")
    running_app.logger.info(running_app.config.keys())
    response = browser.get(url_for("index", _external=True))
    response = browser.get("/")
    pprint(dir(response))
    assert True
