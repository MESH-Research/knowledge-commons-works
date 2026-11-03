# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

import os

from kcworks.api_helpers import (
    choose_record_publish_method,
    format_commons_search_collection_payload,
    format_commons_search_payload,
    record_commons_search_collection_recid,
    record_commons_search_recid,
    record_publish_url_factory,
)
from kcworks.config.site_urls import KC_SEARCH_URL_DOCS

"""Configuration variables related to provisioning external services."""

# we are only indexing published records, not drafts
REMOTE_API_PROVISIONER_EVENTS = {
    "rdm_record": {
        KC_SEARCH_URL_DOCS: {
            "publish": {
                "http_method": choose_record_publish_method,
                "with_record_owner": True,
                "payload": format_commons_search_payload,
                "callback": record_commons_search_recid,
                "url_factory": record_publish_url_factory,
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
                "timing_field": "kcr:commons_search_updated",
            },
            "delete_record": {
                "http_method": "DELETE",
                "with_record_owner": True,
                "url_factory": lambda identity, *args, **kwargs: (
                    f"{KC_SEARCH_URL_DOCS}/"
                    f"{kwargs['record']['custom_fields'].get('kcr:commons_search_recid', '')}"  # noqa: E501
                ),
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
            "delete": {
                "http_method": "DELETE",
                "with_record_owner": True,
                "url_factory": lambda identity, *args, **kwargs: (
                    f"{KC_SEARCH_URL_DOCS}/"
                    f"{kwargs['record']['custom_fields'].get('kcr:commons_search_recid', '')}"  # noqa: E501
                ),
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
            "restore_record": {
                "http_method": "POST",
                "with_record_owner": True,
                "payload": format_commons_search_payload,
                "callback": record_commons_search_recid,
                "url_factory": record_publish_url_factory,
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
        },
    },
    "community": {
        KC_SEARCH_URL_DOCS: {
            "create": {
                "http_method": "POST",
                "with_record_owner": False,
                "payload": format_commons_search_collection_payload,
                "callback": record_commons_search_collection_recid,
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
            "update": {
                "http_method": "PUT",
                "with_record_owner": False,
                "payload": format_commons_search_collection_payload,
                # FIXME: send POST if community hasn't been indexed yet
                "url_factory": lambda identity, **kwargs: (
                    f"{KC_SEARCH_URL_DOCS}/"
                    f"{kwargs['record']['custom_fields'].get('kcr:commons_search_recid', '')}"  # noqa: E501
                ),
                "callback": record_commons_search_collection_recid,
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
                "timing_field": "kcr:commons_search_updated",
            },
            "delete": {  # delete_community method uses delete components
                "http_method": "DELETE",
                "url_factory": lambda identity, *args, **kwargs: (
                    f"{KC_SEARCH_URL_DOCS}/"
                    f"{kwargs['record']['custom_fields'].get('kcr:commons_search_recid', '')}"  # noqa: E501
                ),
                "callback": lambda *args, **kwargs: None,  # to expose testing output
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
            "restore": {  # restore_community method uses restore components
                "http_method": "POST",
                "with_record_owner": True,
                "payload": format_commons_search_collection_payload,
                "callback": record_commons_search_collection_recid,
                "auth_token": os.getenv("COMMONS_SEARCH_API_TOKEN"),
            },
        },
    },
}
