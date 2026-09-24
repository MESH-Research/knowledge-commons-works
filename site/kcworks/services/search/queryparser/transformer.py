# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# Extends Invenio-Records-Resources SearchFieldTransformer:
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.

"""Query tree transformer with multi-field alias expansion.

See https://luqum.readthedocs.io/en/latest/quick_start.html#manipulating for
how to build your own query tree transformer.
"""

import re

from invenio_i18n import gettext as _
from invenio_records_resources.services.errors import QuerystringValidationError
from invenio_records_resources.services.records.queryparser.transformer import (
    FieldValueMapper,
    RestrictedTerm,
    RestrictedTermValue,
    SearchFieldTransformer,
)
from luqum.tree import Group, OrOperation, SearchField

# OpenSearch query_string treats `:` as field/value separator; Invenio custom
# field paths include namespace colons (e.g. `custom_fields.kcr:tags`).
_UNESCAPED_COLON = re.compile(r"(?<!\\):")


def escape_query_string_field(field_name: str) -> str:
    r"""Escape `:` in a field path for OpenSearch `query_string`.

    Args:
        field_name: Resolved OpenSearch field path (may already contain
            `\\:` escapes).

    Returns:
        The path with unescaped colons replaced by `\\:`.
    """
    return _UNESCAPED_COLON.sub(r"\:", field_name)


class MultiFieldSearchTransformer(SearchFieldTransformer):
    r"""Transform user-friendly field names to internal field names.

    Behaves like upstream `SearchFieldTransformer`, with two extensions:

    - A mapping value that is a `list` or `tuple` of field paths expands a
      single fielded clause into an OR group.
    - Colons in resolved field paths are escaped for `query_string` (needed
      for Invenio custom fields such as `custom_fields.kcr:…`).

    Example:

        mapping = {
            "publisher": "metadata.publisher",
            "title": ("metadata.title", "metadata.additional_titles.title"),
            "keyword": "custom_fields.kcr:user_defined_tags",
        }

    Then `title:computer` becomes:

        (metadata.title:computer OR metadata.additional_titles.title:computer)

    And `keyword:methodology` becomes:

        custom_fields.kcr\\:user_defined_tags:methodology
    """

    def visit_search_field(self, node, context):
        """Visit a search field.

        Args:
            node: The luqum `SearchField` node.
            context: Visitor context; must include `identity`.

        Yields:
            A rewritten `SearchField`, or a `Group` of OR-ed `SearchField`
            nodes when the mapping target is a sequence of paths.

        Raises:
            QuerystringValidationError: If the field is restricted or not
                allowed by `allow_list`.
        """
        # Use the node name if not mapped for transformation.
        term_name = self._mapping.get(node.name, node.name)
        field_value_mapper = None

        # Same special-case chain as upstream SearchFieldTransformer.
        if isinstance(term_name, FieldValueMapper):
            field_value_mapper = term_name
            term_name = field_value_mapper.term_name
        if isinstance(term_name, RestrictedTermValue):
            field_value_mapper = term_name
            term_name = node.name
        if isinstance(term_name, RestrictedTerm):
            allows = term_name.allows(context["identity"])
            term_name = node.name
            # field_value_mapper is left as None on purpose - if the permission
            # allows, we don't map any query, we allow it "as is"
            if not allows:
                raise QuerystringValidationError(
                    _("Invalid search field: %(field_name)s.", field_name=node.name)
                )

        if isinstance(term_name, (list, tuple)):
            targets = tuple(term_name)
        else:
            targets = (term_name,)

        # If a allow list exists, each resolved term must be allowed.
        if self._allow_list:
            for target in targets:
                if target not in self._allow_list:
                    raise QuerystringValidationError(
                        _(
                            "Invalid search field: %(field_name)s.",
                            field_name=node.name,
                        )
                    )

        if field_value_mapper:
            context["field_value_mapper"] = field_value_mapper

        if len(targets) == 1:
            # Returns a copy of the node (upstream behavior).
            new_node = node.clone_item()
            new_node.name = escape_query_string_field(targets[0])
            new_node.children = list(self.clone_children(node, new_node, context))
            yield new_node
            return

        operands = []
        for target in targets:
            child_node = SearchField(escape_query_string_field(target), None)
            child_node.children = list(self.clone_children(node, child_node, context))
            operands.append(child_node)
        yield Group(OrOperation(*operands))
