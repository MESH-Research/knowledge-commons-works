# Part of Knowledge Commons Works
#
# Copyright (C) 2025 MESH Research.
#
# Knowledge Commons Works is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User related pytest fixtures for testing."""

import os
from collections.abc import Callable

import pytest
from flask_login import login_user
from flask_principal import Identity
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import any_user, authenticated_user, superuser_access
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
def mock_user_data_api(requests_mock) -> Callable:
    """Mock the user data api."""

    def mock_api_call(saml_id: str, mock_remote_data: dict) -> Matcher:
        protocol = os.environ.get(
            "INVENIO_COMMONS_API_REQUEST_PROTOCOL", "https"
        )  # noqa: E501
        base_url = f"{protocol}://hcommons-dev.org/wp-json/commons/v1/users"
        remote_url = f"{base_url}/{saml_id}"
        mock_adapter = requests_mock.get(
            remote_url,
            json=mock_remote_data,
        )
        return mock_adapter

    return mock_api_call


@pytest.fixture(scope="function")
def user_data_to_remote_data(requests_mock):
    """Factory fixture providing function to convert user data format."""

    def convert_user_data_to_remote_data(
        saml_id: str, email: str, user_data: dict
    ) -> dict[str, str | list[dict[str, str]]]:
        """Convert user fixture data to format for remote data."""
        mock_remote_data = {
            "username": saml_id,
            "email": email,
            "name": user_data.get("name", ""),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "institutional_affiliation": user_data.get("institutional_affiliation", ""),
            "orcid": user_data.get("orcid", ""),
            "preferred_language": user_data.get("preferred_language", ""),
            "time_zone": user_data.get("time_zone", ""),
            "groups": user_data.get("groups", ""),
        }
        return mock_remote_data

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
        saml_src: str | None = "knowledgeCommons",
        saml_id: str | None = "myuser",
        orcid: str | None = "",
        kc_username: str | None = "",
        new_remote_data: dict | None = None,
    ) -> AugmentedUserFixture:
        """Create an augmented pytest-invenio user fixture.

        Parameters:
            email: The email address of the user.
            password: The password of the user.
            token: Whether the user should have a token.
            admin: Whether the user should have admin access.
            saml_src: The source of the user's saml authentication.
            saml_id: The user's ID for saml authentication.

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
        mock_remote_data = user_data_to_remote_data(
            saml_id, new_remote_data.get("email") or email, new_remote_data
        )
        # Mock the remote api call.
        mock_adapter = mock_user_data_api(saml_id, mock_remote_data)

        if not orcid and new_remote_data.get("orcid"):
            orcid = new_remote_data.get("orcid")

        u = AugmentedUserFixture(
            email=email,
            password=hash_password(password),
        )
        u.create(app, db)

        if token:
            u.allowed_token = Token.create_personal(
                "webhook", u.id, scopes=[]  # , is_internal=False
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

        if u.user and saml_src and saml_id:
            u.user.username = f"{saml_src}-{saml_id}"
            profile = u.user.user_profile
            profile["identifier_kc_username"] = saml_id
            u.user.user_profile = profile
            UserIdentity.create(u.user, saml_src, saml_id)
            u.mock_adapter = mock_adapter

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
    """
    role = Role(name="administration-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=administration_access_action, role=role)
    db.session.add(action_role)

    db.session.commit()
    return action_role.need


@pytest.fixture(scope="function")
def admin(user_factory) -> AugmentedUserFixture:
    """Admin user for requests."""
    u: AugmentedUserFixture = user_factory(
        email="admin@inveniosoftware.org",
        password="password",
        admin=True,
        token=True,
        saml_src="knowledgeCommons",
        saml_id="admin",
    )

    return u


@pytest.fixture(scope="function")
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="function")
def superuser_identity(admin: AugmentedUserFixture, superuser_role_need) -> Identity:
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="module")
def user1_data() -> dict:
    """Data for user1."""
    return {
        "saml_id": "user1",
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
    }


user_data_set = {
    "joanjett": {
        "saml_id": "joanjett",
        "email": "jj@inveniosoftware.com",
        "name": "Joan Jett",
        "first_name": "Joan",
        "last_name": "Jett",
        "institutional_affiliation": "Uc Davis",
        "orcid": "",
        "groups": [],
    },
    "user1": {
        "saml_id": "user1",
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
        "saml_id": "janedoe",
        "email": "jane.doe@msu.edu",
        "name": "Jane Doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "institutional_affiliation": "College Of Human Medicine",
        "orcid": "0000-0002-1825-0097",  # official dummy orcid
    },
    "user3": {
        "saml_id": "gihctester",
        "email": "ghosthc@lblyoehp.mailosaur.net",
        # FIXME: Unobfuscated email not sent by
        # KC because no email marked as official.
        # Also, different email address than shown in KC profile.
        "name": "Ghost Hc",
        "first_name": "Ghost",
        "last_name": "Hc",
        "groups": [
            {"id": 1004089, "name": "Teaching and Learning", "role": "member"},
            {"id": 1004090, "name": "Humanities, Arts, and Media", "role": "member"},
            {
                "id": 1004091,
                "name": "Technology, Networks, and Sciences",
                "role": "member",
            },
            {"id": 1004092, "name": "Social and Political Issues", "role": "member"},
            {
                "id": 1004093,
                "name": "Educational and Cultural Institutions",
                "role": "member",
            },
            {"id": 1004094, "name": "Publishing and Archives", "role": "member"},
            {
                "id": 1004651,
                "name": "Hidden Testing Group New Name",
                "role": "administrator",
            },
            {
                "id": 1004939,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004940,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004941,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004942,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004943,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004944,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004945,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004946,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004947,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004948,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004949,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004950,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004951,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004952,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
            {
                "id": 1004953,
                "name": "GI Hidden Group for testing",
                "role": "administrator",
            },
        ],
    },
    "user4": {
        "saml_id": "ghostrjtester",
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
    """

    def log_in_user(
        client,
        user: User,
    ):
        """Log in a user to the client.

        Parameters:
            client: The client to log in with.
            user: The user to log in.
        """
        login_user(user)
        login_user_via_session(client, email=user.email)
        return client

    return log_in_user
