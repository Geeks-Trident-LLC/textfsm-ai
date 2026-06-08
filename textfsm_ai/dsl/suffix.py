# textfsm_ai/dsl/suffix.py


def parse_suffix(keyword: str):
    if keyword.endswith("-group"):
        return keyword[:-6], True
    if keyword.endswith("-item"):
        return keyword[:-5], False
    return keyword, False
