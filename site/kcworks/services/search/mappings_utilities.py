"""OpenSearch mapping utilities for KCWorks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invenio_search import current_search_client
from invenio_search.engine import dsl
from invenio_search.proxies import current_search
from invenio_search.utils import build_alias_name

_DYNAMIC_ALLOWS_UNDECLARED = frozenset({True, "true"})


def _object_allows_undeclared_children(val: dict[str, Any]) -> bool:
    """Return whether an object mapping may carry OS-only nested properties.

    Only `object` fields with `dynamic` true (or unset, defaulting to true)
    are treated as open containers whose live children the incoming file may omit.
    """
    if val.get("type") != "object":
        return False
    dynamic = val.get("dynamic", "true")
    return dynamic in _DYNAMIC_ALLOWS_UNDECLARED


def _declared_object_metadata_matches(
    old_val: dict[str, Any], new_val: dict[str, Any]
) -> bool:
    """Return whether OS object metadata matches the incoming file where declared."""
    if old_val.get("type") != new_val.get("type"):
        return False
    for meta_key in ("dynamic", "enabled"):
        if meta_key in new_val and old_val.get(meta_key) != new_val[meta_key]:
            return False
    return True


def additive_mapping_properties(
    old: dict[str, Any] | None,
    new: dict[str, Any],
    *,
    path: str = "",
) -> tuple[dict[str, Any], list[str]]:
    """Build a `put_mapping` properties patch with only additive changes.

    Compares the live mapping tree to the incoming file and returns nested
    properties OpenSearch can accept on an existing index. Existing fields whose
    definitions differ from the incoming file are left unchanged and reported in
    `warnings`.

    Args:
        old: Live `mappings.properties` subtree (or `None`).
        new: Incoming-file `mappings.properties` subtree.
        path: Dot path prefix used in warning messages.

    Returns:
        A tuple of `(patch, warnings)`. `patch` is empty when nothing can be
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

        if (
            old_props is not None
            and _object_allows_undeclared_children(new_val)
            and _declared_object_metadata_matches(old_val, new_val)
        ):
            continue

        if old_val != new_val:
            warnings.append(
                f"{field_path}: existing mapping differs; skipped (cannot change)"
            )

    return patch, warnings


def load_mapping_properties(record_index_name: str) -> dict[str, Any]:
    """Load `mappings.properties` from the incoming mapping file.

    Args:
        record_index_name: Logical index name (e.g. `communities-communities-v2.0.0`).

    Returns:
        The `properties` dict from the mapping JSON.
    """
    mapping_path = Path(current_search.mappings[record_index_name])
    with mapping_path.open(encoding="utf-8") as body:
        return json.load(body)["mappings"]["properties"]


def live_mapping_properties(record_index_name: str) -> dict[str, Any]:
    """Return `mappings.properties` from the live index on OpenSearch.

    Args:
        record_index_name: Logical index name (e.g. `communities-communities-v2.0.0`).

    Returns:
        Properties dict for the single index behind the write alias.
    """
    index_alias_name = build_alias_name(record_index_name)
    index_dict = current_search_client.indices.get(index=index_alias_name)
    index_keys = list(index_dict.keys())
    assert len(index_keys) == 1, (
        f"expected one index for alias {index_alias_name!r}, got {index_keys}"
    )
    return index_dict[index_keys[0]]["mappings"]["properties"]


def plan_additive_mapping_update(
    record_index_name: str,
) -> tuple[dict[str, Any], list[str]]:
    """Compute the additive `put_mapping` body for an index.

    Args:
        record_index_name: Logical index name (e.g. `communities-communities-v2.0.0`).

    Returns:
        `(body, warnings)` where `body` is `{}` or `{"properties": ...}`.
    """
    incoming = load_mapping_properties(record_index_name)
    live = live_mapping_properties(record_index_name)
    patch, warnings = additive_mapping_properties(live, incoming)
    if not patch:
        return {}, warnings
    return {"properties": patch}, warnings


def mapping_update_targets() -> list[tuple[str, str]]:
    """Return additive mapping update targets as `(label, logical_index_name)`.

    Includes the communities index plus the active RDM record and draft indices
    whose mapping JSON is registered with ``invenio_search``.

    Returns:
        Ordered list of human-readable label and logical index name pairs.
    """
    from invenio_communities.proxies import current_communities
    from invenio_rdm_records.records.api import RDMDraft, RDMRecord

    return [
        (
            "Communities",
            current_communities.service.config.record_cls.index._name,
        ),
        ("RDM records", RDMRecord.index._name),
        ("RDM drafts", RDMDraft.index._name),
    ]


def apply_additive_mapping_update(record_index_name: str) -> list[str]:
    """Apply additive mapping updates to the live index on OpenSearch.

    Args:
        record_index_name: Logical index name (e.g. `communities-communities-v2.0.0`).

    Returns:
        Warning strings for fields that could not be updated in place.
    """
    body, warnings = plan_additive_mapping_update(record_index_name)
    if not body:
        return warnings

    index_alias_name = build_alias_name(record_index_name)
    index_dict = current_search_client.indices.get(index=index_alias_name)
    index_keys = list(index_dict.keys())
    assert len(index_keys) == 1, (
        f"expected one index for alias {index_alias_name!r}, got {index_keys}"
    )
    full_index_name = index_keys[0]
    index_ = dsl.Index(full_index_name, using=current_search_client)
    index_.put_mapping(using=current_search_client, body=body)
    return warnings
