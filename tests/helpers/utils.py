"""Utility functions for tests."""

from typing import Any

from invenio_records.dictutils import parse_lookup_key


def remove_value_by_path(d: dict, path: str) -> dict:
    """Remove a value from a nested dictionary based on a dot-separated path string.

    Usage example:
    >>> d = {"a": {"b": {"c": 1}}}
    >>> remove_value_by_path(d, "a.b.c")
    {'a': {'b': {}}}

    :param d: The dictionary to modify
    :param path: The dot-separated path string to the value
    :return: The modified dictionary
    """
    keys = parse_lookup_key(path)
    if not keys:
        return d

    if len(keys) == 1:
        d.pop(keys[0], None)
        return d

    if keys[0] not in d:
        return d

    d[keys[0]] = remove_value_by_path(d[keys[0]], ".".join(keys[1:]))
    return d


def replace_value_in_nested_dict(d: dict, path: str, new_value: Any) -> dict | bool:
    """Replace a value in a nested dictionary based on a bar-separated path string.

    Numbers in the path are treated as list indices.

    Usage examples:

    >>> replace_value_in_nested_dict({"a": {"b": {"c": 1}}}, "a|b|c", 2)
    {'a': {'b': {'c': 2}}}

    >>> e = {"a": {"b": [{"c": 1}, {"d": 2}]}}
    >>> replace_value_in_nested_dict(e, "a|b|1|c", 3)
    {'a': {'b': [{'c': 1}, {'d': 2, 'c': 3}]}}

    >>> f = {"a": {"b": [{"c": 1}, {"d": 2}]}}
    >>> replace_value_in_nested_dict(f, "a|b", {"e": 3})
    {'a': {'b': {'e': 3}}}

    :param d: The dictionary or list to update.
    :param path: The bar-separated path string to the value.
    :param new_value: The new value to set.

    returns: dict: The updated dictionary.
    """
    keys = path.split("|")
    current = d
    for i, key in enumerate(keys):
        if i == len(keys) - 1:  # If this is the last key
            if key.isdigit() and isinstance(current, list):  # Handle list index
                current[int(key)] = new_value
            else:  # Handle dictionary key
                current[key] = new_value
        else:
            if key.isdigit():  # Next level is a list
                key = int(key)  # Convert to integer for list access
                if not isinstance(current, list) or key >= len(current):
                    # If current is not a list or index is out of bounds
                    return False
                current = current[key]
            else:  # Next level is a dictionary
                if isinstance(current, dict) and key not in current:
                    # Add new dictionary or list at this level to hold deeper keys
                    if keys[i + 1].isdigit():
                        current[key] = []
                    else:
                        current[key] = {}
                elif not isinstance(current[key], dict | list):
                    # If key not found or next level is not a dict/list
                    return False
                current = current[key]
    return d
