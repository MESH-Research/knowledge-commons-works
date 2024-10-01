import requests
import json
import os
import pytest
from flask_login import login_user


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
    assert actual_resp["groups"] == [
        {"id": 1004089, "name": "Teaching and Learning", "role": "member"},
        {
            "id": 1004090,
            "name": "Humanities, Arts, and Media",
            "role": "member",
        },
        {
            "id": 1004091,
            "name": "Technology, Networks, and Sciences",
            "role": "member",
        },
        {
            "id": 1004092,
            "name": "Social and Political Issues",
            "role": "member",
        },
        {
            "id": 1004093,
            "name": "Educational and Cultural Institutions",
            "role": "member",
        },
        {
            "id": 1004094,
            "name": "Publishing and Archives",
            "role": "member",
        },
        {
            "id": 1004651,
            "name": "Hidden Testing Group New Name",
            "role": "admin",
        },
    ]
    # TODO: add orcid to the api call
    # assert actual_resp["orcid"] == "0000-0000-0000-0000"


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_creation(running_app):
    assert True


def test_user_data_sync_on_login(running_app, user_factory, user1_data):
    """
    Test that the user data is synced when a user logs in.

    The actual api call is mocked, so this tests that the api request is made
    and that the user data is updated in Invenio.

    Also tests that the api call does *not* happen for simple programmatic
    user creation. It only happens when the user logs in.
    """
    app = running_app.app

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
    app.logger.warning(profile.keys())
    app.logger.warning(profile.values())
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
def test_user_data_sync_on_logout(running_app):
    """Test that the remote api call does not happen for local logins.

    We want to make sure that the user data sync does not create errors when
    logging someone in who doesn't have an account on the remote service.

    """
    pass


@pytest.mark.skip(reason="Not implemented")
def test_user_data_sync_on_webhook(running_app):
    assert True
