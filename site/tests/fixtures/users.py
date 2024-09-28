from flask_login import login_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access
from invenio_accounts.testutils import login_user_via_session
from invenio_administration.permissions import administration_access_action
from invenio_oauthclient.models import UserIdentity
from invenio_oauth2server.models import Token
import pytest


@pytest.fixture(scope="function")
def user_factory(UserFixture, app, db, admin_role_need):
    """Factory for creating test users."""

    def make_user(
        email: str = "myuser@inveniosoftware.org",
        password: str = "password",
        token: bool = False,
        admin: bool = False,
        saml: str = "knowledgeCommons",
    ) -> UserFixture:
        u = UserFixture(
            email=email,
            password=password,
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

        if saml:
            UserIdentity.create(u.user, "knowledgeCommons", "myuser")

        db.session.commit()

        return u

    return make_user


@pytest.fixture()
def users(UserFixture, app, db) -> list:
    """Create example user."""
    # user1 = UserFixture(
    #     email="scottia4@msu.edu",
    #     password="password"
    # )
    # user1.create(app, db)
    # user2 = UserFixture(
    #     email="scottianw@gmail.com",
    #     password="password"
    # )
    # user2.create(app, db)
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="ser-testalot@inveniosoftware.org",
            password=hash_password("beetlesmasher"),
            active=True,
        )

    db.session.commit()
    return [user1, user2]


@pytest.fixture()
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


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    u.allowed_token = Token.create_personal(
        "webhook", u.id, scopes=[]  # , is_internal=False
    ).access_token

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(
        u.user, "administration-access"
    )

    UserIdentity.create(u.user, "knowledgeCommons", "myuser")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture()
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


@pytest.fixture()
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    # user = users[0].user
    # pprint('^^^^^^^')
    # pprint(user.__class__())
    # pprint(dir(user))
    login_user(user)
    login_user_via_session(client, email=user.email)
    return client
