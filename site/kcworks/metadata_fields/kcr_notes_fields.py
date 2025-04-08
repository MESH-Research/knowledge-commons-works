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

"""Notes custom field.

kcr:notes           Notes related to the record. This value is an array of
                    objects, each of which has the keys "note_text",
                    "note_text_sanitized", and "note_description". The
                    "note_text_sanitized" field contains the same string as
                    "note_text" but with any allowed html tags stripped out.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF, TextCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode, StrippedHTML


class NotesCF(BaseCF):
    """Notes custom field."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args={
                "nested": {
                    "note_text": SanitizedHTML(),
                    "note_text_sanitized": StrippedHTML(),
                    "note_description": SanitizedUnicode(),
                }
            },
            multiple=True,
            **kwargs,
        )

    @property
    def mapping(self):
        """Notes search mappings."""
        return {
            "type": "object",
            "properties": {
                "note_text": {"type": "text"},
                "note_text_sanitized": {"type": "text"},
                "note_description": {"type": "text"},
            },
        }


KCR_NOTES_FIELDS = [
    TextCF(name="kcr:notes"),
]


KCR_NOTES_SECTION_UI = {
    "section": _("Notes"),
    "fields": [
        {
            "field": "kcr:notes",
            "ui_widget": "RichInput",
            "props": {
                "label": _("Notes"),
                "note_description": {
                    "label": _("Description"),
                    "placeholder": "",
                    "description": _(
                        "A few words describing the kind of notes recorded here."
                    ),
                },
                "note_text": {
                    "label": _("Note"),
                    "placeholder": _("Type your note content here"),
                    "description": _("The text of your note"),
                },
                "icon": "pencil",
                "description": "Notes",
            },
        }
    ],
}
