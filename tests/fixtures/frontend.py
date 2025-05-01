# Part of Knowledge Commons Works
# Copyright (C) 2023, 2024 MESH Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License

"""Pytest fixtures for frontend."""

from flask_webpackext.manifest import (
    JinjaManifest,
    JinjaManifestEntry,
    JinjaManifestLoader,
)


class MockJinjaManifest(JinjaManifest):
    """Mock the webpack manifest to avoid having to compile the full assets."""

    def __getitem__(self, key):
        """Get a manifest entry."""
        return JinjaManifestEntry(key, [key])

    def __getattr__(self, name):
        """Get a manifest entry."""
        return JinjaManifestEntry(name, [name])


class MockManifestLoader(JinjaManifestLoader):
    """Manifest loader creating a mocked manifest."""

    def load(self, filepath):
        """Load the manifest."""
        return MockJinjaManifest()
