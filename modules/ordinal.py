#!/usr/bin/python3

def ordinal(value):
    """Adds a filter to Jinja2 for ordinal number representation.

    Args:
    - value: The number to be converted into an ordinal representation.

    Returns:
    - The value with the appropriate ordinal suffix:
    ('st', 'nd', 'rd', or 'th') appended.

    Notes:
    - The function checks for special cases (11, 12, 13) and appends 'th'.
    - For other cases, it determines the appropriate ordinal suffix based
    on the last digit.
    """
    if int(value) % 100 in (11, 12, 13):
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(int(value) % 10, 'th')
    return f"{value}{suffix}"
