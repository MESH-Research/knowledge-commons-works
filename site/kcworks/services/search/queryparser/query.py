# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Knowledge Commons Works is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

from invenio_records_resources.services.records.queryparser.query import (
    QueryParser,
)

from invenio_search.engine import dsl
from luqum.auto_head_tail import auto_head_tail
from luqum.exceptions import ParseError
from luqum.parser import parser as luqum_parser

from invenio_records_resources.services.errors import (
    QuerystringValidationError,
)


class MemberQueryParser(QueryParser):
    """
    Query parser for members search.

    Adds a wildcard to the query string.
    """

    def parse(self, query_str):
        """Parse the query."""
        try:
            # We parse the Lucene query syntax in Python, so we know upfront
            # if the syntax is correct before executing it in the search engine
            tree = luqum_parser.parse(query_str)
            # Perform transformation on the abstract syntax tree (AST)
            if self.tree_transformer_cls is not None:
                transformer = self.tree_transformer_cls(
                    mapping=self.mapping,
                    allow_list=self.allow_list,
                )
                new_tree = transformer.visit(
                    tree, context={"identity": self.identity}
                )
                new_tree = auto_head_tail(new_tree)
                query_str = str(new_tree)
            return dsl.Q(
                "query_string",
                query=f"{query_str}*",
                **self.extra_params,
            )
        except (ParseError, QuerystringValidationError):
            # Fallback to a multi-match query.
            if self.allow_list:
                # if there is an allow list it must overwrite a potential value
                # given by the query to include it in the fields
                kwargs = {**self.extra_params, "fields": self.fields}
                return dsl.Q("multi_match", query=query_str, **kwargs)

            # if there is no allow list we pass the parameters as default, without
            # modifying the fields, or nothing if it was not passed. this is to
            # avoid passing `fields=None`
            return dsl.Q(
                "multi_match",
                query=query_str,
                **self.extra_params,
            )
