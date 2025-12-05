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

"""LaTeX previewer."""

from flask import render_template
from invenio_previewer.proxies import current_previewer

previewable_extensions = [".tex", ".bib", ".cls"]


def can_preview(file):
    """Check if file can be previewed.

    Returns:
        bool: True if file can be previewed, False otherwise.
    """
    return file.has_extensions(*previewable_extensions)


def preview(file):
    """Preview file.

    Returns:
        str: Rendered template for file preview.
    """
    return render_template(
        "custom_previewers/invenio_custom_latex_viewer/latex_viewer.html",
        # html_tags='',
        file=file,
        js_bundles=current_previewer.js_bundles,
        css_bundles=current_previewer.css_bundles,
    )
