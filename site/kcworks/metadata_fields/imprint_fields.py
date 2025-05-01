# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# Based on invenio-rdm-records, Copyright (C) 2021-2024 TU Wien.
#
# invenio-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI configuration for the imprint section custom fields.

These fields are included in invenio-rdm-records and simply need to be
enabled, but we want to customize the UI configuration.
"""

from invenio_i18n import lazy_gettext as _

KCR_IMPRINT_CUSTOM_FIELDS_UI = {
    "section": _("Book / Report / Chapter"),
    "fields": [
        {
            "field": "imprint:imprint.title",
            "ui_widget": "ImprintTitleField",
            "template": "imprint.html",
            "props": {
                "label": _("Book title"),
                "placeholder": "",
                "description": _(
                    "Title of the book or report which this upload is part of."
                ),
            },
        },
        {
            "field": "imprint:imprint.place",
            "ui_widget": "ImprintPlaceField",
            "template": "imprint.html",
            "props": {
                "label": _("Place"),
                "placeholder": _("e.g. city, country"),
                "description": _("Place where the imprint was published"),
            },
        },
        {
            "field": "imprint:imprint.isbn",
            "ui_widget": "ImprintISBNField",
            "template": "imprint.html",
            "props": {
                "label": _("ISBN"),
                "placeholder": _("e.g. 0-06-251587-X"),
                "description": _("International Standard Book Number"),
            },
        },
        {
            "field": "imprint:imprint.pages",
            "ui_widget": "ImprintPagesField",
            "template": "imprint.html",
            "props": {
                "label": _("Pages"),
                "placeholder": "",
                "description": _(""),
                "icon": "copy",
            },
        },
    ],
}
