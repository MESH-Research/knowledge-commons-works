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

from idutils import is_doi, is_gnd, is_isni, is_ror
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
        "validator": is_doi,
        "datacite": "DOI",
    },
    "alternate-doi:": {
        "label": _("Alternate DOI"),
        "validator": is_doi,
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
    "gnd": {"label": _("GND"), "validator": is_gnd},
    "isni": {"label": _("ISNI"), "validator": is_isni},
    "ror": {"label": _("ROR"), "validator": is_ror},
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
    "doi": {"label": _("DOI"), "validator": is_doi},
}
"""Funders allowed identifier schemes."""

VOCABULARIES_AWARDS_OPENAIRE_FUNDERS = {
    **_UPSTREAM_OPENAIRE_FUNDERS,
    "cf__________": "01kpjmx04",  # Carlsberg Foundation (DK)
    "ibf_________": "05bgf9v38",  # Innovaatiorahoituskeskus Business Finland (FI)
    "fcf_________": "027xav248",  # The Finnish Cultural Foundation (FI)
    "jaef________": "03vxy9y38",  # Jane and Aatos Erkko Foundation (FI)
    # OpenAIRE diff (projects.tar) funders — verified against ROR, Jul 2026 audit.
    # Counts are project records in Zenodo 20407508 at audit time.
    "erasmusplus_": "00k4n6c32",  # European Commission (Erasmus+) — 10,977
    # Sweden
    "vinnova_____": "01kd5m353",  # Vinnova — 23,923
    "vr__________": "03zttf063",  # Swedish Research Council — 22,097
    "formas______": "03pjs1y45",  # Formas — 7,285
    "stem________": "0359z7n90",  # Swedish Energy Agency — 5,386
    "forte_______": "02d290r06",  # Forte — 2,657
    "hl__________": "052261q33",  # Swedish Heart-Lung Foundation — 1,211
    "rj__________": "02jkbm893",  # Riksbankens Jubileumsfond — 1,201
    "snsa________": "04t512h04",  # Swedish National Space Agency — 604
    "kff_________": "03qb1q739",  # Kamprad Family Foundation — 294
    "fbs_________": "055mqk127",  # Baltic and East European Studies — 242
    "ki__________": "056d84691",  # Karolinska Institutet — 451
    "ifau________": "015zanq20",  # IFAU — 120
    # Czech Republic
    "ga0_________": "01pv73b02",  # Czech Science Foundation — 21,619
    "msm_________": "037n8p820",  # Ministry of Education, Youth and Sports — 11,357
    "mpo_________": "03j4eb467",  # Ministry of Industry and Trade — 5,803
    "ta0_________": "04v0fk911",  # Technology Agency of the Czech Republic — 5,496
    "av0_________": "053avzc18",  # Czech Academy of Sciences — 3,666
    "mzp_________": "04e74dh47",  # Ministry of the Environment — 572
    "mps_________": "01bvj3e58",  # Ministry of Labour and Social Affairs — 256
    "md0_________": "00p9p2506",  # Ministry of Transport — 269
    # Ireland & Greece
    "100010414___": "003hb2249",  # Health Research Board — 1,890
    "ri__________": "010t7sr36",  # Taighde Éireann — Research Ireland — 404
    "hfri________": "05v75r592",  # HFRI (GR) — 378
    "gsri________": "04yeh8h63",  # GSRT Greece — 3,246
    # Italy & Finland
    "miur________": "01ehyh486",  # Ministero dell'Istruzione e del Merito — 443
    "kf__________": "05jwty529",  # Kone Foundation — 228
    "kaute_______": "00zwv5854",  # Kaute Foundation — 38
    # Full OpenAIRE graph (project.tar) — verified against ROR, Jul 2026 audit.
    # Counts are project records in Zenodo 20428976 at audit time.
    "dfgf________": "018mejw64",  # DFG — 32,199
    "rcn_________": "00epmv149",  # Research Council of Norway — 25,208
    "irfd________": "05svhj534",  # Independent Research Fund Denmark (DFF) — 4,019
    "nnf_________": "04txyc737",  # Novo Nordisk Foundation — 3,082
    "lf__________": "03hz8wd80",  # Lundbeck Foundation — 1,279
    "rif_________": "00en9ce74",  # Research and Innovation Foundation (CY) — 1,170
    "ve__________": "05nqkay65",  # Villum Foundation — 773
    # Review: three ROR Velux foundations; OpenAIRE jurisdiction is DK.
    "vf__________": "013w1n936",  # VELUX Foundation — 257
    "pf__________": "048e7gn38",  # Paulo Foundation — 171
    # Review: no CHIST-ERA ROR funder; EU ERA-NET → EC (same as corda_*).
    "chistera____": "00k4n6c32",  # CHIST-ERA — 138
    "drf_________": "004j3q729",  # Diabetes Research Foundation (FI) — 120
    "kks_________": "02cbq7e25",  # KK-stiftelsen — 32
    # Review: exact name match; literary society typed as funder in ROR.
    "sslf________": "04a31ep84",  # Society of Swedish Literature in Finland — 27
    # Still unmapped in latest diff (no confident ROR funder match at audit time):
    # mz0_________ Ministry of Health (CZ) — 6,248
    # mze_________ Ministry of Agriculture (CZ) — 2,051
    # mk0_________ Ministry of Culture (CZ) — 947
    # mo0_________ Ministry of Defence (CZ) — 924
    # mv0_________ Ministry of Interior (CZ) — 708
    # mzv_________ Ministry of Foreign Affairs (CZ) — 292
    # frif________ Finnish Research Impact Foundation — 30 (no ROR record yet)
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
