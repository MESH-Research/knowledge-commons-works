# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the accounts API."""
import datetime
import json
from collections.abc import Callable
from types import SimpleNamespace

import pytest
import pytz
from flask import Flask
from invenio_accounts import current_accounts
from invenio_accounts.models import User
from invenio_record_importer_kcworks.services.users import UsersHelper
from kcworks.services.accounts.saml import (
    acs_handler_factory,
    knowledgeCommons_account_get_user,
    knowledgeCommons_account_info,
    knowledgeCommons_account_setup,
)
from requests_mock.adapter import _Matcher as Matcher

from ..fixtures.saml import idp_responses
from ..fixtures.users import AugmentedUserFixture, user_data_set


@pytest.mark.parametrize(
    "attributes,output,user_data",
    [
        (
            idp_responses["joanjett"]["raw_data"],
            idp_responses["joanjett"]["extracted_data"],
            user_data_set["joanjett"],
        ),
        (
            idp_responses["user1"]["raw_data"],
            idp_responses["user1"]["extracted_data"],
            user_data_set["user1"],
        ),
        (
            idp_responses["user2"]["raw_data"],
            idp_responses["user2"]["extracted_data"],
            user_data_set["user2"],
        ),
        (
            idp_responses["user3"]["raw_data"],
            idp_responses["user3"]["extracted_data"],
            user_data_set["user3"],
        ),
        (
            idp_responses["user4"]["raw_data"],
            idp_responses["user4"]["extracted_data"],
            user_data_set["user4"],
        ),
    ],
)
def test_knowledgeCommons_account_info(
    running_app,
    appctx,
    db,
    attributes: dict,
    output: dict,
    user_data: dict,
    mock_user_data_api: Callable,
    user_data_to_remote_data: Callable,
) -> None:
    """Test the custom handler for the knowledgeCommons account info."""
    mock_adapter: Matcher = mock_user_data_api(
        user_data["saml_id"],
        user_data_to_remote_data(user_data["saml_id"], user_data["email"], user_data),
    )

    info: dict = knowledgeCommons_account_info(
        attributes, remote_app="knowledgeCommons"
    )
    assert mock_adapter.called
    assert mock_adapter.call_count == 1

    expected_result_email: str = (
        output["user"]["email"]
        if output["user"]["email"]
        else user_data["email"]
        # To handle the case where the IDP response does not have an email
        # and we are retrieving it from the api
    )

    assert info["user"]["email"] == expected_result_email
    assert (
        info["user"]["profile"]["full_name"] == output["user"]["profile"]["full_name"]
    )
    assert info["user"]["profile"]["username"] == output["user"]["profile"]["username"]
    assert info["external_id"] == output["external_id"]
    assert info["external_method"] == output["external_method"]
    assert info["user"]["profile"].get("identifier_orcid", "") == output["user"][
        "profile"
    ].get("identifier_orcid", "")
    assert info["user"]["profile"].get("identifier_kc_username", "") == output["user"][
        "profile"
    ].get("identifier_kc_username", "")
    assert info["active"] == output["active"]
    assert datetime.datetime.now(tz=pytz.timezone("US/Eastern")) - info[
        "confirmed_at"
    ] < datetime.timedelta(seconds=10)


@pytest.mark.parametrize(
    "original_email,original_orcid,original_kc_username,"
    "user_data,idp_data,already_linked,user_expected",
    [
        (  # pre-existing user with same email and ORCID
            user_data_set["user1"]["email"],
            user_data_set["user1"]["orcid"],
            user_data_set["user1"]["saml_id"],
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            False,
            True,
        ),
        (  # pre-existing user with same email and empty ORCID
            user_data_set["user1"]["email"],
            "",
            user_data_set["user1"]["saml_id"],
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            False,
            True,
        ),
        (  # pre-existing user with different email and same ORCID
            "other@example.com",
            user_data_set["user1"]["orcid"],
            user_data_set["user1"]["saml_id"],
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            False,
            True,
        ),
        (  # already linked user with same email and ORCID
            user_data_set["user1"]["email"],
            user_data_set["user1"]["orcid"],
            user_data_set["user1"]["saml_id"],
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            True,
            True,
        ),
        (  # pre-existing user with different email and empty ORCID but KC username
            "other@example.com",
            "",
            user_data_set["user1"]["saml_id"],
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            False,
            True,
        ),
        (  # pre-existing user with different email, empty ORCID, and empty KC username
            "other@example.com",
            "",
            "",
            user_data_set["user1"],
            idp_responses["user1"]["extracted_data"],
            False,
            False,
        ),
    ],
)
def test_knowledgeCommons_account_get_user(
    running_app,
    appctx,
    db,
    user_factory: Callable,
    original_email: str,
    original_orcid: str,
    original_kc_username: str,
    user_data: dict,
    idp_data: dict,
    already_linked: bool,
    user_expected: bool,
    mock_user_data_api: Callable,
    user_data_to_remote_data: Callable,
) -> None:
    """Test that account_get_user matches a SAML login based on either email or ORCID.

    case 1: The pre-existing KCWorks user has the same email as the IDP response
    case 2: The pre-existing KCWorks user has a different email as the IDP response
    case 3: The KCWorks user is already linked to an external ID
    """
    if not already_linked:
        u: AugmentedUserFixture = user_factory(
            email=original_email,
            password="password",
            saml_id=None,
            orcid=original_orcid,
            kc_username=original_kc_username,
        )
        assert not u.mock_adapter
    else:
        u: AugmentedUserFixture = user_factory(
            email=original_email,
            password="password",
            saml_src="knowledgeCommons",
            saml_id=user_data["saml_id"],
            new_remote_data=user_data,
        )
    assert u.user is not None

    matched_user: User | None = knowledgeCommons_account_get_user(idp_data)

    if user_expected:
        assert matched_user is not None
        assert matched_user.id == u.user.id
        # email, username, identifier_orcid, identifier_kc_username are not
        # updated yet on returned User object
        assert matched_user.email == original_email
        assert matched_user.username == (
            None if not already_linked else f"knowledgeCommons-{user_data['saml_id']}"
        )
        assert matched_user.user_profile.get("identifier_orcid") == (
            original_orcid if original_orcid != "" else None
        )  # not updated yet
        assert matched_user.user_profile.get("identifier_kc_username") == (
            original_kc_username if original_kc_username != "" else None
        )
    else:
        assert matched_user is None


