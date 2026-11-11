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

from idutils import is_doi, normalize_doi
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.services.pids import providers

from kcworks.config.site_urls import KC_PROFILES_URL_BASE
from kcworks.services.pids.datacite import RetryingDataCitePIDProvider

# DataCite client configuration
# -----------------------------
DATACITE_ENABLED = True
DATACITE_PREFIX = "10.17613"
DATACITE_TEST_MODE = (
    False if os.getenv("INVENIO_DATACITE_TEST_MODE") == "False" else True
)
DATACITE_DATACENTER_SYMBOL = "MSU.CORE"

# Transient DataCite API retries (transport errors and 5xx / server errors).
DATACITE_RETRY_ATTEMPTS = 3
DATACITE_RETRY_BACKOFF_SECONDS = 0.5

# Persistent identifier providers
# -------------------------------
RDM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite DOI provider (retries transient remote API failures)
    RetryingDataCitePIDProvider(
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
        "validator": is_doi,
        "normalizer": normalize_doi,
        "is_enabled": RetryingDataCitePIDProvider.is_enabled,
        "ui": {"default_selected": "no"},
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
        "validator": is_doi,
        "normalizer": normalize_doi,
        "is_enabled": RetryingDataCitePIDProvider.is_enabled,
    },
}
"""Persistent identifiers for parent record."""

# Identifier urls
# pid follows end of each string
# urn expects to begin 'urn:nbn'
LANDING_URLS = {
    "ads": "https://ui.adsabs.harvard.edu/#abs/",
    "arrayexpress_array": "https://www.ebi.ac.uk/arrayexpress/arrays/",
    "arrayexpress_experiment": "https://www.ebi.ac.uk/arrayexpress/experiments/",
    "arxiv": "https://arxiv.org/abs/",
    "ascl": "https://ascl.net/",
    "bioproject": "https://www.ebi.ac.uk/ena/data/view/",
    "biosample": "https://www.ebi.ac.uk/ena/data/view/",
    "doi": "https://doi.org/",
    "ensembl": "https://www.ensembl.org/id/",
    "genome": "https://www.ncbi.nlm.nih.gov/assembly/",
    "geo": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
    "gnd": "https://d-nb.info/gnd/",
    "hal": "https://hal.archives-ouvertes.fr/",
    "handle": "https://hdl.handle.net/",
    "hcommons_username": KC_PROFILES_URL_BASE,
    "kcommons_username": KC_PROFILES_URL_BASE,
    "isni": "https://isni.org/isni/",
    "orcid": "https://orcid.org/",
    "pmid": "https://pubmed.ncbi.nlm.nih.gov/",
    "pmcid": "https://www.ncbi.nlm.nih.gov/pmc/",
    "refseq": "https://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi?val=",
    "ror": "https://ror.org/",
    "sra": "https://www.ebi.ac.uk/ena/data/view/",
    "swh": "https://archive.softwareheritage.org/",
    "urn": "https://nbn-resolving.org/",
    "uniprot": "https://purl.uniprot.org/uniprot/",
    "viaf": "https://viaf.org/viaf/",
}
"""URL generation configuration for the supported PID providers."""
