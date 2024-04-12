def update_nested_dict(starting_dict, updates):
    """Update a nested dictionary with another dictionary."""
    for key, value in updates.items():
        if isinstance(value, dict):
            starting_dict[key] = update_nested_dict(
                starting_dict.get(key, {}), value
            )
        else:
            starting_dict[key] = value
    return starting_dict
