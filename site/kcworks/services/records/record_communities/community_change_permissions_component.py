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

"""Service component allowing fine-grained control of changing record communities."""

from pprint import pformat
from typing import Any

from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_communities.errors import SetDefaultCommunityError
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import UnitOfWork
from kcworks.services.records.permissions import per_field_edit_permission_factory


class CommunityChangePermissionsComponent(ServiceComponent):
    """Service component that prevents unauthorized changes to a record's communities.

    Intended for use with the RecordCommunitiesService from invenio-rdm-records.
    """

    def _check_default_community_permission(
        self,
        identity: Identity,
        record: RDMRecord,
        action: str,
        old_default_community_id: str | None = None,
    ) -> None:
        """Check if the identity has permission to modify the default community.

        Parameters:
            identity (Any): The identity to check permissions for
            record (RDMRecord): The record containing the default community
            action (str): The action being performed ("remove" or "change")
            old_default_community_id (str | None, optional): The default community ID
                to check permissions for. Defaults to None.

        Raises:
            PermissionDeniedError: If the identity doesn't have permission
            SetDefaultCommunityError: If the identity doesn't have permission to change
                the default community
        """
        if not (
            record.parent
            and record.parent.communities  # type: ignore
            and record.parent.communities.default  # type: ignore
        ):
            return

        permission_community = (
            old_default_community_id
            if old_default_community_id
            else record.parent.communities.default.id  # type: ignore
        )
        current_app.logger.info(
            f"checking default community permission for: "
            f"{action} {permission_community}"
        )

        # Get the permissions configuration for the community
        community_configs = current_app.config.get(
            "RDM_RECORDS_PERMISSIONS_PER_FIELD", {}
        )
        community = current_communities.service.read(
            system_identity, id_=permission_community
        )
        community_config = community_configs.get(community.data["slug"], {})

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
        current_app.logger.info(f"policy: {policy}")
        # If the field is restricted, check permissions
        if "parent.communities.default" in policy:
            current_app.logger.info(f"policy has default community: {policy}")
            community_field_policy = per_field_edit_permission_factory(
                community_id=permission_community,
                roles=policy["parent.communities.default"],
            )
            current_app.logger.info(
                f"community_field_policy allows? {community_field_policy.allows(identity)}"
            )
            if not community_field_policy.allows(identity):
                raise PermissionDeniedError(
                    f"You do not have permission to {action} this default community. "
                    f"Please contact the community owner or manager for assistance."
                )

    def remove(
        self,
        identity: Identity,
        record: RDMRecord,
        communities: list[dict[str, Any]],
        errors: list[dict[str, Any]],
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> None:
        """Prevent unauthorized removal of the default community from a record.

        If the permissions are not granted, the default community is not removed.
        An error is added to the errors list for the service operation.

        Parameters:
            identity (Any): The identity performing the action
            _id (str): The record ID
            data (dict[str, Any]): The data containing the communities to remove
            errors (list[dict[str, Any]]): The errors to add to
            uow (UnitOfWork | None, optional): The unit of work manager. Defaults
                to None.
            **kwargs (Any): Additional keyword arguments
        """
        communities_to_remove = [c["id"] for c in communities]
        current_app.logger.info(f"communities_to_remove: {communities_to_remove}")
        if (
            record.parent
            and record.parent.communities  # type: ignore
            and record.parent.communities.default  # type: ignore
        ):
            default_community_id = record.parent.communities.default.id  # type: ignore
            current_app.logger.info(
                f"default_community_id in remove: {default_community_id}"
            )
            if str(default_community_id) in communities_to_remove:
                try:
                    self._check_default_community_permission(identity, record, "remove")
                except PermissionDeniedError:
                    communities.remove(
                        next(
                            c
                            for c in communities
                            if c["id"] == str(default_community_id)
                        )
                    )
                    current_app.logger.info(
                        f"communities after removing default: {communities}"
                    )
                    errors.append(
                        {
                            "field": "parent.communities.default",
                            "message": (
                                "You do not have permission to remove this community: "
                                f"{default_community_id}. Please contact the community"
                                " owner or manager for assistance."
                            ),
                        }
                    )

    def set_default(
        self,
        identity: Identity,
        record: RDMRecord,
        default_community_id: str | None,
        valid_data: dict[str, Any],
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> None:
        """Prevent unauthorized changes to the default community.

        If the permissions are not granted, the default community is not changed.
        An error is raised.

        Parameters:
            identity (Any): The identity performing the action
            record (RDMRecord): The record containing the default community
            default_community_id (str | None): The new default community ID
            valid_data (dict[str, Any]): The data containing the new default community
            uow (UnitOfWork | None, optional): The unit of work manager. Defaults
                to None.
            **kwargs (Any): Additional keyword arguments

        Raises:
            PermissionDeniedError: If the identity doesn't have permission
        """
        if record.is_published:
            published_version_rec = RDMRecord.get_latest_published_by_parent(
                record.parent
            )
            published_version = current_rdm_records_service.read(
                system_identity,
                id_=published_version_rec.pid.pid_value,  # type: ignore
            )
            current_app.logger.info(
                f"published_version entries: {pformat(published_version._record.parent.communities.entries)}"
            )
            current_app.logger.info(
                f"published_version default: {pformat(published_version.data['parent']['communities'].get('default'))}"
            )
            if published_version._record.parent.communities.default:
                previous_default_id = (
                    published_version._record.parent.communities.default.id  # type: ignore
                )
            else:
                previous_default_id = None
            current_app.logger.info(f"previous_default_id: {previous_default_id}")

            if previous_default_id != default_community_id:
                current_app.logger.info(
                    f"new default community id: {default_community_id}"
                )
                try:
                    self._check_default_community_permission(
                        identity,
                        record,
                        "change",
                        old_default_community_id=previous_default_id,
                    )
                except PermissionDeniedError as e:
                    raise SetDefaultCommunityError() from e
