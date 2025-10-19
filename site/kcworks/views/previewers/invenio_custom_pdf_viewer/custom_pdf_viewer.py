# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PDF previewer based on pdf.js."""

from flask import render_template
from invenio_previewer.proxies import current_previewer

previewable_extensions = ["pdf", "pdfa"]


def can_preview(file):
    """Check if file can be previewed.
    
    Returns:
        bool: True if file can be previewed, False otherwise.
    """
    return file.has_extensions(".pdf", ".pdfa")


def preview(file):
    """Preview file.
    
    Returns:
        str: Rendered template for file preview.
    """
    return render_template(
        "custom_previewers/invenio_custom_pdf_viewer/pdfjs.html",
        file=file,
        html_tags='dir="ltr" mozdisallowselectionprint moznomarginboxes',
        css_bundles=["custom_pdf_viewer_css.css"],
        js_bundles=current_previewer.js_bundles
        + ["custom_pdf_viewer_js.js", "fullscreen_js.js"],
    )