@pytest.mark.parametrize(
    "user_data,idp_data",
    [
        (user_data_set["joanjett"], idp_responses["joanjett"]["extracted_data"]),
        (user_data_set["user1"], idp_responses["user1"]["extracted_data"]),
        (user_data_set["user2"], idp_responses["user2"]["extracted_data"]),
        (user_data_set["user3"], idp_responses["user3"]["extracted_data"]),
        (user_data_set["user4"], idp_responses["user4"]["extracted_data"]),
    ],
)
def test_knowledgeCommons_account_setup(
    running_app,
    appctx,
    db,
    user_factory: Callable,
    user_data: dict,
    idp_data: dict,
    search_clear: Callable,
) -> None:
    """Test that account_setup links the user with the IDP.

    Test that the user is activated and the user data is updated in the db
    based on the data from the (mocked) remote service api call.
    """
    u: AugmentedUserFixture = user_factory(
        email=user_data["email"],
        password="password",
        saml_src="knowledgeCommons",
        saml_id=user_data["saml_id"],
        new_remote_data=user_data,
    )
    assert isinstance(u.user, User)
    mock_adapter: Matcher | None = u.mock_adapter
    assert isinstance(mock_adapter, Matcher)
    # Ensure that any group roles are being added by the setup function
    assert u.user.roles == []
    # Deactivate the user if it is already active so that we can test the
    # activation
    if u.user.active:
        assert current_accounts.datastore.deactivate_user(u.user)
    assert not mock_adapter.called

    synced: bool = knowledgeCommons_account_setup(u.user, idp_data)
    assert synced
    assert mock_adapter.called  # The user data api call was made
    assert mock_adapter.call_count == 1

    user: User = current_accounts.datastore.get_user_by_id(u.user.id)
    assert user.active  # The user was activated
    assert user.confirmed_at is not None
    assert user.confirmed_at - datetime.datetime.now() < datetime.timedelta(
        hours=5, seconds=10
    )
    assert user.email == user_data.get("email")  # TODO: Test updating email
    assert user.username == f"knowledgeCommons-{user_data['saml_id']}"
    assert user.user_profile.get("full_name") == user_data["name"]
    assert user.user_profile.get("affiliations") == user_data.get(
        "institutional_affiliation"
    )
    assert user.user_profile.get("identifier_kc_username") == user_data["saml_id"]
    assert user.user_profile.get("identifier_orcid") == (user_data.get("orcid") or None)
    assert json.loads(user.user_profile.get("name_parts")) == {
        "first": user_data["first_name"],
        "last": user_data["last_name"],
    }
    assert user.external_identifiers[0].id == user_data["saml_id"]
    assert user.external_identifiers[0].id_user == user.id
    assert user.external_identifiers[0].method == "knowledgeCommons"
    assert set([r.name for r in user.roles]) == (
        set([f"knowledgeCommons---{g['id']}|{g['role']}" for g in user_data["groups"]])
        if "groups" in user_data.keys()
        else set()
    )


