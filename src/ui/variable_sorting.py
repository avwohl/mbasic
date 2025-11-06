"""Common variable sorting logic for all UIs (Tk, Curses, Web).

This module provides consistent variable sorting behavior across all UI backends.
"""


def get_variable_sort_modes():
    """Get list of available sort modes with their definitions.

    Returns:
        list: List of dicts with keys:
            - 'key': Internal sort mode name
            - 'label': Display label for UI
            - 'default_reverse': Default sort direction for this mode
    """
    return [
        {'key': 'accessed', 'label': 'Last Accessed', 'default_reverse': True},
        {'key': 'written', 'label': 'Last Written', 'default_reverse': True},
        {'key': 'read', 'label': 'Last Read', 'default_reverse': True},
        {'key': 'name', 'label': 'Name', 'default_reverse': False},
    ]


def cycle_sort_mode(current_mode):
    """Get next sort mode in the cycle.

    The cycle order is: accessed -> written -> read -> name -> (back to accessed)
    This matches the Tk UI implementation.

    Args:
        current_mode: Current sort mode key

    Returns:
        str: Next mode key in cycle
    """
    cycle_order = ['accessed', 'written', 'read', 'name']

    try:
        current_idx = cycle_order.index(current_mode)
        next_idx = (current_idx + 1) % len(cycle_order)
        return cycle_order[next_idx]
    except ValueError:
        # If current mode not in cycle (e.g., 'type' or 'value'), default to 'accessed'
        return 'accessed'


def get_sort_key_function(sort_mode):
    """Get the sort key function for a given sort mode.

    Args:
        sort_mode: One of 'accessed', 'written', 'read', 'name'

    Returns:
        function: Sort key function that takes a variable dict
    """
    if sort_mode == 'name':
        return lambda v: v['name'].lower()

    elif sort_mode == 'accessed':
        # Sort by most recent access (read OR write)
        def accessed_key(v):
            read_ts = v['last_read']['timestamp'] if v.get('last_read') else 0
            write_ts = v['last_write']['timestamp'] if v.get('last_write') else 0
            return max(read_ts, write_ts)
        return accessed_key

    elif sort_mode == 'written':
        # Sort by most recent write
        return lambda v: v['last_write']['timestamp'] if v.get('last_write') else 0

    elif sort_mode == 'read':
        # Sort by most recent read
        return lambda v: v['last_read']['timestamp'] if v.get('last_read') else 0

    else:
        # Default to name sorting (unknown modes fall back to this)
        return lambda v: v['name'].lower()


def sort_variables(variables, sort_mode='accessed', reverse=True):
    """Sort variables list by specified mode.

    Args:
        variables: List of variable dicts from runtime.get_all_variables()
        sort_mode: One of 'accessed', 'written', 'read', 'name'
        reverse: If True, sort descending (default True for timestamp modes)

    Returns:
        list: Sorted copy of variables list
    """
    sort_key_func = get_sort_key_function(sort_mode)
    return sorted(variables, key=sort_key_func, reverse=reverse)


def get_sort_mode_label(sort_mode):
    """Get display label for a sort mode.

    Args:
        sort_mode: Sort mode key

    Returns:
        str: Display label for this mode
    """
    modes = get_variable_sort_modes()
    for mode in modes:
        if mode['key'] == sort_mode:
            return mode['label']
    return 'Unknown'


def get_default_reverse_for_mode(sort_mode):
    """Get the default reverse setting for a sort mode.

    Timestamp-based sorts default to reverse=True (newest first).
    Name/type/value sorts default to reverse=False (ascending).

    Args:
        sort_mode: Sort mode key

    Returns:
        bool: Default reverse setting
    """
    modes = get_variable_sort_modes()
    for mode in modes:
        if mode['key'] == sort_mode:
            return mode['default_reverse']
    return False
