# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Unit tests for detail-page type-family layout helpers."""

from kcworks.config.detail_page_layout import (
    _DETAILS_PUBLICATION_BASE,
    _DETAILS_PUBLICATION_BY_FAMILY,
    _SIDEBAR_DETAILS_BY_FAMILY,
    DETAIL_DISPLAY_DEFAULT_FAMILY,
    DETAIL_DISPLAY_TYPE_TO_FAMILY,
    detail_display_family_for,
)


def test_detail_display_family_for_known_types():
    """Known resource types map to the expected display family."""
    assert detail_display_family_for("textDocument-journalArticle") == "journal"
    assert detail_display_family_for("textDocument-bookSection") == "book_section"
    assert (
        detail_display_family_for("textDocument-proceedingsPaper")
        == "proceedings_paper"
    )
    assert detail_display_family_for("textDocument-book") == "book"
    assert detail_display_family_for("textDocument-thesis") == "thesis"
    assert (
        detail_display_family_for("instructionalResource-syllabus")
        == "instructional"
    )


def test_detail_display_family_for_unknown_and_missing():
    """Unknown or missing types fall back to the default family."""
    assert detail_display_family_for("other-weird") == DETAIL_DISPLAY_DEFAULT_FAMILY
    assert detail_display_family_for(None) == DETAIL_DISPLAY_DEFAULT_FAMILY
    assert detail_display_family_for("") == DETAIL_DISPLAY_DEFAULT_FAMILY


def test_type_to_family_map_covers_configured_types():
    """Dumped type→family map includes representative configured types."""
    assert DETAIL_DISPLAY_TYPE_TO_FAMILY["textDocument-preprint"] == "journal"
    assert DETAIL_DISPLAY_TYPE_TO_FAMILY["textDocument-essay"] == "book_section"
    assert (
        DETAIL_DISPLAY_TYPE_TO_FAMILY["instructionalResource"] == "instructional"
    )


def test_sidebar_journal_vs_book_section_order():
    """Sidebar journal strip omits Place/ISBN; book section includes them."""
    journal = _SIDEBAR_DETAILS_BY_FAMILY["journal"]
    book_section = _SIDEBAR_DETAILS_BY_FAMILY["book_section"]
    assert journal[0] == "Published in"
    assert "Place" not in journal
    assert "ISBN" not in journal
    assert book_section[0] == "Published in"
    assert "Place" in book_section
    assert "ISBN" in book_section


def test_phase_b_family_sidebar_rules():
    """Phase B: curated sidebar row membership matches locked family rules."""
    journal = _SIDEBAR_DETAILS_BY_FAMILY["journal"]
    book_section = _SIDEBAR_DETAILS_BY_FAMILY["book_section"]
    proceedings = _SIDEBAR_DETAILS_BY_FAMILY["proceedings_paper"]
    book = _SIDEBAR_DETAILS_BY_FAMILY["book"]
    thesis = _SIDEBAR_DETAILS_BY_FAMILY["thesis"]
    instructional = _SIDEBAR_DETAILS_BY_FAMILY["instructional"]
    default = _SIDEBAR_DETAILS_BY_FAMILY["default"]

    # journal: Published in; imprint Place/ISBN not in sidebar
    assert journal[0] == "Published in"
    assert "In proceedings" not in journal
    assert "Place" not in journal
    assert "ISBN" not in journal
    assert "ISSN" not in journal

    # book_section: Published in + discrete Place/ISBN
    assert book_section[0] == "Published in"
    assert "In proceedings" not in book_section
    assert "Place" in book_section
    assert "ISBN" in book_section

    # proceedings_paper: In proceedings + same discrete pattern as book_section
    assert proceedings[0] == "In proceedings"
    assert "Published in" not in proceedings
    assert "Place" in proceedings
    assert "ISBN" in proceedings

    # book: no container row; Place/ISBN when set
    assert "Published in" not in book
    assert "In proceedings" not in book
    assert "Place" in book
    assert "ISBN" in book

    # thesis: no imprint container / Place / ISBN in sidebar
    assert "Published in" not in thesis
    assert "In proceedings" not in thesis
    assert "Place" not in thesis
    assert "ISBN" not in thesis
    assert "Awarding university" in thesis

    # instructional: combined Course; optional Published in; Place/ISBN allowed
    assert instructional[0] == "Course"
    assert "Published in" in instructional
    assert "In proceedings" not in instructional
    assert "Place" in instructional
    assert "ISBN" in instructional

    # default: dense fallback lists container slots (values stay empty for
    # unknown types); ISBN allowed, Place omitted
    assert "Published in" in default
    assert "In proceedings" in default
    assert "ISBN" in default
    assert "Place" not in default


