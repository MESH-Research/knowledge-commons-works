import idutils
from invenio_rdm_records.services.pids import providers
from invenio_rdm_records.config import (
    always_valid,
    RDM_RECORDS_IDENTIFIERS_SCHEMES,
    RDM_RECORDS_PERSONORG_SCHEMES,
)
from ..helpers.fake_datacite_client import FakeDataCiteClient


def _(x):
    """Identity function for string extraction."""
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
                lambda rec: rec.pids.get("doi", {}).get("provider")
                == "datacite"
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
            validators=[
                providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])
            ],
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
            validators=[
                providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])
            ],
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
        "kc_username": {
            "label": _("Knowledge Commons Username"),
            "validator": always_valid,
            "datacite": "Other",
        },
        "hc_username": {
            "label": _("Humanities Commons Username"),
            "validator": always_valid,
            "datacite": "Other",
        },
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
    },
    "RDM_RECORDS_PERSONORG_SCHEMES": {
        **RDM_RECORDS_PERSONORG_SCHEMES,
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
