def safe_cast(value, to_type):
    """
    Safely cast a value to a specified type, returning None if the cast fails.

    Args:
        value: The value to cast
        to_type: The type to cast to (int, float, str, etc.)

    Returns:
        The cast value or None if casting fails or is empty/whitespace string
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return None
