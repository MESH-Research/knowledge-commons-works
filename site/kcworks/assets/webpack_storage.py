# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.
"""Webpack collect storage that symlinks files, not directories."""

from collections.abc import Iterator

from pywebpack.storage import LinkStorage, iter_files


class FlatLinkStorage(LinkStorage):
    """Symlink individual files into the build context.

    Parent directories under `var/instance/assets` are created as real dirs
    (via `makedirs` in `run`). Multiple bundles can contribute files under
    the same folder (e.g. `templates/custom_fields/`) without last-bundle-wins.
    """

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """Iterator magic method that iterates over files instead of folder paths.

        Returns:
            Iterator[tuple[str, str]]: Iterator of (absolute_path, relative_path) pairs.
        """
        return iter_files(self.srcdir)
