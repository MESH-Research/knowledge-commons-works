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

from typing import Any, cast

from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_communities.errors import SetDefaultCommunityError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import UnitOfWork
from kcworks.services.records.components.per_field_permissions_component import (
    PerFieldEditPermissionsComponent,
)
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
        old_record: RDMRecord | None = None,
    ) -> bool:
        """Check if the identity has permission to modify the default community.

        Parameters:
            identity (Any): The identity to check permissions for
            record (RDMRecord): The record containing the default community
            action (str): The action being performed ("remove" or "change")
            old_record (RDMRecord | None, optional): The previous version of the record
                to check permissions for. Defaults to None.

        Returns:
            bool: True if the identity has permission, False otherwise

        Raises:
            PermissionDeniedError: If the identity doesn't have permission
        """
        if not (
            record.parent
            and record.parent.communities  # type: ignore
            and record.parent.communities.default  # type: ignore
        ):
            return True

        communities = (
            old_record.parent.communities  # type: ignore
            if old_record
            else record.parent.communities  # type: ignore
        )

        # Get the permissions configuration for the community
        community_config = PerFieldEditPermissionsComponent.get_permissions_config(
            communities
        )

        # Check if the field is restricted
        policy = community_config.get("policy", {})
        # If the field is restricted, check permissions
        if "parent.communities.default" in policy.keys():
            community_field_policy = per_field_edit_permission_factory(
                community_id=communities.default.id,  # type: ignore
                roles=policy["parent.communities.default"],
            )
            if not community_field_policy.allows(identity):
                raise PermissionDeniedError(
                    f"You do not have permission to {action} this default community. "
                    f"Please contact the community owner or manager for assistance."
                )
        return True

    def remove_community(
        self,
        identity: Identity,
        uow: UnitOfWork | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Prevent unauthorized removal of the default community from a record.

        If the permissions are not granted, the default community is not removed.
        An error is added to the errors list for the service operation.

        Parameters:
            identity (Any): The identity performing the action
            uow (UnitOfWork | None, optional): The unit of work manager. Defaults
                to None.
            **kwargs (Any): Additional keyword arguments
        """
        record = cast(RDMRecord, kwargs.get("record"))
        errors = cast(list, kwargs.get("errors"))
        # valid_data = kwargs.get("valid_data")
        communities_to_remove = [kwargs.get("community", {}).get("id")]
        if (
            record.parent is not None
            and record.parent.communities  # type: ignore
            and record.parent.communities.default  # type: ignore
        ):
            default_community = record.parent.communities.default  # type: ignore
            default_community_title = (
                default_community.metadata.get("title", "") or default_community.slug
            )
            if str(default_community.id) in communities_to_remove:
                try:
                    self._check_default_community_permission(identity, record, "remove")
                except PermissionDeniedError as e:
                    errors.append({
                        "field": "parent.communities.default",
                        "message": (
                            "You do not have permission to remove this work from "
                            f"{default_community_title}. "
                            "Please contact the collection"
                            " owner or manager for assistance."
                        ),
                    })
                    raise e

    def set_default(
        self,
        identity: Identity,
        record: RDMRecord | None = None,
        default_community_id: str | None = None,
        valid_data: dict[str, Any] | None = None,
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> None:
        """Prevent unauthorized changes to the default community.

        If the permissions are not granted, the default community is not changed.
        An error is raised.

        Note: This component is limited to raising the handled errors in the
            configuration for the RDMRecordCommunitiesResource if we want the error
            to be passed to the client.

        Parameters:
            identity (Any): The identity performing the action
            record (RDMRecord): The record containing the default community
            default_community_id (str | None): The new default community ID
            valid_data (dict[str, Any]): The data containing the new default community
            uow (UnitOfWork | None, optional): The unit of work manager. Defaults
                to None.
            **kwargs (Any): Additional keyword arguments

        Raises:
            SetDefaultCommunityError: If the identity doesn't have permission to change
                the default community
        """
        if record and record.is_published:
            published_version_rec = RDMRecord.get_latest_published_by_parent(
                record.parent
            )
            # NOTE: This is a hack to get the previous version of the record
            #       via the search engine which has not yet been updated
            #       with changes made during the current service operation.
            published_version = current_rdm_records_service.read(
                system_identity,
                id_=published_version_rec.pid.pid_value,  # type: ignore
            )
            if published_version._record.parent.communities.default:  # type: ignore
                previous_default_id = (
                    published_version._record.parent.communities.default.id
                )
            else:
                previous_default_id = None

            if previous_default_id != default_community_id:
                try:
                    self._check_default_community_permission(
                        identity,
                        record,
                        "change",
                        old_record=published_version._record,
                    )
                except PermissionDeniedError as e:
                    raise SetDefaultCommunityError() from e
