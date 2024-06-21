"""
kcr:notes           Notes related to the record. This value is an array of
                    objects, each of which has the keys "note_text",
                    "note_text_sanitized", and "note_description". The "note_text_sanitized" field contains the same string as "note_text" but with any allowed html tags stripped out.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    BaseCF,
    TextCF,
    IntegerCF
)
from marshmallow import fields, validate
from marshmallow_utils.fields import (
    SanitizedUnicode,
    SanitizedHTML,
    StrippedHTML
)
from .kcr_metadata_fields import KCR_NAMESPACE


class NotesCF(BaseCF):
#     """Nested custom field."""
    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
          name,
          field_cls=fields.Nested,
          field_args={
            'nested': {
                "note_text": SanitizedHTML(),
                "note_text_sanitized": StrippedHTML(),
                "note_description": SanitizedUnicode(),
            }
          },
          multiple=True,
          **kwargs
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
                        "A few words describing the kind of notes recorded "
                        "here."
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
