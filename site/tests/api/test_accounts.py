import pytest
import datetime
from flask import Flask
from invenio_accounts import current_accounts
from invenio_accounts.models import User
from invenio_saml.handlers import acs_handler_factory
import json
from kcworks.services.accounts.saml import (
    knowledgeCommons_account_info,
    knowledgeCommons_account_setup,
)
import pytz
from requests_mock.adapter import _Matcher as Matcher
from types import SimpleNamespace
from typing import Callable, Optional
from ..fixtures.saml import idp_responses
from ..fixtures.users import user_data_set, AugmentedUserFixture


@pytest.mark.parametrize(
    "attributes,output,user_data,api_call_count",
    [
        (
            idp_responses["joanjett"]["raw_data"],
            idp_responses["joanjett"]["extracted_data"],
            user_data_set["joanjett"],
            0,
        ),
        (
            idp_responses["user1"]["raw_data"],
            idp_responses["user1"]["extracted_data"],
            user_data_set["user1"],
            0,
        ),
        (
            idp_responses["user2"]["raw_data"],
            idp_responses["user2"]["extracted_data"],
            user_data_set["user2"],
            0,
        ),
        (
            idp_responses["user3"]["raw_data"],
            idp_responses["user3"]["extracted_data"],
            user_data_set["user3"],
            1,
        ),
        (
            idp_responses["user4"]["raw_data"],
            idp_responses["user4"]["extracted_data"],
            user_data_set["user4"],
            0,
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
    api_call_count: int,
) -> None:
    """
    Test the custom handler
    """

    mock_adapter: Matcher = mock_user_data_api(
        user_data["saml_id"],
        user_data_to_remote_data(user_data["saml_id"], user_data["email"], user_data),
    )

    info: dict = knowledgeCommons_account_info(
        attributes, remote_app="knowledgeCommons"
    )
    if api_call_count == 1:  # Here the api is only called if no email is provided
        assert mock_adapter.called
        assert mock_adapter.call_count == 1
    else:
        assert not mock_adapter.called
        assert mock_adapter.call_count == 0

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
    assert info["active"] == output["active"]
    assert datetime.datetime.now(tz=pytz.timezone("US/Eastern")) - info[
        "confirmed_at"
    ] < datetime.timedelta(seconds=10)


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
    """
    Test the account setup function

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
    mock_adapter: Optional[Matcher] = u.mock_adapter
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
    assert [r.name for r in user.roles] == (
        [f"knowledgeCommons---{g['id']}|{g['role']}" for g in user_data["groups"]]
        if "groups" in user_data.keys()
        else []
    )


@pytest.mark.parametrize(
    "idp_data,user_data,api_call_count",
    [
        (idp_responses["joanjett"]["raw_data"], user_data_set["joanjett"], 1),
        (idp_responses["user1"]["raw_data"], user_data_set["user1"], 1),
        (idp_responses["user2"]["raw_data"], user_data_set["user2"], 1),
        (
            idp_responses["user3"]["raw_data"],
            user_data_set["user3"],
            2,
        ),  # IDP response has no email
        (idp_responses["user4"]["raw_data"], user_data_set["user4"], 1),
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
    """
    Test the registration function if a user is not already registered.

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
    assert [r.name for r in user.roles] == (
        [f"knowledgeCommons---{g['id']}|{g['role']}" for g in user_data["groups"]]
        if "groups" in user_data.keys()
        else []
    )

    assert next_url == "https://localhost/next-url.com"
