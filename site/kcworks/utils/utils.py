# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Utility functions for KCWorks."""

from typing import Any

from invenio_accounts.models import User
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.records.systemfields.access.field.record import RecordAccess

from invenio_remote_user_data_kcworks.proxies import current_remote_user_data_service
from invenio_remote_user_data_kcworks.types.auth import AccountInfo
from invenio_remote_user_data_kcworks.utils.auth import (
    CILogonHelpers,
    UserIdentifierHelpers,
)


def update_nested_dict(starting_value: Any, updates: Any) -> Any:
    """Update a nested dictionary with another dictionary.

    This function is a recursive function that updates a nested dictionary with another
    dictionary. It handles nested dictionaries and lists.

    List items are updated by index. If there are more items in a list in the updates
    than in the equivalent list in the starting_value, the remaining items are added
    to the end of the list.

    If there are more items in the starting_value than in the updates, the remaining
    items are not removed from the list.

    The two starting values must have lists and dictionaries in compatible locations
    in the structure. If one has a list where the other has a dictionary, the function
    will raise a TypeError.

    Returns:
        Any: The updated nested dictionary.
    """
    if isinstance(updates, dict):
        for key, value in updates.items():
            starting_value[key] = update_nested_dict(starting_value.get(key, {}), value)
    elif isinstance(updates, list):
        for idx, item in enumerate(updates):
            if idx < len(starting_value):
                starting_value[idx] = update_nested_dict(starting_value[idx], item)
            else:
                starting_value.append(item)
    else:
        starting_value = updates
    return starting_value


def _account_info_from_contributor(contributor: dict) -> AccountInfo | None:
    """Build an `AccountInfo` from a contributor's person/org identifiers.

    Collects `kc_username` / `hc_username`, `orcid`, and `email` schemes.
    Returns `None` when none of those identifiers are present.

    Args:
        contributor: A creator/contributor metadata dict.

    Returns:
        An `AccountInfo` suitable for `CILogonHelpers.get_user_from_account_info`,
        or `None` when there is nothing to look up.
    """
    kc_username = ""
    email = ""
    orcid: str | None = None
    identifiers = contributor.get("person_or_org", {}).get("identifiers") or []
    for identifier in identifiers:
        scheme = identifier.get("scheme")
        value = identifier.get("identifier") or ""
        if not value:
            continue
        if scheme in ("hc_username", "kc_username") and not kc_username:
            kc_username = value
        elif scheme == "email" and not email:
            email = value
        elif scheme == "orcid" and not orcid:
            orcid = value
    if not (kc_username or email or orcid):
        return None
    return AccountInfo(
        external_id="",
        external_method="knowledgeCommons",
        email=email,
        orcid=orcid,
        kc_username=kc_username,
    )


def get_commons_user_from_contributor(contributor: dict) -> str:
    """Get the Commons username from a contributor dict.

    Prefers an explicit `kc_username` / `hc_username` identifier. When those
    are absent, resolves a local user via ORCID/email and reads the username
    from that user.

    If one can't be found, return an empty string.

    Parameters:
        contributor: A contributor dict.

    Returns:
        The Commons username as a string.
    """
    identifiers = contributor.get("person_or_org", {}).get("identifiers") or []
    for identifier in identifiers:
        if identifier.get("scheme") in ("hc_username", "kc_username"):
            value = identifier.get("identifier") or ""
            if value:
                return value
    # FIXME: add a field to the contributor model for the kc_username?
    user = get_kcworks_user_from_contributor(contributor)
    return UserIdentifierHelpers.username_from_user(user) or ""


def get_user_by_commons_username(commons_username: str) -> User | None:
    """Get a KCWorks user by their Commons / KC member username.

    Delegates to `RemoteUserDataService.find_local_user_by_kc_username`, which
    matches `identifier_kc_username`, legacy `UserIdentity` rows, and username
    heuristics shared with login matching.

    Parameters:
        commons_username: The Commons username to search for.

    Returns:
        The matching KCWorks user, or `None` if none is found.
    """
    if not commons_username:
        return None
    return current_remote_user_data_service.find_local_user_by_kc_username(
        commons_username
    )


def get_kcworks_user_from_contributor(contributor: dict) -> User | None:
    """Get the KCWorks user from a contributor dict.

    Builds an `AccountInfo` from the contributor's identifiers and delegates
    to `CILogonHelpers.get_user_from_account_info`, which matches by ORCID,
    KC username, and email (same chain used at login).

    Parameters:
        contributor: A contributor dict.

    Returns:
        The KCWorks user. If one can't be found, return None.
    """
    account_info = _account_info_from_contributor(contributor)
    if account_info is None:
        return None
    return CILogonHelpers.get_user_from_account_info(account_info)


