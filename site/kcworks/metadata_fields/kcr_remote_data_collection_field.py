"""Custom field for a linked Globus remote data collection.

Adds the ``kcr:remote_data_collection`` field with nested identifiers:

- ``host_endpoint_id`` — Globus host / server endpoint ID.
- ``mapped_collection_id`` — Globus mapped collection ID.
- ``guest_collection_id`` — Globus guest (shared) collection ID.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow.fields import Nested
from marshmallow_utils.fields import SanitizedUnicode


class RemoteDataCollectionCF(BaseCF):
    """Custom field for a linked Globus remote data collection."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(name, **kwargs)

    @property
    def field(self):
        """Remote data collection nested field definition."""
        return Nested(
            {
                "host_endpoint_id": SanitizedUnicode(),
                "mapped_collection_id": SanitizedUnicode(),
                "guest_collection_id": SanitizedUnicode(),
            }
        )

    @property
    def mapping(self):
        """Remote data collection search mappings."""
        return {
            "type": "object",
            "properties": {
                "host_endpoint_id": {"type": "keyword"},
                "mapped_collection_id": {"type": "keyword"},
                "guest_collection_id": {"type": "keyword"},
            },
        }


KCR_REMOTE_DATA_COLLECTION_FIELDS = [
    RemoteDataCollectionCF(name="kcr:remote_data_collection"),
]

KCR_REMOTE_DATA_COLLECTION_UI = {
    "field": "kcr:remote_data_collection",
    "ui_widget": "RemoteDataCollectionField",
}

KCR_REMOTE_DATA_COLLECTION_SECTION_UI = {
    "section": _("Remote Data"),
    "fields": [KCR_REMOTE_DATA_COLLECTION_UI],
}
