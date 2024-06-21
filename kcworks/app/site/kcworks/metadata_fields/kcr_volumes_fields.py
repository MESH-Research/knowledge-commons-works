"""
kcr:volumes     Information on the total number of volumes and the current
                volume identifier for multi-volume works. This value is an
                object with the keys "total_volumes" (for the total number of
                volumes in the whole work) and "volume" (for the identifier for
                the current item's volume). This is not used for the volume of
                a journal in which a journalArticle appears. For that value,
                see journal:journal.volume.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    BaseCF,
    TextCF,
    IntegerCF,
)
from marshmallow import fields, validate
from marshmallow_utils.fields import (
    SanitizedUnicode,
    SanitizedHTML,
    StrippedHTML,
)
from .kcr_metadata_fields import KCR_NAMESPACE


class VolumesCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Volumes fields definitions."""
        return fields.Nested(
            {"total_volumes": SanitizedUnicode(), "volume": SanitizedUnicode()}
        )

    @property
    def mapping(self):
        """Volumes search mappings."""
        return {
            "type": "object",
            "properties": {
                "total_volumes": {"type": "text"},
                "volume": {"type": "text"},
            },
        }


KCR_VOLUMES_FIELDS = [VolumesCF(name="kcr:volumes")]


KCR_VOLUMES_FIELDS_UI = [
    {
        "field": "kcr:volumes",
        "ui_widget": "Volumes",
        "template": "kcworks/volumes.html",
        "props": {
            "label": _("Volumes"),
            "total_volumes": {
                "label": _("Total volumes"),
                "placeholder": "",
                # "description": _("Total number of volumes in the work"),
                "icon": "th",
            },
            "volume": {
                "label": _("Volume"),
                "placeholder": "",
                # "description": _("The number or label of the volume containing this deposit")
                "icon": "book",
            },
        },
        "icon": "book",
    }
]
