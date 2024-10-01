import json
import pytest
from pprint import pprint
import re

import arrow

links_template = {
    "self": "{0}/records/{1}/draft",
    "self_html": "{0}/uploads/{1}",
    "self_iiif_manifest": "{0}/iiif/draft:{1}/manifest",
    "self_iiif_sequence": "{0}/iiif/draft:{1}/sequence/default",
    "files": "{0}/records/{1}/draft/files",
    "media_files": "{0}/records/{1}/draft/media-files",
    "archive": "{0}/records/{1}/draft/files-archive",
    "archive_media": "{0}/records/{1}/draft/media-files-archive",
    "record": "{0}/records/{1}",
    "record_html": "{0}/records/{1}",
    "publish": "{0}/records/{1}/draft/actions/publish",
    "review": "{0}/records/{1}/draft/review",
    "versions": "{0}/records/{1}/versions",
    "access_links": "{0}/records/{1}/access/links",
    "access_grants": "{0}/records/{1}/access/grants",
    "access_users": "{0}/records/{1}/access/users",
    "access_groups": "{0}/records/{1}/access/groups",
    "access_request": "{0}/records/{1}/access/request",
    "access": "{0}/records/{1}/access",
    "reserve_doi": "{0}/records/{1}/draft/pids/doi",
    "communities": "{0}/records/{1}/communities",
    "communities-suggestions": "{0}/records/{1}/communities-suggestions",
    "requests": "{0}/records/{1}/requests",
}


def test_draft_creation(
    running_app,
    user_factory,
    client_with_login,
    minimal_record,
    headers,
    search_clear,
):
    """Test that a user can create a draft record."""
    app = running_app.app

    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
    )
    user = u.user
    print(user)
    # identity = u.identity
    # print(identity)
    token = u.allowed_token
    print(token)

    with app.test_client() as client:
        logged_in_client, _ = client_with_login(client, user)
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/api/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        pprint("$$$$$$$")
        app.logger.warning(response.json)
        pprint(response.json)
        pprint(response.headers)
        assert response.status_code == 201

        actual_draft = response.json
        actual_draft_id = actual_draft["id"]

        # ensure the id is in the correct format
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual_draft_id)
        # ensure the created and updated dates are valid ISO-8601
        assert (
            arrow.get(actual_draft["created"]).format(
                "YYYY-MM-DDTHH:mm:ss.SSSSSS+00:00"
            )
            == actual_draft["created"]
        )
        assert (
            arrow.get(actual_draft["updated"]).format(
                "YYYY-MM-DDTHH:mm:ss.SSSSSS+00:00"
            )
            == actual_draft["updated"]
        )

        test_url = app.config["SITE_UI_URL"]
        assert actual_draft["links"] == {
            k: v.format(test_url, actual_draft_id)
            for k, v in links_template.items()
        }

        # assert actual_draft['revision_id'] == 5  # TODO: Why is this 5?

        actual_parent_id = actual_draft["parent"]["id"]
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual_parent_id)
        assert actual_draft["parent"]["access"] == {
            "grants": [],
            "owned_by": {"user": "1"},
            "links": [],
            "settings": {
                "allow_user_requests": False,
                "allow_guest_requests": False,
                "accept_conditions_text": None,
                "secret_link_expiration": 0,
            },
        }
        assert actual_draft["parent"]["communities"] == {}
        assert actual_draft["parent"]["pids"] == {}
        assert actual_draft["versions"] == {
            "is_latest": False,
            "is_latest_draft": True,
            "index": 1,
        }

        assert not actual_draft["is_published"]
        assert actual_draft["is_draft"]
        assert (
            arrow.get(actual_draft["expires_at"]).format(
                "YYYY-MM-DD HH:mm:ss.SSSSSS"
            )
            == actual_draft["expires_at"]
        )
        assert actual_draft["pids"] == {}
        assert actual_draft["metadata"]["resource_type"] == {
            "id": "image-photograph",
            "title": {"en": "Photo"},
        }
        assert actual_draft["metadata"]["creators"] == [
            {
                "person_or_org": {
                    "type": "personal",
                    "name": "Brown, Troy",
                    "given_name": "Troy",
                    "family_name": "Brown",
                }
            },
            {"person_or_org": {"type": "organizational", "name": "Troy Inc."}},
        ]
        assert actual_draft["metadata"]["title"] == "A Romans story"
        assert actual_draft["metadata"]["publisher"] == "Acme Inc"
        assert (
            arrow.get(actual_draft["metadata"]["publication_date"]).format(
                "YYYY-MM-DD"
            )
            == "2020-06-01"
        )
        assert actual_draft["custom_fields"] == {}
        assert actual_draft["access"] == {
            "record": "public",
            "files": "public",
            "embargo": {"active": False, "reason": None},
            "status": "metadata-only",
        }
        assert actual_draft["files"] == {
            "enabled": False,
            "order": [],
            "count": 0,
            "total_bytes": 0,
            "entries": {},
        }
        assert actual_draft["media_files"] == {
            "enabled": False,
            "order": [],
            "count": 0,
            "total_bytes": 0,
            "entries": {},
        }
        assert actual_draft["status"] == "draft"
        publication_date = arrow.get(
            actual_draft["metadata"]["publication_date"]
        )
        assert actual_draft["ui"][
            "publication_date_l10n_medium"
        ] == publication_date.format("MMM D, YYYY")
        assert actual_draft["ui"][
            "publication_date_l10n_long"
        ] == publication_date.format("MMMM D, YYYY")
        created_date = arrow.get(actual_draft["created"])
        assert actual_draft["ui"][
            "created_date_l10n_long"
        ] == created_date.format("MMMM D, YYYY")
        updated_date = arrow.get(actual_draft["updated"])
        assert actual_draft["ui"][
            "updated_date_l10n_long"
        ] == updated_date.format("MMMM D, YYYY")
        assert actual_draft["ui"]["resource_type"] == {
            "id": "image-photograph",
            "title_l10n": "Photo",
        }
        assert actual_draft["ui"]["custom_fields"] == {}
        assert actual_draft["ui"]["access_status"] == {
            "id": "metadata-only",
            "title_l10n": "Metadata-only",
            "description_l10n": "No files are available for this record.",
            "icon": "tag",
            "embargo_date_l10n": None,
            "message_class": "",
        }
        assert actual_draft["ui"]["creators"] == {
            "affiliations": [],
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "name": "Brown, Troy",
                        "given_name": "Troy",
                        "family_name": "Brown",
                    }
                },
                {
                    "person_or_org": {
                        "type": "organizational",
                        "name": "Troy Inc.",
                    }
                },
            ],
        }
        assert actual_draft["ui"]["version"] == "v1"
        assert actual_draft["ui"]["is_draft"]


@pytest.mark.skip(reason="Not implemented")
def test_db(running_app, client):

    res = client.get("/api/records/")
    assert res.json == {
        "message": "The requested URL was not found on the server. If you "
        "entered the URL manually please check your spelling and "
        "try again.",
        "status": 404,
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
