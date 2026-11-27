# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for resolve-first person aliases in MultiFieldSearchTransformer."""

from invenio_db import db
from kcworks.config.search import RECORD_SEARCH_FIELD_ALIASES
from kcworks.services.search.queryparser.transformer import (
    MultiFieldSearchTransformer,
    extract_plain_person_term,
)
from luqum.parser import parser
from luqum.tree import Group, OrOperation


def _set_profile(user, **fields):
    profile = dict(user.user_profile or {})
    profile.update(fields)
    user.user_profile = profile
    db.session.commit()
    return user


def _transform(query: str):
    tree = parser.parse(query)
    transformer = MultiFieldSearchTransformer(RECORD_SEARCH_FIELD_ALIASES, None)
    return transformer.visit(tree, context={"identity": None})


def test_extract_plain_person_term_skips_wildcards_and_fuzzy():
    """Only plain Word/Phrase values are resolvable."""
    assert extract_plain_person_term(parser.parse("author:smith")) == "smith"
    assert extract_plain_person_term(parser.parse('author:"Jane Doe"')) == "Jane Doe"
    assert extract_plain_person_term(parser.parse("author:smi*")) is None
    assert extract_plain_person_term(parser.parse("author:smith~")) is None
    assert extract_plain_person_term(parser.parse("author:(a b)")) is None


def test_author_alias_resolves_local_user(user_factory, app):
    """author:username expands to UserSearchHelper creatibutor clauses."""
    u = user_factory(email="resolvealias@example.org", kc_username="resolvealias")
    _set_profile(
        u.user,
        full_name="Resolve Alias",
        display_name="Alias, Resolve",
    )

    with app.app_context():
        out = _transform("author:resolvealias")
    rendered = str(out)
    assert "Alias, Resolve" in rendered
    assert "metadata.creators.person_or_org.name" in rendered
    assert "resolvealias" in rendered


def test_user_and_name_aliases_resolve(user_factory, app):
    """user: and name: share resolve-first behavior."""
    u = user_factory(email="namedalias@example.org", kc_username="namedalias")
    _set_profile(u.user, full_name="Named Alias", display_name="Alias, Named")

    with app.app_context():
        for q in ("user:namedalias", 'name:"Alias, Named"'):
            rendered = str(_transform(q))
            assert "Alias, Named" in rendered
            assert "metadata.creators.person_or_org.name" in rendered


def test_author_miss_falls_back_to_literal_multifield(app):
    """Unknown person keeps path-tuple OR expansion."""
    with app.app_context():
        out = _transform("author:definitely-not-a-local-user-xyz")
    assert isinstance(out, Group)
    assert isinstance(out.children[0], OrOperation)
    rendered = str(out)
    assert "definitely-not-a-local-user-xyz" in rendered
    assert "metadata.creators.person_or_org.name" in rendered
    assert "metadata.contributors.person_or_org.identifiers.identifier" in rendered


def test_author_wildcard_skips_resolve_uses_literal(user_factory, app):
    """Wildcards do not hit the user table; literal multi-field OR remains."""
    user_factory(email="wild@example.org", kc_username="wildcarduser")
    with app.app_context():
        out = _transform("author:wild*")
    rendered = str(out)
    assert "wild*" in rendered
    assert isinstance(out, Group)


def test_nested_bool_still_resolves_person_clause(user_factory, app):
    """Person resolve works inside AND with other aliases."""
    u = user_factory(email="nested@example.org", kc_username="nesteduser")
    _set_profile(u.user, full_name="Nested User", display_name="User, Nested")

    with app.app_context():
        out = _transform("title:climate AND author:nesteduser")
    rendered = str(out)
    assert "metadata.title" in rendered or "additional_titles" in rendered
    assert "User, Nested" in rendered
    assert "nesteduser" in rendered
