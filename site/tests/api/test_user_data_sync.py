from flask_login import login_user
from invenio_accounts.proxies import current_accounts
import json
import os
import pytest
import requests

# from invenio_accounts.testutils import login_user_via_session
from kcworks.services.accounts.saml import knowledgeCommons_account_setup


def test_user_data_kc_endpoint():
    """Test that the production kc endpoint returns the correct data.

    The focus here is on the json schema being returned
    """
    url = "https://hcommons.org/wp-json/commons/v1/users/gihctester"
    headers = {
        "Authorization": f"Bearer {os.environ.get('COMMONS_API_TOKEN_PROD')}"
    }

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    actual_resp = response.json()
    assert actual_resp["username"] == "gihctester"
    assert actual_resp["email"] == "ghosthc@email.ghostinspector.com"
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
    pass


def test_user_data_sync_on_login(
    running_app, db, user_factory, user1_data, search_clear
):
    """
    Test that the user data is synced when a user logs in.

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
    profile = u.user.user_profile
    assert profile.get("full_name") == user1_data["name"]
    assert (
        profile.get("affiliations") == user1_data["institutional_affiliation"]
    )
    assert profile.get("identifier_orcid") == user1_data["orcid"]
    assert profile.get("identifier_kc_username") == user1_data["saml_id"]
    assert json.loads(profile.get("name_parts")) == {
        "first": user1_data["first_name"],
        "last": user1_data["last_name"],
    }

    # Check that the user is a member of the linked communities
    assert sorted([r.name for r in u.user.roles]) == sorted(
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
):
    app = running_app.app

    # Create a user
    # The user is created with a saml auth record because saml_src
    # and saml_id are supplied.
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
    base_url = "https://hcommons-dev.org/wp-json/commons/v1/users"
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
        == user1_data["saml_id"]
    )
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
        == user1_data["institutional_affiliation"]
    )


def test_user_data_sync_on_account_setup(
    running_app, db, user_factory, requests_mock, search_clear
):
    # Mock the remote API endpoint
    requests_mock.get(
        "https://hcommons-dev.org/wp-json/commons/v1/users/testuser",
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

    # Prepare account_info
    account_info = {
        "external_id": "testuser",
        "external_method": "knowledgeCommons",
    }

    updated = knowledgeCommons_account_setup(user, account_info)
    assert updated

    # Verify that the user was activated and updated
    updated_user = current_accounts.datastore.get_user_by_id(user_id)
    assert updated_user.active
    assert updated_user.username == "knowledgeCommons-testuser"
    assert updated_user.email == "testuser@example.com"
    assert updated_user.user_profile.get("full_name") == "Test User"
    assert updated_user.user_profile.get("affiliations") == "Test University"
    assert (
        updated_user.user_profile.get("identifier_orcid")
        == "0000-0001-2345-6789"
    )
    assert json.loads(updated_user.user_profile.get("name_parts")) == {
        "first": "Test",
        "last": "User",
    }

    # Verify group membership
    user_roles = [role.name for role in user.roles]
    assert "knowledgeCommons---12345|member" in user_roles


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_account_setup_already_linked(running_app):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_after_one_week(running_app):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_group_data_sync_on_webhook(running_app):
    pass
