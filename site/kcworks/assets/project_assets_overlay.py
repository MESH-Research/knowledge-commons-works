# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Overlay repo assets/ and static/ onto the instance.

`assets/` is overlaid with per-file symlinks (consumed by webpack inside the
app/builder container). `static/` is overlaid with real file **copies** so the
served tree on the `static_data` volume contains no symlinks pointing at
`/opt/invenio/src` — that path does not exist in the separate nginx container,
which would follow such symlinks to a missing target and return 404.
"""

import shutil
from pathlib import Path

from invenio_cli.helpers import filesystem


def _place_file(src: Path, dst: Path, copy: bool) -> None:
    """Overlay `src` at `dst` as a real copy or a symlink.

    Any existing entry at `dst` (regular file or symlink) is replaced.

    Args:
        src: Source file in the project tree.
        dst: Destination path in the instance tree.
        copy: When `True` copy the file; otherwise create a symlink to `src`.
    """
    if copy:
        if dst.is_symlink() or dst.exists():
            dst.unlink()
        shutil.copy2(src, dst)
    else:
        filesystem.force_symlink(src, dst)


def _materialize_dir_symlink(link_path: Path) -> None:
    """Replace a directory symlink with a real directory of per-file symlinks.

    Bundled files that were only reachable through `link_path` are preserved
    as symlinks into the former target tree.

    Args:
        link_path: Instance path that is currently a symlink to a directory.
    """
    if not link_path.is_symlink():
        return

    target_root = link_path.resolve()
    link_path.unlink()
    link_path.mkdir()

    if not target_root.is_dir():
        return

    for src in target_root.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(target_root)
        dst = link_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        filesystem.force_symlink(src, dst)


def _ensure_real_ancestors(root: Path, dst: Path) -> None:
    """Ensure each ancestor of `dst` under `root` is a real directory.

    Args:
        root: Base directory in the instance tree (e.g. `instance/assets`).
        dst: Destination file path to overlay.

    Raises:
        NotADirectoryError: If an ancestor path exists but is not a directory.
    """
    rel_parent = dst.parent.relative_to(root)
    current = root
    for part in rel_parent.parts:
        current = current / part
        if current.is_symlink():
            _materialize_dir_symlink(current)
        elif not current.exists():
            current.mkdir()
        elif not current.is_dir():
            raise NotADirectoryError(current)


def link_project_tree(
    project_dir: Path, instance_path: Path, name: str, copy: bool = False
) -> list[Path]:
    """Overlay every file under `project_dir / name` into `instance_path / name`.

    Args:
        project_dir: Repository root (e.g. `/opt/invenio/src`).
        instance_path: Instance root (e.g. `/opt/invenio/var/instance`).
        name: Subtree to overlay (`"assets"` or `"static"`).
        copy: When `True` copy files (real files on the served volume); otherwise
            symlink them back to `project_dir / name`.

    Returns:
        list[Path]: list of paths for the files that were overlaid
    """
    src_root = project_dir / name
    if not src_root.is_dir():
        return []

    linked: list[Path] = []
    dst_root = instance_path / name

    for src in src_root.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        _ensure_real_ancestors(dst_root, dst)
        _place_file(src, dst, copy)
        linked.append(dst)
    return linked


def link_project_assets_and_static(project_dir: Path, instance_path: Path) -> None:
    """Overlay repo `assets/` (and `static/` when present) onto the instance.

    `static/` is copied (not symlinked) into the served `static_data` volume so
    the separate nginx container can serve it. The served `static/` lives on that
    disposable volume, never on the host `./static` (dev binds host `./static` to
    `/opt/invenio/src/static`), so copying into a mounted instance `static/` is
    safe and, in dev, refreshes the served tree from the live source on re-run.
    """
    link_project_tree(project_dir, instance_path, "assets")
    link_project_tree(project_dir, instance_path, "static", copy=True)
