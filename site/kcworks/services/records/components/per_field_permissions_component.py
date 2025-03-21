from pprint import pformat
from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import UnitOfWork
from kcworks.services.records.permissions import per_field_edit_permission_factory
from kcworks.utils import get_changed_fields, get_value_by_path
import re
from typing import Union


class PerFieldEditPermissionsComponent(ServiceComponent):
    """
    A service component that applies per-field permissions to records.
    """

    @staticmethod
    def _get_config_for_community(
        record: Union[RDMDraft, RDMRecord],
    ) -> dict:
        """
        Get the configuration for a community.

        If the record has a parent, get the configuration for the community.

        Returns the per-field permissions configuration dictionary for the
        community if there is one. Otherwise, returns an empty dictionary.
        """
        community_config = {}
        if record.parent:
            record_communities = record.parent.communities  # type: ignore
            community_config = current_app.config[
                "RDM_RECORDS_PERMISSIONS_PER_FIELD"
            ].get(record_communities.default.slug)
        return community_config

    @staticmethod
    def _find_changed_restricted_fields(
        record: Union[RDMDraft, RDMRecord], data: dict, community_config: dict
    ) -> list[str]:
        """
        Find the changed restricted fields.

        Returns a list of field paths for values that have been changed and are
        restricted in the per-field permissions configuration. The field paths
        will include the list indices for the changed values, but the matching
        to determine whether the field is restricted will be done without the
        list indices.
        """
        restricted_fields = [
            k.replace(".", "|") for k in community_config.get("policy", {}).keys()
        ]
        current_app.logger.info(f"Restricted fields: {restricted_fields}")
        changed_fields = get_changed_fields(record, data, separator="|")
        current_app.logger.info(f"Changed fields: {changed_fields}")

        # When checking for matches, since the paths in restricted_field config
        # won't have the list indices, we need to strip them from the changed fields
        changed_restricted_fields = [
            f
            for f in changed_fields
            if any(re.sub(r"\|\d+\|?", "|", f).startswith(p) for p in restricted_fields)
            or any(p.startswith(re.sub(r"\|\d+\|?", "|", f)) for p in restricted_fields)
            # second check for when the list index is the last part of the path
            or any(p.startswith(re.sub(r"\|\d+$", "", f)) for p in restricted_fields)
        ]
        current_app.logger.info(
            f"Changed restricted fields: {changed_restricted_fields}"
        )
        return changed_restricted_fields

    def update_draft(
        self,
        identity: Identity,
        data: dict,
        record: RDMDraft,
        errors: list,
        **kwargs,
    ):
        """
        Apply per-field permissions to a draft of a record.

        Check for per-field permissions in the community configuration and apply
        them to the fields that are restricted in the community configuration.

        If the permission policy is not satisfied, does not raise a ValidationError but
        instead reverts the restricted fields to the previous values and adds an error
        to the errors list.

        Args:
            identity: The identity performing the update.
            data: The data to update the record with (complete record data, not just
                new values).
            record: The draft being updated.
            errors: The list of errors to add to.
        """
        changed_restricted_fields = []

        # only apply if there is a previous published version
        if record.is_published and record.parent:

            community_config = (
                PerFieldEditPermissionsComponent._get_config_for_community(record)
            )

            if community_config:
                # have to get the previous published version to compare against,
                # since the draft may already have been updated with the new values

                previous_published_version = self.service.record_cls.get_record(
                    record.versions.latest_id
                )
                previous_published_data = {
                    k: v
                    for k, v in previous_published_version.dumps().items()
                    if k in ["access", "metadata", "custom_fields", "pids"]
                }
                changed_restricted_fields = (
                    PerFieldEditPermissionsComponent._find_changed_restricted_fields(
                        previous_published_data, data, community_config
                    )
                )

                if changed_restricted_fields:
                    community_policy = per_field_edit_permission_factory(
                        community_id=record.parent.communities.default.id,
                        roles=community_config.get("policy", {}).values(),
                    )
                    if not community_policy.allows(identity):
                        current_app.logger.info(
                            f"Community policy disallows editing restricted fields"
                        )
                        for field in changed_restricted_fields:
                            errors.append(
                                {
                                    "field": field,
                                    "messages": [
                                        "You do not have permission to edit this field "
                                        "because the record is included in the "
                                        f"{record.parent.communities.default.slug}"
                                        " community. "
                                        "Please contact the community owner or manager "
                                        "for assistance."
                                    ],
                                }
                            )

                            old_value = get_value_by_path(
                                previous_published_data, field, separator="|"
                            )
                            current_app.logger.info(
                                f"Old value for {field}: {old_value}"
                            )
                            replace_value_in_nested_dict(data, field, old_value)
                        record.metadata = data["metadata"]
                        current_app.logger.info(f"Metadata: {record.metadata}")
                        if "custom_fields" in data.keys():
                            record.custom_fields = data["custom_fields"]
                            current_app.logger.info(
                                f"Custom fields: {record.custom_fields}"
                            )
                        if "access" in data.keys():
                            record.access = data["access"]
                            current_app.logger.info(f"Access: {record.access}")
                        if "pids" in data.keys():
                            record.pids = data["pids"]
                            current_app.logger.info(f"PIDs: {record.pids}")

    def new_version(
        self,
        identity: Identity,
        draft: RDMDraft,
        record: RDMRecord,
        uow: UnitOfWork,
    ):
        """
        Create a new version of a record.

        The `draft` argument is the *new* draft object for the new version.
        """
        # check against the previous published version, if any
        pass

    def delete_record(
        self,
        identity: Identity,
        data: dict,
        record: RDMRecord,
        uow: UnitOfWork,
    ):
        """
        Delete a record.
        """
        # check for per-field permissions
        pass
