# Part of Knowledge Commons Works
# Copyright (C) MESH Research, 2023
#
# Based on Invenio-RDM-Records, Copyright (C) 2023 CERN.
#
# KCWorks and Invenio-RDM-Records are free software; you can redistribute them
# and/or modify them under the terms of the MIT License; see LICENSE file for
# more details.

"""Custom fields UI configuration for codemeta metadata.

Implements UI configuration for the following fields:
- code:codeRepository
- code:programmingLanguage
- code:runtimePlatform
- code:operatingSystem
- code:developmentStatus
"""

from invenio_i18n import lazy_gettext as _

KCR_CODEMETA_CUSTOM_FIELDS_UI = {
    "section": _("Software"),
    "fields": [
        {
            "field": "code:codeRepository",
            "ui_widget": "TextField",
            "props": {
                "label": "Repository URL",
                "icon": "linkify",
                "description": "URL or link where the code repository is hosted.",
            },
        },
        {
            "field": "code:programmingLanguage",
            "ui_widget": "TextField",
            "props": {
                "label": "Programming language",
                "icon": "code",
                "description": "Repository's programming language.",
                "placeholder": "Python ...",
            },
        },
        {
            "field": "code:runtimePlatform",
            "ui_widget": "TextField",
            "props": {
                "label": "Runtime platform",
                "icon": "cog",
                "description": (
                    "Repository runtime platform or script interpreter dependencies."
                ),
                "placeholder": "Java v1, Python2.3, .Net Framework 3.0 ...",
            },
        },
        {
            "field": "code:operatingSystem",
            "ui_widget": "TextField",
            "props": {
                "label": "Supported operating system",
                "icon": "laptop",
                "description": "Supported operating systems.",
                "placeholder": "Windows 7, OSX 10.6, Android 1.6 ...",
            },
        },
        {
            "field": "code:developmentStatus",
            "ui_widget": "Dropdown",
            "props": {
                "label": "Development status",
                "placeholder": "",
                "icon": "heartbeat",
                "description": "Repository current status",
                "search": False,
                "multiple": False,
                "clearable": True,
            },
        },
    ],
}
