from typing import Any, Dict, Optional

from flask import current_app
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import UnitOfWork
from kcworks.services.records.permissions import per_field_edit_permission_factory
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_rdm_records.records.api import RDMRecord


class CommunityChangePermissionsComponent(ServiceComponent):
    """
    A service component that prevents unauthorized changes to the community of a record

    Intended for use with the RecordCommunitiesService from invenio-rdm-records.
    """

    def _check_default_community_permission(
        self,
        identity: Any,
        record: RDMRecord,
        action: str,
    ) -> None:
        """
        Check if the identity has permission to modify the default community.

        Args:
            identity: The identity to check permissions for
            record: The record containing the default community
            action: The action being performed ("remove" or "change")

        Raises:
            PermissionDeniedError: If the identity doesn't have permission
        """
        if not (
            record.parent
            and record.parent.communities
            and record.parent.communities.default
        ):
            return

        # Get the permissions configuration for the community
        community_configs = current_app.config.get(
            "RDM_RECORDS_PERMISSIONS_PER_FIELD", {}
        )
        community_config = community_configs.get(
            record.parent.communities.default.slug, {}
        )

        if not community_config:
            community_config = community_configs.get("default", {})

        # Check if the field is restricted
        policy = community_config.get("policy", {})
        if isinstance(policy, list):
            if "parent.communities.default" in policy:
                # Use default editors for the community
                default_editors = community_config.get(
                    "default_editors", ["manager", "owner", "curator"]
                )
                policy = {"parent.communities.default": default_editors}
            else:
                policy = {}

        # If the field is restricted, check permissions
        if "parent.communities.default" in policy:
            community_field_policy = per_field_edit_permission_factory(
                community_id=(
                    record.parent.communities.default.id
                    if record.parent
                    and record.parent.communities
                    and record.parent.communities.default
                    else "default"
                ),
                roles=policy["parent.communities.default"],
            )
            if not community_field_policy.allows(identity):
                raise PermissionDeniedError(
                    f"You do not have permission to {action} this default community. "
                    f"Please contact the community owner or manager for assistance."
                )

    def remove(
        self,
        identity: Any,
        _id: str,
        data: Dict[str, Any],
        uow: Optional[UnitOfWork] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prevent unauthorized removal of communities from a record.

        Args:
            identity: The identity performing the action
            _id: The record ID
            data: The data containing the communities to remove
            uow: The unit of work manager
            **kwargs: Additional keyword arguments
        """
        # Resolve the record from the id using the service's record_cls
        record = self.service.record_cls.pid.resolve(_id)

        # Check if any of the communities to be removed is the default community
        communities_to_remove = [c["id"] for c in data.get("communities", [])]
        if (
            record.parent
            and record.parent.communities
            and record.parent.communities.default
        ):
            default_community_id = record.parent.communities.default.id
            if default_community_id in communities_to_remove:
                self._check_default_community_permission(identity, record, "remove")

    def set_default(
        self,
        identity: Any,
        _id: str,
        data: Dict[str, Any],
        uow: Optional[UnitOfWork] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prevent unauthorized changes to the default community.

        Args:
            identity: The identity performing the action
            _id: The record ID
            data: The data containing the new default community
            uow: The unit of work manager
            **kwargs: Additional keyword arguments
        """
        # Resolve the record from the id using the service's record_cls
        record = self.service.record_cls.pid.resolve(_id)

        # Get the new default community ID from the data
        new_default_id = data.get("default", {}).get("id")
        if new_default_id:
            self._check_default_community_permission(identity, record, "change")
