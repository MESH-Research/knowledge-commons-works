# Part of Knowledge Commons Works
# Copyright (C) MESH Research, 2023
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Custom field for legacy groups_for_deposit from the CORE repository.

This field is not used in the current repository, but is retained as legacy
data.
"""

from invenio_records_resources.services.custom_fields import BaseListCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class GroupsForDepositCF(BaseListCF):
    """Custom field for legacy groups_for_deposit from the CORE repository."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args={
                "nested": {
                    "group_name": SanitizedUnicode(),
                    "group_identifier": SanitizedUnicode(),
                }
            },
            multiple=True,
            **kwargs,
        )

    @property
    def mapping(self):
        """groups_for_deposit search mappings."""
        return {
            "type": "object",
            "properties": {
                "group_name": {"type": "text"},
                "group_identifier": {"type": "text"},
            },
        }


HCLEGACY_GROUPS_FOR_DEPOSIT_FIELD = [
    GroupsForDepositCF(name="hclegacy:groups_for_deposit"),
]