@pytest.mark.parametrize(
    "idp_data,user_data,api_call_count",
    [
        (idp_responses["joanjett"]["raw_data"], user_data_set["joanjett"], 2),
        (idp_responses["user1"]["raw_data"], user_data_set["user1"], 2),
        (idp_responses["user2"]["raw_data"], user_data_set["user2"], 2),
        (
            idp_responses["user3"]["raw_data"],
            user_data_set["user3"],
            2,
        ),  # IDP response has no email (now making request for everyone)
        (idp_responses["user4"]["raw_data"], user_data_set["user4"], 2),
    ],
)
def test_account_register_on_login(
    running_app,
    appctx,
    db,
    idp_data,
    user_data,
    mocker,
    mock_user_data_api: Callable,
    user_data_to_remote_data: Callable,
    api_call_count: int,
    mailbox,
    celery_worker,
    search_clear: Callable,
) -> None:
    """Test that account_register_on_login creates a new user from SAML data.

    Tests that:
    - The new user is created from SAML data
    - The new user's data is synced from remote
    - The new user is activated
    - The new user is sent a welcome email
    """
    app: Flask = running_app.app
    mock_current_user = SimpleNamespace(is_authenticated=False)
    mocker.patch("invenio_saml.handlers.current_user", mock_current_user)
    mock_auth = SimpleNamespace(get_attributes=lambda: idp_data)
    handler = acs_handler_factory(
        "knowledgeCommons",
        account_info=knowledgeCommons_account_info,
        account_setup=knowledgeCommons_account_setup,
    )

    mock_adapter: Matcher = mock_user_data_api(
        user_data["saml_id"],
        user_data_to_remote_data(user_data["saml_id"], user_data["email"], user_data),
    )
    next_url: str = handler(mock_auth, "https://localhost/next-url.com")
    assert mock_adapter.called
    assert mock_adapter.call_count == api_call_count

    assert len(mailbox) == 1
    assert mailbox[0].subject == "Welcome to KCWorks!"
    assert mailbox[0].recipients == [user_data["email"]]
    assert mailbox[0].sender == app.config["MAIL_DEFAULT_SENDER"]
    assert "Welcome to Knowledge Commons Works!" in mailbox[0].html
    assert (
        f"Welcome {user_data['email']} to Knowledge Commons Works," in mailbox[0].body
    )
    assert user_data["email"] in mailbox[0].html
    assert user_data["email"] in mailbox[0].body
    assert app.config["KC_HELP_URL"] in mailbox[0].html
    assert app.config["KC_HELP_URL"] in mailbox[0].body
    assert app.config["KC_CONTACT_FORM_URL"] in mailbox[0].html
    assert app.config["KC_CONTACT_FORM_URL"] in mailbox[0].body

    user: User = current_accounts.datastore.get_user_by_email(user_data["email"])
    assert user.email == user_data["email"]
    assert user.active
    assert user.confirmed_at is not None
    assert user.confirmed_at - datetime.datetime.now() < datetime.timedelta(
        hours=5, seconds=10
    )
    assert user.username == f"knowledgeCommons-{user_data['saml_id']}"
    assert user.user_profile.get("full_name") == user_data["name"]
    assert user.user_profile.get("affiliations") == user_data.get(
        "institutional_affiliation", ""
    )
    assert user.user_profile.get("identifier_kc_username") == user_data["saml_id"]
    assert user.user_profile.get("identifier_orcid") == (
        user_data.get("orcid") if user_data.get("orcid") != "" else None
    )
    assert user.external_identifiers[0].id == user_data["saml_id"]
    assert user.external_identifiers[0].id_user == user.id
    assert user.external_identifiers[0].method == "knowledgeCommons"
    expected_roles = (
        [f"knowledgeCommons---{g['id']}|{g['role']}" for g in user_data["groups"]]
        if "groups" in user_data.keys()
        else []
    )
    assert all(r for r in user.roles if r.name in expected_roles)
    assert not any(r for r in user.roles if r.name not in expected_roles)

    assert next_url == "https://localhost/next-url.com"


def test_create_user_via_importer(
    running_app,
    appctx,
    db,
    mailbox,
    celery_worker,
    search_clear: Callable,
) -> None:
    """Test the creation of a user programmatically via the importer.

    Among other things, test that the correct welcome email is sent to the user.
    """
    user = UsersHelper().create_invenio_user(
        user_email="test@example.com",
        full_name="Test User",
        community_owner=[],
        orcid="0000-0002-1825-0097",
        other_user_ids=[
            {"identifier": "test", "scheme": "neh_user_id"},
            {"identifier": "test2", "scheme": "import_user_id"},
        ],
    )
    assert user["user"] is not None
    assert user["user"].email == "test@example.com"
    assert user["user"].username is None
    assert user["user"].user_profile.get("full_name") == "Test User"
    assert user["user"].user_profile.get("identifier_kc_username") is None
    assert user["user"].user_profile.get("identifier_orcid") == "0000-0002-1825-0097"
    assert user["user"].user_profile.get("name_parts") is None
    assert user["user"].user_profile.get("affiliations") is None
    assert len(mailbox) == 0
