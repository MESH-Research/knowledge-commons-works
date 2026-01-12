# Part of Knowledge Commons Works
#
# Copyright (C) 2025 MESH Research.
#
# Knowledge Commons Works is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User related pytest fixtures for testing."""

from collections.abc import Callable
from copy import deepcopy

import pytest
from flask import current_app
from flask_login import login_user
from flask_principal import AnonymousIdentity, Identity
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import (
    any_user,
    authenticated_user,
    superuser_access,
)
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_accounts.testutils import login_user_via_session
from invenio_administration.permissions import administration_access_action
from invenio_oauth2server.models import Token
from invenio_oauthclient.models import UserIdentity
from pytest_invenio.fixtures import UserFixtureBase
from requests_mock.adapter import _Matcher as Matcher


def get_authenticated_identity(user: User | Identity) -> Identity:
    """Return an authenticated identity for the given user.

    If an Identity is provided, it is returned with the any_user and authenticated_user
    needs added.
    """
    identity = get_identity(user) if isinstance(user, User) else user
    identity.provides.add(any_user)
    identity.provides.add(authenticated_user)
    return identity


@pytest.fixture(scope="function")
def anon_identity():
    """Anonymous identity fixture for UI view tests.

    Returns:
        Identity: An anonymous identity with any_user need.
    """
    identity = AnonymousIdentity()
    identity.provides.add(any_user)
    return identity


@pytest.fixture(scope="function")
def mock_user_data_api(requests_mock) -> Callable:
    """Mock the user data api.

    Returns:
        Callable: Mock API call function.
    """

    def mock_api_call(
        kc_username: str,
        oauth_id: str,
        mock_remote_data_subs: dict,
        mock_remote_data_members: dict,
    ) -> tuple[Matcher, Matcher]:
        base_url = current_app.config.get("IDMS_BASE_API_URL")

        mock_adapter_members = requests_mock.get(
            f"{base_url}members/{kc_username}",
            json=mock_remote_data_members,
        )
        mock_adapter_subs = requests_mock.get(
            f"{base_url}subs/?sub={oauth_id}",
            json=mock_remote_data_subs,
        )
        return mock_adapter_subs, mock_adapter_members

    return mock_api_call


@pytest.fixture(scope="function")
def user_data_to_remote_data(requests_mock):
    """Factory fixture providing function to convert user data format.

    Returns:
        function: Function to convert user data to remote data format.
    """

    def convert_user_data_to_remote_data(
        kc_username: str, email: str, user_data: dict, oauth_id: str = ""
    ) -> tuple[
        dict[str, str | list[dict[str, str]]], dict[str, str | list[dict[str, str]]]
    ]:
        """Convert user fixture data to format for remote data.

        Returns:
            tuple[dict, dict]: Returns two dictionaries with the same user data: [0] in
                the shape returned from the "subs" endpoint and [1] in the shape
                returned from the "members" endpoint.
        """
        if user_data.get("first_name", "") != "":
            mock_remote_data = {
                "data": [
                    {
                        "sub": oauth_id if oauth_id else user_data.get("oauth_id"),
                        "profile": {
                            "username": kc_username,
                            "email": email,
                            "name": user_data.get("name", ""),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", ""),
                            "institutional_affiliation": user_data.get(
                                "institutional_affiliation", ""
                            ),
                            "orcid": user_data.get("orcid", ""),
                            "preferred_language": user_data.get(
                                "preferred_language", ""
                            ),
                            "time_zone": user_data.get("time_zone", ""),
                            "groups": user_data.get("groups", ""),
                            "memberships": [],
                        },
                        "idp_name": "Michigan State University",
                    }
                ],
                "next": None,
                "previous": None,
                "meta": {"authorized": True},
            }
        else:
            try:
                profile = user_data.get("data", [])[0].get("profile", {})
            except IndexError:
                profile = {}

            mock_remote_data = {
                "data": [
                    {
                        "sub": "user1",
                        "profile": {
                            "username": oauth_id,
                            "email": email,
                            "name": profile.get("name", ""),
                            "first_name": profile.get("first_name", ""),
                            "last_name": profile.get("last_name", ""),
                            "institutional_affiliation": profile.get(
                                "institutional_affiliation", ""
                            ),
                            "orcid": profile.get("orcid", ""),
                            "preferred_language": profile.get("preferred_language", ""),
                            "time_zone": profile.get("time_zone", ""),
                            "groups": profile.get("groups", []),
                            "memberships": [],
                        },
                        "idp_name": "Michigan State University",
                    }
                ],
                "next": None,
                "previous": None,
                "meta": {"authorized": True},
            }

        profile = mock_remote_data["data"][0]["profile"]
        mock_remote_data_members = {"results": profile}
        return mock_remote_data, mock_remote_data_members

    return convert_user_data_to_remote_data


