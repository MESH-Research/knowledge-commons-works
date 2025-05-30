# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""UI tests for Knowledge Commons Works."""

from pprint import pprint

import pytest


@pytest.mark.skip(reason="Not implemented")
def test_frontpage(running_app, client):
    """Test the frontpage view."""
    response = client.get("/")
    pprint(response.response)
    assert response.status_code == 200
    assert b"Knowledge Commons Repository" in response.data
    assert "Knowledge Commons Repository" in response.text
    assert True


"""
dir(client )
'__annotations__',
 '__call__',
 '__class__',
 '__delattr__',
 '__dict__',
 '__dir__',
 '__doc__',
 '__enter__',
 '__eq__',
 '__exit__',
 '__format__',
 '__ge__',
 '__getattribute__',
 '__gt__',
 '__hash__',
 '__init__',
 '__init_subclass__',
 '__le__',
 '__lt__',
 '__module__',
 '__ne__',
 '__new__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__sizeof__',
 '__str__',
 '__subclasshook__',
 '__test__',
 '__weakref__',
 '_clean_status',
 '_compat_tuple',
 '_ensure_sequence',
 '_is_range_request_processable',
 '_on_close',
 '_process_range_request',
 '_status',
 '_status_code',
 '_wrap_range_response',
 'accept_ranges',
 'access_control_allow_credentials',
 'access_control_allow_headers',
 'access_control_allow_methods',
 'access_control_allow_origin',
 'access_control_expose_headers',
 'access_control_max_age',
 'add_etag',
 'age',
 'allow',
 'autocorrect_location_header',
 'automatically_set_content_length',
 'cache_control',
 'calculate_content_length',
 'call_on_close',
 'charset',
 'close',
 'content_encoding',
 'content_language',
 'content_length',
 'content_location',
 'content_md5',
 'content_range',
 'content_security_policy',
 'content_security_policy_report_only',
 'content_type',
 'cross_origin_embedder_policy',
 'cross_origin_opener_policy',
 'data', # bytes response
 'date',
 'default_mimetype',
 'default_status',
 'delete_cookie',
 'direct_passthrough',
 'expires',
 'force_type',
 'freeze',
 'from_app',
 'get_app_iter',
 'get_data',
 'get_etag',
 'get_json',
 'get_wsgi_headers',
 'get_wsgi_response',
 'headers',
 'history',
 'implicit_sequence_conversion',
 'is_json',
 'is_sequence',
 'is_streamed',
 'iter_encoded',
 'json',
 'json_module',
 'last_modified',
 'location',
 'make_conditional',
 'make_sequence',
 'max_cookie_size',
 'mimetype',
 'mimetype_params',
 'request',
 'response',
 'retry_after',
 'set_cookie',
 'set_data',
 'set_etag',
 'status',
 'status_code',
 'stream',
 'text', # string response
 'vary',
 'www_authenticate']
"""
