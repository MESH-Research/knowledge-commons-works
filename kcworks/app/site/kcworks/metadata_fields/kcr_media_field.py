"""
kcr:media       Free user-defined descriptors of the media or materials
                involved in the creation of a workd. This value is an array of
                strings.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    TextCF,
)
from marshmallow_utils.fields import SanitizedUnicode


KCR_MEDIA_FIELD = [
    TextCF(name="kcr:media", field_cls=SanitizedUnicode, multiple=True),
]


KCR_MEDIA_SECTION_UI = {
    "section": _("Media"),
    "fields": [
        {
            "field": "kcr:media",
            "ui_widget": "MultiInput",
            # "template": "kcworks/user_defined_tags.html",
            "props": {
                "label": _("Media and materials"),
                "placeholder": _(
                    "Enter each of the materials used here (press 'enter' to"
                    " add each one)"
                ),
                "icon": "tags",
                "description": (
                    "The media and materials used in the production of the"
                    " work."
                ),
            },
        }
    ],
}
