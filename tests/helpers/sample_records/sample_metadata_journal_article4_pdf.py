# Part of Knowledge Commons Works
# Copyright (C) 2025 Mesh Research
#
# KCWorks is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample metadata for a journal article 4 with PDF file for testing purposes."""

sample_metadata_journal_article4_pdf = {
    "id": "jthhs-g4b38",
    "created": "2025-06-03T20:51:12.325212+00:00",
    "updated": "2025-06-03T20:51:12.462073+00:00",
    "pids": {
        "doi": {
            "identifier": "10.17613/jthhs-g4b38",
            "provider": "datacite",
            "client": "datacite",
        },
        "oai": {
            "identifier": "oai:https://works.hcommons.org:jthhs-g4b38",
            "provider": "oai",
        },
    },
    "metadata": {
        "resource_type": {
            "id": "textDocument-journalArticle",
            "title": {"de": "Zeitschriftenartikel", "en": "Journal article"},
        },
        "creators": [
            {
                "person_or_org": {
                    "type": "personal",
                    "name": "Friedman, Hal",
                    "given_name": "Hal",
                    "family_name": "Friedman",
                    "identifiers": [],
                },
                "role": {"id": "author", "title": {"en": "Author"}},
                "affiliations": [{"name": "Henry Ford College"}],
            }
        ],
        "title": (
            '"1955 in 1947: Historical Conjecture and Strategic Planning in the Office of the Chief of Naval Operations"'
        ),
        "publisher": "Knowledge Commons",
        "publication_date": "2025-06-02",
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "rights": [
            {
                "id": "cc-by-sa-4.0",
                "title": {
                    "en": ("Creative Commons Attribution Share Alike 4.0 International")
                },
                "description": {
                    "en": (
                        "Allows re-distribution of a licensed work on the condition that the creator is appropriately credited and that any derivative works or transformed versions of the licensed work must be distributed under the same license as the original."
                    )
                },
                "icon": "cc-by-sa-icon",
                "props": {
                    "url": "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
                    "scheme": "spdx",
                },
            }
        ],
        "description": (
            "In late 1947, the Office of the Chief of Naval Operations (OPNAV) employed historical conjecture to determine U.S. Fleet requirements for the mid-1950s.  Needing to be prepared for a war against the U.S.S.R. as well as for competition from its interservice rivals, the Navy's leadership attempted as much as possible to anticipate what a future war against the Soviet Union might be like so that the Naval Operating Forces that would be necessary for the U.S. could be procured  Given the national security problems in our own time period, study of this 1947 historical exercise provides perspective on how naval policy was made and how it might still be made in the present and future."
        ),
    },
    "custom_fields": {
        "journal:journal": {"title": "N/A"},
        "kcr:ai_usage": {"ai_used": False},
    },
    "access": {
        "record": "public",
        "files": "public",
        "embargo": {"active": False, "reason": None},
        "status": "open",
    },
    "files": {
        "enabled": True,
        "order": [],
        "count": 1,
        "total_bytes": 1984949,
        "entries": {
            "1955 in 1947.pdf": {
                "ext": "pdf",
                "size": 1984949,
                "mimetype": "application/pdf",
                "key": "1955 in 1947.pdf",
            }
        },
    },
}
