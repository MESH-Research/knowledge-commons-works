# -*- coding: utf-8 -*-
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
