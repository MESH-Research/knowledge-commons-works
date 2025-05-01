# Part of Knowledge Commons Works
# Copyright (C) 2023, 2024 Knowledge Commons
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License

"""Pytest fixtures for custom fields."""

import pytest
from invenio_communities.proxies import current_communities
from invenio_rdm_records.contrib.codemeta import (
    CODEMETA_CUSTOM_FIELDS,
    CODEMETA_NAMESPACE,
)
from invenio_rdm_records.contrib.imprint import (
    IMPRINT_CUSTOM_FIELDS,
    IMPRINT_NAMESPACE,
)
from invenio_rdm_records.contrib.journal import (
    JOURNAL_CUSTOM_FIELDS,
    JOURNAL_NAMESPACE,
)
from invenio_rdm_records.contrib.meeting import (
    MEETING_CUSTOM_FIELDS,
    MEETING_NAMESPACE,
)
from invenio_rdm_records.contrib.thesis import (
    THESIS_CUSTOM_FIELDS,
    THESIS_NAMESPACE,
)
from invenio_rdm_records.proxies import current_rdm_records
from invenio_records_resources.services.custom_fields import (
    TextCF,
)
from invenio_records_resources.services.custom_fields.errors import (
    CustomFieldsException,
)
from invenio_records_resources.services.custom_fields.mappings import Mapping
from invenio_records_resources.services.custom_fields.validate import (
    validate_custom_fields,
)
from invenio_search import current_search_client
from invenio_search.engine import dsl
from invenio_search.engine import search as search_engine
from invenio_search.utils import build_alias_name
from marshmallow_utils.fields import SanitizedUnicode

from .metadata_fields.hclegacy_groups_for_deposit import (
    HCLEGACY_GROUPS_FOR_DEPOSIT_FIELD,
)
from .metadata_fields.hclegacy_metadata_fields import (
    HCLEGACY_CUSTOM_FIELDS,
    HCLEGACY_NAMESPACE,
)
from .metadata_fields.kcr_ai_field import (
    KCR_AI_USAGE_FIELDS,
)
from .metadata_fields.kcr_media_field import (
    KCR_MEDIA_FIELD,
)
from .metadata_fields.kcr_metadata_fields import (
    KCR_CUSTOM_FIELDS,
    KCR_NAMESPACE,
)
from .metadata_fields.kcr_notes_fields import (
    KCR_NOTES_FIELDS,
)
from .metadata_fields.kcr_series_field import (
    KCR_SERIES_FIELDS,
)
from .metadata_fields.kcr_user_tags_fields import (
    KCR_USER_TAGS_FIELDS,
)
from .metadata_fields.kcr_volumes_fields import (
    KCR_VOLUMES_FIELDS,
)


def _(x):
    """Identity function for string extraction."""
    return x


test_config_fields = {}
test_config_fields["RDM_NAMESPACES"] = {
    **JOURNAL_NAMESPACE,
    **IMPRINT_NAMESPACE,
    **THESIS_NAMESPACE,
    **MEETING_NAMESPACE,
    **CODEMETA_NAMESPACE,
    **KCR_NAMESPACE,
    **HCLEGACY_NAMESPACE,
}

test_config_fields["RDM_CUSTOM_FIELDS"] = [
    *IMPRINT_CUSTOM_FIELDS,
    *THESIS_CUSTOM_FIELDS,
    *CODEMETA_CUSTOM_FIELDS,
    *JOURNAL_CUSTOM_FIELDS,
    *MEETING_CUSTOM_FIELDS,
    *KCR_CUSTOM_FIELDS,
    *KCR_VOLUMES_FIELDS,
    *KCR_MEDIA_FIELD,
    *KCR_NOTES_FIELDS,
    *KCR_USER_TAGS_FIELDS,
    *HCLEGACY_CUSTOM_FIELDS,
    *HCLEGACY_GROUPS_FOR_DEPOSIT_FIELD,
    *KCR_AI_USAGE_FIELDS,
    *KCR_SERIES_FIELDS,
    TextCF(
        name="kcr:commons_search_recid",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:commons_search_updated",
        field_cls=SanitizedUnicode,
    ),
]

