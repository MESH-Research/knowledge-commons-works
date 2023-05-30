"""
kcr:user_defined_tags       Free user-defined tags associated with the current
                            item. This value is an array of objects, each with
                            the keys "tag_label" and "tag_identifier". The
                            tag_identifier is an integer assigned automatically. The tag_label is the string entered
                            by the user.
"""


from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    BaseListCF,
    TextCF,
    IntegerCF
)
from marshmallow import fields, Schema, validate
from marshmallow_utils.fields import (
    SanitizedUnicode,
    SanitizedHTML,
    StrippedHTML
)
from .kcr_metadata_fields import KCR_NAMESPACE


class UserTagSchema(Schema):
    """
    """
    tag_label = SanitizedUnicode()
    tag_identifier = SanitizedUnicode()


class UserTagsCF(BaseListCF):
    """Nested custom field."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args={
                "nested": {
                    "tag": fields.List(fields.Nested(UserTagSchema)),
                }
            },
            multiple=False,
            **kwargs
        )

    # @property
    # def field(self):
    #     """Notes fields definitions."""
    #     return fields.Nested(
    #         {
    #         "tag_label": SanitizedUnicode(),
    #         "tag_identifier": IntegerCF()
    #         }
    #     )

    @property
    def mapping(self):
        """user_definted_tags search mappings."""
        return {
            "type": "object",
            "properties": {
                "tag": {
                    "properties": {
                        "tag_label": {"type": "text"},
                        "tag_identifier": {"type": "text"}
                    }
                }
            },
        }


KCR_USER_TAGS_FIELDS = [
    UserTagsCF(name="kcr:user_defined_tags"),
]


KCR_USER_TAGS_SECTION_UI = {
    "section": _("Tags"),
    "fields": [
        {
            "field": "kcr:user_defined_tags",
            "ui_widget": "UserDefinedTags",
            "template": "user_defined_tags.html",
            "props": {
                "label": _("Tags"),
                "tag": {
                    "props": {
                        "tag_label": {
                            "label": _("Tags"),
                            "placeholder": _("Enter your tags here"),
                            "description": _()
                        },
                        "tag_identifier": {
                            "label": _("Tag ids"),
                            "placeholder": "",
                            "description": ""
                        }
                    }
                },
                "icon": "tags",
                "description": "Tags for this deposit that do not appear in the subject terms.",
            },
        }
    ],
}
