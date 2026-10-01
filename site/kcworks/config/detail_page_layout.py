# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Layout configuration for the invenio-modular-detail-page KCWorks record pages.

Details-tab field lists stay a full metadata inventory (reorder / light regroup
by resource-type family). Sidebar Details stays a denser curated strip.
"""

from __future__ import annotations

from typing import Any

from invenio_i18n import lazy_gettext as _

# ---------------------------------------------------------------------------
# Resource-type display families
# ---------------------------------------------------------------------------

DETAIL_DISPLAY_TYPE_FAMILIES: dict[str, list[str]] = {
    "journal": [
        "textDocument-journalArticle",
        "textDocument-journal",
        "textDocument-abstract",
        "textDocument-legalComment",
        "textDocument-legalResponse",
        "textDocument-preprint",
        "textDocument-review",
        "other-peerReview",
    ],
    "book_section": [
        "textDocument-bookSection",
        "textDocument-essay",
        "textDocument-bibliography",
        "textDocument-poeticWork",
    ],
    "proceedings_paper": ["textDocument-proceedingsPaper"],
    "book": [
        "textDocument-book",
        "textDocument-monograph",
        "textDocument-conferenceProceeding",
        "textDocument-musicalNotation",
    ],
    "thesis": ["textDocument-thesis"],
}

DETAIL_DISPLAY_DEFAULT_FAMILY = "default"

DETAIL_DISPLAY_TYPE_TO_FAMILY: dict[str, str] = {
    type_id: family
    for family, type_ids in DETAIL_DISPLAY_TYPE_FAMILIES.items()
    for type_id in type_ids
}


def detail_display_family_for(resource_type_id: str | None) -> str:
    """Return the detail-display family for a resource type id.

    Args:
        resource_type_id: Vocabulary id such as ``textDocument-journalArticle``.

    Returns:
        Family key (e.g. ``journal``), or ``DETAIL_DISPLAY_DEFAULT_FAMILY``.
    """
    if not resource_type_id:
        return DETAIL_DISPLAY_DEFAULT_FAMILY
    return DETAIL_DISPLAY_TYPE_TO_FAMILY.get(
        resource_type_id, DETAIL_DISPLAY_DEFAULT_FAMILY
    )


def _section(name: str) -> dict[str, str]:
    return {"section": name}


def _rename_section(
    fields: list[dict[str, str]], old: str, new: str
) -> list[dict[str, str]]:
    """Return a copy of ``fields`` with ``old`` section name replaced by ``new``.

    Returns:
        New list of section dicts with the renamed entry.
    """
    return [
        _section(new) if entry["section"] == old else entry for entry in fields
    ]


# ---------------------------------------------------------------------------
# Sidebar Details — curated strip (family-keyed)
# ---------------------------------------------------------------------------

_SIDEBAR_DETAILS_CORE = [
    _section("Publisher"),
    _section("Languages"),
    _section("Formats"),
    _section("Sizes"),
    _section("DOI"),
]

_SIDEBAR_DETAILS_JOURNAL = [
    _section("Published in"),
    *_SIDEBAR_DETAILS_CORE,
]

_SIDEBAR_DETAILS_BOOK_SECTION = [
    _section("Published in"),
    _section("Place"),
    *[s for s in _SIDEBAR_DETAILS_CORE if s["section"] != "DOI"],
    _section("ISBN"),
    _section("DOI"),
]

_SIDEBAR_DETAILS_PROCEEDINGS_PAPER = _rename_section(
    _SIDEBAR_DETAILS_BOOK_SECTION, "Published in", "In proceedings"
)

_SIDEBAR_DETAILS_BOOK = [
    _section("Place"),
    _section("Publisher"),
    _section("Publication date"),
    _section("Languages"),
    _section("Formats"),
    _section("Sizes"),
    _section("ISBN"),
    _section("DOI"),
]

_SIDEBAR_DETAILS_THESIS = [
    _section("Awarding university"),
    _section("Thesis type"),
    _section("Awarding department"),
    _section("Publisher"),
    _section("Publication date"),
    _section("Languages"),
    _section("Formats"),
    _section("Sizes"),
    _section("DOI"),
]

# Dense fallback matching the pre-family sidebar inventory.
_SIDEBAR_DETAILS_DEFAULT = [
    _section("Published in"),
    _section("In proceedings"),
    _section("Awarding university"),
    _section("Thesis type"),
    _section("Awarding department"),
    _section("Conference"),
    _section("Conference organization"),
    _section("Publisher"),
    _section("Publication date"),
    _section("Languages"),
    _section("Formats"),
    _section("Sizes"),
    _section("Duration"),
    _section("ISBN"),
    _section("DOI"),
]

_SIDEBAR_DETAILS_BY_FAMILY: dict[str, list[dict[str, str]]] = {
    "journal": _SIDEBAR_DETAILS_JOURNAL,
    "book_section": _SIDEBAR_DETAILS_BOOK_SECTION,
    "proceedings_paper": _SIDEBAR_DETAILS_PROCEEDINGS_PAPER,
    "book": _SIDEBAR_DETAILS_BOOK,
    "thesis": _SIDEBAR_DETAILS_THESIS,
    "default": _SIDEBAR_DETAILS_DEFAULT,
}

# ---------------------------------------------------------------------------
# Details tab — full Publication inventory (reorder only)
# ---------------------------------------------------------------------------

# Published in / In proceedings first; remainder mirrors the prior layout.
_DETAILS_PUBLICATION_BASE = [
    _section("Published in"),
    _section("In proceedings"),
    _section("Additional titles"),
    _section("Chapter label"),
    _section("Course title"),
    _section("URLs"),
    _section("Version"),
    _section("Edition"),
    _section("Development status"),
    _section("Source code repository"),
    _section("Place"),
    _section("Publisher"),
    _section("ISBN"),
    _section("ISSN"),
    _section("Conference"),
    _section("Conference organization"),
    _section("Languages"),
    _section("Publication date"),
    _section("Additional dates"),
    _section("Media and materials"),
    _section("Formats"),
    _section("Sizes"),
    _section("Series"),
    _section("Volumes"),
]


def _move_section_after(
    fields: list[dict[str, str]], section: str, after: str
) -> list[dict[str, str]]:
    """Move ``section`` to immediately follow ``after`` (no-op if missing).

    Returns:
        New list of section dicts with the moved entry.
    """
    names = [entry["section"] for entry in fields]
    if section not in names or after not in names:
        return list(fields)
    entry = next(e for e in fields if e["section"] == section)
    without = [e for e in fields if e["section"] != section]
    after_idx = next(i for i, e in enumerate(without) if e["section"] == after)
    return without[: after_idx + 1] + [entry] + without[after_idx + 1 :]


# Journals: ISSN next to Publisher; ISBN after ISSN.
_DETAILS_PUBLICATION_JOURNAL = _move_section_after(
    _DETAILS_PUBLICATION_BASE, "ISSN", "Publisher"
)
_DETAILS_PUBLICATION_JOURNAL = _move_section_after(
    _DETAILS_PUBLICATION_JOURNAL, "ISBN", "ISSN"
)

_DETAILS_PUBLICATION_PROCEEDINGS_PAPER = [
    _section("In proceedings"),
    *[
        s
        for s in _DETAILS_PUBLICATION_BASE
        if s["section"] not in ("Published in", "In proceedings")
    ],
]

_DETAILS_PUBLICATION_BY_FAMILY: dict[str, list[dict[str, str]]] = {
    "journal": _DETAILS_PUBLICATION_JOURNAL,
    "book_section": list(_DETAILS_PUBLICATION_BASE),
    "proceedings_paper": _DETAILS_PUBLICATION_PROCEEDINGS_PAPER,
    "book": list(_DETAILS_PUBLICATION_BASE),
    "thesis": list(_DETAILS_PUBLICATION_BASE),
    "default": list(_DETAILS_PUBLICATION_BASE),
}


def _details_tab_panels(
    publication_fields: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Full Details-tab accordion panels with the given Publication field order.

    Returns:
        Accordion panel configs for the Details tab.
    """
    return [
        {
            "section": _("Contributors"),
            "subsections": [
                _section("Contributors"),
            ],
            "show": "mobile only",
        },
        {
            "section": _("Publication"),
            "subsections": publication_fields,
        },
        {
            "section": _("Thesis/Dissertation details"),
            "subsections": [
                _section("Awarding university"),
                _section("Awarding department"),
                _section("Thesis type"),
                _section("Submission date"),
                _section("Defense date"),
                _section("Discipline"),
            ],
        },
        {
            "section": _("Technical specifications"),
            "subsections": [
                _section("Operating systems supported"),
                _section("Frameworks or runtimes"),
                _section("Programming languages"),
            ],
        },
        {
            "section": _("Project details"),
            "subsections": [
                _section("Project title"),
                _section("Project or publication website"),
                _section("Sponsoring institution"),
            ],
        },
        {
            "section": _("Additional titles"),
            "subsections": [
                _section("Additional titles"),
            ],
        },
        {
            "section": _("Funding"),
            "subsections": [_section("Funding")],
        },
        {
            "section": _("Identifiers"),
            "subsections": [
                _section("DOI"),
                _section("Alternate identifiers"),
            ],
        },
        {
            "section": _("Related"),
            "subsections": [
                _section("Related identifiers"),
            ],
        },
        {
            "section": _("References"),
            "subsections": [
                _section("References"),
            ],
        },
        {
            "section": _("AI Usage"),
            "subsections": [
                {
                    "section": "kcr:ai_usage",
                    "subsections": [
                        _section("ai_used"),
                        _section("ai_description"),
                    ],
                }
            ],
        },
        {
            "section": _("Analytics"),
            "subsections": [
                {
                    "section": "Analytics",
                }
            ],
            "show": "mobile only",
        },
    ]


