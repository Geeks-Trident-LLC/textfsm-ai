# textfsm_ai/dsl/tokenclass.py

from .charclass import is_digit, is_letter, is_non_ws, is_punct, is_space


def token_is_space(tok: str) -> bool:
    return tok != "" and all(is_space(c) for c in tok)


def token_is_digit(tok: str) -> bool:
    return tok != "" and all(is_digit(c) for c in tok)


def token_is_letter(tok: str) -> bool:
    return tok != "" and all(is_letter(c) for c in tok)


def token_is_alnum(tok: str) -> bool:
    return tok != "" and all(c.isalnum() for c in tok)


def token_is_punct(tok: str) -> bool:
    return tok != "" and all(is_punct(c) for c in tok)


def token_is_non_ws(tok: str) -> bool:
    return tok != "" and all(is_non_ws(c) for c in tok)


def token_is_word(tok: str) -> bool:
    # word: alnum + underscore, must contain ≥1 letter
    if tok == "":
        return False
    if not all(c.isalnum() or c == "_" for c in tok):
        return False
    return any(is_letter(c) for c in tok)


def token_is_mixed_word(tok: str) -> bool:
    # mixed-word: alnum + punct, must contain ≥1 alnum
    if tok == "":
        return False
    if not all(c.isalnum() or is_punct(c) for c in tok):
        return False
    return any(c.isalnum() for c in tok)


def token_is_number(tok: str) -> bool:
    if tok == "":
        return False
    try:
        float(tok)
        return True
    except ValueError:
        return False


def token_is_mixed_number(tok: str) -> bool:
    if tok == "":
        return False
    if token_is_number(tok):
        return False
    if not any(is_digit(c) for c in tok):
        return False
    if not any(not is_digit(c) for c in tok):
        return False
    return True