test_config_fields["RDM_CUSTOM_FIELDS_UI"] = [
    {
        "section": _("Commons search update info"),
        "fields": [
            {
                "field": "kcr:commons_search_recid",
                "ui_widget": "TextField",
                "props": {},
            },
            {
                "field": "kcr:commons_search_updated",
                "ui_widget": "EDTFDateStringCF",
                "props": {},
            },
        ],
    }
]

# FIXME: provide proper namespace url
test_config_fields["COMMUNITIES_NAMESPACES"] = {
    "kcr": "https://invenio-dev.hcommons-staging.org/terms/"
}

test_config_fields["COMMUNITIES_CUSTOM_FIELDS"] = [
    TextCF(name="kcr:commons_instance"),
    TextCF(name="kcr:commons_group_id"),
    TextCF(name="kcr:commons_group_name"),
    TextCF(name="kcr:commons_group_description"),
    TextCF(name="kcr:commons_group_visibility"),
    TextCF(name="kcr:commons_search_recid"),
    TextCF(name="kcr:commons_search_updated"),
]

test_config_fields["COMMUNITIES_CUSTOM_FIELDS_UI"] = [
    {
        "section": "Linked Commons Group",
        "hidden": False,
        "description": "Information about a Commons group that owns the collection",
        "fields": [
            {
                "field": "kcr:commons_group_name",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Group Name",
                    "placeholder": "",
                    "icon": "",
                    "description": "Name of the Commons group.",
                    "disabled": True,
                },
            },
            {
                "field": "kcr:commons_group_id",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Group ID",
                    "placeholder": "",
                    "icon": "",
                    "description": "ID of the Commons group",
                    "disabled": True,
                },
            },
            {
                "field": "kcr:commons_instance",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Instance",
                    "placeholder": "",
                    "icon": "",
                    "description": (
                        "The Commons to which the group belongs (e.g., "
                        "STEMEd+ Commons, MLA Commons, Humanities Commons)"
                    ),
                    "disabled": True,
                },
            },
            {
                "field": "kcr:commons_group_description",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Group Description",
                    "placeholder": "",
                    "icon": "",
                    "description": "Description of the Commons group.",
                    "disabled": True,
                },
            },
            {
                "field": "kcr:commons_group_visibility",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Group Visibility",
                    "placeholder": "",
                    "icon": "",
                    "description": "Visibility of the Commons group.",
                    "disabled": True,
                },
            },
        ],
    }
]


@pytest.fixture(scope="function")
def create_records_custom_fields(app):
    """Creates one or all custom fields for records.

    like with
    ```shell
    invenio custom-fields records create [field].
    ```
    """
    available_fields = app.config.get("RDM_CUSTOM_FIELDS")
    namespaces = set(app.config.get("RDM_NAMESPACES").keys())
    try:
        validate_custom_fields(
            given_fields=None,
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as e:
        print(f"Custom record fields configuration is not valid. {e.description}")
    properties = Mapping.properties_for_fields(None, available_fields)
    try:
        mycls = current_rdm_records.records_service.config.record_cls
        rdm_records_index = dsl.Index(
            build_alias_name(mycls.index._name),
            using=current_search_client,  # type: ignore
        )
        rdm_records_index.put_mapping(body={"properties": properties})
    except search_engine.RequestError as e:
        print("An error occured while creating custom records fields.")
        print(e)


@pytest.fixture(scope="function")
def create_communities_custom_fields(app):
    """Creates one or all custom fields for communities.

    like with
    ```shell
    invenio custom-fields communities create [field].
    ```
    """
    available_fields = app.config.get("COMMUNITIES_CUSTOM_FIELDS")
    namespaces = set(app.config.get("COMMUNITIES_NAMESPACES").keys())
    try:
        validate_custom_fields(
            given_fields=None,
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as e:
        print(f"Custom fields configuration is not valid. {e.description}")
    # multiple=True makes it an iterable
    properties = Mapping.properties_for_fields(None, available_fields)

    try:
        communities_index = dsl.Index(
            build_alias_name(current_communities.service.config.record_cls.index._name),
            using=current_search_client,  # type: ignore
        )
        communities_index.put_mapping(body={"properties": properties})
    except search_engine.RequestError as e:
        print("An error occured while creating custom fields.")
        print(e)
