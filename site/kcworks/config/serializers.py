# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Record response serializer overrides."""

from copy import deepcopy

from flask_resources import ResponseHandler
from invenio_app_rdm.config import APP_RDM_RECORD_EXPORTERS as _STOCK_RECORD_EXPORTERS
from invenio_rdm_records.resources.config import record_serializers
from invenio_records_resources.resources.records.headers import etag_headers

from kcworks.resources.serializers.bibtex.serializer import KCWorksBibtexSerializer

RDM_RECORDS_SERIALIZERS = {
    **record_serializers,
    "application/x-bibtex": ResponseHandler(
        KCWorksBibtexSerializer(),
        headers=etag_headers,
    ),
}
"""API content negotiation (`Accept: application/x-bibtex`)."""

APP_RDM_RECORD_EXPORTERS = deepcopy(_STOCK_RECORD_EXPORTERS)
APP_RDM_RECORD_EXPORTERS["bibtex"] = {
    **APP_RDM_RECORD_EXPORTERS["bibtex"],
    "serializer": (
        "kcworks.resources.serializers.bibtex.serializer:KCWorksBibtexSerializer"
    ),
}
"""UI export dropdown (`/records/<id>/export/bibtex`)."""