def get_changed_fields(
    existing_data: dict | RDMDraft | RDMRecord | Any | None,
    new_data: dict | RDMRecord | RDMDraft | Any | None,
    separator: str = ".",
    current_field_path: str = "",
) -> list:
    """Get the fields that have been changed in the new version of a metadata record.

    By default the output list of field paths will use a dot (`.`) as the separator.
    This can be changed by passing a different separator (e.g., `|`) to the
    `separator` parameter. Be careful, though, that the separator is a character
    that is not present in the field names. A colon, for example, is not safe.

    Parameters:
        existing_data: The initial state of the record data.
        new_data: The new state of the record data.
        current_field_path: The current field path of the for the section of the
            data dictionary we are currently processing. (Used for recursion only.)
        separator: The separator to use between segments in the field paths. Used
            internally and in the output list.

    Returns:
        list: A list of field paths that have been changed.
    """
    changed_field_paths = []
    existing_data_val = existing_data
    new_data_val = new_data
    if isinstance(existing_data, RDMDraft) or isinstance(existing_data, RDMRecord):
        existing_data_dict = {"metadata": existing_data.metadata}
        if hasattr(existing_data, "custom_fields"):
            existing_data_dict["custom_fields"] = existing_data.custom_fields
        if hasattr(existing_data, "access"):
            if isinstance(existing_data.access, RecordAccess):
                existing_data_dict["access"] = existing_data.access.dump()
            else:
                existing_data_dict["access"] = existing_data.access
        existing_data_val = existing_data_dict

    if isinstance(new_data, RDMDraft) or isinstance(new_data, RDMRecord):
        new_data_dict = {"metadata": new_data.metadata}
        if hasattr(new_data, "custom_fields"):
            new_data_dict["custom_fields"] = new_data.custom_fields
        if hasattr(new_data, "access"):
            new_data_dict["access"] = new_data.access
        new_data_val = new_data_dict

    if not existing_data_val and current_field_path:
        return [current_field_path]
    if isinstance(new_data_val, dict) and isinstance(existing_data_val, dict):
        if not current_field_path:
            existing_data_val = {
                k: v
                for k, v in existing_data_val.items()
                if k not in ["id", "created", "updated", "pid"]
            }
            new_data_val = {
                k: v
                for k, v in new_data_val.items()
                if k not in ["id", "created", "updated", "pid"]
            }
        for key, value in new_data_val.items():
            changed_field_paths.extend(
                get_changed_fields(
                    (
                        existing_data_val.get(key)
                        if isinstance(existing_data_val, dict)
                        else None
                    ),
                    value,
                    separator=separator,
                    current_field_path=separator.join([
                        p for p in [current_field_path, str(key)] if p
                    ]),
                )
            )
        # Check for keys in existing_data that are missing from new_data
        for key in existing_data_val.keys():
            if key not in new_data_val:
                changed_field_paths.append(
                    separator.join([p for p in [current_field_path, str(key)] if p])
                )
    elif (
        isinstance(new_data_val, list)
        or isinstance(new_data_val, tuple)
        or isinstance(new_data_val, set)
    ):
        for index, value in enumerate(new_data_val):
            try:
                existing_value = (
                    list(existing_data_val)[index]
                    if isinstance(existing_data_val, list | tuple | set)
                    else None
                )
            except IndexError:
                existing_value = None
            changed_field_paths.extend(
                get_changed_fields(
                    existing_value,
                    value,
                    separator=separator,
                    current_field_path=separator.join([
                        p for p in [current_field_path, str(index)] if p
                    ]),
                )
            )
        # handle the case where the existing data is longer than the new data
        for index in (
            range(len(existing_data_val) - len(new_data_val))
            if isinstance(existing_data_val, list)
            else []
        ):
            changed_field_paths.append(
                separator.join([
                    p for p in [current_field_path, str(index + len(new_data_val))] if p
                ])
            )
    else:
        if existing_data_val != new_data_val:
            changed_field_paths.append(current_field_path)
    return list(set(changed_field_paths))


def get_value_by_path(data: dict[str, Any], path: str, separator: str = ".") -> Any:
    """Get a value from a nested dictionary using a path string.

    Parameters:
        data: The dictionary to search. The dictionary may include nested
            dictionaries and lists.
        path: The path string to search for. The path string is a dot-separated list
            of keys. If one of the keys is a digit, it will be treated as an
            integer index in a list.
        separator: The separator to use between segments in the path.

    Raises a KeyError if the path is not found.

    Returns:
        Any: The value at the end of the path.
    """
    path_segments = path.split(separator)
    result: Any = data
    for key in path_segments:
        if isinstance(result, dict):
            result = result.get(key)
        elif isinstance(result, list) and result is not None:
            try:
                result = result[int(key)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return result


def matching_list_parts_skip_digits(listA: list, listB: list) -> list:
    """Check if the lists begin with a matching set of elements, ignoring digits.

    Parameters:
        listA: The list to check.
        listB: The list to compare to.

    Returns:
        The list of elements that match the restricted parts.
        If the lists do not match, returns an empty list.

    Note:
        Assumes that listB may pack digit elements that listA has, as when listB
        is a field path that omits indices for list fields. ListA is expected to
        have the indices.
    """
    i = j = 0
    while i < len(listA) and j < len(listB):
        # If restricted part is a digit, it must match exactly
        if listB[j].isdigit():
            if not listA[i].isdigit() or listA[i] != listB[j]:
                return []
            i += 1
            j += 1
        # If changed part is a digit but restricted isn't, skip the digit
        elif listA[i].isdigit():
            i += 1
        # Otherwise compare the parts normally
        else:
            if listA[i] != listB[j]:
                return []
            i += 1
            j += 1
    # Make sure we've used all restricted parts
    if j == len(listB):
        return listA[:i]
    else:
        return []
