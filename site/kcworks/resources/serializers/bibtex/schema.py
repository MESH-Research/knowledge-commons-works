# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""BibTeX schema with mappings for KCWorks resource type IDs.

Upstream `BibTexSchema.entry_mapper` keys stock Invenio IDs such as
`publication-conferencepaper`. KCWorks uses COAR-style IDs (for example
`textDocument-proceedingsPaper`), so unmapped types always fall through to
`@misc`. This schema keeps the stock map and adds KC equivalents.
"""

from invenio_rdm_records.resources.serializers.bibtex.schema import BibTexSchema
from invenio_rdm_records.resources.serializers.bibtex.schema_formats import (
    BibTexFormatter,
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
            BibTexFormatter.in_collection,
            BibTexFormatter.in_book,
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
