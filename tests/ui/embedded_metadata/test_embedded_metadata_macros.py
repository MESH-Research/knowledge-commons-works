# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Serialize embedded metadata macros against record_metadata type wrappers."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any
from urllib.parse import parse_qs, unquote

from flask import render_template_string

from tests.conftest import RunningApp
from tests.fixtures import records as records_fixtures


def _meta_content(html: str, name: str) -> str | None:
    """Return the content attribute for a meta tag with the given name.

    Returns:
        The content string, or None if no matching tag is found.
    """
    match = re.search(
        rf'name="{re.escape(name)}"\s+content="([^"]*)"',
        html,
    )
    return match.group(1) if match else None


def _published_with_links(meta: records_fixtures.TestRecordMetadata) -> dict[str, Any]:
    """Return meta.published with links for template URL fields.

    Returns:
        Published dump dict including links from build_published_record_links.
    """
    record = deepcopy(meta.published)
    record_id = record.get("id") or "XXXX"
    record["id"] = record_id
    record["links"] = records_fixtures.TestRecordMetadata.build_published_record_links(
        record_id=record_id,
        base_url=meta.app.config["SITE_API_URL"],
        ui_base_url=meta.app.config["SITE_UI_URL"],
        parent_id=record_id,
        record_doi=record.get("pids", {}).get("doi", {}).get("identifier", ""),
    )
    return record


def _creator_names(record: dict[str, Any]) -> list[str]:
    """Return person_or_org.name values from record creators.

    Returns:
        Creator display names in record order.
    """
    return [
        creator["person_or_org"]["name"]
        for creator in record["metadata"].get("creators", [])
    ]


def _highwire_kwargs(record: dict[str, Any]) -> dict[str, Any]:
    """Build meta_highwire kwargs from a dumped record.

    Returns:
        Keyword arguments for the Highwire macro.
    """
    metadata = record["metadata"]
    return {
        "record": record,
        "meta_title": metadata["title"],
        "meta_description": metadata.get("description", ""),
        "meta_authors": _creator_names(record),
        "meta_contributors": [],
        "meta_editors": [],
        "meta_publisher": metadata.get("publisher"),
        "meta_publication_date": metadata.get("publication_date"),
        "meta_doi": record.get("pids", {}).get("doi", {}).get("identifier"),
        "meta_keywords": ", ".join(
            s.get("subject", "")
            for s in metadata.get("subjects", [])
            if s.get("subject")
        ),
        "meta_url": record["links"]["self_html"],
    }


def _dublin_core_kwargs(record: dict[str, Any]) -> dict[str, Any]:
    """Build meta_dublin_core kwargs from a dumped record.

    Returns:
        Keyword arguments for the Dublin Core macro.
    """
    metadata = record["metadata"]
    return {
        "record": record,
        "meta_title": metadata["title"],
        "meta_authors": _creator_names(record),
        "meta_description": metadata.get("description", ""),
        "meta_publication_date": metadata.get("publication_date"),
        "meta_publisher": metadata.get("publisher"),
        "meta_doi": record.get("pids", {}).get("doi", {}).get("identifier"),
        "meta_url": record["links"]["self_html"],
    }


def _render_macro(
    app,
    import_path: str,
    call: str,
    **ctx: Any,
) -> str:
    """Render a single embedded-metadata macro under a request context.

    Returns:
        Rendered HTML for the macro call.
    """
    template = f"""
    {{% from "{import_path}" import {call.split("(")[0]} %}}
    {{{{ {call} }}}}
    """
    with app.app_context(), app.test_request_context():
        return render_template_string(template, **ctx)


