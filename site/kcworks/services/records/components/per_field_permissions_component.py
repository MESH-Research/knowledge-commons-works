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

"""Service component for applying per-field editing permissions to records."""

import re

from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_administration.generators import Administration
from invenio_communities.records.records.systemfields.communities.manager import (
    CommunitiesRelationManager,
)
from invenio_rdm_records.proxies import current_rdm_records_service as record_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from invenio_records_permissions.generators import SystemProcess
from invenio_records_resources.services.records.components.base import ServiceComponent
from kcworks.services.records.permissions import per_field_edit_permission_factory
from kcworks.utils import (
    get_changed_fields,
    get_value_by_path,
    matching_list_parts_skip_digits,
)


class PerFieldEditPermissionsComponent(ServiceComponent):
    """A service component that applies per-field permissions to records.

    Intended for use with the RDMRecordsService.
    """

    @staticmethod
    def get_permissions_config(
        parent_communities: CommunitiesRelationManager,
    ) -> dict:
        """Get the configuration for a community.

        If the record has a parent, get the configuration for the community.

        Parameters:
            parent_communities (dict): The communities of the record's parent.

        Returns:
            dict: The per-field permissions configuration dictionary for the
            community if there is one. Otherwise, returns an empty dictionary.
        """
        default_editors_fallback = ["manager", "owner", "curator"]
        community_config = {}
        community_configs = current_app.config.get(
            "RDM_RECORDS_PERMISSIONS_PER_FIELD", {}
        )
        if community_configs and parent_communities:
            if parent_communities.default:  # type: ignore
                community_config = community_configs.get(
                    parent_communities.default.slug  # type: ignore
                )

        if not community_config:
            community_config = community_configs.get("default", {})
            default_editors_fallback = [Administration, SystemProcess]

        if community_config:
            policy = community_config.get("policy", {})
            if isinstance(policy, list):
                default_editors = community_config.get(
                    "default_editors", default_editors_fallback
                )
                policy = dict.fromkeys(policy, default_editors)
            community_config["policy"] = policy

        return community_config

    @staticmethod
    def _check_field_condition(
        published_data: dict,
        path: str,
        condition: str,
    ) -> bool:
        result = True

        if condition and "=" in condition:
            subfield, value = condition.split("=")
            full_check_path = path + "|" + subfield
            actual_value = get_value_by_path(
                published_data, full_check_path, separator="|"
            )
            if str(actual_value) != value:
                result = False
        elif condition:
            # Handle direct value condition (e.g., "neh")
            actual_value = get_value_by_path(published_data, path, separator="|")
            if str(actual_value) != condition:
                result = False

        return result

    @staticmethod
    def _separate_conditional_fields(
        restricted_fields: list[str],
    ) -> tuple[list[str], list[tuple[str, str, str]]]:
        """Separate the fields with bracketed conditions from those without.

        Returns a tuple of two lists: the first is a list of path strings without
        bracketed conditions, and the second is a list of tuples, each containing
        the base part of the path, the conditions, and the full restricted path.
        """
        restricted_fields_with_conditions = []
        simple_restricted_fields = []
        for restricted_field in restricted_fields:
            bracket_section_match = re.match(r"^(.*?)(?:\[(.*?)\])", restricted_field)
            if bracket_section_match:
                base_part, conditions = bracket_section_match.groups()
                restricted_fields_with_conditions.append(
                    (base_part, conditions, restricted_field)
                )
            else:
                simple_restricted_fields.append(restricted_field)
        return simple_restricted_fields, restricted_fields_with_conditions

    @staticmethod
    def _fields_match(
        changed_field: str,
        restricted_field: str,
        matched_parts: list[str] | None = None,
    ) -> bool:
        """Check if the changed field matches the restricted field.

        Returns True if the fields match, False otherwise.
        """
        if not matched_parts:
            matched_parts = matching_list_parts_skip_digits(
                changed_field.split("|"), restricted_field.split("|")
            )
        return (
            changed_field.startswith(restricted_field + "|")
            or changed_field == restricted_field
            or matched_parts != []
        )

    @staticmethod
    def _find_changed_restricted_fields(
        published_data: dict, new_data: dict, community_config: dict
    ) -> list[tuple[str, str]]:
        """Find the changed restricted fields.

        Returns a list of field paths for values that have been changed and are
        restricted in the per-field permissions configuration.

        Args:
            published_data (dict): The data of the previous published version of the
                record.
            new_data (dict): The data of the new draft version of the record.
            community_config (dict): The per-field permissions configuration for the
                community.

        Returns:
            list[tuple[str, str]]: A list of tuples, each containing a field path that
            has changed and the restricted field path that matches it. If no restricted
            fields are found, or no changes appear in restricted fields, returns an
            empty list.

        Note:
            Expects the restricted fields to be in the format "metadata|funding" with
            either a bar or a dot as the delimiter. Returned fields will always use
            a bar as the delimiter.

            With list fields, any member of the list is restricted if no specific index
            is given (e.g., "metadata|funding"). If a specific index is given, only that
            index is restricted (e.g., "metadata|funding|0") and other indices are not
            restricted. This is to allow for the possibility of restricting specific
            members of a list field while allowing other members to be edited.

            If square brackets are placed following the final field name, the value
            inside the brackets is used to determine whether the field is restricted,
            based on the starting value of the field. If a simple value is provided,
            without an equals sign, the field will be restricted if the starting value
            matches the starting value for the field. For example,
            "metadata|funding|funder[neh]" would match "metadata|funding|0|funder"
            *only* if the starting value of "metadata|funding|0|funder" is "neh".

            If the square brackets contain an equals sign, the field will be restricted
            based on the value of a subfield. For example,
            "metadata|funding[funder|id=neh]" would match any field path for
            "metadata|funding" ("metadata|funding|0|funder", "metadata|funding|1|award",
            "metadata|funding", etc.) but will match *only* if the starting value of
            "metadata|funding|0|funder|id" is "neh".

        Examples:
            When "metadata|funding" is restricted:
                - Will match "metadata|funding"
                - Will match "metadata|funding|0|funder"
                - Will match "metadata|funding|1|funder"

            When "metadata|funding|0" is restricted:
                - Will match "metadata|funding|0"
                - Will match "metadata|funding|0|funder"
                - Will NOT match "metadata|funding|1|funder"

            When "metadata|funding|funder" is restricted:
                - Will match "metadata|funding|0|funder"
                - Will match "metadata|funding|1|funder"
                - Will NOT match "metadata|funding|0|award"

            When "metadata|funding|funder|id[neh]" is restricted:
                - Will match "metadata|funding|0|funder" *only* if the starting value of
                  "metadata|funding|0|funder" is "neh"
                - Will NOT match "metadata|funding|0|award"

            When "metadata|funding[funder|id=neh]" is restricted:
                - Will match "metadata|funding" ONLY if the starting value of
                  "metadata|funding|0|funder|id" is "neh"
                - Will NOT match "metadata|funding|1|funder" if the starting value of
                  "metadata|funding|1|funder|id" is "neh"
                - Will match "metadata|funding|0|award" if the starting value of
                  "metadata|funding|0|funder|id" is "neh"
        """
        restricted_fields = [
            k.replace(".", "|") for k in community_config.get("policy", {}).keys()
        ]
        changed_fields = get_changed_fields(published_data, new_data, separator="|")

        simple_restricted_fields, restricted_fields_with_conditions = (
            PerFieldEditPermissionsComponent._separate_conditional_fields(
                restricted_fields
            )
        )

        changed_restricted_fields = []
        for changed_field in changed_fields:
            # For each changed field, check if it matches any restricted field pattern
            for restricted_field in simple_restricted_fields:
                if PerFieldEditPermissionsComponent._fields_match(
                    changed_field, restricted_field
                ):
                    changed_restricted_fields.append((changed_field, restricted_field))
                    continue

            for (
                base_part,
                condition,
                restricted_field,
            ) in restricted_fields_with_conditions:
                changed_field_parts = changed_field.split("|")
                matched_parts = matching_list_parts_skip_digits(
                    changed_field_parts, base_part.split("|")
                )

                # Account for the situation where the endpoint of the matched parts
                # is a list field, but the restricted field provided no digit index.
                if (
                    len(changed_field_parts) > len(matched_parts)
                    and changed_field_parts[len(matched_parts)].isdigit()
                ):
                    matched_parts.append(changed_field_parts[len(matched_parts)])

                if PerFieldEditPermissionsComponent._fields_match(
                    changed_field, base_part, matched_parts=matched_parts
                ):
                    if PerFieldEditPermissionsComponent._check_field_condition(
                        published_data, "|".join(matched_parts), condition
                    ):
                        changed_restricted_fields.append(
                            (changed_field, restricted_field)
                        )
                        continue

        return changed_restricted_fields

    def update_draft(
        self,
        identity: Identity,
        data: dict,
        record: RDMDraft,
        errors: list,
        **kwargs,
    ) -> None:
        """Apply per-field permissions to a draft of a record.

        Check for per-field permissions in the community configuration and apply
        them to the fields that are restricted in the community configuration.

        If the permission policy is not satisfied, does not raise a ValidationError but
        instead reverts the restricted fields to the previous values and adds an error
        to the errors list.

        Args:
            identity (Identity): The identity performing the update.
            data (dict): The data to update the record with (complete record data, not
                just new values).
            record (RDMDraft): The draft being updated.
            errors (list): The list of errors to add to.
            **kwargs: Additional keyword arguments.
        """
        changed_restricted_fields = []
        current_app.logger.debug("Updating draft")

        # only apply if there is a previous published version
        if (record.is_published or record.versions.index > 1) and record.parent:
            community_config: (
                dict | None
            ) = PerFieldEditPermissionsComponent.get_permissions_config(
                record.parent.communities  # type: ignore
            )

            if community_config:
                # have to get the previous published version to compare against,
                # since the draft may already have been updated with the new values

                # previous_published_version_rec = self.service.record_cls.get_record(
                #     record.versions.latest_id
                # )
                record_communities = record.parent.communities  # type: ignore
                previous_published_version_rec = (
                    RDMRecord.get_latest_published_by_parent(record.parent)
                )
                previous_published_version = record_service.read(
                    system_identity,
                    id_=previous_published_version_rec.pid.pid_value,  # type: ignore
                )
                previous_published_data = {
                    k: v
                    for k, v in previous_published_version.to_dict().items()
                    if k in ["access", "metadata", "custom_fields", "pids"]
                }
                changed_restricted_fields = (
                    PerFieldEditPermissionsComponent._find_changed_restricted_fields(
                        previous_published_data, data, community_config
                    )
                )

                for field, key in changed_restricted_fields:
                    current_app.logger.debug(f"Checking field: {field} with key: {key}")
                    policy: dict | list = community_config.get("policy", [])
                    if isinstance(policy, dict):
                        roles: list = policy.get(key, []) or policy.get(
                            key.replace("|", "."), []
                        )
                    else:
                        roles = policy
                    community_field_policy = per_field_edit_permission_factory(
                        community_id=record_communities.default.id,  # type: ignore
                        roles=roles,
                    )
                    if not community_field_policy.allows(identity):
                        current_app.logger.debug(f"Field {field} is restricted")
                        new_error = {
                            # frontend needs dot notation
                            "field": field.replace("|", "."),
                            "messages": [
                                "You do not have permission to edit this field "
                                "because the record is included in the "
                                f"{record_communities.default.slug}"
                                " community. "
                                "Please contact the community owner or manager "
                                "for assistance."
                            ],
                        }
                        errors.append(new_error)
                        # raise ValidationError(
                        #     field_name=field, message=new_error["messages"][0]
                        # )
                        old_value = get_value_by_path(
                            previous_published_data, field, separator="|"
                        )
                        replace_value_in_nested_dict(data, field, old_value)
                    record.metadata = data["metadata"]
                    if "custom_fields" in data.keys():
                        record.custom_fields = data["custom_fields"]
                    if "access" in data.keys():
                        record.access = data["access"]
                    if "pids" in data.keys():
                        record.pids = data["pids"]
