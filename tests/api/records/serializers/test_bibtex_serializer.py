# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for KCWorks BibTeX resource-type mappings."""

import pytest
from kcworks.resources.serializers.bibtex.schema import KCWorksBibTexSchema
from kcworks.resources.serializers.bibtex.serializer import KCWorksBibtexSerializer


def _minimal_record(resource_type_id: str, **extra) -> dict:
    """Build a minimal record dict for BibTeX serialization.

    Returns:
        A record-shaped dict suitable for `KCWorksBibtexSerializer`.
    """
    record = {
        "id": "abcde-fghij",
        # Deliberately different from publication_date so year/month tests
        # prove we prefer metadata.publication_date over record created.
        "created": "2026-01-01T00:00:00.000000+00:00",
        "pids": {},
        "parent": {"id": "parent-id", "pids": {}},
        "metadata": {
            "resource_type": {"id": resource_type_id},
            "title": "A Romans story",
            "publication_date": "2023-03-13",
            "publisher": "Acme Inc",
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "name": "Brown, Sam",
                        "family_name": "Brown",
                        "given_name": "Sam",
                    }
                }
            ],
        },
        "custom_fields": {},
    }
    record.update(extra)
    return record


@pytest.mark.parametrize(
    ("resource_type_id", "expected_entry"),
    [
        ("textDocument-proceedingsPaper", "inproceedings"),
        ("textDocument-conferenceProceeding", "proceedings"),
        ("textDocument-journalArticle", "article"),
        ("textDocument-magazineArticle", "article"),
        ("textDocument-preprint", "unpublished"),
        ("textDocument-thesis", "phdthesis"),
        ("textDocument-documentation", "manual"),
        ("textDocument-workingPaper", "unpublished"),
        ("textDocument-monograph", "book"),
        ("software-computationalNotebook", "software"),
        ("dataset", "dataset"),
        # Intentionally unmapped
        ("presentation-conferencePaper", "misc"),
        ("textDocument-report", "misc"),
    ],
)
def test_kcworks_bibtex_entry_type(resource_type_id, expected_entry):
    """Mapped KC types select the expected BibTeX entry; others stay misc."""
    record = _minimal_record(resource_type_id)
    if expected_entry == "inproceedings":
        record["custom_fields"] = {"imprint:imprint": {"title": "Proc. Example"}}
    elif expected_entry == "article":
        record["custom_fields"] = {"journal:journal": {"title": "Example Journal"}}
    elif expected_entry == "phdthesis":
        record["custom_fields"] = {"thesis:university": "Example University"}
    elif expected_entry == "unpublished":
        # @unpublished requires note (from additional_descriptions type=other)
        record["additional_descriptions"] = [
            {"type": {"id": "other"}, "description": "a description"}
        ]

    serialized = KCWorksBibtexSerializer().serialize_object(record)
    assert serialized.startswith(f"@{expected_entry}{{")


def test_proceedings_paper_falls_back_to_misc_without_booktitle():
    """Without imprint title, inproceedings requirements fail → misc."""
    record = _minimal_record("textDocument-proceedingsPaper")
    serialized = KCWorksBibtexSerializer().serialize_object(record)
    assert serialized.startswith("@misc{")


def test_serialize_proceedings_paper_full_output():
    """Spot-check full BibTeX for `textDocument-proceedingsPaper`."""
    record = _minimal_record(
        "textDocument-proceedingsPaper",
        pids={"doi": {"identifier": "10.1234/abcde-fghij"}},
        custom_fields={
            "imprint:imprint": {"title": "Proc. of Example Conf", "pages": "12-19"},
            "meeting:meeting": {"place": "Rome"},
        },
    )
    expected = "\n".join(
        [
            "@inproceedings{brown_2023_abcde-fghij,",
            "  author       = {Brown, Sam},",
            "  title        = {A Romans story},",
            "  booktitle    = {Proc. of Example Conf},",
            "  year         = 2023,",
            "  pages        = {12-19},",
            "  publisher    = {Acme Inc},",
            "  month        = mar,",
            "  venue        = {Rome},",
            "  doi          = {10.1234/abcde-fghij},",
            "  url          = {https://doi.org/10.1234/abcde-fghij}",
            "}",
        ]
    )
    assert KCWorksBibtexSerializer().serialize_object(record) == expected


def test_serialize_journal_article_full_output():
    """Spot-check full BibTeX for `textDocument-journalArticle`."""
    record = _minimal_record(
        "textDocument-journalArticle",
        pids={"doi": {"identifier": "10.1234/abcde-fghij"}},
        custom_fields={
            "journal:journal": {
                "title": "Journal of Examples",
                "volume": "4",
                "issue": "2",
            },
        },
    )
    expected = "\n".join(
        [
            "@article{brown_2023_abcde-fghij,",
            "  author       = {Brown, Sam},",
            "  title        = {A Romans story},",
            "  journal      = {Journal of Examples},",
            "  year         = 2023,",
            "  volume       = 4,",
            "  number       = 2,",
            "  month        = mar,",
            "  doi          = {10.1234/abcde-fghij},",
            "  url          = {https://doi.org/10.1234/abcde-fghij}",
            "}",
        ]
    )
    assert KCWorksBibtexSerializer().serialize_object(record) == expected


def test_entry_mapper_keeps_stock_keys():
    """Stock Invenio IDs remain available alongside KC mappings."""
    assert "publication-conferencepaper" in KCWorksBibTexSchema.entry_mapper
    assert "textDocument-proceedingsPaper" in KCWorksBibTexSchema.entry_mapper
    assert "presentation-conferencePaper" not in KCWorksBibTexSchema.entry_mapper


def test_year_uses_publication_date_not_created():
    """BibTeX year/month come from publication_date, not record created."""
    record = _minimal_record(
        "textDocument-journalArticle",
        created="2026-01-01T00:00:00.000000+00:00",
        custom_fields={"journal:journal": {"title": "Example Journal"}},
    )
    record["metadata"]["publication_date"] = "2022-09-13"
    serialized = KCWorksBibtexSerializer().serialize_object(record)
    assert "year         = 2022," in serialized
    assert "month        = sep," in serialized
    assert "brown_2022_abcde-fghij" in serialized


def test_year_falls_back_to_created_without_publication_date():
    """If publication_date is missing, fall back to record created."""
    record = _minimal_record(
        "dataset",
        created="2021-06-01T00:00:00.000000+00:00",
    )
    del record["metadata"]["publication_date"]
    serialized = KCWorksBibtexSerializer().serialize_object(record)
    assert "year         = 2021," in serialized
    assert "month        = jun," in serialized
