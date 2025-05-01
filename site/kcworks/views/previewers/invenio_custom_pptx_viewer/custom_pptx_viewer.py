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

"""PPTX previewer."""

from flask import render_template
from invenio_previewer.proxies import current_previewer

previewable_extensions = [".pptx", ".ppt"]


def can_preview(file):
    """Check if file can be previewed."""
    return file.has_extensions(*previewable_extensions)


def preview(file):
    """Preview file."""
    return render_template(
        "custom_previewers/invenio_custom_pptx_viewer/pptx_viewer.html",
        file=file,
        # html_tags='',
        js_bundles=current_previewer.js_bundles,
        css_bundles=current_previewer.css_bundles,
    )
