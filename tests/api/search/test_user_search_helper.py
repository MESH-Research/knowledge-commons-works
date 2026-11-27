# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for UserSearchHelper works-by-user query construction."""

from invenio_db import db
from kcworks.services.search.user_search import UserSearchHelper
from kcworks.templates.template_filters import user_works_search_url


def _set_profile(user, **fields):
    profile = dict(user.user_profile or {})
    profile.update(fields)
    user.user_profile = profile
    db.session.commit()
    return user


def test_query_string_for_user_includes_name_variants_and_identifiers(user_factory):
    """Works query ORs full_name, display_name, and profile identifiers."""
    u = user_factory(
        email="workshelper@example.org",
        kc_username="workshelper",
        orcid="0000-0002-1825-0097",
    )
    _set_profile(
        u.user,
        full_name="Jane Doe",
        display_name="Doe, Jane",
        identifier_email="workshelper@example.org",
    )

    query = UserSearchHelper.query_string_for_user(u.user)

    assert 'metadata.creators.person_or_org.name:"Jane Doe"' in query
    assert 'metadata.creators.person_or_org.name:"Doe, Jane"' in query
    assert 'metadata.contributors.person_or_org.name:"Doe, Jane"' in query
    assert (
        'metadata.creators.person_or_org.identifiers.identifier:'
        '"0000-0002-1825-0097"'
    ) in query
    assert (
        'metadata.creators.person_or_org.identifiers.identifier:"workshelper"'
    ) in query
    assert (
        'metadata.creators.person_or_org.identifiers.identifier:'
        '"workshelper@example.org"'
    ) in query
    assert " OR " in query


def test_query_string_for_user_url_encoded_matches_literal_shape(user_factory):
    """URL-encoded form quotes `%22` and joins with `%20OR%20`."""
    u = user_factory(email="worksenc@example.org", kc_username="worksenc")
    _set_profile(u.user, full_name="Ada Lovelace", display_name="Lovelace, Ada")

    encoded = UserSearchHelper.query_string_for_user_url_encoded(u.user)
    literal = UserSearchHelper.query_string_for_user(u.user)

    assert "%22" in encoded
    assert "%20OR%20" in encoded
    assert encoded == literal.replace('"', "%22").replace(" OR ", "%20OR%20")


def test_resolve_contributor_user_by_kc_username_and_orcid(user_factory):
    """Exact identifier resolution finds the local user."""
    u = user_factory(
        email="resolve@example.org",
        kc_username="resolve_me",
        orcid="0000-0001-2345-6789",
    )

    by_username = UserSearchHelper.resolve_contributor_user(
        contributor_kc_username="resolve_me"
    )
    by_orcid = UserSearchHelper.resolve_contributor_user(
        contributor_orcid="0000-0001-2345-6789"
    )

    assert by_username.id == u.user.id
    assert by_orcid.id == u.user.id


def test_user_works_search_url_embeds_helper_query(user_factory, app):
    """Dashboard My Works URL uses the URL-encoded helper query."""
    u = user_factory(email="myworks@example.org", kc_username="myworks")
    _set_profile(u.user, full_name="Grace Hopper", display_name="Hopper, Grace")

    with app.test_request_context():
        url = user_works_search_url(u.user)
        empty = user_works_search_url(None)

    expected_q = UserSearchHelper.query_string_for_user_url_encoded(u.user)
    assert url.endswith(f"?q={expected_q}")
    assert "q=" not in empty or empty.endswith("/search") or empty.rstrip("/").endswith(
        "search"
    )


def test_resolve_users_from_search_term_by_orcid_username_name_email(user_factory):
    """Cascade: ORCID, email, username, then exact name; empty on miss."""
    u = user_factory(
        email="cascade@example.org",
        kc_username="cascade_user",
        orcid="0000-0002-1825-0097",
    )
    _set_profile(
        u.user,
        full_name="Cascade Example",
        display_name="Example, Cascade",
        identifier_email="cascade@example.org",
    )

    by_orcid = UserSearchHelper.resolve_users_from_search_term(
        "https://orcid.org/0000-0002-1825-0097"
    )
    by_email = UserSearchHelper.resolve_users_from_search_term("cascade@example.org")
    by_username = UserSearchHelper.resolve_users_from_search_term("cascade_user")
    by_display = UserSearchHelper.resolve_users_from_search_term("Example, Cascade")
    by_full = UserSearchHelper.resolve_users_from_search_term("cascade example")
    miss = UserSearchHelper.resolve_users_from_search_term("no-such-person")

    assert [x.id for x in by_orcid] == [u.user.id]
    assert [x.id for x in by_email] == [u.user.id]
    assert [x.id for x in by_username] == [u.user.id]
    assert [x.id for x in by_display] == [u.user.id]
    assert [x.id for x in by_full] == [u.user.id]
    assert miss == []


def test_group_for_users_builds_or_of_search_fields(user_factory):
    """AST builder emits SearchField phrases for name variants."""
    from luqum.tree import Group, SearchField

    u = user_factory(email="ast@example.org", kc_username="astuser")
    _set_profile(u.user, full_name="Ada Lovelace", display_name="Lovelace, Ada")

    node = UserSearchHelper.group_for_users([u.user])
    assert node is not None
    assert isinstance(node, (Group, SearchField))
    rendered = str(node)
    assert "Lovelace, Ada" in rendered
    assert "metadata.creators.person_or_org.name" in rendered
    assert "astuser" in rendered
