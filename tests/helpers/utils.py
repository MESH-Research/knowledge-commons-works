"""Utility functions for tests."""

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
