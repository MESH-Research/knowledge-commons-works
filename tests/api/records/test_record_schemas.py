# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for KCWorks record schema overrides.

Currently focused on `KCWorksPersonOrOrganizationSchema`, which preserves
a caller-supplied `name` for personal entries instead of unconditionally
recomposing it as `"family_name, given_name"` (the upstream behavior).
"""

import pytest
from flask import Flask
from kcworks.services.records.schemas import (
    KCWorksContributorSchema,
    KCWorksCreatorSchema,
    KCWorksPersonOrOrganizationSchema,
)


@pytest.fixture
def app_ctx():
    """Push a minimal Flask app context for the schema's ``LocalProxy`` lookups.

    ``PersonOrOrganizationSchema.identifiers`` resolves
    ``RDM_RECORDS_PERSONORG_SCHEMES`` lazily via a ``LocalProxy``; supplying an
    empty mapping is enough for loads that don't include identifier values.

    Yields:
        The Flask app whose context is active for the test.
    """
    app = Flask("kcworks-record-schema-tests")
    app.config["RDM_RECORDS_PERSONORG_SCHEMES"] = {}
    with app.app_context():
        yield app


class TestKCWorksPersonOrOrganizationSchema:
    """``update_names`` preserves a caller-supplied ``name`` for personal entries."""

    def test_personal_with_name_preserves_caller_value(self, app_ctx):
        """When ``name`` is supplied, the schema does not recompose it."""
        result = KCWorksPersonOrOrganizationSchema().load(
            {
                "type": "personal",
                "family_name": "van der Berg",
                "given_name": "Jan",
                "name": "Jan van der Berg",
            }
        )
        assert result["name"] == "Jan van der Berg"
        assert result["family_name"] == "van der Berg"
        assert result["given_name"] == "Jan"

    def test_personal_with_blank_name_falls_back_to_composition(self, app_ctx):
        """Whitespace-only ``name`` is treated as absent and recomposed."""
        result = KCWorksPersonOrOrganizationSchema().load(
            {
                "type": "personal",
                "family_name": "Curie",
                "given_name": "Marie",
                "name": "   ",
            }
        )
        assert result["name"] == "Curie, Marie"

    def test_personal_without_name_composes_from_parts(self, app_ctx):
        """When ``name`` is omitted, the upstream composition behavior still runs."""
        result = KCWorksPersonOrOrganizationSchema().load(
            {
                "type": "personal",
                "family_name": "Curie",
                "given_name": "Marie",
            }
        )
        assert result["name"] == "Curie, Marie"

    def test_personal_without_given_name_uses_family_only(self, app_ctx):
        """Composition handles missing ``given_name`` (e.g. mononymic family)."""
        result = KCWorksPersonOrOrganizationSchema().load(
            {"type": "personal", "family_name": "Plato"}
        )
        assert result["name"] == "Plato"

    def test_organizational_drops_personal_only_fields(self, app_ctx):
        """Org entries still get ``family_name`` / ``given_name`` stripped."""
        result = KCWorksPersonOrOrganizationSchema().load(
            {
                "type": "organizational",
                "name": "ACME Corp",
                "family_name": "stray",
                "given_name": "stray",
            }
        )
        assert result == {"type": "organizational", "name": "ACME Corp"}


class TestKCWorksCreatorContributorSchemas:
    """``person_or_org`` is loaded through the KCWorks override in both layers."""

    def test_creator_preserves_name(self, app_ctx):
        """Caller-supplied ``name`` survives through ``KCWorksCreatorSchema``."""
        result = KCWorksCreatorSchema().load(
            {
                "person_or_org": {
                    "type": "personal",
                    "family_name": "van der Berg",
                    "given_name": "Jan",
                    "name": "Jan van der Berg",
                }
            }
        )
        assert result["person_or_org"]["name"] == "Jan van der Berg"

    def test_contributor_preserves_name(self, app_ctx):
        """Caller-supplied ``name`` survives through ``KCWorksContributorSchema``."""
        result = KCWorksContributorSchema().load(
            {
                "person_or_org": {
                    "type": "personal",
                    "family_name": "van der Berg",
                    "given_name": "Jan",
                    "name": "Jan van der Berg",
                },
                "role": {"id": "researcher"},
            }
        )
        assert result["person_or_org"]["name"] == "Jan van der Berg"
