# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Record and community custom field definitions for KCWorks.

The five upstream-contrib custom field sets (codemeta, journal, imprint,
meeting, thesis) — both their Python definitions and their UI configs — are
delegated to ``invenio-modular-deposit-form``. We import its
``RDM_NAMESPACES`` / ``RDM_CUSTOM_FIELDS`` / ``RDM_CUSTOM_FIELDS_UI`` directly
and concatenate KCR/HCLEGACY pieces on top, instead of relying on the
package's ``finalize_app`` "if still empty" gate (which would never fire here
because we set non-empty config for KCR/HCLEGACY anyway).

KCR additions to the upstream sections (formerly inlined as section-extras
between upstream sections in ``RDM_CUSTOM_FIELDS_UI``) are now standalone
sections appended after the modular sections, not interleaved with them.
"""

from invenio_i18n import lazy_gettext as _
from invenio_modular_deposit_form.config.config import (
    RDM_CUSTOM_FIELDS as MODULAR_RDM_CUSTOM_FIELDS,
)
from invenio_modular_deposit_form.config.config import (
    RDM_CUSTOM_FIELDS_UI as MODULAR_RDM_CUSTOM_FIELDS_UI,
)
from invenio_modular_deposit_form.config.config import (
    RDM_NAMESPACES as MODULAR_RDM_NAMESPACES,
)
from invenio_records_resources.services.custom_fields import TextCF

from invenio_stats_dashboard.records.communities.custom_fields.custom_fields import (
    COMMUNITIES_NAMESPACES as STATS_COMMUNITIES_NAMESPACES,
)
from kcworks.metadata_fields.hclegacy_groups_for_deposit import (
    HCLEGACY_GROUPS_FOR_DEPOSIT_FIELD,
)
from kcworks.metadata_fields.hclegacy_metadata_fields import (
    HCLEGACY_CUSTOM_FIELDS,
    HCLEGACY_INFO_SECTION_UI,
    HCLEGACY_NAMESPACE,
)
from kcworks.metadata_fields.kcr_ai_field import (
    KCR_AI_USAGE_FIELDS,
    KCR_AI_USAGE_FIELDS_UI,
)
from kcworks.metadata_fields.kcr_media_field import (
    KCR_MEDIA_FIELD,
    KCR_MEDIA_SECTION_UI,
)
from kcworks.metadata_fields.kcr_metadata_fields import (
    KCR_ADMIN_INFO_SECTION_UI,
    KCR_CONTENT_WARNING_FIELD_UI,
    KCR_COURSE_SECTION_UI,
    KCR_CUSTOM_FIELDS,
    KCR_IMPRINT_SECTION_EXTRAS_UI,
    KCR_JOURNAL_SECTION_EXTRAS_UI,
    KCR_MEETING_SECTION_EXTRAS_UI,
    KCR_NAMESPACE,
    KCR_PROJECT_SECTION_UI,
    KCR_THESIS_SECTION_EXTRAS_UI,
)
from kcworks.metadata_fields.kcr_notes_fields import (
    KCR_NOTES_FIELDS,
    KCR_NOTES_SECTION_UI,
)
from kcworks.metadata_fields.kcr_series_field import (
    KCR_SERIES_FIELDS,
    KCR_SERIES_FIELDS_UI,
)
from kcworks.metadata_fields.kcr_user_tags_fields import (
    KCR_USER_TAGS_FIELDS,
    KCR_USER_TAGS_SECTION_UI,
)
from kcworks.metadata_fields.kcr_volumes_fields import (
    KCR_VOLUMES_FIELDS,
    KCR_VOLUMES_FIELDS_UI,
)

from .site_urls import SITE_UI_URL

RDM_NAMESPACES = {
    **MODULAR_RDM_NAMESPACES,
    **KCR_NAMESPACE,
    **HCLEGACY_NAMESPACE,
}

RDM_CUSTOM_FIELDS = [
    *MODULAR_RDM_CUSTOM_FIELDS,
    *KCR_CUSTOM_FIELDS,
    *KCR_VOLUMES_FIELDS,
    *KCR_MEDIA_FIELD,
    *KCR_NOTES_FIELDS,
    *KCR_USER_TAGS_FIELDS,
    *HCLEGACY_CUSTOM_FIELDS,
    *HCLEGACY_GROUPS_FOR_DEPOSIT_FIELD,
    *KCR_AI_USAGE_FIELDS,
    *KCR_SERIES_FIELDS,
]

RDM_CUSTOM_FIELDS_UI = [
    *MODULAR_RDM_CUSTOM_FIELDS_UI,
    {
        "section": _("KCR thesis information"),
        "hidden": False,
        "fields": [*KCR_THESIS_SECTION_EXTRAS_UI],
    },
    {
        "section": _("KCR journal information"),
        "hidden": False,
        "fields": [*KCR_JOURNAL_SECTION_EXTRAS_UI],
    },
    KCR_SERIES_FIELDS_UI,
    {
        "section": _("KCR Book information"),
        "hidden": False,
        "fields": [*KCR_IMPRINT_SECTION_EXTRAS_UI, *KCR_VOLUMES_FIELDS_UI],
    },
    {
        "section": _("KCR Conference information"),
        "fields": [*KCR_MEETING_SECTION_EXTRAS_UI],
    },
    {
        "section": _("Content warning"),
        "fields": [KCR_CONTENT_WARNING_FIELD_UI],
    },
    KCR_ADMIN_INFO_SECTION_UI,
    KCR_MEDIA_SECTION_UI,
    KCR_NOTES_SECTION_UI,
    KCR_PROJECT_SECTION_UI,
    KCR_USER_TAGS_SECTION_UI,
    KCR_AI_USAGE_FIELDS_UI,
    HCLEGACY_INFO_SECTION_UI,
    KCR_COURSE_SECTION_UI,
]

# FIXME: provide proper namespace url
COMMUNITIES_NAMESPACES = {
    "kcr": f"{SITE_UI_URL}/terms/",
    **STATS_COMMUNITIES_NAMESPACES,
}

COMMUNITIES_CUSTOM_FIELDS = [
    TextCF(name="kcr:commons_instance"),
    TextCF(name="kcr:commons_group_id"),
    TextCF(name="kcr:commons_group_name"),
    TextCF(name="kcr:commons_group_description"),
    TextCF(name="kcr:commons_group_visibility"),
    TextCF(name="kcr:commons_search_recid"),
    TextCF(name="kcr:commons_search_updated"),
    # *COMMUNITY_STATS_FIELDS,
]

COMMUNITIES_CUSTOM_FIELDS_UI = [
    {
        "section": "Linked Commons Group",
        "hidden": False,
        "show_on_about": False,
        "description": "Information about a Commons group that owns the collection",
        "fields": [
            {
                "field": "kcr:commons_group_name",
                "ui_widget": "Input",
                "props": {
                    "label": "Commons Group Name",
                    "placeholder": "",
                    "icon": "",
                    # "description": ("Name of the Commons group."),
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
                    # "description": ("Description of the Commons group."),
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
                    # "description": (
                    #     "The Commons to which the group belongs (e.g., "
                    #     "STEMEd+ Commons, MLA Commons, Humanities Commons)"
                    # ),
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
                    # "description": ("Visibility of the Commons group."),
                    "disabled": True,
                },
            },
        ],
    },
    # COMMUNITY_STATS_FIELDS_UI(),  # needs app context for defaults
]