_DETAILS_TAB_BY_FAMILY: dict[str, list[dict[str, Any]]] = {
    family: _details_tab_panels(fields)
    for family, fields in _DETAILS_PUBLICATION_BY_FAMILY.items()
}

# ---------------------------------------------------------------------------
# Layout trees (chrome unchanged; Details subsections family-keyed)
# ---------------------------------------------------------------------------

MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_RIGHT = [
    {"section": _("Manage")},
    {
        "section": _("Download"),
        "component_name": "SidebarDownloadSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Collections"),
        "component_name": "CommunitiesBanner",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Content Warning"),
        "component_name": "ContentWarning",
    },
    {
        "section": _("AI Use"),
        "component_name": "AIUsageAlert",
    },
    {
        "section": _("Versions"),
        "component_name": "VersionsDropdownSection",
        "show_heading": False,
    },
    {
        "section": _("Keywords & Subjects"),
        "component_name": "SidebarSubjectsSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Cite this"),
        "component_name": "CitationSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Details"),
        "component_name": "SidebarDetailsSection",
        "subsections": _SIDEBAR_DETAILS_BY_FAMILY,
        "show_heading": False,
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Copyright & permissions"),
        "component_name": "SidebarRightsSection",
        "show": "tablet computer only",
    },
    {
        "section": _("Export"),
        "component_name": "SidebarExportSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Share"),
        "component_name": "SidebarSharingSection",
        "show": "computer large screen widescreen only",
    },
]
MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_LEFT = []

