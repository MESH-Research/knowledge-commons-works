#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Journal custom fields.

Implements the following fields:
- meeting:meeting.title
- meeting:meeting.acronym
- meeting:meeting.dates
- meeting:meeting.place
- meeting:meeting.url
- meeting:meeting.session
- meeting:meeting.session_part

"""

from invenio_i18n import lazy_gettext as _

KCR_MEETING_CUSTOM_FIELDS_UI = {
    "section": _("Conference"),
    "fields": [
        {
            "field": "meeting:meeting.title",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Event title"),
                "placeholder": "",
                "description": "",
            },
        },
        {
            "field": "meeting:meeting.acronym",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Acronym"),
                "placeholder": "",
                "description": "",
            },
        },
        {
            "field": "meeting:meeting.dates",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Dates"),
                "placeholder": _("e.g. 21-22 November 2022."),
                "description": "",
                "icon": "calendar",
            },
        },
        {
            "field": "meeting:meeting.place",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Location"),
                "placeholder": "",
                "description": "",
                "icon": "map marker alternate",
            },
        },
        {
            "field": "meeting:meeting.url",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Event URL"),
                "placeholder": "",
                "description": "",
                "icon": "linkify",
            },
        },
        {
            "field": "meeting:meeting.session",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Session"),
                "placeholder": _("e.g. VI"),
                "description": "",
            },
        },
        {
            "field": "meeting:meeting.session_part",
            "ui_widget": "TextField",
            "template": "meeting.html",
            "props": {
                "label": _("Session part"),
                "placeholder": _("e.g. 1"),
                "description": "",
            },
        },
    ],
}
