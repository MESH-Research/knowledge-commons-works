# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Search-related configuration variables."""

import os

from invenio_access.permissions import system_permission
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.contrib.codemeta import CODEMETA_FACETS
from invenio_rdm_records.services import facets
from invenio_rdm_records.services.queryparser import word_internal_notes
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records_resources.services.records.queryparser.transformer import (
    RestrictedTerm,
    RestrictedTermValue,
)

from kcworks.services.search.queryparser import MultiFieldSearchTransformer

# OpenSearch configuration
# =======================

SEARCH_DOMAIN = os.getenv("INVENIO_SEARCH_DOMAIN", "search:9200")
SEARCH_INDEX_PREFIX = "kcworks-"


SEARCH_CLIENT_CONFIG = {
    "http_compress": True,
    # Built-in resilience features - compatible with OpenSearch client
    "timeout": 60,  # Default timeout for normal operations (searches, health checks)
    "max_retries": 5,  # Number of retry attempts (increased for production)
    "retry_on_timeout": True,  # Retry on timeout
    "retry_on_status": [429, 500, 502, 503, 504],  # HTTP status codes to retry
    "backoff_factor": 2,  # Exponential backoff multiplier
    "max_backoff": 120,  # Maximum backoff time in seconds (increased)
    # Connection pooling
    "maxsize": 25,  # Maximum number of connections in pool
    "retry_on_connection_error": True,
    # SSL configuration (if needed)
    # "use_ssl": False,
    # "verify_certs": False,
    # "ssl_assert_hostname": False,
    # "ssl_show_warn": False,
}

# Search alias configuration
# ========================

# --- Combined field groups (OR-expanded by MultiFieldSearchTransformer) ---

_TITLE_FIELDS = (
    "metadata.title",
    "metadata.additional_titles.title",
)

_DESCRIPTION_FIELDS = (
    "metadata.description",
    "metadata.additional_descriptions.description",
)

_CREATORS_AND_CONTRIBUTORS_FIELD = (
    "metadata.creators.person_or_org.name",
    "metadata.contributors.person_or_org.name",
    "metadata.creators.person_or_org.identifiers.identifier",
    "metadata.contributors.person_or_org.identifiers.identifier",
)

_AFFILIATIONS_FIELD = (
    "metadata.creators.affiliations.name",
    "metadata.contributors.affiliations.name",
    "metadata.creators.affiliations.identifiers.identifier",
    "metadata.contributors.affiliations.identifiers.identifier",
)

_FUNDER_FIELDS = (
    "metadata.funding.funder.name",
    "metadata.funding.funder.identifiers.identifier",
)

_AWARD_FIELDS = (
    "metadata.funding.award.title.*",
    "metadata.funding.award.number",
)

# Indexed identifier values for scheme `ror` (and other schemes stored alongside).
_ROR_FIELDS = (
    "metadata.creators.affiliations.identifiers.identifier",
    "metadata.contributors.affiliations.identifiers.identifier",
    "metadata.funding.funder.identifiers.identifier",
    "metadata.creators.person_or_org.identifiers.identifier",
    "metadata.contributors.person_or_org.identifiers.identifier",
)

_DEGREE_FIELDS = (
    "custom_fields.kcr:degree",
    "custom_fields.thesis:thesis.type",
)

_DEPARTMENT_FIELDS = (
    "custom_fields.thesis:thesis.department",
    "custom_fields.kcr:institution_department",
)

_DEPARTMENT_AND_DISCIPLINE_FIELDS = (
    "custom_fields.thesis:thesis.department",
    "custom_fields.kcr:institution_department",
    "custom_fields.kcr:discipline",
)

_PLACE_FIELDS = (
    "metadata.locations.features.place",
    "custom_fields.meeting:meeting.place",
    "custom_fields.imprint:imprint.place",
)

_URL_FIELDS = (
    "metadata.identifiers.identifier",
    "metadata.related_identifiers.identifier",
    "custom_fields.kcr:publication_url",
    "custom_fields.meeting:meeting.url",
    "custom_fields.code:codeRepository",
)

# Broad org search: names and identifiers, not creator person names.
_ORGANIZATION_FIELDS = (
    *_AFFILIATIONS_FIELD,
    *_FUNDER_FIELDS,
    "metadata.publisher",
    "custom_fields.thesis:thesis.university",
    "custom_fields.kcr:sponsoring_institution",
    "custom_fields.kcr:meeting_organization",
)