class AugmentedUserFixture(UserFixtureBase):
    """Augmented UserFixtureBase class."""

    def __init__(self, *args, **kwargs):
        """Initialize the AugmentedUserFixture."""
        super().__init__(*args, **kwargs)
        self.mock_adapter: Matcher | None = None
        self.allowed_token: str | None = None


@pytest.fixture(scope="function")
def user_factory(
    app,
    db,
    admin_role_need,
    requests_mock,
    mock_user_data_api,
    user_data_to_remote_data,
) -> Callable:
    """Factory for creating test users.

    Returns:
        a factory function that returns a user.
    """

    def make_user(
        email: str = "myuser@inveniosoftware.org",
        password: str = "password",
        token: bool = False,
        admin: bool = False,
        oauth_src: str | None = "cilogon",
        oauth_id: str | None = "1234",
        orcid: str | None = "",
        kc_username: str | None = "myuser",
        new_remote_data: dict | None = None,
    ) -> AugmentedUserFixture:
        """Create an augmented pytest-invenio user fixture.

        Parameters:
            email: The email address of the user.
            password: The password of the user.
            token: Whether the user should have a token.
            admin: Whether the user should have admin access.
            oauth_src: The source of the user's oauth authentication.
            oauth_id: The user's ID for oauth authentication.
            kc_username: The user's username on Knowledge Commons.
            new_remote_data: The user's remote data for mocking api responses.

        Returns:
            The created UserFixture object. This has the following attributes:
            - user: The created Invenio User object.
            - mock_adapter: The requests_mock adapter for the api call to
                sync user data from the remote service.
            - identity: The identity of the user.
            - allowed_token: The API auth token of the user.
        """
        new_remote_data = new_remote_data or {}

        # Mock remote data that's already in the user fixture.
        mock_remote_data_subs, mock_remote_data_members = user_data_to_remote_data(
            kc_username,
            new_remote_data.get("email") or email,
            new_remote_data,
            oauth_id,
        )
        # Mock the remote api call.
        mock_adapter_subs, mock_adapter_members = mock_user_data_api(
            kc_username, oauth_id, mock_remote_data_subs, mock_remote_data_members
        )

        if not orcid and new_remote_data.get("orcid"):
            orcid = new_remote_data.get("orcid")

        u = AugmentedUserFixture(
            email=email,
            password=hash_password(password),
        )
        u.create(app, db)

        if token:
            u.allowed_token = Token.create_personal(
                "webhook",
                u.id,
                scopes=[],  # , is_internal=False
            ).access_token

        if admin:
            datastore = app.extensions["security"].datastore
            _, role = datastore._prepare_role_modify_args(
                u.user, "administration-access"
            )
            datastore.add_role_to_user(u.user, role)

        if u.user and orcid:
            profile = u.user.user_profile
            profile["identifier_orcid"] = orcid
            u.user.user_profile = profile

        if u.user and kc_username:
            profile = u.user.user_profile
            profile["identifier_kc_username"] = kc_username
            u.user.user_profile = profile

        if u.user and oauth_src and oauth_id:
            u.user.username = f"knowledgeCommons-{oauth_id}"
            UserIdentity.create(u.user, oauth_src, oauth_id)
            u.mock_adapter_members = mock_adapter_members
            u.mock_adapter_subs = mock_adapter_subs

        u.user.mock = True

        current_accounts.datastore.commit()
        db.session.commit()

        return u

    return make_user


