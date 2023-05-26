"""
kcr:commons_domain      The commons domain from which the record was deposited.
kcr:chapter_label       The title or heading for a chapter. Used primarily
                        for bookSection resource type.
kcr:edition             The edition number (or other identifier) for the
                        current item.
kcr:meeting_organization    The convening organization for a meeting or
                            conference.
kcr:notes           Notes related to the record. This value is an array of
                    objects, each of which has the keys "note_text",
                    "note_text_sanitized", and "note_description". The "note_text_sanitized" field contains the same string as "note_text" but with any allowed html tags stripped out.
kcr:sponsoring_institution      The institution responsible for the current
                                item. Used primarily for resource types like
                                thesis, whitePaper, and report.
kcr:submitter_email     The email address of the user who submitted the
                        deposit. This is important for aligning the Invenio
                        user with the HC user account.
kcr:submitter_username  The HC (Wordpress) username of the user who
                        submitted the original CORE deposit.
kcr:user_defined_tags       Free user-defined tags associated with the current
                            item. This value is an array of objects, each with
                            the keys "tag_label" and "tag_identifier". The
                            tag_identifier is an integer assigned automatically. The tag_label is the string entered
                            by the user.
kcr:volumes     Information on the total number of volumes and the current
                volume identifier for multi-volume works. This value is an
                object with the keys "total_volumes" (for the total number of
                volumes in the whole work) and "volume" (for the identifier for
                the current item's volume). This is not used for the volume of
                a journal in which a journalArticle appears. For that value,
                see journal:journal.volume.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF, TextCF, IntegerCF
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedUnicode, SanitizedHTML, StrippedHTML

class NotesCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Notes fields definitions."""
        return fields.Nested(
            {
                "note_text": SanitizedHTML(),
                "note_text_sanitized": StrippedHTML(),
                "note_description": SanitizedUnicode(),
            }
        )


class VolumesCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Notes fields definitions."""
        return fields.Nested(
            {
                "total_volumes": SanitizedUnicode(),
                "volume": SanitizedUnicode()
            }
        )


class UserTagsCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Notes fields definitions."""
        return fields.Nested(
            {
            "tag_label": SanitizedUnicode(),
            "tag_identifier": IntegerCF()
            }
        )


KCR_NAMESPACE = {
    "kcr": "",
}

KCR_CUSTOM_FIELDS = [
    TextCF(
        name="kcr:submitter_email",
        field_cls=SanitizedUnicode,
        field_args={
            "validate": validate.Email()
        }
    ),
    TextCF(
        name="kcr:submitter_username",
        field_cls=SanitizedUnicode,
    ),
    UserTagsCF(name="kcr:user_defined_tags"),
    NotesCF(name="kcr:notes"),
    VolumesCF(name="kcr:volumes"),
    TextCF(
        name="kcr:commons_domain",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:chapter_label",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:edition",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:meeting_organization",
        field_cls=SanitizedUnicode,
    ),
    # FIXME: Optionally use a CV for institutions?
    TextCF(
        name="kcr:sponsoring_institution",
        field_cls=SanitizedUnicode,
    )
]

KCR_SUBMITTER_INFO_FIELDS_UI = {
    "section": _("Submitter info"),
    "fields": [
        {"field": "kcr:submitter_email",
         "ui_widget": "Input",
         "props": {"label": "Submitter email",
                   "placeholder": "my@email.com",
                    icon="lab",
                    description="You should fill this field with one of the experiments e.g LHC, ATLAS etc.",
                    search=False,  # True for autocomplete dropdowns with search functionality
                    multiple=False,   # True for selecting multiple values
                    clearable=True,
         }
         }
    ]
}

KCR_VOLUMES_FIELDS_UI = {
    "section": _("Commons info"),
    "fields": [
            {
                "field": "kcr:commons_domain",
        }
    ]
}

KCR_COMMONS_INFO_FIELDS_UI = {
    "section": _("Commons info"),
    "fields": [
            {
                "field": "kcr:commons_domain",
        }
    ]
}

KCR_USER_TAGS_FIELDS_UI = {

}

KCR_CHAPTER_LABEL_FIELDS_UI = {

}

KCR_EDITION_FIELDS_UI = {

}

KCR_NOTES_FIELDS_UI = {
    "section": _("Notes"),
    "fields": [
        {
            "field": "kcr:notes",
            "ui_widget": "Notes",
            "template": "notes.html",
            "props": {
                "label": _("Notes"),
                "note_text": {
                    "label": _("Note"),
                    "placeholder": _("Type your note content here"),
                    "description": _("The text of your note"),
                },
                "note_description": {
                    "label": _("Description"),
                    "placeholder": "",
                    "description": _(
                        "Title of the book or report which this upload is part of."
                    ),
                },
                "icon": "book",
                "description": "Notes",
            },
        }
    ],
}

KCR_CUSTOM_FIELDS_UI = {
    "section": _("Book / Report / Chapter"),
    "fields": [
        {
            "field": "kcr:notes",
            "ui_widget": "Notes",
            "template": "notes.html",
            "props": {
                "label": _("Notes"),
                "note_text": {
                    "label": _("Note"),
                    "placeholder": _("Type your note content here"),
                    "description": _("The text of your note"),
                },
                "note_description": {
                    "label": _("Description"),
                    "placeholder": "",
                    "description": _(
                        "Title of the book or report which this upload is part of."
                    ),
                },
                "icon": "book",
                "description": "Notes",
            },
        }
    ],
}