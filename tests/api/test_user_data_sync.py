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
from unittest.mock import patch

import pytest
import requests
from flask_login import login_user
from invenio_accounts.profiles import UserProfileDict
from invenio_accounts.proxies import current_accounts
from kcworks.services.accounts.idms import knowledgeCommons_account_setup

from ..fixtures.users import user_data_set


def test_user_data_kc_endpoint_members(running_app):
    """Test that the production kc endpoint returns the correct data.

    The focus here is on the json schema being returned
    """
    base_url = running_app.app.config.get("IDMS_BASE_API_URL")
    url = f"{base_url}members/gihctester/"
    token = os.environ.get("COMMONS_PROFILES_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    actual_resp = response.json()
    actual_data = actual_resp["results"]
    assert actual_data["username"] == "gihctester"
    assert actual_data["email"] == "gihctester@gmail.com"
    assert actual_data["name"] == "Ghost Hc"
    assert actual_data["first_name"] == "Ghost"
    assert actual_data["last_name"] == "Hc"
    assert not actual_data["institutional_affiliation"]
    assert "gravatar" in actual_data["avatar"]
    for g in actual_data["groups"]:
        assert list(g.keys()) == [
            "id",
            "group_name",
            "role",
            "url",
            "status",
            "avatar",
            "inviter_id",
            "inviter",
        ]
        assert isinstance(g["id"], int)
        if g["group_name"]:
            assert isinstance(g["group_name"], str)
    assert not actual_data["orcid"]
    assert "MLA" in actual_data["memberships"].keys()


def test_user_data_kc_endpoint_subs(running_app):
    """Test that the production kc endpoint returns the correct data.

    The focus here is on the json schema being returned
    """
    base_url = running_app.app.config.get("IDMS_BASE_API_URL")
    url = f"{base_url}subs/ianscott/"
    token = os.environ.get("COMMONS_PROFILES_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    actual_resp = response.json()
    target_data = [
        d for d in actual_resp["data"] if d["profile"]["username"] == "ianscott"
    ]
    oauth_id = target_data[0]["sub"]

    response2 = requests.get(f"{base_url}subs/?sub={oauth_id}", headers=headers)
    actual_resp2 = response2.json()
    running_app.app.logger.error(actual_resp2)
    actual_data = actual_resp2["data"][0]["profile"]
    assert actual_data["username"] == "ianscott"
    assert "scottianw" in actual_data["email"]
    assert actual_data["name"] == "Ian W. Scott"
    assert actual_data["first_name"] == "Ian W."
    assert actual_data["last_name"] == "Scott"
    assert (
        actual_data["institutional_affiliation"]
        == "MESH Research, Michigan State University"
    )
    for g in actual_data["groups"]:
        assert list(g.keys()) == ["id", "name", "role"]
        assert isinstance(g["id"], int)
        if g["name"]:
            assert isinstance(g["name"], str)
    assert "0000-0002-0722" in actual_data["orcid"]
    assert "MLA" in actual_data["memberships"].keys()


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
    new_data_payload = user_data_set["user1"]

    # Create a user
    # The user is created with a saml auth record because oauth_src
    # and oauth_id are supplied.
    u = user_factory(
        email=new_data_payload["email"],
        oauth_src="cilogon",
        oauth_id=new_data_payload["oauth_id"],
        kc_username=new_data_payload["kc_username"],
        new_remote_data=new_data_payload,
    )

    for mock_adapter in u.mock_adapter_subs, u.mock_adapter_members:
        assert not mock_adapter.called
        assert mock_adapter.call_count == 0
    login_user(u.user)
    assert u.mock_adapter_subs.called
    assert u.mock_adapter_subs.call_count == 1
    assert not u.mock_adapter_members.called
    assert u.mock_adapter_members.call_count == 0

    assert u.user.email == new_data_payload["email"]

    profile: UserProfileDict = u.user.user_profile
    assert profile.get("full_name") == new_data_payload["name"]
    assert profile.get("affiliations") == new_data_payload["institutional_affiliation"]  # noqa: E501
    assert profile.get("identifier_orcid") == new_data_payload["orcid"]
    assert profile.get("identifier_kc_username") == new_data_payload["kc_username"]
    assert json.loads(profile.get("name_parts")) == {
        "first": new_data_payload["first_name"],
        "last": new_data_payload["last_name"],
    }

    merged_user = db.session.merge(u.user)

    # Check that the user is a member of the linked communities
    assert sorted([r.name for r in merged_user.roles]) == sorted([
        "knowledgeCommons---12345|administrator",
        "knowledgeCommons---67891|member",
    ])


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
    client,
    requests_mock,
    headers,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    user_data_to_remote_data,
):
    """Test that the user data is synced when a user logs in.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.

    Also tests that the api call does *not* happen for simple programmatic
    user creation. It only happens when the user logs in.
    """
    app = running_app.app

    profile_data = user_data_set["user1"]

    # Create a user
    u = user_factory(
        email=profile_data["email"],
        oauth_src="cilogon",
        oauth_id=profile_data["oauth_id"],
        kc_username=profile_data["kc_username"],
        new_remote_data={},
        token=True,
        admin=True,
    )
    token = u.allowed_token
    user_id = u.user.id
    for mock_adapter in u.mock_adapter_subs, u.mock_adapter_members:
        assert not mock_adapter.called  # no call to the remote api yet
        assert mock_adapter.call_count == 0

    # Mock additional user data from the remote service
    # api response
    base_url = app.config.get("IDMS_BASE_API_URL")

    mock_remote_data_subs, mock_remote_data_members = user_data_to_remote_data(
        kc_username=profile_data["kc_username"],
        email=profile_data["email"],
        user_data=profile_data,
        oauth_id=profile_data["oauth_id"],
    )
    app.logger.error(f"test: mock remote data members: {mock_remote_data_members}")

    mock_adapter_members = requests_mock.get(
        f"{base_url}members/{profile_data['kc_username']}",
        json=mock_remote_data_members,
    )
    mock_adapter_subs = requests_mock.get(
        f"{base_url}subs/?sub={profile_data['oauth_id']}",
        json=mock_remote_data_subs,
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
    # we patch the current user so that the webhook does not
    # try to access it in invenio_accounts.utils.set_session_info
    # thereby triggering a detached session exception in SQLAlchemy
    with patch("invenio_accounts.utils.current_user"):
        response2 = client.post(
            f"{app.config['SITE_API_URL']}/webhooks/user_data_update",
            data=json.dumps({
                "idp": "knowledgeCommons",
                "updates": {
                    "users": [
                        {
                            "id": profile_data["oauth_id"],
                            "event": "updated",
                        },
                    ],
                },
            }),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )

    assert response2.status_code == 202
    assert response2.json == {
        "message": "Webhook notification accepted",
        "status": 202,
        "updates": {
            "users": [
                {
                    "id": profile_data["oauth_id"],
                    "event": "updated",
                },
            ],
        },
    }

    assert mock_adapter_subs.called
    assert mock_adapter_subs.call_count == 1  # only one call to the remote api
    assert not mock_adapter_members.called

    # Check that the user data was updated in the db
    user = current_accounts.datastore.get_user_by_id(user_id)
    assert user.email == profile_data["email"]
    assert user.user_profile.get("full_name") == profile_data["name"]
    assert (
        user.user_profile.get("identifier_kc_username") == profile_data["kc_username"]  # noqa: E501
    )  # noqa: E501
    assert user.user_profile.get("identifier_orcid") == profile_data["orcid"]
    assert json.loads(user.user_profile.get("name_parts")) == {
        "first": profile_data["first_name"],
        "last": profile_data["last_name"],
    }
    assert [r.name for r in user.roles] == [
        "administration-access",
        "knowledgeCommons---12345|administrator",
        "knowledgeCommons---67891|member",
    ]
    assert (
        user.user_profile.get("affiliations")
        == profile_data["institutional_affiliation"]  # noqa: E501
    )


def test_user_data_sync_on_account_setup(
    running_app, db, user_factory, requests_mock, search_clear
):
    """Test that the user data is synced when a user is created.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.
    """
    # Mock the remote API endpoint
    base_url = running_app.app.config.get("IDMS_BASE_API_URL")
    mock_adapter_members = requests_mock.get(
        f"{base_url}members/testuser",
        json={
            "results": [
                {
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
                }
            ]
        },
    )

    mock_remote_data_subs = {
        "data": [
            {
                "sub": "testuser",
                "profile": {
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
            }
        ],
        "next": None,
        "previous": None,
        "meta": {"authorized": True},
    }

    mock_adapter_subs = requests_mock.get(
        f"{base_url}subs/?sub=testuser1",
        json=mock_remote_data_subs,
    )

    # Create a new user
    u = user_factory(
        email="testuser@example.com",
        token=False,
        admin=False,
        oauth_src=None,
        oauth_id=None,
    )
    user = u.user
    user_id = user.id

    # Prepare account_info
    account_info = {
        "external_id": "testuser1",
        "external_method": "cilogon",
    }

    updated = knowledgeCommons_account_setup(user, account_info)
    assert updated
    assert mock_adapter_subs.called
    assert mock_adapter_subs.call_count == 1
    assert not mock_adapter_members.called

    # Verify that the user was activated and updated
    updated_user = current_accounts.datastore.get_user_by_id(user_id)
    assert updated_user.active
    assert updated_user.username == "knowledgeCommons-testuser"
    assert updated_user.email == "testuser@example.com"
    assert updated_user.user_profile.get("full_name") == "Test User"
    assert updated_user.user_profile.get("affiliations") == "Test University"
    assert (
        updated_user.user_profile.get("identifier_orcid") == "0000-0001-2345-6789"  # noqa: E501
    )
    assert json.loads(updated_user.user_profile.get("name_parts")) == {
        "first": "Test",
        "last": "User",
    }

    # Verify group membership
    user_roles = [role.name for role in user.roles]
    assert "knowledgeCommons---12345|member" in user_roles


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_account_setup_already_linked(running_app, search_clear):
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
