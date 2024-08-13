from invenio_accounts.proxies import current_accounts
from invenio_saml.invenio_accounts.utils import account_link_external_id
from invenio_oauthclient.errors import AlreadyLinkedError


def knowledgeCommons_account_setup(user, account_info):
    """SAML account setup which extends invenio_saml default.

    The default only links ``User`` and ``UserIdentity``. This
    also ensures that the user is activated once

    """
    try:
        account_link_external_id(
            user,
            dict(
                id=account_info["external_id"],
                method=account_info["external_method"],
            ),
        )
        if not user.active:
            assert current_accounts.datastore.activate_user(user)
        current_accounts.datastore.commit()
    except AlreadyLinkedError:
        pass
