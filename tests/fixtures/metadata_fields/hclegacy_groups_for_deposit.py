"""Metadata fields for legacy groups for deposit.

hclegacy:groups_for_deposit       The groups that the user belongs to. This value
                                  is an array of objects, each with the keys
                                  "group_name" and "group_identifier".
"""

from invenio_records_resources.services.custom_fields import BaseListCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class GroupsForDepositCF(BaseListCF):
    """Custom field for groups for deposit."""

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
        """Groups for deposit search mappings."""
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
