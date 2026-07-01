"""Additive OpenSearch mapping updates for the communities index."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invenio_search import current_search_client
from invenio_search.engine import dsl
from invenio_search.proxies import current_search
from invenio_search.utils import build_alias_name


def additive_mapping_properties(
    old: dict[str, Any] | None,
    new: dict[str, Any],
    *,
    path: str = "",
) -> tuple[dict[str, Any], list[str]]:
    """Build a ``put_mapping`` properties patch with only additive changes.

    Compares the live mapping tree to the target (registered JSON) and returns
    nested properties OpenSearch can accept on an existing index. Existing fields
    whose definitions differ from the target are left unchanged and reported in
    ``warnings``.

    Args:
        old: Live ``mappings.properties`` subtree (or ``None``).
        new: Target ``mappings.properties`` subtree from the mapping file.
        path: Dot path prefix used in warning messages.

    Returns:
        A tuple of ``(patch, warnings)``. ``patch`` is empty when nothing can be
        added.
    """
    old = old or {}
    patch: dict[str, Any] = {}
    warnings: list[str] = []

    for key, new_val in new.items():
        field_path = f"{path}.{key}" if path else key
        old_val = old.get(key)
        if old_val is None:
            patch[key] = new_val
            continue
        if not isinstance(old_val, dict) or not isinstance(new_val, dict):
            if old_val != new_val:
                warnings.append(
                    f"{field_path}: existing mapping differs; skipped (cannot change)"
                )
            continue

        new_props = new_val.get("properties")
        old_props = old_val.get("properties")
        if new_props is not None:
            if old_props is None:
                patch[key] = {"properties": new_props}
                continue
            sub_patch, sub_warnings = additive_mapping_properties(
                old_props,
                new_props,
                path=field_path,
            )
            warnings.extend(sub_warnings)
            if sub_patch:
                merged: dict[str, Any] = {"properties": sub_patch}
                if "type" in new_val:
                    merged["type"] = new_val["type"]
                for meta_key in ("dynamic", "enabled"):
                    if meta_key in new_val:
                        merged[meta_key] = new_val[meta_key]
                patch[key] = merged
            continue

        if old_val != new_val:
            warnings.append(
                f"{field_path}: existing mapping differs; skipped (cannot change)"
            )

    return patch, warnings


def communities_index_name(record_index_name: str) -> str:
    """Return the prefixed communities write-alias name."""
    return build_alias_name(record_index_name)


def load_target_communities_properties(record_index_name: str) -> dict[str, Any]:
    """Load ``mappings.properties`` from the registered communities mapping file.

    Args:
        record_index_name: Logical index name (e.g. ``communities-communities-v2.0.0``).

    Returns:
        The ``properties`` dict from the registered mapping JSON.
    """
    mapping_path = Path(current_search.mappings[record_index_name])
    with mapping_path.open(encoding="utf-8") as body:
        return json.load(body)["mappings"]["properties"]


def live_communities_properties(record_index_name: str) -> dict[str, Any]:
    """Return ``mappings.properties`` from the live communities index.

    Args:
        record_index_name: Logical index name (e.g. ``communities-communities-v2.0.0``).

    Returns:
        Properties dict for the single index behind the write alias.
    """
    index_alias_name = communities_index_name(record_index_name)
    index_dict = current_search_client.indices.get(index=index_alias_name)
    index_keys = list(index_dict.keys())
    assert len(index_keys) == 1, (
        f"expected one index for alias {index_alias_name!r}, got {index_keys}"
    )
    return index_dict[index_keys[0]]["mappings"]["properties"]


def communities_search_index(record_index_name: str) -> dsl.Index:
    """Return an OpenSearch index handle for the communities write alias."""
    return dsl.Index(
        communities_index_name(record_index_name),
        using=current_search_client,
    )


def plan_additive_communities_mapping_update(
    record_index_name: str,
) -> tuple[dict[str, Any], list[str]]:
    """Compute the additive ``put_mapping`` body for the communities index.

    Args:
        record_index_name: Logical index name (e.g. ``communities-communities-v2.0.0``).

    Returns:
        ``(body, warnings)`` where ``body`` is ``{}`` or ``{"properties": ...}``.
    """
    target = load_target_communities_properties(record_index_name)
    live = live_communities_properties(record_index_name)
    patch, warnings = additive_mapping_properties(live, target)
    if not patch:
        return {}, warnings
    return {"properties": patch}, warnings


def apply_additive_communities_mapping_update(record_index_name: str) -> list[str]:
    """Apply additive mapping updates to the live communities index.

    Args:
        record_index_name: Logical index name (e.g. ``communities-communities-v2.0.0``).

    Returns:
        Warning strings for fields that could not be updated in place.
    """
    body, warnings = plan_additive_communities_mapping_update(record_index_name)
    if body:
        communities_search_index(record_index_name).put_mapping(body=body)
    return warnings
