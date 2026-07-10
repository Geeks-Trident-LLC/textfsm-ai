import re
from typing import Optional

from textfsm_ai.dsl.core.patterns import PATTERNS

from .base import BaseNode
from .groups import CUSTOM_KEYWORD_MAPPING

# ------------------------------------------------------------
# Literal
# ------------------------------------------------------------


class LiteralNode(BaseNode):
    def __init__(self, text: str):
        self.text = text
        self.name = "literal"
        self.regex = re.escape(self.text)

    def to_regex(self, include_var=False):
        return self.regex

    def to_expression(self):
        return self.text


# ------------------------------------------------------------
# Keyword
# ------------------------------------------------------------


class KeywordNode(BaseNode):
    def __init__(self, keyword: str, generalize: bool = False):
        self.keyword = keyword
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"

        return self.keyword

    def to_regex(self, include_var=False):
        return self.regex

    def to_expression(self):
        return f"{self.name}()"


# ------------------------------------------------------------
# Variable Keyword
# ------------------------------------------------------------


class VariableKeywordNode(BaseNode):
    def __init__(
        self, keyword: str, varname: str, extra: str = "", generalize: bool = False
    ):
        self.keyword = keyword
        self.varname = varname
        self.extra = extra
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"

        return self.keyword

    def to_regex(self, include_var=False):
        if include_var:
            return f"(?P<{self.varname}>{self.regex})"
        return self.regex

    def to_expression(self):
        if self.extra:
            return f"{self.name}(var-{self.varname}, options-{self.extra})"
        return f"{self.name}(var-{self.varname})"

    def to_expression_regex(self):
        return self.regex


def check_custom_keyword(keyword):
    return keyword in CUSTOM_KEYWORD_MAPPING


class CustomKeywordNode(BaseNode):
    def __init__(
        self,
        keyword: str,
        varname: Optional[str] = None,
        extra: str = "",
        generalize: bool = False,
    ):
        if not check_custom_keyword(keyword):
            custom_keywords = list(CUSTOM_KEYWORD_MAPPING)
            raise ValueError(
                f"Unknown custom keyword: {keyword}.  Must be {custom_keywords}"
            )
        self.keyword = keyword
        self.varname = varname
        self.extra = extra
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = CUSTOM_KEYWORD_MAPPING[self.name]

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "char":
            return "any"
        if self.keyword == "ws":
            return "wss"
        if self.keyword == "whitespace":
            return "whitespaces"

        return self.keyword

    def to_regex(self, include_var=False):
        if self.varname and include_var:
            return f"(?P<{self.varname}>{self.regex})"
        return self.regex

    def to_expression(self):
        if self.varname:
            if self.extra:
                return f"{self.name}(var-{self.varname}, options-{self.extra})"
            return f"{self.name}(var-{self.varname})"
        return f"{self.name}()"

    def to_expression_regex(self):
        return self.regex