_UNIVERSITY_FIELDS = (
    *_AFFILIATIONS_FIELD,
    "custom_fields.thesis:thesis.university",
    "custom_fields.kcr:sponsoring_institution",
)

_SPONSORING_INSTITUTION_FIELD = "custom_fields.kcr:sponsoring_institution"

_EDITION_FIELDS = (
    "custom_fields.imprint:imprint.edition",
    "custom_fields.kcr:edition",
)

# Collection membership: UUID ids plus denormalized slug/title on the parent.
_COLLECTION_FIELDS = (
    "parent.communities.ids",
    "parent.communities.entries.slug",
    "parent.communities.entries.metadata.title",
)

RECORD_SEARCH_FIELD_ALIASES = {
    # --- Record identity ---
    "id": "id",
    "recid": "id",
    "doi": "pids.doi.identifier",
    "identifier": "metadata.identifiers.identifier",
    "identifiers": "metadata.identifiers.identifier",
    "owner": "parent.access.owned_by.user",
    # --- Core bibliographic metadata ---
    "title": _TITLE_FIELDS,
    "description": _DESCRIPTION_FIELDS,
    "abstract": _DESCRIPTION_FIELDS,
    "additional_description": "metadata.additional_descriptions.description",
    "additional_descriptions": "metadata.additional_descriptions.description",
    "publisher": "metadata.publisher",
    "publication_date": "metadata.publication_date",
    "date": "metadata.publication_date",
    "version": "metadata.version",
    "language": "metadata.languages.id",
    "languages": "metadata.languages.id",
    "format": "metadata.formats",
    "formats": "metadata.formats",
    "size": "metadata.sizes",
    "sizes": "metadata.sizes",
    "reference": "metadata.references.reference",
    "references": "metadata.references.reference",
    "place": _PLACE_FIELDS,
    # --- URLs: broad + per-source ---
    "url": _URL_FIELDS,
    "alternate_url": "metadata.identifiers.identifier",
    "identifier_url": "metadata.identifiers.identifier",
    "related_url": "metadata.related_identifiers.identifier",
    "publication_url": "custom_fields.kcr:publication_url",
    "meeting_url": "custom_fields.meeting:meeting.url",
    "repository_url": "custom_fields.code:codeRepository",
    "repository": "custom_fields.code:codeRepository",
    # --- People (creators + contributors unified) ---
    "contributor": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "contributors": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "creator": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "creators": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "author": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "authors": _CREATORS_AND_CONTRIBUTORS_FIELD,
    "affiliation": _AFFILIATIONS_FIELD,
    "affiliations": _AFFILIATIONS_FIELD,
    "funder": _FUNDER_FIELDS,
    "funding": _FUNDER_FIELDS,
    "award": _AWARD_FIELDS,
    "ror": _ROR_FIELDS,
    # --- Organizations (broad + specific) ---
    "organization": _ORGANIZATION_FIELDS,
    "institution": _ORGANIZATION_FIELDS,
    "university": _UNIVERSITY_FIELDS,
    "sponsoring_institution": _SPONSORING_INSTITUTION_FIELD,
    "sponsor": _SPONSORING_INSTITUTION_FIELD,
    # --- Subjects vs user keywords ---
    "subject": "metadata.subjects.subject",
    "subjects": "metadata.subjects.subject",
    "keyword": "custom_fields.kcr:user_defined_tags",
    "keywords": "custom_fields.kcr:user_defined_tags",
    # --- Degree / department / discipline ---
    "degree": _DEGREE_FIELDS,
    "thesis_type": _DEGREE_FIELDS,
    "department": _DEPARTMENT_AND_DISCIPLINE_FIELDS,
    "thesis_department": _DEPARTMENT_FIELDS,
    "discipline": _DEPARTMENT_AND_DISCIPLINE_FIELDS,
    # --- Resource type & access ---
    "type": "metadata.resource_type.id",
    "resource_type": "metadata.resource_type.id",
    "access": "access.status",
    "access_status": "access.status",
    "published": "is_published",
    "is_published": "is_published",
    # --- Files ---
    "file": "files.entries.key",
    "filename": "files.entries.key",
    "file_type": "files.types",
    # --- Collections (Invenio communities on the parent) ---
    "collection": _COLLECTION_FIELDS,
    "collections": _COLLECTION_FIELDS,
    # --- Stock custom fields: journal ---
    "journal": "custom_fields.journal:journal.title",
    "journal_title": "custom_fields.journal:journal.title",
    "journal_volume": "custom_fields.journal:journal.volume",
    "journal_issue": "custom_fields.journal:journal.issue",
    "issn": "custom_fields.journal:journal.issn",
    # --- Stock custom fields: thesis (no generic "thesis" shorthand) ---
    "thesis_university": "custom_fields.thesis:thesis.university",
    # --- Stock custom fields: meeting ---
    "meeting": "custom_fields.meeting:meeting.title",
    "meeting_title": "custom_fields.meeting:meeting.title",
    "meeting_acronym": "custom_fields.meeting:meeting.acronym",
    "meeting_dates": "custom_fields.meeting:meeting.dates",
    "conference": "custom_fields.meeting:meeting.title",
    # --- Stock custom fields: imprint ---
    "imprint": "custom_fields.imprint:imprint.title",
    "book_title": "custom_fields.imprint:imprint.title",
    "book": "custom_fields.imprint:imprint.title",
    "isbn": "custom_fields.imprint:imprint.isbn",
    "edition": _EDITION_FIELDS,
    # --- Stock custom fields: codemeta ---
    "code_repository": "custom_fields.code:codeRepository",
    "programming_language": "custom_fields.code:programmingLanguage",
    "development_status": "custom_fields.code:developmentStatus.id",
    # --- KCWorks custom fields ---
    "note": "custom_fields.kcr:notes.note_text",
    "notes": "custom_fields.kcr:notes.note_text",
    "chapter": "custom_fields.kcr:chapter_label",
    "course": "custom_fields.kcr:course_title",
    "project": "custom_fields.kcr:project_title",
    "series": "custom_fields.kcr:book_series.series_title",
    "ai": "custom_fields.kcr:ai_usage.ai_used",
    "ai_used": "custom_fields.kcr:ai_usage.ai_used",
    "ai_description": "custom_fields.kcr:ai_usage.ai_description",
    # --- Upstream permission gates (from invenio-rdm-records RDM_SEARCH) ---
    "internal_notes.note": RestrictedTerm(system_permission),
    "internal_notes.id": RestrictedTerm(system_permission),
    "internal_notes.added_by": RestrictedTerm(system_permission),
    "internal_notes.timestamp": RestrictedTerm(system_permission),
    "_exists_": RestrictedTermValue(
        system_permission,
        word=word_internal_notes,
    ),
}

