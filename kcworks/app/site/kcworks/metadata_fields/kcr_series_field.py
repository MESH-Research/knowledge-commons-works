#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
kcr:notes           Notes related to the record. This value is an array of
                    objects, each of which has the keys "note_text",
                    "note_text_sanitized", and "note_description". The "note_text_sanitized" field contains the same string as "note_text" but with any allowed html tags stripped out.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    BaseCF,
    BaseListCF,
    TextCF,
    IntegerCF,
)
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedUnicode, SanitizedHTML, StrippedHTML
from .kcr_metadata_fields import KCR_NAMESPACE


class BookSeriesCF(BaseListCF):
    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args=dict(
                nested=dict(
                    series_title=SanitizedUnicode(), series_volume=SanitizedUnicode()
                )
            ),
            multiple=True,
            **kwargs
        )

    @property
    def mapping(self):
        """Notes search mappings."""
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
