# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Vocabulary and identifier-scheme settings for KCWorks.

``invenio.cfg`` re-exports these values so
Flask's config loader picks them up as instance config.
"""

import idutils
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.config import (
    RDM_RECORDS_IDENTIFIERS_SCHEMES,
    RDM_RECORDS_PERSONORG_SCHEMES,
    always_valid,
)
from invenio_vocabularies.config import (
    VOCABULARIES_AWARDS_OPENAIRE_FUNDERS as _UPSTREAM_OPENAIRE_FUNDERS,
)
from invenio_vocabularies.config import (
    VOCABULARIES_NAMES_SCHEMES as _UPSTREAM_NAMES_SCHEMES,
)

from kcworks.services.records.validators import is_email

RDM_RECORDS_IDENTIFIERS_SCHEMES.update({
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
    "datacite-doi": {
        "label": _("DOI (DataCite)"),
        "validator": idutils.is_doi,
        "datacite": "DOI",
    },
    "alternate-doi:": {
        "label": _("Alternate DOI"),
        "validator": idutils.is_doi,
        "datacite": "Other",
    },
    "import-recid": {
        "label": _("Import record ID"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "neh-recid": {
        "label": _("NEH record ID"),
        "validator": always_valid,
        "datacite": "Other",
    },
})
"""Record-level identifier schemes"""

RDM_RECORDS_PERSONORG_SCHEMES.update({
    "hcid": {
        "label": _("hcid"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "kcid": {
        "label": _("kcid"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "hc_username": {
        "label": _("KC member"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "kc_username": {
        "label": _("KC member"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "neh_user_id": {
        "label": _("NEH user ID"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "import_user_id": {
        "label": _("Import user ID"),
        "validator": always_valid,
        "datacite": "Other",
    },
    "email": {
        "label": _("Email"),
        "validator": is_email,
        "datacite": "Other",
    },
})
""" Person/organisation identifier schemes (creators, contributors)"""

VOCABULARIES_IDENTIFIER_SCHEMES = {
    "grid": {"label": _("GRID"), "validator": lambda x: True},
    "gnd": {"label": _("GND"), "validator": idutils.is_gnd},
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni},
    "ror": {"label": _("ROR"), "validator": idutils.is_ror},
}
"""Generic identifier schemes, usable by other vocabularies."""

VOCABULARIES_NAMES_SCHEMES = {
    **_UPSTREAM_NAMES_SCHEMES,
    "kc_username": {
        "label": _("KC member"),
        "validator": always_valid,
        "datacite": "Other",
    },
}
"""Names vocabulary allowed identifier schemes (KCWorks extensions)."""

VOCABULARIES_FUNDER_SCHEMES = {
    **VOCABULARIES_IDENTIFIER_SCHEMES,
    "doi": {"label": _("DOI"), "validator": idutils.is_doi},
}
"""Funders allowed identifier schemes."""

VOCABULARIES_AWARDS_OPENAIRE_FUNDERS = {
    **_UPSTREAM_OPENAIRE_FUNDERS,
    "cf__________": "01kpjmx04",  # Carlsberg Foundation (DK)
    "ibf_________": "05bgf9v38",  # Innovaatiorahoituskeskus Business Finland (FI)
    "fcf_________": "027xav248",  # The Finnish Cultural Foundation (FI)
    "jaef________": "03vxy9y38",  # Jane and Aatos Erkko Foundation (FI)
    # "edtech______": "04h9xka55",  # Teknologi Pendidikan ID (Indonesia).
    # Disabled: ROR record is typed only as ``company``, so the funders
    # vocabulary loader skips it and the awards writer would fail with
    # "funder not found" for every EDTECH-ID project. Re-enable once ROR
    # adds ``funder`` to the record's types or we seed the funder entry
    # manually.
}
"""OpenAIRE funder prefix -> ROR ID overrides.

Extends the upstream OpenAIRE → ROR funder prefix mapping with funders
that appear in the OpenAIRE projects feed but are not yet covered by
invenio-vocabularies' built-in dictionary. 
"""
