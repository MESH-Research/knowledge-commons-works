# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Layout configuration for the invenio-modular-detail-page KCWorks record pages.

Details-tab field lists stay a full metadata inventory (reorder / light regroup
by resource-type family). Sidebar Details stays a denser curated strip.

Leaf field-order entries may be authored as bare section-name strings; they are
normalized to `{"section": name}` once when the exported layout trees are
built.
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
    "instructional": [
        "instructionalResource",
        "instructionalResource-syllabus",
        "instructionalResource-lessonPlan",
        "instructionalResource-curriculum",
        "instructionalResource-other",
    ],
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
        resource_type_id: Vocabulary id such as `textDocument-journalArticle`.

    Returns:
        Family key (e.g. `journal`), or `DETAIL_DISPLAY_DEFAULT_FAMILY`.
    """
    if not resource_type_id:
        return DETAIL_DISPLAY_DEFAULT_FAMILY
    return DETAIL_DISPLAY_TYPE_TO_FAMILY.get(
        resource_type_id, DETAIL_DISPLAY_DEFAULT_FAMILY
    )


def _rename_section(fields: list[str], old: str, new: str) -> list[str]:
    """Return a copy of `fields` with `old` section name replaced by `new`.

    Returns:
        New list of section names with the renamed entry.
    """
    return [new if entry == old else entry for entry in fields]


def _move_section_after(fields: list[str], section: str, after: str) -> list[str]:
    """Move `section` to immediately follow `after` (no-op if missing).

    Returns:
        New list of section names with the moved entry.
    """
    if section not in fields or after not in fields:
        return list(fields)
    without = [entry for entry in fields if entry != section]
    after_idx = without.index(after)
    return without[: after_idx + 1] + [section] + without[after_idx + 1 :]


def _normalize_layout_entry(entry: Any) -> Any:
    """Coerce a bare section name to `{"section": name}`; recurse into dicts.

    Returns:
        A layout node dict, or `entry` unchanged when it is neither a string
        nor a dict.
    """
    if isinstance(entry, str):
        return {"section": entry}
    if isinstance(entry, dict):
        out = dict(entry)
        if "subsections" in out:
            out["subsections"] = _normalize_subsections(out["subsections"])
        return out
    return entry


def _normalize_subsections(subsections: Any) -> Any:
    """Normalize subsection lists or family-keyed maps for export to the client.

    Args:
        subsections: A list of layout entries (strings or dicts), or a
            family-keyed dict of such lists.

    Returns:
        The same structure with bare strings expanded to `{"section": ...}`.
    """
    if isinstance(subsections, list):
        return [_normalize_layout_entry(entry) for entry in subsections]
    if isinstance(subsections, dict):
        return {
            key: _normalize_subsections(value) for key, value in subsections.items()
        }
    return subsections


# ---------------------------------------------------------------------------
# Sidebar Details — curated strip (family-keyed)
# ---------------------------------------------------------------------------

_SIDEBAR_DETAILS_CORE = [
    "Publisher",
    "Languages",
    "Formats",
    "Sizes",
    "DOI",
]

_SIDEBAR_DETAILS_JOURNAL = [
    "Published in",
    *_SIDEBAR_DETAILS_CORE,
]

_SIDEBAR_DETAILS_BOOK_SECTION = [
    "Published in",
    "Place",
    *[s for s in _SIDEBAR_DETAILS_CORE if s != "DOI"],
    "ISBN",
    "DOI",
]

_SIDEBAR_DETAILS_PROCEEDINGS_PAPER = _rename_section(
    _SIDEBAR_DETAILS_BOOK_SECTION, "Published in", "In proceedings"
)

_SIDEBAR_DETAILS_BOOK = [
    "Place",
    "Publisher",
    "Publication date",
    "Languages",
    "Formats",
    "Sizes",
    "ISBN",
    "DOI",
]

_SIDEBAR_DETAILS_THESIS = [
    "Awarding university",
    "Thesis type",
    "Awarding department",
    "Publisher",
    "Publication date",
    "Languages",
    "Formats",
    "Sizes",
    "DOI",
]

_SIDEBAR_DETAILS_INSTRUCTIONAL = [
    "Course",
    "Published in",
    "Publisher",
    "Place",
    "ISBN",
    "Publication date",
    "Languages",
    "DOI",
]

# Dense fallback matching the pre-family sidebar inventory.
_SIDEBAR_DETAILS_DEFAULT = [
    "Published in",
    "In proceedings",
    "Awarding university",
    "Thesis type",
    "Awarding department",
    "Conference",
    "Conference organization",
    "Publisher",
    "Publication date",
    "Languages",
    "Formats",
    "Sizes",
    "Duration",
    "ISBN",
    "DOI",
]

_SIDEBAR_DETAILS_BY_FAMILY: dict[str, list[str]] = {
    "journal": _SIDEBAR_DETAILS_JOURNAL,
    "book_section": _SIDEBAR_DETAILS_BOOK_SECTION,
    "proceedings_paper": _SIDEBAR_DETAILS_PROCEEDINGS_PAPER,
    "book": _SIDEBAR_DETAILS_BOOK,
    "thesis": _SIDEBAR_DETAILS_THESIS,
    "instructional": _SIDEBAR_DETAILS_INSTRUCTIONAL,
    "default": _SIDEBAR_DETAILS_DEFAULT,
}

# ---------------------------------------------------------------------------
# Details tab — full Publication inventory (reorder only)
# ---------------------------------------------------------------------------

# Published in / In proceedings first; remainder mirrors the prior layout.
_DETAILS_PUBLICATION_BASE = [
    "Published in",
    "In proceedings",
    "Additional titles",
    "Chapter label",
    "Course title",
    "URLs",
    "Version",
    "Edition",
    "Development status",
    "Source repository",
    "Place",
    "Publisher",
    "ISBN",
    "ISSN",
    "Conference",
    "Conference organization",
    "Languages",
    "Publication date",
    "Additional dates",
    "Media and materials",
    "Formats",
    "Sizes",
    "Series",
    "Volumes",
]

# Instructional: course cluster near the top (deposit Course details order).
# Details tab uses discrete course fields; sidebar uses the combined Course line.
_DETAILS_PUBLICATION_INSTRUCTIONAL = [
    "Published in",
    "In proceedings",
    "Course title",
    "Course URL",
    "Institution",
    "Department or discipline",
    *[
        s
        for s in _DETAILS_PUBLICATION_BASE
        if s
        not in (
            "Published in",
            "In proceedings",
            "Course title",
        )
    ],
]

_DETAILS_THESIS_BASE = [
    "Awarding university",
    "Awarding department",
    "Thesis type",
    "Submission date",
    "Defense date",
    "Discipline",
]

# Instructional records do not use thesis panels (avoids a second
# department-titled row beside "Department or discipline").
_DETAILS_THESIS_BY_FAMILY: dict[str, list[str]] = {
    "instructional": [],
    "default": _DETAILS_THESIS_BASE,
}

_DETAILS_PROJECT_BASE = [
    "Project title",
    "Project or publication website",
    "Sponsoring institution",
]

# Course URL / Institution moved into Publication for instructional types.
_DETAILS_PROJECT_BY_FAMILY: dict[str, list[str]] = {
    "instructional": ["Project title"],
    "default": _DETAILS_PROJECT_BASE,
}

# Journals: ISSN next to Publisher; ISBN after ISSN.
_DETAILS_PUBLICATION_JOURNAL = _move_section_after(
    _DETAILS_PUBLICATION_BASE, "ISSN", "Publisher"
)
_DETAILS_PUBLICATION_JOURNAL = _move_section_after(
    _DETAILS_PUBLICATION_JOURNAL, "ISBN", "ISSN"
)

_DETAILS_PUBLICATION_PROCEEDINGS_PAPER = [
    "In proceedings",
    *[
        s
        for s in _DETAILS_PUBLICATION_BASE
        if s not in ("Published in", "In proceedings")
    ],
]

_DETAILS_PUBLICATION_BY_FAMILY: dict[str, list[str]] = {
    "journal": _DETAILS_PUBLICATION_JOURNAL,
    "book_section": list(_DETAILS_PUBLICATION_BASE),
    "proceedings_paper": _DETAILS_PUBLICATION_PROCEEDINGS_PAPER,
    "book": list(_DETAILS_PUBLICATION_BASE),
    "thesis": list(_DETAILS_PUBLICATION_BASE),
    "instructional": _DETAILS_PUBLICATION_INSTRUCTIONAL,
    "default": list(_DETAILS_PUBLICATION_BASE),
}


def _details_tab_panels(
    publication_fields: list[str],
    *,
    thesis_fields: list[str],
    project_fields: list[str],
) -> list[dict[str, Any]]:
    """Full Details-tab accordion panels with the given panel field orders.

    Args:
        publication_fields: Ordered Publication-panel section names.
        thesis_fields: Thesis panel section names.
        project_fields: Project panel section names.

    Returns:
        Accordion panel configs for the Details tab (leaf names still bare
        strings until export normalization).
    """
    return [
        {
            "section": _("Contributors"),
            "subsections": [
                "Contributors",
            ],
            "show": "mobile only",
        },
        {
            "section": _("Publication"),
            "subsections": publication_fields,
        },
        {
            "section": _("Thesis/Dissertation details"),
            "subsections": thesis_fields,
        },
        {
            "section": _("Technical specifications"),
            "subsections": [
                "Operating systems supported",
                "Frameworks or runtimes",
                "Programming languages",
            ],
        },
        {
            "section": _("Project details"),
            "subsections": project_fields,
        },
        {
            "section": _("Additional titles"),
            "subsections": [
                "Additional titles",
            ],
        },
        {
            "section": _("Funding"),
            "subsections": ["Funding"],
        },
        {
            "section": _("Identifiers"),
            "subsections": [
                "DOI",
                "Alternate identifiers",
            ],
        },
        {
            "section": _("Related"),
            "subsections": [
                "Related identifiers",
            ],
        },
        {
            "section": _("References"),
            "subsections": [
                "References",
            ],
        },
        {
            "section": _("AI Usage"),
            "subsections": [
                {
                    "section": "kcr:ai_usage",
                    "subsections": [
                        "ai_used",
                        "ai_description",
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
    family: _details_tab_panels(
        pub_fields,
        thesis_fields=_DETAILS_THESIS_BY_FAMILY.get(
            family, _DETAILS_THESIS_BY_FAMILY["default"]
        ),
        project_fields=_DETAILS_PROJECT_BY_FAMILY.get(
            family, _DETAILS_PROJECT_BY_FAMILY["default"]
        ),
    )
    for family, pub_fields in _DETAILS_PUBLICATION_BY_FAMILY.items()
}

# ---------------------------------------------------------------------------
# Layout trees (chrome unchanged; Details subsections family-keyed)
# ---------------------------------------------------------------------------

MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_RIGHT = _normalize_subsections(
    [
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
)
MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_LEFT = []

# top-level objects are tabs in main detail page column
MODULAR_DETAIL_PAGE_MAIN_SECTIONS = _normalize_subsections(
    [
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
)
