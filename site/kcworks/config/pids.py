# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier (DOI/OAI) settings for KCWorks.

Centralizes the DataCite client configuration and the InvenioRDM
``RDM_PERSISTENT_IDENTIFIER*`` settings that depend on it: the DOI/OAI
provider list and the per-record / parent-record PID definitions.

See https://inveniordm.docs.cern.ch/customize/dois/ for the upstream
config surface; this module just supplies KCWorks' values.
"""

import os

import idutils
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.services.pids import providers

# DataCite client configuration
# -----------------------------
DATACITE_ENABLED = True
DATACITE_PREFIX = "10.17613"
DATACITE_TEST_MODE = (
    False if os.getenv("INVENIO_DATACITE_TEST_MODE") == "False" else True
)
DATACITE_DATACENTER_SYMBOL = "MSU.CORE"

# Persistent identifier providers
# -------------------------------
RDM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite DOI provider
    providers.DataCitePIDProvider(
        "datacite",
        client=providers.DataCiteClient("datacite", config_prefix="DATACITE"),
        label=_("DOI"),
    ),
    # DOI provider for externally managed DOIs
    providers.ExternalPIDProvider(
        "external",
        "doi",
        validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
        label=_("DOI"),
    ),
    # OAI identifier
    providers.OAIPIDProvider(
        "oai",
        label=_("OAI ID"),
    ),
]

# TODO: Remove this and next config value when the updated default
#       implementation is merged in Invenio-RDM-Records
RDM_PERSISTENT_IDENTIFIERS = {
    # DOI automatically removed if DATACITE_ENABLED is False.
    "doi": {
        "providers": ["datacite", "external"],
        "required": True,
        "label": _("DOI"),
        "validator": idutils.is_doi,
        "normalizer": idutils.normalize_doi,
        "is_enabled": providers.DataCitePIDProvider.is_enabled,
    },
    "oai": {
        "providers": ["oai"],
        "required": True,
        "label": _("OAI"),
        "is_enabled": providers.OAIPIDProvider.is_enabled,
    },
}
"""The configured persistent identifiers for records."""

RDM_PARENT_PERSISTENT_IDENTIFIERS = {
    "doi": {
        "providers": ["datacite"],
        "required": True,
        "condition": lambda rec: rec.pids.get("doi", {}).get("provider") == "datacite",
        "label": _("Concept DOI"),
        "validator": idutils.is_doi,
        "normalizer": idutils.normalize_doi,
        "is_enabled": providers.DataCitePIDProvider.is_enabled,
    },
}
"""Persistent identifiers for parent record."""
