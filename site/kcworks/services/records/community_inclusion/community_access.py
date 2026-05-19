# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Disable RDM's 'public record cannot be added to restricted community' check.

When adding or publishing a record to a community, invenio-rdm-records calls
``is_access_restriction_valid(record, community)`` and raises
InvalidAccessRestrictions if a public record is added to a restricted community.
We patch that function to always allow (return True), so community visibility
can be changed (e.g. from remote sync) without blocking existing or new records.
No changes to invenio-rdm-records source are required.
"""


def _allow_all_access_restrictions(record, community) -> bool:
    """Always allow; disables the public-record-in-restricted-community check.

    Returns:
        True in every case
    """
    return True


def patch_community_access_restriction_check() -> None:
    """Patch RDM's is_access_restriction_valid to always allow.

    Call once at app init (e.g. from kcworks.ext init_components).
    """
    from invenio_rdm_records import requests as rdm_requests

    rdm_requests.community_inclusion.is_access_restriction_valid = (
        _allow_all_access_restrictions
    )