class TestHighwireMacros:
    """Highwire citation_* tags from dumped records."""

    def test_journal_article_emits_core_and_journal_fields(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Journal articles emit title/author/DOI plus journal imprint tags."""
        record = _published_with_links(journal_article_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/highwire.html",
            "meta_highwire(record, meta_title, meta_description, meta_authors, "
            "meta_contributors, meta_editors, meta_publisher, meta_publication_date, "
            "meta_doi, meta_keywords, meta_url)",
            **_highwire_kwargs(record),
        )

        assert _meta_content(html, "citation_title") == "A Romans story"
        assert _meta_content(html, "citation_author") == "Brown, Troy"
        assert _meta_content(html, "citation_doi") == "10.17613/XXXX"
        assert _meta_content(html, "citation_journal_title") == "Journal of Examples"
        assert _meta_content(html, "citation_issn") == "1234-5678"
        assert _meta_content(html, "citation_volume") == "4"
        assert _meta_content(html, "citation_issue") == "2"
        assert _meta_content(html, "citation_firstpage") == "45"

    def test_blog_post_emits_fulltext_html_url(
        self, running_app: RunningApp, blog_post_record_metadata
    ) -> None:
        """Blog posts emit citation_fulltext_html_url from URL identifiers."""
        record = _published_with_links(blog_post_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/highwire.html",
            "meta_highwire(record, meta_title, meta_description, meta_authors, "
            "meta_contributors, meta_editors, meta_publisher, meta_publication_date, "
            "meta_doi, meta_keywords, meta_url)",
            **_highwire_kwargs(record),
        )

        post_url = record["metadata"]["identifiers"][0]["identifier"]
        assert _meta_content(html, "citation_fulltext_html_url") == post_url
        assert _meta_content(html, "citation_journal_title") is None

    def test_book_section_emits_isbn_and_inbook_title(
        self, running_app: RunningApp, book_section_record_metadata
    ) -> None:
        """Book sections emit imprint ISBN and container title tags."""
        record = _published_with_links(book_section_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/highwire.html",
            "meta_highwire(record, meta_title, meta_description, meta_authors, "
            "meta_contributors, meta_editors, meta_publisher, meta_publication_date, "
            "meta_doi, meta_keywords, meta_url)",
            **_highwire_kwargs(record),
        )

        imprint = record["custom_fields"]["imprint:imprint"]
        assert _meta_content(html, "citation_isbn") == imprint["isbn"]
        assert _meta_content(html, "citation_inbook_title") == imprint["title"]


class TestDublinCoreMacros:
    """Dublin Core DC.* tags from dumped records."""

    def test_journal_article_emits_common_and_type(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Non-blog records emit common DC fields plus UI type label."""
        record = _published_with_links(journal_article_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/dublin_core.html",
            "meta_dublin_core(record, meta_title, meta_authors, meta_description, "
            "meta_publication_date, meta_publisher, meta_doi, meta_url)",
            **_dublin_core_kwargs(record),
        )

        assert 'name="DC.title" content="A Romans story"' in html
        assert 'name="DC.creator" content="Brown, Troy"' in html
        assert 'name="DC.identifier" content="10.17613/XXXX"' in html
        assert 'name="DC.type" content="Journal Article"' in html

    def test_blog_post_emits_blog_type_source_and_url(
        self, running_app: RunningApp, blog_post_record_metadata
    ) -> None:
        """Blog posts emit DC.type Blog, source blog title, and post URL id."""
        record = _published_with_links(blog_post_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/dublin_core.html",
            "meta_dublin_core(record, meta_title, meta_authors, meta_description, "
            "meta_publication_date, meta_publisher, meta_doi, meta_url)",
            **_dublin_core_kwargs(record),
        )

        blog_title = record["custom_fields"]["journal:journal"]["title"]
        post_url = record["metadata"]["identifiers"][0]["identifier"]
        assert 'name="DC.type" content="Blog"' in html
        assert f'name="DC.source" content="{blog_title}"' in html
        assert f'name="DC.identifier" content="{post_url}"' in html


class TestZoteroMacros:
    """Zotero Connector property tags."""

    def test_blog_post_sets_item_type(
        self, running_app: RunningApp, blog_post_record_metadata
    ) -> None:
        """Blog posts emit zotero:itemType."""
        record = _published_with_links(blog_post_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/zotero.html",
            "meta_zotero(record)",
            record=record,
        )
        assert 'property="zotero:itemType" content="blogPost"' in html

    def test_journal_article_omits_item_type(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Non-blog records emit no Zotero item-type override."""
        record = _published_with_links(journal_article_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/zotero.html",
            "meta_zotero(record)",
            record=record,
        )
        assert "zotero:itemType" not in html


class TestCoinsMacros:
    """COinS body spans from dumped records."""

    def test_blog_post_emits_coins_span_with_genre_blog(
        self, running_app: RunningApp, blog_post_record_metadata
    ) -> None:
        """Blog posts emit a COinS span with rft.genre=blog."""
        record = _published_with_links(blog_post_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/coins.html",
            "meta_coins(record)",
            record=record,
        )

        assert 'class="Z3988"' in html
        assert "rft.genre=blog" in html

        start = html.find('title="') + len('title="')
        end = html.find('"', start)
        coins_title = unquote(html[start:end].replace("&amp;", "&"))
        params = parse_qs(coins_title)
        assert params["rft.genre"] == ["blog"]
        assert params["rft.title"] == [record["metadata"]["title"]]
        assert params["rft.au"] == _creator_names(record)
        assert params["rft.jtitle"] == [
            record["custom_fields"]["journal:journal"]["title"]
        ]
        post_url = record["metadata"]["identifiers"][0]["identifier"]
        assert any(post_url in value for value in params.get("rft_id", []))

    def test_journal_article_emits_nothing(
        self, running_app: RunningApp, journal_article_record_metadata
    ) -> None:
        """Non-blog records currently emit no COinS span."""
        record = _published_with_links(journal_article_record_metadata())
        html = _render_macro(
            running_app.app,
            "kcworks/macros/embedded_metadata/coins.html",
            "meta_coins(record)",
            record=record,
        )
        assert "Z3988" not in html
