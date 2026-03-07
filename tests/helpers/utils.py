"""Utility functions for tests."""

import json
from typing import Any, cast

from bs4 import BeautifulSoup
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


def extract_json_from_html_attribute(
    rendered: str, attribute_name: str
) -> dict[str, Any] | None:
    r"""Extract and parse JSON from an HTML data attribute.

    This function parses HTML using BeautifulSoup, finds an element with the
    specified attribute, extracts its value, and parses it as JSON. It handles
    HTML entity unescaping and various edge cases.

    Usage example:
        >>> html = '<div data-config=\'{"key": "value"}\'></div>'
        >>> extract_json_from_html_attribute(html, "data-config")
        {'key': 'value'}

    Args:
        rendered: The rendered HTML string
        attribute_name: The name of the data attribute (e.g., "data-community")

    Returns:
        dict: The parsed JSON object, or None if the value is "None"

    Raises:
        AssertionError: If the attribute is not found or JSON cannot be parsed
    """
    soup = BeautifulSoup(rendered, "html.parser")
    element = soup.find(attrs={attribute_name: True})
    assert element is not None, (
        f"Could not find element with {attribute_name} attribute"
    )
    assert hasattr(element, "get"), (
        f"Element found but is not a Tag: {type(element)}"
    )

    # Get the attribute value (BeautifulSoup handles HTML entity unescaping)
    attr_value = element.get(attribute_name)
    # Handle case where attribute might be a list
    if isinstance(attr_value, list):
        json_str = attr_value[0] if attr_value else None
    else:
        json_str = attr_value

    # Handle the case where it might be "None" as a string
    if json_str == "None" or json_str is None:
        return None

    # Ensure we have a string
    if not isinstance(json_str, str):
        raise AssertionError(
            f"Expected string value for {attribute_name}, got {type(json_str)}"
        )

    try:
        parsed = json.loads(json_str)
        # Type check: ensure it's a dict
        if not isinstance(parsed, dict):
            raise AssertionError(
                f"Expected dict from {attribute_name}, got {type(parsed)}"
            )
        return cast(dict[str, Any], parsed)
    except json.JSONDecodeError as e:
        # If parsing fails, provide helpful error message
        raise AssertionError(
            f"Failed to parse JSON from {attribute_name}: "
            f"{json_str[:200]}... Error: {e}"
        ) from e