DEFAULT_SEARCH_FIELDS = [
    # Upstream defaults from record-v7.0.0.json mapping
    "id",
    "metadata.title^5",
    "metadata.title.original^5",
    "metadata.contact",
    "metadata.contributors.affiliations.name",
    "metadata.contributors.person_or_org.name^5",
    "metadata.contributors.person_or_org.family_name^5",
    "metadata.contributors.person_or_org.given_name^3",
    "metadata.creators.affiliations.name^1",
    "metadata.creators.person_or_org.name^5",
    "metadata.creators.person_or_org.family_name^5",
    "metadata.creators.person_or_org.given_name^3",
    "metadata.description",
    "metadata.formats",
    "metadata.funding.award.identifiers.identifier^1",
    "metadata.funding.award.acronym.text",
    "metadata.funding.award.number^1",
    "metadata.funding.funder.name^1",
    "metadata.identifiers.identifier^1",
    "metadata.locations.features.place",
    "metadata.locations.features.description",
    "metadata.publication_date",
    "metadata.publisher",
    "metadata.subjects.subject^1",
    "metadata.version",
    "metadata.dates.description",
    "metadata.additional_descriptions.description",
    "metadata.references.reference",
    "metadata.additional_titles.title^3",
    # Added by us to the default fields
    "custom_fields.kcr:sponsoring_institution",
    "custom_fields.kcr:meeting_organization",
    "custom_fields.kcr:project_title",
    "custom_fields.kcr:course_title",
    "custom_fields.kcr:user_defined_tags^1",
    "custom_fields.imprint:imprint.title^3",
    "custom_fields.journal:journal.title",
    "custom_fields.meeting:meeting.title",
    "pids.doi.identifier",
]


RECORD_SEARCH_QUERY_PARSER = QueryParser.factory(
    mapping=RECORD_SEARCH_FIELD_ALIASES,
    tree_transformer_cls=MultiFieldSearchTransformer,
    fields=DEFAULT_SEARCH_FIELDS,
)


