# textfsm_ai/dsl/charclass.py


def is_space(ch: str) -> bool:
    return ch.isspace()


def is_digit(ch: str) -> bool:
    return ch.isdigit()


def is_letter(ch: str) -> bool:
    return ch.isalpha()


def is_punct(ch: str) -> bool:
    # punctuation = not alnum and not space
    return not ch.isalnum() and not ch.isspace()


def is_non_ws(ch: str) -> bool:
    return not ch.isspace()
