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

"""Default rendering returning a default web page."""

from flask import render_template

from invenio_previewer.proxies import current_previewer

previewable_extensions = [".docx", ".doc", ".pptx", ".ppt", ".tex"]


def can_preview(file):
    """Return if file type can be previewed."""
    return True


def preview(file):
    """Return the appropriate template and passes the file and embed flag."""
    return render_template(
        "custom_previewers/invenio_custom_default_viewer/default_viewer.html",
        file=file,
        js_bundles=current_previewer.js_bundles,
        css_bundles=current_previewer.css_bundles
        + ["custom_default_viewer_css.css"],
    )