# Search facets
# ==============

RDM_FACETS = {
    "is_published": {
        "facet": facets.is_published,
        "ui": {
            "field": "is_published",
        },
    },
    "resource_type": {
        "facet": facets.resource_type,
        "ui": {
            "field": "resource_type.type",
            "childAgg": {
                "field": "resource_type.subtype",
            },
        },
    },
    "file_type": {
        "facet": facets.filetype,
        "ui": {
            "field": "files.types",
        },
    },
    "language": {
        "facet": facets.language,
        "ui": {
            "field": "languages",
        },
    },
    "access_status": {
        "facet": facets.access_status,
        "ui": {
            "field": "access.status",
        },
    },
    "subject_nested": {
        "facet": facets.subject_nested,
        "ui": {
            "field": "subjects.scheme",
            "childAgg": {
                "field": "subjects.subject",
            },
        },
    },
    "subject": {
        "facet": facets.subject,
        "ui": {
            "field": "subjects.subject",
        },
    },
    **CODEMETA_FACETS,
}

# Search sorting
# ==============

RDM_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # search defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
    "published-desc": dict(
        title=_("Most recently published"),
        fields=["-metadata.publication_date"],
    ),
    "published-asc": dict(
        title=_("Earliest published"),
        fields=["metadata.publication_date"],
    ),
    "version": dict(
        title=_("Version"),
        fields=["-versions.index"],
    ),
    "updated-desc": dict(
        title=_("Recently updated"),
        fields=["-updated"],
    ),
    "updated-asc": dict(
        title=_("Least recently updated"),
        fields=["updated"],
    ),
    "mostviewed": dict(
        title=_("Most viewed"), fields=["-stats.all_versions.unique_views"]
    ),
    "mostdownloaded": dict(
        title=_("Most downloaded"), fields=["-stats.all_versions.unique_downloads"]
    ),
}

# Service search configurations
# ===============================

# Backend search options for /api/records and community-records API (q=
# parsing/aliases, service facets/sort). Community UI sidebar does NOT read this
# for which facets/sort to display — see COMMUNITIES_RECORDS_SEARCH.
RDM_SEARCH = {
    "facets": [
        "resource_type",
        "language",
        "file_type",
        "access_status",
        "programmingLanguage",
        "developmentStatus",
    ],
    "sort": [
        "bestmatch",
        "newest",
        "oldest",
        "published-desc",
        "published-asc",
        "version",
        "mostviewed",
        "mostdownloaded",
    ],
    "query_parser_cls": RECORD_SEARCH_QUERY_PARSER,
}

# User uploads / drafts search (/api/user/records). Facets/sort match upstream
# RDM defaults; aliases use the same parser as RDM_SEARCH.
RDM_SEARCH_DRAFTS = {
    "facets": ["access_status", "is_published", "resource_type", "file_type"],
    "sort": [
        "bestmatch",
        "updated-desc",
        "updated-asc",
        "newest",
        "oldest",
        "version",
    ],
    "query_parser_cls": RECORD_SEARCH_QUERY_PARSER,
}

# React-SearchKit config for community/collection records pages only: which
# facets and sort options the sidebar shows. Keep facet/sort lists aligned with
# RDM_SEARCH. Query aliases still come from RDM_SEARCH via the API.
COMMUNITIES_RECORDS_SEARCH = {
    "facets": [
        "resource_type",
        "language",
        "file_type",
        "access_status",
        "programmingLanguage",
        "developmentStatus",
    ],
    "sort": [
        "bestmatch",
        "newest",
        "oldest",
        "published-desc",
        "published-asc",
        "version",
        "mostviewed",
        "mostdownloaded",
    ],
}

RDM_SEARCH_USER_COMMUNITIES = {
    "facets": ["visibility", "type"],
    "sort": ["bestmatch", "newest", "oldest"],
    "sort_default": "bestmatch",
    "sort_default_no_query": "newest",
}
"""User communities search configuration (i.e list of user communities)
This affects the community search modal in the detail page.
"""

COMMUNITIES_SEARCH = {
    "facets": ["type", "visibility"],
    "sort": ["bestmatch", "newest", "oldest"],
    "sort_default": "bestmatch",
    "sort_default_no_query": "newest",
}
"""Community search configuration (i.e list of communities)
This affects the community search modal in the upload form.
"""
