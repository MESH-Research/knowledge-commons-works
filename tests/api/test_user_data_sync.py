# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the user data sync.

These tests are designed to test the user data sync between the KC IDP and
the Invenio app.


"""
import json
import os

import pytest
import requests
from flask_login import login_user
from invenio_accounts.profiles import UserProfileDict
from invenio_accounts.proxies import current_accounts


def test_user_data_kc_endpoint():
    """Test that the production kc endpoint returns the correct data.

    The focus here is on the json schema being returned
    """
    protocol = os.environ.get("INVENIO_COMMONS_API_REQUEST_PROTOCOL", "https")
    base_url = f"{protocol}://hcommons.org/wp-json/commons/v1/users"
    url = f"{base_url}/gihctester"
    token = os.environ.get("COMMONS_API_TOKEN_PROD")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    actual_resp = response.json()
    assert actual_resp["username"] == "gihctester"
    assert actual_resp["email"] == "ghosthc@lblyoehp.mailosaur.net"
    assert actual_resp["name"] == "Ghost Hc"
    assert actual_resp["first_name"] == "Ghost"
    assert actual_resp["last_name"] == "Hc"
    assert actual_resp["institutional_affiliation"] == ""
    for g in actual_resp["groups"]:
        assert list(g.keys()) == ["id", "name", "role"]
        assert isinstance(g["id"], int)
        if g["name"]:
            assert isinstance(g["name"], str)
    # TODO: add orcid to the api call
    # assert actual_resp["orcid"] == "0000-0000-0000-0000"


@pytest.mark.skip(reason="Not implemented")
def test_group_data_kc_endpoint():
    """Test that the production kc endpoint returns the correct data.

    The focus here is on the json schema being returned
    """
    raise NotImplementedError


def test_user_data_sync_on_login(
    running_app,
    db,
    user_factory,
    user1_data,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test that the user data is synced when a user logs in.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.

    Also tests that the api call does *not* happen for simple programmatic
    user creation. It only happens when the user logs in.
    """
    # Mock additional user data from the remote service
    # api response
    new_data_payload = {k: v for k, v in user1_data.items() if k != "saml_id"}
    new_data_payload["username"] = user1_data["saml_id"]

    # Create a user
    # The user is created with a saml auth record because saml_src
    # and saml_id are supplied.
    u = user_factory(
        email=user1_data["email"],
        saml_src="knowledgeCommons",
        saml_id=user1_data["saml_id"],
        new_remote_data=new_data_payload,
    )

    assert not u.mock_adapter.called
    assert u.mock_adapter.call_count == 0
    login_user(u.user)
    assert u.mock_adapter.called
    assert u.mock_adapter.call_count == 1

    assert u.user.email == user1_data["email"]
    profile: UserProfileDict = u.user.user_profile
    assert profile.get("full_name") == user1_data["name"]
    assert (
        profile.get("affiliations") == user1_data["institutional_affiliation"]
    )  # noqa: E501
    assert profile.get("identifier_orcid") == user1_data["orcid"]
    assert profile.get("identifier_kc_username") == user1_data["saml_id"]
    assert json.loads(profile.get("name_parts")) == {
        "first": user1_data["first_name"],
        "last": user1_data["last_name"],
    }

    merged_user = db.session.merge(u.user)

    # Check that the user is a member of the linked communities
    assert sorted([r.name for r in merged_user.roles]) == sorted(
        [
            "knowledgeCommons---12345|admin",
            "knowledgeCommons---67891|member",
        ]
    )


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_login_no_remote_data(running_app):
    """Test that the remote api call does not happen for local logins.

    We want to make sure that the user data sync does not create errors when
    logging someone in who doesn't have an account on the remote service.

    """
    pass


