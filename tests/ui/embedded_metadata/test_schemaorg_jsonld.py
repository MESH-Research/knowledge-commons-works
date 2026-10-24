# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schema.org JSON-LD serialization for detail-page embedded metadata.

The modular detail template must pass the dumped record_ui dict into
transform_record('SchemaorgJSONLDSerializer'). Passing a RecordItem
fails because get_creation_date / get_modification_date call
obj.get(...).
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

import pytest
from flask import render_template
from invenio_rdm_records.resources.serializers.schemaorg import (
    SchemaorgJSONLDSerializer,
)

from tests.conftest import RunningApp

RECORD_JSONLD_TEMPLATE = "invenio_modular_detail_page/record_jsonld.html"


class _RecordItemLike:
    """Minimal stand-in for RecordItem: item access, no .get."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def to_dict(self) -> dict[str, Any]:
        return self._data


def _record_ui_dict(journal_article_record_metadata) -> dict[str, Any]:
    """Published dump with created/updated for Schema.org date fields.

    Returns:
        A dict shaped like a dumped record_ui for SchemaorgJSONLDSerializer.
    """
    record = deepcopy(journal_article_record_metadata().published)
    # Same timestamps as full_sample_record_metadata; required for dateCreated.
    record["created"] = "2023-01-01"
    record["updated"] = "2023-01-02"
    return record


def _parse_jsonld_script(html: str) -> dict[str, Any] | None:
    """Extract the JSON-LD payload from a rendered script tag.

    Returns:
        Parsed JSON object, or None if no script tag is present.
    """
    match = re.search(
        r"<script type='application/ld\+json'>(.*?)</script>",
        html,
        re.DOTALL,
    )
    if match is None:
        return None
    return json.loads(match.group(1))


class TestSchemaorgJsonldSerialization:
    """Detail-page Schema.org path expects a dumped record dict."""

    def test_serializer_accepts_dumped_record_with_created_updated(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Dict dumps include dateCreated/dateModified from top-level dates."""
        record_ui = _record_ui_dict(journal_article_record_metadata)
        serialized = SchemaorgJSONLDSerializer().dump_obj(record_ui)

        assert serialized["dateCreated"] == record_ui["created"]
        assert serialized["dateModified"] == record_ui["updated"]
        assert serialized["name"] == record_ui["metadata"]["title"]
        assert serialized["@context"] == "http://schema.org"

    def test_serializer_rejects_record_item_like_without_get(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """RecordItem-like objects without .get raise AttributeError (prod bug)."""
        record_ui = _record_ui_dict(journal_article_record_metadata)
        with pytest.raises(AttributeError, match="has no attribute 'get'"):
            SchemaorgJSONLDSerializer().dump_obj(_RecordItemLike(record_ui))


class TestDetailRecordJsonldInclude:
    """Landing-page JSON-LD include must wire record_ui, not record."""

    def test_include_emits_jsonld_when_record_and_record_ui_both_present(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Shared include uses record_ui even when record is a RecordItem-like."""
        record_ui = _record_ui_dict(journal_article_record_metadata)
        with running_app.app.app_context(), running_app.app.test_request_context():
            html = render_template(
                RECORD_JSONLD_TEMPLATE,
                record=_RecordItemLike(record_ui),
                record_ui=record_ui,
            )

        payload = _parse_jsonld_script(html)
        assert payload is not None
        assert payload["dateCreated"] == record_ui["created"]
        assert payload["dateModified"] == record_ui["updated"]
        assert payload["name"] == record_ui["metadata"]["title"]
