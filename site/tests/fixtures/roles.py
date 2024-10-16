import pytest
from invenio_accounts.proxies import current_accounts


@pytest.fixture(scope="module")
def admin_roles():
    current_accounts.datastore.create_role(name="admin-moderator")
    current_accounts.datastore.create_role(name="administrator")