def test_user_data_sync_on_webhook(
    running_app,
    db,
    user_factory,
    user1_data,
    client,
    requests_mock,
    headers,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test that the user data is synced when a user logs in.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.

    Also tests that the api call does *not* happen for simple programmatic
    user creation. It only happens when the user logs in.
    """
    app = running_app.app
    # Create a user
    # The user is created with a saml auth record because saml_src
    u = user_factory(
        email=user1_data["email"],
        saml_src="knowledgeCommons",
        saml_id=user1_data["saml_id"],
        new_remote_data={},
        token=True,
        admin=True,
    )
    token = u.allowed_token
    user_id = u.user.id
    assert not u.mock_adapter.called  # no call to the remote api yet
    assert u.mock_adapter.call_count == 0

    # Mock additional user data from the remote service
    # api response
    mock_remote_data = {k: v for k, v in user1_data.items() if k != "saml_id"}
    mock_remote_data["username"] = user1_data["saml_id"]

    # Mock the remote api call.
    protocol = os.environ.get("INVENIO_COMMONS_API_REQUEST_PROTOCOL", "https")
    base_url = f"{protocol}://hcommons-dev.org/wp-json/commons/v1/users"
    remote_url = f"{base_url}/{user1_data['saml_id']}"
    mock_adapter = requests_mock.get(
        remote_url,
        json=mock_remote_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Ping the webhook endpoint (no data is sent)
    response = client.get(
        f"{app.config['SITE_API_URL']}/webhooks/user_data_update",
    )
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "message": "Webhook receiver is active",
        "status": 200,
    }
    assert not mock_adapter.called
    assert mock_adapter.call_count == 0

    # Signal the webhook endpoint for update (data is sent)
    response2 = client.post(
        f"{app.config['SITE_API_URL']}/webhooks/user_data_update",
        data=json.dumps(
            {
                "idp": "knowledgeCommons",
                "updates": {
                    "users": [
                        {"id": user1_data["saml_id"], "event": "updated"},
                    ],
                },
            }
        ),
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == 202
    assert response2.json == {
        "message": "Webhook notification accepted",
        "status": 202,
        "updates": {
            "users": [
                {"id": user1_data["saml_id"], "event": "updated"},
            ],
        },
    }

    assert mock_adapter.called
    assert mock_adapter.call_count == 1  # only one call to the remote api

    # Check that the user data was updated in the db
    user = current_accounts.datastore.get_user_by_id(user_id)
    assert user.email == user1_data["email"]
    assert user.user_profile.get("full_name") == user1_data["name"]
    assert (
        user.user_profile.get("identifier_kc_username")
        == user1_data["saml_id"]  # noqa: E501
    )  # noqa: E501
    assert user.user_profile.get("identifier_orcid") == user1_data["orcid"]
    assert json.loads(user.user_profile.get("name_parts")) == {
        "first": user1_data["first_name"],
        "last": user1_data["last_name"],
    }
    assert [r.name for r in user.roles] == [
        "administration-access",
        "knowledgeCommons---12345|admin",
        "knowledgeCommons---67891|member",
    ]
    assert (
        user.user_profile.get("affiliations")
        == user1_data["institutional_affiliation"]  # noqa: E501
    )


def test_user_data_sync_on_account_setup(
    running_app, db, user_factory, requests_mock, search_clear
):
    """Test that the user data is synced when a user is created.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.
    """
    # Mock the remote API endpoint
    protocol = os.environ.get("INVENIO_COMMONS_API_REQUEST_PROTOCOL", "https")
    base_url = f"{protocol}://hcommons-dev.org/wp-json/commons/v1/users"
    remote_url = f"{base_url}/testuser"
    requests_mock.get(
        remote_url,
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "name": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "institutional_affiliation": "Test University",
            "orcid": "0000-0001-2345-6789",
            "groups": [
                {"id": 12345, "name": "test-group", "role": "member"},
            ],
        },
    )

    # Create a new user
    u = user_factory(
        email="testuser@example.com",
        token=False,
        admin=False,
        saml_src=None,
        saml_id=None,
    )
    user = u.user
    user_id = user.id

    # Verify that the user was activated and updated
    updated_user = current_accounts.datastore.get_user_by_id(user_id)
    assert updated_user.active
    assert updated_user.username == "knowledgeCommons-testuser"
    assert updated_user.email == "testuser@example.com"
    assert updated_user.user_profile.get("full_name") == "Test User"
    assert updated_user.user_profile.get("affiliations") == "Test University"
    assert (
        updated_user.user_profile.get("identifier_orcid")
        == "0000-0001-2345-6789"  # noqa: E501
    )
    assert json.loads(updated_user.user_profile.get("name_parts")) == {
        "first": "Test",
        "last": "User",
    }

    # Verify group membership
    user_roles = [role.name for role in user.roles]
    assert "knowledgeCommons---12345|member" in user_roles


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_account_setup_already_linked(
    running_app, search_clear
):
    """Test that the user's data is synced when already linked to KC IDP.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.
    """
    pass


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_after_one_week(running_app, search_clear):
    """Test that the user's data is synced after one week (stale).

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.
    """
    pass


@pytest.mark.skip(reason="Not implemented")
def test_group_data_sync_on_webhook(running_app, search_clear):
    """Test that the group data is synced when a webhook is received.

    The actual api call is mocked, so this tests that the api request is made
    and that the group data is updated in Invenio.
    """
    pass
