"""Tests for KCWorks customizations of community access rules.

KCWorks swaps `invenio-rdm-records`' stricter `CommunityAccessComponent`
for the base `invenio-communities` one in `COMMUNITIES_SERVICE_COMPONENTS`.
The base component allows visibility changes that KCWorks needs for remote
group visibility sync and related administrative workflows.
"""

from __future__ import annotations

from invenio_communities.communities.services.components import (  # type: ignore[import-not-found]
    CommunityAccessComponent as BaseCommunityAccessComponent,
)
from invenio_rdm_records.services.communities.components import (  # type: ignore[import-untyped]
    CommunityAccessComponent as RDMCommunityAccessComponent,
)


def test_ext_swaps_rdm_access_for_base_access(running_app) -> None:
    """KCWorks replaces RDM's stricter access component with the base one."""
    components = running_app.app.config["COMMUNITIES_SERVICE_COMPONENTS"]
    assert BaseCommunityAccessComponent in components
    assert RDMCommunityAccessComponent not in components
