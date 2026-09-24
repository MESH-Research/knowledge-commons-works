"""Volumes custom field.

kcr:volumes     Information on the total number of volumes and the current
                volume identifier for multi-volume works. This value is an
                object with the keys "total_volumes" (for the total number of
                volumes in the whole work) and "volume" (for the identifier for
                the current item's volume). This is not used for the volume of
                a journal in which a journalArticle appears. For that value,
                see journal:journal.volume.

The Python schema stays nested under ``kcr:volumes``. The UI config exposes
separate entries for each subfield so the modular deposit form can place
``VolumeComponent`` and ``TotalVolumesComponent`` independently in a FormRow.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


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
        "field": "kcr:volumes.volume",
        "ui_widget": "Input",
        "template": "kcworks/volumes.html",
        "props": {
            "label": _("Volume"),
            "placeholder": "",
            "description": "",
            "icon": "book",
        },
    },
    {
        "field": "kcr:volumes.total_volumes",
        "ui_widget": "Input",
        "template": "kcworks/volumes.html",
        "props": {
            "label": _("Total volumes"),
            "placeholder": "",
            "description": "",
            "icon": "th",
        },
    },
]
