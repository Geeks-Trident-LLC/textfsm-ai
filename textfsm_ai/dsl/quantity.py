# textfsm_ai/dsl/quantity.py

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
}


def parse_quantity(part: str):
    """
    Returns (min_count, max_count) or (None, None)
    """
    part = part.lower()

    # range: 2-to-3
    if "-to-" in part:
        left, right = part.split("-to-", 1)
        return _parse_num(left), _parse_num(right)

    # exact: 3 or three
    n = _parse_num(part)
    if n is not None:
        return n, n

    return None, None


def _parse_num(s: str):
    if s.isdigit():
        return int(s)
    return NUMBER_WORDS.get(s)