@pytest.fixture(scope="function")
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.

    Returns:
        Role: The created admin role.
    """
    role = Role(name="administration-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=administration_access_action, role=role)
    db.session.add(action_role)

    db.session.commit()
    return action_role.need


@pytest.fixture(scope="function")
def admin(user_factory) -> AugmentedUserFixture:
    """Admin user for requests.

    Returns:
        AugmentedUserFixture: Admin user fixture.
    """
    u: AugmentedUserFixture = user_factory(
        email="admin@inveniosoftware.org",
        password="password",
        admin=True,
        token=True,
        oauth_src="knowledgeCommons",
        oauth_id="admin",
    )

    return u


@pytest.fixture(scope="function")
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.

    Returns:
        Role: The created superuser role.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="function")
def superuser_identity(
    admin: AugmentedUserFixture, superuser_role_need, db
) -> Identity:
    """Superuser identity fixture.

    Returns:
        Identity: Superuser identity.
    """
    # Merge the user to ensure it's attached to the current session
    merged_user = db.session.merge(admin.user)
    identity = get_identity(merged_user)
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="module")
def user1_data() -> dict:
    """Data for user1.

    Returns:
        dict: User data dictionary.
    """
    return {
        "data": [
            {
                "sub": "user1",
                "profile": {
                    "oauth_id": "1",
                    "username": "user1",
                    "email": "user1@inveniosoftware.org",
                    "name": "User Number One",
                    "first_name": "User Number",
                    "last_name": "One",
                    "institutional_affiliation": "Michigan State University",
                    "orcid": "0000-0002-1825-0097",  # official dummy orcid
                    "preferred_language": "en",
                    "time_zone": "UTC",
                    "groups": [
                        {"id": 12345, "name": "awesome-mock", "role": "admin"},
                        {"id": 67891, "name": "admin", "role": "member"},
                    ],
                },
            }
        ],
        "next": None,
        "previous": None,
        "meta": {"authorized": True},
    }


user_data_set = {
    "joanjett": {
        "oauth_id": "joanjett1",
        "kc_username": "joanjett",
        "email": "jj@inveniosoftware.com",
        "name": "Joan Jett",
        "first_name": "Joan",
        "last_name": "Jett",
        "institutional_affiliation": "Uc Davis",
        "orcid": "",
        "groups": [],
    },
    "user1": {
        "oauth_id": "id1",
        "kc_username": "user1",
        "email": "user1@inveniosoftware.org",
        "name": "User Number One",
        "first_name": "User Number",
        "last_name": "One",
        "institutional_affiliation": "Michigan State University",
        "orcid": "0000-0002-1825-0097",  # official dummy orcid
        "preferred_language": "en",
        "time_zone": "UTC",
        "groups": [
            {"id": 12345, "name": "awesome-mock", "role": "administrator"},
            {"id": 67891, "name": "admin", "role": "member"},
        ],
    },
    "user2": {
        "oauth_id": "doe2",
        "kc_username": "janedoe",
        "email": "jane.doe@msu.edu",
        "name": "Jane Doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "institutional_affiliation": "College Of Human Medicine",
        "orcid": "0000-0002-1825-0097",  # official dummy orcid
    },
    "user3": {
        "oauth_id": "gihctester3",
        "kc_username": "gihctester",
        "email": "ghosthc@email.ghostinspector.com",
        # FIXME: Unobfuscated email not sent by
        # KC because no email marked as official.
        # Also, different email address than shown in KC profile.
        "name": "Ghost Hc",
        "first_name": "Ghost",
        "last_name": "Hc",
        "groups": [
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
            {
                "id": 1004939,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004940,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004941,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004942,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004943,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004944,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004945,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004946,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004947,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004948,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004949,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004950,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004951,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004952,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
            {
                "id": 1004953,
                "name": "GI Hidden Group for testing",
                "role": "admin",
            },
        ],
    },
    "user4": {
        "oauth_id": "ghostrjtester4",
        "kc_username": "ghostrjtester",
        "email": "jrghosttester@email.ghostinspector.com",
        "name": "Ghost Tester",
        "first_name": "Ghost",
        "last_name": "Tester",
        "institutional_affiliation": "Michigan State University",
        "orcid": "0000-0002-1825-0097",  # official dummy orcid
        "groups": [],
    },
}


@pytest.fixture(scope="function")
def client_with_login(requests_mock, app):
    """Log in a user to the client.

    Returns a factory function that returns a client with a logged in user.

    Returns:
        function: Function to log in a user to a client.
    """

    def log_in_user(
        client,
        user: User,
    ):
        """Log in a user to the client.

        Parameters:
            client: The client to log in with.
            user: The user to log in.

        Returns:
            None: This function doesn't return anything.
        """
        login_user(user)
        login_user_via_session(client, email=user.email)
        return client

    return log_in_user
