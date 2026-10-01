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


def test_detail_display_family_for_unknown_and_missing():
    """Unknown or missing types fall back to the default family."""
    assert detail_display_family_for("other-weird") == DETAIL_DISPLAY_DEFAULT_FAMILY
    assert detail_display_family_for(None) == DETAIL_DISPLAY_DEFAULT_FAMILY
    assert detail_display_family_for("") == DETAIL_DISPLAY_DEFAULT_FAMILY


def test_type_to_family_map_covers_configured_types():
    """Dumped type→family map includes representative configured types."""
    assert DETAIL_DISPLAY_TYPE_TO_FAMILY["textDocument-preprint"] == "journal"
    assert DETAIL_DISPLAY_TYPE_TO_FAMILY["textDocument-essay"] == "book_section"


def test_sidebar_journal_vs_book_section_order():
    """Sidebar journal strip omits Place/ISBN; book section includes them."""
    journal = [s["section"] for s in _SIDEBAR_DETAILS_BY_FAMILY["journal"]]
    book_section = [
        s["section"] for s in _SIDEBAR_DETAILS_BY_FAMILY["book_section"]
    ]
    assert journal[0] == "Published in"
    assert "Place" not in journal
    assert "ISBN" not in journal
    assert book_section[0] == "Published in"
    assert "Place" in book_section
    assert "ISBN" in book_section


def test_details_publication_keeps_full_baseline_membership():
    """Details Publication lists keep full baseline membership (reorder only)."""
    baseline = {s["section"] for s in _DETAILS_PUBLICATION_BASE}
    for family, fields in _DETAILS_PUBLICATION_BY_FAMILY.items():
        names = {s["section"] for s in fields}
        assert len(names) == len(fields), family  # no duplicate section names
        if family == "proceedings_paper":
            assert "In proceedings" in names
            assert "Published in" not in names
            assert names == (baseline - {"Published in"}) | {"In proceedings"}
            assert fields[0]["section"] == "In proceedings"
        else:
            assert names == baseline
            assert fields[0]["section"] == "Published in"


def test_journal_publication_puts_issn_near_publisher():
    """Journal Details Publication places ISSN immediately after Publisher."""
    names = [s["section"] for s in _DETAILS_PUBLICATION_BY_FAMILY["journal"]]
    publisher_idx = names.index("Publisher")
    issn_idx = names.index("ISSN")
    assert issn_idx == publisher_idx + 1
