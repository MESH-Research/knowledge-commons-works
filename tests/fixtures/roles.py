# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Roles related pytest fixtures for testing."""

import pytest
from invenio_accounts.proxies import current_accounts


@pytest.fixture(scope="module")
def admin_roles():
    """Fixture to create admin roles."""
    current_accounts.datastore.create_role(name="admin-moderator")
    current_accounts.datastore.create_role(name="administration")
    current_accounts.datastore.create_role(name="administration-moderation")
