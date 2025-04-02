#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Journal custom fields.

Implements the following fields:
- journal.issue
- journal.pages
- journal.title
- journal.volume
"""

from invenio_i18n import lazy_gettext as _


KCR_JOURNAL_CUSTOM_FIELDS_UI = {
    "section": _("Journal"),
    "fields": [
        {
            "field": "journal:journal.title",
            "ui_widget": "JournalTitleField",
            "template": "journal.html",
            "props": {
                "label": _("Journal Title"),
                "placeholder": "",
                # "description": _(
                #     "Title of the journal on which the article was published"
                # ),
            },
        },
        {
            "field": "journal:journal.volume",
            "ui_widget": "JournalVolumeField",
            "template": "journal.html",
            "props": {
                "label": _("Volume"),
                "placeholder": "",
                "description": "",
            },
        },
        {
            "field": "journal:journal.issue",
            "ui_widget": "JournalIssueField",
            "template": "journal.html",
            "props": {
                "label": _("Issue"),
                "placeholder": "",
                "description": "",
            },
        },
        {
            "field": "journal:journal.pages",
            "ui_widget": "JournalPagesField",
            "template": "journal.html",
            "props": {
                "label": _("Pages"),
                "placeholder": "",
                "description": "",
            },
        },
        {
            "field": "journal:journal.issn",
            "ui_widget": "JournalISSNField",
            "template": "journal.html",
            "props": {
                "label": _("ISSN"),
                "placeholder": "",
                "description": _("International Standard Serial Number"),
            },
        },
    ],
}
