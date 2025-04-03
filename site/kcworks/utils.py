from functools import reduce
from pprint import pformat
from flask import current_app
from invenio_accounts.models import User
from typing import Optional, Union, Any
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.records.systemfields.access.field.record import RecordAccess


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


def get_commons_user_from_contributor(contributor: dict) -> str:
    """Get the Commons username from a contributor dict.

    If one can't be found, return an empty string.
    """
    id = ""
    if contributor["person_or_org"].get("identifiers"):
        for identifier in contributor["person_or_org"]["identifiers"]:
            if identifier["scheme"] in ["hc_username", "kc_username"]:
                id = identifier["identifier"]
    # FIXME: get the username from the email?
    # FIXME: get the username from orcid?
    # FIXME: add a field to the contributor model for the kc_username?
    return id


# FIXME: implement
def get_user_by_commons_username(commons_username: str) -> Optional[User]:
    """Get a kcworks user by their Commons username based on saml login."""
    return None


def get_kcworks_user_from_contributor(contributor: dict) -> Optional[User]:
    """Get the KCWorks user from a contributor dict.

    If one can't be found, return None.
    """
    user = None
    commons_user = get_commons_user_from_contributor(contributor)
    if commons_user:
        user = get_user_by_commons_username(commons_user)
    else:
        orcid = [
            i
            for i in contributor["person_or_org"].get("identifiers", [])
            if i["scheme"] == "orcid"
        ]
        # FIXME: get the user by orcid
    return user


def get_changed_fields(
    existing_data: Union[
        dict, RDMDraft, RDMRecord, list, tuple, set, str, int, float, bool, None
    ],
    new_data: Union[
        dict, RDMRecord, RDMDraft, list, tuple, set, str, int, float, bool, None
    ],
    separator: str = ".",
    current_field_path: str = "",
) -> list:
    """
    Get the fields that have been changed in the new version of a metadata record.

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

    Returns a list of field paths that have been changed.
    """
    changed_field_paths = []
    if isinstance(existing_data, RDMDraft) or isinstance(existing_data, RDMRecord):
        existing_data_dict = {"metadata": existing_data.metadata}
        if hasattr(existing_data, "custom_fields"):
            existing_data_dict["custom_fields"] = existing_data.custom_fields
        if hasattr(existing_data, "access"):
            if isinstance(existing_data.access, RecordAccess):
                existing_data_dict["access"] = existing_data.access.dump()
            else:
                existing_data_dict["access"] = existing_data.access
        current_app.logger.info(f"Existing data: {pformat(existing_data_dict)}")
        existing_data = existing_data_dict

    if isinstance(new_data, RDMDraft) or isinstance(new_data, RDMRecord):
        new_data_dict = {"metadata": new_data.metadata}
        if hasattr(new_data, "custom_fields"):
            new_data_dict["custom_fields"] = new_data.custom_fields
        if hasattr(new_data, "access"):
            new_data_dict["access"] = new_data.access
        current_app.logger.info(f"New data: {pformat(new_data_dict)}")
        new_data = new_data_dict

    if not existing_data and current_field_path:
        return [current_field_path]
    if isinstance(new_data, dict) and isinstance(existing_data, dict):
        if not current_field_path:
            existing_data = {
                k: v
                for k, v in existing_data.items()
                if k not in ["id", "created", "updated", "pid"]
            }
            new_data = {
                k: v
                for k, v in new_data.items()
                if k not in ["id", "created", "updated", "pid"]
            }
        for key, value in new_data.items():
            changed_field_paths.extend(
                get_changed_fields(
                    existing_data.get(key) if isinstance(existing_data, dict) else None,
                    value,
                    separator=separator,
                    current_field_path=separator.join(
                        [p for p in [current_field_path, str(key)] if p]
                    ),
                )
            )
        # Check for keys in existing_data that are missing from new_data
        for key, value in existing_data.items():
            if key not in new_data:
                changed_field_paths.append(
                    separator.join([p for p in [current_field_path, str(key)] if p])
                )
    elif (
        isinstance(new_data, list)
        or isinstance(new_data, tuple)
        or isinstance(new_data, set)
    ):
        for index, value in enumerate(new_data):
            changed_field_paths.extend(
                get_changed_fields(
                    existing_data[index] if isinstance(existing_data, list) else None,
                    value,
                    separator=separator,
                    current_field_path=separator.join(
                        [p for p in [current_field_path, str(index)] if p]
                    ),
                )
            )
        # handle the case where the existing data is longer than the new data
        for index, value in enumerate(existing_data[len(new_data) :]):
            changed_field_paths.append(
                separator.join(
                    [p for p in [current_field_path, str(index + len(new_data))] if p]
                )
            )
    else:
        if existing_data != new_data:
            changed_field_paths.append(current_field_path)
    return list(set(changed_field_paths))


def get_value_by_path(data: dict, path: str, separator: str = ".") -> Any:
    """
    Get a value from a dictionary by a path string.

    Parameters:
        data: The dictionary to search.
        path: The path string to search for.
        separator: The separator to use between segments in the path.

    The path string is a dot-separated list of keys. The dictionary may include nested
    dictionaries and lists. If one of the keys is an integer, it will be treated as an
    integer index in a list.

    raises a KeyError if the path is not found.

    Returns the value at the end of the path.

    """
    path_segments = path.split(separator)
    return reduce(
        lambda d, key: d.get(key) if isinstance(d, dict) else d[int(key)],
        path_segments,
        data,
    )


def matching_list_parts_skip_digits(listA: list, listB: list) -> list:
    """
    Check if the lists begin with a matching set of elements, ignoring digits.

    Assumes that listB may lack digit elements that listA has, as when listB
    is a field path that omits indices for list fields. ListA is expected to
    have the indices.

    Returns the list of elements that match the restricted parts.
    If the lists do not match, returns an empty list.
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
