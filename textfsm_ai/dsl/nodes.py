# textfsm_ai/dsl/nodes.py

import re

from textfsm_ai.dsl.patterns import PATTERNS


class BaseNode:
    name: str  # keyword name, e.g. "mixed-word", "digits", "puncts"

    def to_regex(self, include_var: bool = False) -> str:
        raise NotImplementedError

    def to_expression(self) -> str:
        raise NotImplementedError

    def to_expression_regex(self) -> str:
        return self.to_regex(include_var=False)

    def __str__(self):
        return self.to_expression()


class LiteralNode(BaseNode):
    def __init__(self, text: str):
        self.text = text
        self.name = "literal"  # or None if you prefer
        self.regex = re.escape(self.text)

    def to_regex(self, include_var: bool = False) -> str:
        return re.escape(self.text)

    def to_expression(self) -> str:
        return self.text


class KeywordNode(BaseNode):
    def __init__(self, keyword: str, generalize: bool = False):
        self.keyword = keyword
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self) -> str:
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"
        if self.keyword == "space":
            return "spaces"

        return self.keyword

    def to_regex(self, include_var: bool = False) -> str:
        return self.regex

    def to_expression(self) -> str:
        return f"{self.name}()"


class VariableKeywordNode(BaseNode):
    def __init__(self, keyword: str, varname: str, generalize: bool = False):
        self.keyword = keyword
        self.varname = varname
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self) -> str:
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"
        if self.keyword == "space":
            return "spaces"

        return self.keyword

    def to_regex(self, include_var: bool = False) -> str:
        if include_var:
            # Named group for TextFSM compatibility
            return f"(?P<{self.varname}>{self.regex})"
        return self.regex

    def to_expression(self) -> str:
        return f"{self.name}(var-{self.varname})"

    def to_expression_regex(self) -> str:
        # Expression regex should NOT include named groups
        return self.regex
