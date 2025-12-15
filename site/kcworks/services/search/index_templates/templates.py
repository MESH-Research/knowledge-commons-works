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

"""Index template functions for KCWorks."""


def get_index_templates():
    """Get all index templates to register with invenio_search via entrypoints.

    Note that we don't include the stats templates here since they are declared
    in the stats config objects and are registered with invenio_search by
    the stats extension.

    Returns:
        list[str]: List of index template module paths.
    """
    return [
        "kcworks.services.search.index_templates.drafts",
        "kcworks.services.search.index_templates.records",
        "kcworks.services.search.index_templates.affiliations",
        "kcworks.services.search.index_templates.subjects",
        "kcworks.services.search.index_templates.default",
    ]