# top-level objects are tabs in main detail page column
MODULAR_DETAIL_PAGE_MAIN_SECTIONS = [
    {
        "section": _("Title"),
        "component_name": "RecordTitle",
    },
    {
        "section": _("Creators and Contributors"),
        "component_name": "CreatibutorsShortList",
    },
    {
        "section": "Tabs",
        "component_name": "DetailMainTabs",
        "subsections": [
            {
                "section": _("Content"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": _("Descriptions"),
                        "component_name": "Descriptions",
                    },
                    {
                        "section": _("Preview"),
                        "component_name": "FilePreviewWrapper",
                    },
                ],
                "tab": True,
            },
            {
                "section": _("Details"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": _("Publication"),
                        "component_name": "PublishingDetails",
                        "subsections": _DETAILS_TAB_BY_FAMILY,
                    }
                ],
                "tab": True,
            },
            {
                "section": _("Contributors"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "Contributors",
                        "component_name": "Creatibutors",
                        "subsections": [],
                    }
                ],
                "tab": True,
                "show": "tablet computer only",
            },
            {
                "section": _("Analytics"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "Analytics",
                        "component_name": "Analytics",
                    }
                ],
                "tab": True,
                "show": "tablet computer only",
            },
            {
                "section": _("Subjects"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "component_name": "MainSubjectsSection",
                    }
                ],
                "tab": True,
                "show": "mobile tablet only",
            },
            {
                "section": _("Files"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "FilesPreview",
                        "component_name": "FilePreview",
                    },
                    {
                        "section": "FilesBox",
                        "component_name": "FileListBox",
                    },
                ],
                "tab": True,
            },
        ],
    },
]
