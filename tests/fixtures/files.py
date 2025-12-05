# Part of Knowledge Commons Works
# Copyright (C) 2023, 2024 Knowledge Commons
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License

"""Pytest fixtures for files."""

import hashlib
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def test_sample_files_folder():
    """Fixture allowing for flexible sample files location.

    Returns:
        Path: Path to the sample files directory.
    """
    folderpath = Path(__file__).parent.parent / "helpers" / "sample_files"
    if not folderpath.exists():
        folderpath = Path(__file__).parent.parent.parent / "helpers" / "sample_files"
    return folderpath


def file_md5(bytes_object):
    """Calculate the MD5 hash of a bytes object.

    Returns:
        str: MD5 hash as hexadecimal string.
    """
    return hashlib.md5(bytes_object).hexdigest()


def build_file_links(record_id, base_api_url, filename):
    """Build the file links for a record.

    Returns:
        dict: Dictionary containing file links.
    """
    extension = os.path.splitext(filename)[1]

    links = {
        "content": f"{base_api_url}/records/{record_id}/files/{filename}/content",
        "self": f"{base_api_url}/records/{record_id}/files/{filename}",
    }
    if extension not in [".csv", ".zip"]:
        links.update(
            {
                "iiif_api": (
                    f"{base_api_url}/iiif/record:{record_id}:{filename}/full/full/0/"
                    "default.png"
                ),
                "iiif_base": f"{base_api_url}/iiif/record:{record_id}:{filename}",
                "iiif_canvas": (
                    f"{base_api_url}/iiif/record:{record_id}/canvas/{filename}"
                ),
                "iiif_info": (
                    f"{base_api_url}/iiif/record:{record_id}:{filename}/info.json"
                ),
            }
        )
    return links
