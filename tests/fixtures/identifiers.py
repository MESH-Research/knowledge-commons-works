# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 MESH Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures for identifiers."""

import idutils
from invenio_rdm_records.config import (
    RDM_RECORDS_IDENTIFIERS_SCHEMES,
    RDM_RECORDS_PERSONORG_SCHEMES,
    always_valid,
)
from invenio_rdm_records.services.pids import providers

from tests.helpers.fake_datacite_client import FakeDataCiteClient


def is_email(value):
    """Simple email validation function.

    Returns:
        bool: True if value is a valid email, False otherwise.
    """
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def _(x):
    """Identity function for string extraction.

    Returns:
        str: The input string unchanged.
    """
    return x


test_config_identifiers = {
    "RDM_PERSISTENT_IDENTIFIERS": {
        "doi": {
            "providers": ["datacite", "external"],
            "required": True,
            "label": _("DOI"),
            "validator": idutils.is_doi,
            "normalizer": idutils.normalize_doi,
            "is_enabled": lambda x: True,
            # "is_enabled": providers.DataCitePIDProvider.is_enabled,
        },
        "oai": {
            "providers": ["oai"],
            "required": True,
            "label": _("OAI"),
            "is_enabled": providers.OAIPIDProvider.is_enabled,
        },
    },
    "RDM_PARENT_PERSISTENT_IDENTIFIERS": {
        "doi": {
            "providers": ["datacite"],
            "required": True,
            "condition": (
                lambda rec: rec.pids.get("doi", {}).get("provider") == "datacite"
            ),
            "label": _("Concept DOI"),
            "validator": idutils.is_doi,
            "normalizer": idutils.normalize_doi,
            "is_enabled": lambda x: True,
            # "is_enabled": providers.DataCitePIDProvider.is_enabled,
        },
    },
    # TODO: Is there a reason to use a fake Datacite client?
    # the one in fake_datacite_client.py borrowed from invenio_rdm_records
    # conflicts with use of requests_mock in test_component
    "RDM_PERSISTENT_IDENTIFIER_PROVIDERS": [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=FakeDataCiteClient("datacite", config_prefix="DATACITE"),
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
    ],
    "RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS": [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=FakeDataCiteClient("datacite", config_prefix="DATACITE"),
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
    ],
    "RDM_RECORDS_IDENTIFIERS_SCHEMES": {
        **RDM_RECORDS_IDENTIFIERS_SCHEMES,
        "doi:": {
            "label": _("DOI"),
            "validator": idutils.is_doi,
            "datacite": "DOI",
        },
        "datacite-doi": {
            "label": _("DataCite DOI"),
            "validator": idutils.is_doi,
            "datacite": "Other",
        },
        "handle": {
            "label": _("Handle"),
            "validator": idutils.is_handle,
            "datacite": "Handle",
        },
        "isbn": {
            "label": _("ISBN"),
            "validator": idutils.is_isbn,
            "datacite": "ISBN",
        },
        "isni": {
            "label": _("ISNI"),
            "validator": idutils.is_isni,
            "datacite": "ISNI",
        },
        "issn": {
            "label": _("ISSN"),
            "validator": idutils.is_issn,
            "datacite": "ISSN",
        },
        "url": {
            "label": _("URL"),
            "validator": idutils.is_url,
            "datacite": "URL",
        },
        "other": {
            "label": _("Other"),
            "validator": always_valid,
            "datacite": "Other",
        },
        # KCWorks custom identifier schemes
        "hclegacy-pid": {
            "label": _("Humanities Commons Legacy PID"),
            "validator": always_valid,
            "datacite": "Other",
        },
        "hclegacy-record-id": {
            "label": _("Humanities Commons Legacy Record ID"),
            "validator": always_valid,
            "datacite": "Other",
        },
        # Import schemes
        "import-recid": {
            "label": _("Import record ID"),
            "validator": always_valid,
            "datacite": "Other",
        },
    },
    "RDM_RECORDS_PERSONORG_SCHEMES": {
        **RDM_RECORDS_PERSONORG_SCHEMES,
        "orcid": {
            "label": _("ORCID"),
            "validator": idutils.is_orcid,
            "datacite": "ORCID",
        },
        "email": {
            "label": _("Email"),
            "validator": is_email,
            "datacite": "Other",
        },
        # KCWorks custom person/org identifier schemes
        "hc_username": {
            "label": _("KC member"),
            "validator": always_valid,
            "datacite": "Other",
        },
    },
    "VOCABULARIES_IDENTIFIER_SCHEMES": {
        "grid": {"label": _("GRID"), "validator": lambda x: True},
        "gnd": {"label": _("GND"), "validator": idutils.is_gnd},
        "isni": {"label": _("ISNI"), "validator": idutils.is_isni},
        "ror": {"label": _("ROR"), "validator": idutils.is_ror},
    },
    "VOCABULARIES_FUNDER_SCHEMES": {
        "doi": {"label": _("DOI"), "validator": idutils.is_doi},
        "ofr": {
            "label": _("Open Funder Registry"),
            "validator": lambda x: True,
        },
    },
}
