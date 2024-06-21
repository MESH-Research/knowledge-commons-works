import json
from pprint import pprint
from pytest_invenio.fixtures import search_clear


def test_draft_creation(running_app, client, client_with_login, minimal_record,
                        headers, search_clear):
    """
    """
    r = client.get("/records", headers=headers)
    pprint(r.json)
    response = client_with_login.post("/records",
                           data=json.dumps(minimal_record), headers=headers)
    pprint('$$$$$$$')
    # pprint(app_config)
    pprint(response.json)
    pprint(response.headers)
    # my_token = response.headers[2][1][10:].split(';')[0]
    # pprint(my_token)
    # pprint(client_with_login.cookie_jar)
    # pprint(dir(appctx.session_interface))
    assert response.status_code == 201


def test_db(client):

    res = client.get('/')
    assert res.json == {
        'message': 'The requested URL was not found on the server. If you '
                   'entered the URL manually please check your spelling and '
                   'try again.',
        'status': 404
    }

    # res2 = client.get('/api/records/jznz9-qhx89')
    # pprint(dir(res2))
    # assert res2 == {}

    assert True



# dir(response from client.get)
# ['__annotations__',
#  '__call__',
#  '__class__',
#  '__delattr__',
#  '__dict__',
#  '__dir__',
#  '__doc__',
#  '__enter__',
#  '__eq__',
#  '__exit__',
#  '__format__',
#  '__ge__',
#  '__getattribute__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__init_subclass__',
#  '__le__',
#  '__lt__',
#  '__module__',
#  '__ne__',
#  '__new__',
#  '__reduce__',
#  '__reduce_ex__',
#  '__repr__',
#  '__setattr__',
#  '__sizeof__',
#  '__str__',
#  '__subclasshook__',
#  '__test__',
#  '__weakref__',
#  '_clean_status',
#  '_compat_tuple',
#  '_ensure_sequence',
#  '_is_range_request_processable',
#  '_on_close',
#  '_process_range_request',
#  '_status',
#  '_status_code',
#  '_wrap_range_response',
#  'accept_ranges',
#  'access_control_allow_credentials',
#  'access_control_allow_headers',
#  'access_control_allow_methods',
#  'access_control_allow_origin',
#  'access_control_expose_headers',
#  'access_control_max_age',
#  'add_etag',
#  'age',
#  'allow',
#  'autocorrect_location_header',
#  'automatically_set_content_length',
#  'cache_control',
#  'calculate_content_length',
#  'call_on_close',
#  'charset',
#  'close',
#  'content_encoding',
#  'content_language',
#  'content_length',
#  'content_location',
#  'content_md5',
#  'content_range',
#  'content_security_policy',
#  'content_security_policy_report_only',
#  'content_type',
#  'cross_origin_embedder_policy',
#  'cross_origin_opener_policy',
#  'data',
#  'date',
#  'default_mimetype',
#  'default_status',
#  'delete_cookie',
#  'direct_passthrough',
#  'expires',
#  'force_type',
#  'freeze',
#  'from_app',
#  'get_app_iter',
#  'get_data',
#  'get_etag',
#  'get_json',
#  'get_wsgi_headers',
#  'get_wsgi_response',
#  'headers',
#  'history',
#  'implicit_sequence_conversion',
#  'is_json',
#  'is_sequence',
#  'is_streamed',
#  'iter_encoded',
#  'json',
#  'json_module',
#  'last_modified',
#  'location',
#  'make_conditional',
#  'make_sequence',
#  'max_cookie_size',
#  'mimetype',
#  'mimetype_params',
#  'request',
#  'response',
#  'retry_after',
#  'set_cookie',
#  'set_data',
#  'set_etag',
#  'status',
#  'status_code',
#  'stream',
#  'text',
#  'vary',
#  'www_authenticate']


# dir(client)
# '__annotations__',
#  '__class__',
#  '__delattr__',
#  '__dict__',
#  '__dir__',
#  '__doc__',
#  '__enter__',
#  '__eq__',
#  '__exit__',
#  '__format__',
#  '__ge__',
#  '__getattribute__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__init_subclass__',
#  '__le__',
#  '__lt__',
#  '__module__',
#  '__ne__',
#  '__new__',
#  '__reduce__',
#  '__reduce_ex__',
#  '__repr__',
#  '__setattr__',
#  '__sizeof__',
#  '__str__',
#  '__subclasshook__',
#  '__weakref__',
#  '_context_stack',
#  '_copy_environ',
#  '_new_contexts',
#  '_request_from_builder_args',
#  'allow_subdomain_redirects',
#  'application',
#  'cookie_jar',
#  'delete',
#  'delete_cookie',
#  'environ_base',
#  'get',
#  'head',
#  'open',
#  'options',
#  'patch',
#  'post',
#  'preserve_context',
#  'put',
#  'resolve_redirect',
#  'response_wrapper',
#  'run_wsgi_app',
#  'session_transaction',
#  'set_cookie',
#  'trace']