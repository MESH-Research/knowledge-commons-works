"""KCWorks override of ``CommunityParentComponent``.

Upstream ``invenio-communities`` limits community nesting to one level by
rejecting:

- a parent that already has a parent
- a child with ``children.allow=True``

KCWorks allows arbitrary nesting depth for subcommunity hierarchies.
"""

from __future__ import annotations

from invenio_communities.communities.services.components import (
    CommunityParentComponent as BaseCommunityParentComponent,
)
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from marshmallow.exceptions import ValidationError


class CommunityParentComponent(BaseCommunityParentComponent):
    """Community parent component without one-level nesting restrictions."""

    def _validate_and_get_parent(self, parent_data, child):
        """Validate and return parent community.

        Args:
            parent_data: Parent community payload from the service request.
            child: Child community record being linked.

        Returns:
            Resolved parent community record, or ``None`` when ``parent_data`` is
            empty.

        Raises:
            ValidationError: When the parent is invalid or disallowed.
        """
        if not parent_data:
            return None
        try:
            parent = self.service.record_cls.pid.resolve(parent_data["id"])
            if not parent.children.allow:
                raise ValidationError(
                    str(_("Assigned parent is not allowed to be a parent."))
                )
            elif child.id == parent.id:
                raise ValidationError(
                    str(
                        _("Assigned parent community cannot be the same as child.")
                    )
                )
        except PIDDoesNotExistError:
            raise ValidationError(
                str(_("Assigned parent community does not exist."))
            ) from None
        return parent
