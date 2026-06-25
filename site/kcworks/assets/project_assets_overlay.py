# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Overlay repo assets/ and static/ onto the instance with per-file symlinks."""

from pathlib import Path

from invenio_cli.helpers import filesystem


def _materialize_dir_symlink(link_path: Path) -> None:
    """Replace a directory symlink with a real directory of per-file symlinks.

    Bundled files that were only reachable through ``link_path`` are preserved
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
    """Ensure each ancestor of ``dst`` under ``root`` is a real directory.

    Args:
        root: Base directory in the instance tree (e.g. ``instance/assets``).
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


def link_project_tree(project_dir: Path, instance_path: Path, name: str) -> list[Path]:
    """Symlink every file under ``project_dir / name`` into ``instance_path / name``.

    Returns:
        list[Path]: list of paths for the files that were symlinked
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
        filesystem.force_symlink(src, dst)
        linked.append(dst)
    return linked


def link_project_assets_and_static(project_dir: Path, instance_path: Path) -> None:
    """Overlay repo ``assets/`` (and ``static/`` when separate) onto the instance.

    KCWorks dev compose bind-mounts ``./static`` to ``var/instance/static``, so
    project and instance static are the same directory; overlaying would replace
    real files with self-referential symlinks.
    """
    link_project_tree(project_dir, instance_path, "assets")

    project_static = project_dir / "static"
    instance_static = instance_path / "static"
    if (
        project_static.is_dir()
        and project_static.resolve() != instance_static.resolve()
    ):
        link_project_tree(project_dir, instance_path, "static")
