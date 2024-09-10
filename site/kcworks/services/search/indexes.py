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

from invenio_search.proxies import current_search_client
from typing import Optional


def delete_index(index_names: list[str], ignore: Optional[list[int]] = None):
    """Delete the search indices specified in the list.

    The indices are specified by their aliases. These must be complete aliases
    (e.g. `kcworks-stats-record-view`).
    """
    failed_indices = []
    for index_name in index_names:
        lookup_response = current_search_client.indices.get_alias(
            index=index_name, ignore=[404]
        )
        if "error" in lookup_response:
            failed_indices.append(index_name)
            indices_to_delete = []
        else:
            indices_to_delete = list(lookup_response.keys())
        if len(indices_to_delete) == 0:
            pass
        elif len(indices_to_delete) >= 1:
            for index in indices_to_delete:
                yield (
                    index,
                    current_search_client.indices.delete(
                        index=index,
                        ignore=ignore,
                    ),
                )
    if len(failed_indices) > 0:
        print(f"Failed to delete indices: {failed_indices}")
