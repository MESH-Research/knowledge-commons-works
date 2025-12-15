# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for API tests."""

import pytest

# @pytest.fixture(scope="module")
# def create_app():
#     return create_api


@pytest.fixture(scope="function")
def headers():
    """Default headers for making requests.

    Returns:
        dict: Dictionary of default headers.
    """
    return {
        "content-type": "application/json",
        # "accept": "application/vnd.inveniordm.v1+json",
    }


@pytest.fixture(scope="function")
def headers_same_origin(headers, app_config):
    """Headers with Referrer-Policy and Referer set to the same origin.

    Returns:
        dict: Dictionary of headers with same-origin policy.
    """
    headers["Referrer-Policy"] = "origin"
    headers["Referer"] = f"{app_config['SITE_UI_URL']}/"
    return headers