def test_sidebar_instructional_order():
    """Instructional sidebar leads with Course, then optional Published in."""
    instructional = _SIDEBAR_DETAILS_BY_FAMILY["instructional"]
    assert instructional[0] == "Course"
    assert "Published in" in instructional
    assert "Publisher" in instructional
    assert "Place" in instructional
    assert "ISBN" in instructional
    assert "Formats" not in instructional


def test_details_publication_keeps_full_baseline_membership():
    """Details Publication lists keep full baseline membership (reorder only)."""
    baseline = set(_DETAILS_PUBLICATION_BASE)
    for family, fields in _DETAILS_PUBLICATION_BY_FAMILY.items():
        names = set(fields)
        assert len(names) == len(fields), family  # no duplicate section names
        if family == "proceedings_paper":
            assert "In proceedings" in names
            assert "Published in" not in names
            assert names == (baseline - {"Published in"}) | {"In proceedings"}
            assert fields[0] == "In proceedings"
        elif family == "instructional":
            assert names >= baseline
            assert fields[:6] == [
                "Published in",
                "In proceedings",
                "Course title",
                "Course URL",
                "Institution",
                "Department or discipline",
            ]
            assert "Course" not in names  # combined line is sidebar-only
            assert "Source repository" in names
            assert "Source code repository" not in names
        else:
            assert names == baseline
            assert fields[0] == "Published in"


def test_instructional_details_panels_move_course_fields():
    """Instructional Details panels hoist course fields out of thesis/project."""
    from kcworks.config.detail_page_layout import _DETAILS_TAB_BY_FAMILY

    panels = {
        str(panel["section"]): panel
        for panel in _DETAILS_TAB_BY_FAMILY["instructional"]
    }
    publication = panels["Publication"]["subsections"]
    thesis = panels["Thesis/Dissertation details"]["subsections"]
    project = panels["Project details"]["subsections"]

    assert publication.index("Course title") < publication.index("Additional titles")
    assert "Course URL" in publication
    assert "Institution" in publication
    assert "Department or discipline" in publication
    assert "Course" not in publication
    assert "Awarding department" not in thesis
    assert "Discipline" not in thesis
    assert thesis == []
    assert "Sponsoring institution" not in project
    assert "Project or publication website" not in project
    assert project == ["Project title"]


def test_journal_publication_puts_issn_near_publisher():
    """Journal Details Publication places ISSN immediately after Publisher."""
    names = _DETAILS_PUBLICATION_BY_FAMILY["journal"]
    publisher_idx = names.index("Publisher")
    issn_idx = names.index("ISSN")
    assert issn_idx == publisher_idx + 1


def test_exported_layout_normalizes_bare_section_names():
    """Exported layout trees coerce leaf section names to `{"section": ...}`."""
    from kcworks.config.detail_page_layout import (
        MODULAR_DETAIL_PAGE_MAIN_SECTIONS,
        MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_RIGHT,
    )

    details = next(
        s
        for s in MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_RIGHT
        if s.get("component_name") == "SidebarDetailsSection"
    )
    journal = details["subsections"]["journal"]
    assert journal[0] == {"section": "Published in"}
    assert all(isinstance(entry, dict) and "section" in entry for entry in journal)

    tabs = next(
        s for s in MODULAR_DETAIL_PAGE_MAIN_SECTIONS if s.get("section") == "Tabs"
    )
    details_tab = next(
        s for s in tabs["subsections"] if str(s["section"]) == "Details"
    )
    publishing = details_tab["subsections"][0]
    instructional_panels = publishing["subsections"]["instructional"]
    publication = next(
        p for p in instructional_panels if str(p["section"]) == "Publication"
    )
    assert publication["subsections"][0] == {"section": "Published in"}
    assert publication["subsections"][2] == {"section": "Course title"}
