# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to file previewers."""

PREVIEWER_MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024
"""Maximum file size in bytes for JSON/XML/CSV files."""

PREVIEWER_MAX_IMAGE_SIZE_BYTES = 0.5 * 1024 * 1024
"""Maximum file size in bytes for image files."""

PREVIEWER_TXT_MAX_BYTES = 1 * 1024 * 1024
"""Maximum number of .txt file bytes to preview before truncated."""

PREVIEWER_ZIP_MAX_FILES = 1000
"""Max number of files showed in the ZIP previewer."""


PREVIEWER_PREVIEWERS_ORDER = [
    "invenio_previewer.extensions.csv_papaparsejs",
    # KCWorks pdfjs theme via invenio_previewer/pdfjs.html + pdf_viewer_overrides_css
    "invenio_previewer.extensions.pdfjs",
    "invenio_previewer.extensions.iiif_simple",
    "invenio_previewer.extensions.simple_image",
    "invenio_previewer.extensions.json_prismjs",
    "invenio_previewer.extensions.xml_prismjs",
    "invenio_previewer.extensions.mistune",
    "invenio_previewer.extensions.video_videojs",
    "invenio_previewer.extensions.audio_videojs",
    "invenio_previewer.extensions.ipynb",
    "invenio_previewer.extensions.zip",
    "invenio_previewer.extensions.txt_previewer",
    "invenio_previewer.extensions.custom_docx_viewer",
    "invenio_previewer.extensions.custom_pptx_viewer",
    "invenio_previewer.extensions.custom_latex_viewer",
    "invenio_previewer.extensions.custom_default_viewer",
    "invenio_previewer.extensions.default",
]

PREVIEWER_PREFERENCE = [
    "csv_papaparsejs",
    "pdfjs",
    "iiif_simple",
    "simple_image",
    "json_prismjs",
    "xml_prismjs",
    "mistune",
    "video_videojs",
    "audio_videojs",
    "ipynb",
    "zip",
    "txt",
    "custom_docx_viewer",
    "custom_pptx_viewer",
    "custom_latex_viewer",
    "custom_default_viewer",
]
"""Preferred previewers."""
