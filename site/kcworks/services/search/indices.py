# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Functions for managing search indices."""

from collections.abc import Generator

from invenio_search.proxies import current_search_client


def delete_index(
    index_names: list[str], ignore: list[int] | None = None
) -> None | Generator[tuple[str, dict], None, None]:
    """Delete the search indices specified in the list.

    Args:
        index_names (list[str]): The list of index names to delete.
        ignore (list[int] | None, optional): The list of error codes to ignore.
            Defaults to None.

    Returns:
        None | Generator[tuple[str, dict], None, None]: A generator of the deleted
            indices and their responses. If any indices are not found, they are
            added to the list of failed indices. If no indices are found, the
            function returns None.

    Note:
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
