"""Metadata fields for KCR series.

kcr:book_series       Information on the series of books in which the current
                      item appears. This value is an array of objects, each
                      of which has the keys "series_title" and "series_volume".
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseListCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class BookSeriesCF(BaseListCF):
    """Custom field for book series."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args={
                "nested": {
                    "series_title": SanitizedUnicode(),
                    "series_volume": SanitizedUnicode(),
                }
            },
            multiple=True,
            **kwargs,
        )

    @property
    def mapping(self):
        """Book series search mappings."""
        return {
            "type": "object",
            "properties": {
                "series_title": {"type": "text"},
                "series_volume": {"type": "text"},
            },
        }


KCR_SERIES_FIELDS = [
    BookSeriesCF(name="kcr:book_series"),
]


KCR_SERIES_FIELDS_UI = {
    "section": _("Series"),
    "fields": [
        {
            "field": "kcr:book_series",
            "ui_widget": "BookSeriesField",
            "template": "book_series_field.html",
            "props": {
                "label": _("Series"),
                "series_title": {
                    "label": _("Series Title"),
                    "placeholder": "",
                    "description": _(""),
                },
                "series_volume": {
                    "label": _("Volume"),
                    "placeholder": "",
                    "description": "",
                },
                "icon": "",
                "description": "",
            },
        }
    ],
}
