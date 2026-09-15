# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""BibTeX schema with mappings for KCWorks resource type IDs.

Upstream `BibTexSchema.entry_mapper` keys stock Invenio IDs such as
`publication-conferencepaper`. KCWorks uses COAR-style IDs (for example
`textDocument-proceedingsPaper`), so unmapped types always fall through to
`@misc`. This schema keeps the stock map and adds mappings for KC equivalents.

Older invenio-rdm-records builds omit `in_collection` / `in_book` on
`BibTexFormatter`; local fallbacks match upstream when those attributes are
missing.

Older upstream also derives BibTeX year/month from the record `created`
timestamp. We override that to use `metadata.publication_date` (with a
fallback to `created` if unset).
"""

import calendar
import datetime

from babel_edtf import parse_edtf
from edtf.parser.parser_classes import Interval
from invenio_rdm_records.resources.serializers.bibtex.schema import BibTexSchema
from invenio_rdm_records.resources.serializers.bibtex.schema_formats import (
    BibTexFormatter,
)
from pydash import py_

_IN_COLLECTION = getattr(
    BibTexFormatter,
    "in_collection",
    {
        "name": "incollection",
        "req_fields": ["author", "title", "booktitle", "year", "publisher"],
        "opt_fields": [
            "pages",
            "address",
            "month",
            "editor",
            "volume",
            "number",
            "series",
            "doi",
            "url",
        ],
    },
)
_IN_BOOK = getattr(
    BibTexFormatter,
    "in_book",
    {
        "name": "inbook",
        "req_fields": ["author", "title", "pages", "year", "publisher"],
        "opt_fields": [
            "address",
            "month",
            "editor",
            "edition",
            "volume",
            "number",
            "series",
            "note",
            "doi",
            "url",
        ],
    },
)


class KCWorksBibTexSchema(BibTexSchema):
    """BibTeX schema with KCWorks resource-type → entry-type mappings."""

    entry_mapper = {
        **BibTexSchema.entry_mapper,
        # Clear stock equivalents
        "textDocument-proceedingsPaper": [BibTexFormatter.in_proceedings],
        "textDocument-conferenceProceeding": [BibTexFormatter.proceedings],
        "textDocument-book": [
            BibTexFormatter.book,
            BibTexFormatter.booklet,
        ],
        "textDocument-bookSection": [
            _IN_COLLECTION,
            _IN_BOOK,
        ],
        "textDocument-journalArticle": [BibTexFormatter.article],
        "textDocument-preprint": [BibTexFormatter.unpublished],
        "textDocument-thesis": [BibTexFormatter.thesis],
        "textDocument-documentation": [BibTexFormatter.manual],
        "textDocument-workingPaper": [BibTexFormatter.unpublished],
        # Close equivalents
        "textDocument-monograph": [
            BibTexFormatter.book,
            BibTexFormatter.booklet,
        ],
        "software-3DModel": [BibTexFormatter.software],
        "software-application": [BibTexFormatter.software],
        "software-computationalModel": [BibTexFormatter.software],
        "software-computationalNotebook": [BibTexFormatter.software],
        "software-service": [BibTexFormatter.software],
        "software-other": [BibTexFormatter.software],
        # Article stretches (need journal: custom fields for @article)
        "textDocument-abstract": [BibTexFormatter.article],
        "textDocument-editorial": [BibTexFormatter.article],
        "textDocument-essay": [BibTexFormatter.article],
        "textDocument-magazineArticle": [BibTexFormatter.article],
        "textDocument-newspaperArticle": [BibTexFormatter.article],
        "textDocument-review": [BibTexFormatter.article],
    }

    def get_date_created(self, obj):
        """Get BibTeX year/month from publication date, not record `created`.

        Keeps the stock field name `date_created` so `_fetch_fields_map` still
        works. Prefer `metadata.publication_date` (always valid EDTF when set);
        fall back to record `created` only if publication date is absent.

        Returns:
            A dict with `year` and optional `month`, or `None`.
        """
        publication_date = py_.get(obj, "metadata.publication_date")
        if publication_date:
            parsed_date = parse_edtf(publication_date)
            if isinstance(parsed_date, Interval):
                parsed_date = parsed_date.lower
            date_info = {"year": str(parsed_date.year)}
            if parsed_date.month:
                date_info["month"] = calendar.month_abbr[
                    int(parsed_date.month)
                ].lower()
            return date_info

        created = obj.get("created")
        if not created:
            return None
        date_obj = datetime.datetime.fromisoformat(created)
        return {
            "month": date_obj.strftime("%b").lower(),
            "year": date_obj.strftime("%Y"),
        }
