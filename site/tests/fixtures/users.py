from typing import Callable
from flask_login import login_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access
from invenio_accounts.models import User
from invenio_accounts.testutils import login_user_via_session
from invenio_administration.permissions import administration_access_action
from invenio_oauthclient.models import UserIdentity
from invenio_oauth2server.models import Token
import os
import pytest


@pytest.fixture(scope="function")
def user_factory(
    UserFixture, app, db, admin_role_need, requests_mock
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
        saml_src: str = "knowledgeCommons",
        saml_id: str = "myuser",
        new_remote_data: dict = {},
    ) -> UserFixture:
        """Create a user.

        Args:
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

        # Mock remote data that's already in the user fixture.
        mock_remote_data = {
            "username": saml_id,
            "email": email,
            "name": new_remote_data.get("name", ""),
            "first_name": new_remote_data.get("first_name", ""),
            "last_name": new_remote_data.get("last_name", ""),
            "institutional_affiliation": new_remote_data.get(
                "institutional_affiliation", ""
            ),
            "orcid": new_remote_data.get("orcid", ""),
            "preferred_language": new_remote_data.get(
                "preferred_language", ""
            ),
            "time_zone": new_remote_data.get("time_zone", ""),
            "groups": new_remote_data.get("groups", ""),
        }

        # Mock the remote api call.
        base_url = "https://hcommons-dev.org/wp-json/commons/v1/users"
        remote_url = f"{base_url}/{saml_id}"
        mock_adapter = requests_mock.get(
            remote_url,
            json=mock_remote_data,
        )

        u = UserFixture(
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

        if saml_src and saml_id:
            UserIdentity.create(u.user, saml_src, saml_id)
            u.mock_adapter = mock_adapter

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

    action_role = ActionRoles.create(
        action=administration_access_action, role=role
    )
    db.session.add(action_role)

    db.session.commit()
    return action_role.need


@pytest.fixture(scope="function")
def admin(user_factory):
    """Admin user for requests."""

    u = user_factory(
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
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="module")
def user1_data():
    """Data for user1."""

    return {
        "saml_id": "user1",
        "email": "user1@inveniosoftware.org",
        "name": "User One",
        "first_name": "User",
        "last_name": "One",
        "institutional_affiliation": "Michigan State University",
        "orcid": "123-456-7891",
        "preferred_language": "en",
        "time_zone": "UTC",
        "groups": [
            {"id": 12345, "name": "awesome-mock", "role": "admin"},
            {"id": 67891, "name": "admin", "role": "member"},
        ],
    }


@pytest.fixture(scope="function")
def client_with_login(requests_mock, app):
    """Log in a user to the client.

    Returns a factory function that returns a client with a logged in user.

    Args:
        user: The user to log in.
        new_remote_data: Optional. Data absent from the user's initial data
            that should be added in the mocked remote API call at login.
    """

    def log_in_user(
        client,
        user: User,
        new_remote_data: dict = {},
    ):
        saml_id = user.external_identifiers[0].id
        token = os.getenv("COMMONS_API_TOKEN")

        # Mock remote data that's already in the user fixture.
        mock_remote_data = {
            "username": saml_id,
            "email": user.email,
            "name": user.user_profile.get("full_name", ""),
            "first_name": user.user_profile.get("first_name", ""),
            "last_name": user.user_profile.get("last_name", ""),
            "institutional_affiliation": user.user_profile.get(
                "affiliations", ""
            ),
            "orcid": user.user_profile.get("orcid", ""),
            "preferred_language": user.user_profile.get(
                "preferred_language", ""
            ),
            "time_zone": user.user_profile.get("time_zone", ""),
            "groups": user.user_profile.get("groups", ""),
        }

        # Mock adding any missing data from remote API call.
        mock_remote_data.update(new_remote_data)

        # Mock the remote api call.
        base_url = "https://hcommons-dev.org/wp-json/commons/v1/users"
        remote_url = f"{base_url}/{saml_id}"
        mock_adapter = requests_mock.get(
            remote_url,
            json=mock_remote_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        login_user(user)
        login_user_via_session(client, email=user.email)
        return client, mock_adapter

    return log_in_user
