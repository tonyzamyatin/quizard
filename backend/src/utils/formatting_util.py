def format_num(number: int) -> str:
    """
    Formats an integer number with thousands separators.

    Parameters:
        number (int): The number to format.

    Returns:
        str: The formatted number with dot separators.
    """
    reversed_str = str(number)[::-1]
    formatted_str = '.'.join(reversed_str[i:i + 3] for i in range(0, len(reversed_str), 3))
    return formatted_str[::-1]


def inset_into_string(insert: str, target: str, position: int) -> str:
    """
    Inserts a string into a target string at a given position.

    Parameters:
        insert (str): The string to insert.
        target (str): The target string into which to insert.
        position (int): The position at which to insert the string. Bounds: -1 <= position <= len(target), where -1 is shorthand for appending.
    Returns:
        str: The combined string after insertion.

    Raises:
        ValueError: If the position is out of bounds of the target string.
    """
    if not (-1 <= position <= len(target)):
        raise ValueError(f"Position {position} is out of bounds for target string of length {len(target)}.")
    if position == -1:
        # Append the insert string to the end of the target string
        return target + insert
    else:
        # Insert the string at the specified position
        return target[:position] + insert + target[position:]
