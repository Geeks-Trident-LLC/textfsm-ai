def mask_middle(
    value: str,
    side_len: int = 4,
    mask_char: str = "x",
    min_visible: int = 2,
) -> str:
    """
    Mask the middle portion of a string while preserving the left and right sides.

    Rules:
    - If the string is too short (<= min_visible), mask the entire string.
    - If we can preserve `side_len` characters on both sides, do so.
    - Otherwise, preserve only `min_visible` characters on both sides.
    """
    total = len(value)

    # Entire string masked if too short
    if total <= min_visible:
        return mask_char * total

    # Ideal case: enough length to keep both sides fully
    if side_len * 2 + min_visible <= total:
        left = side_len
        middle = total - side_len * 2
        return value[:left] + mask_char * middle + value[-left:]

    # Fallback: preserve only minimal visible characters on both sides
    left = (total - min_visible) // 2
    middle = total - left * 2
    return value[:left] + mask_char * middle + value[-left:]


def format_block_title(
    text: str,
    bar_char: str = "=",
    ended: bool = False,
    width: int = 4,
) -> str:
    """Return a formatted block title with optional END marker."""
    width = max(width, 2)
    bar = bar_char * width

    if ended:
        return f"{bar} END {text} {bar}"
    return f"{bar} {text} {bar}"
