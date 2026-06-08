# textfsm_ai/dsl/nodes.py


class BaseNode:
    generalize: bool = False

    def to_expression(self) -> str:
        raise NotImplementedError

    def __str__(self):
        return self.to_expression()


class LiteralNode(BaseNode):
    def __init__(self, text: str):
        self.text = text

    def to_expression(self) -> str:
        return self.text


class KeywordNode(BaseNode):
    def __init__(self, keyword: str, generalize: bool = False):
        self.keyword = keyword
        self.generalize = generalize

    def _generalized_keyword(self) -> str:
        if not self.generalize:
            return self.keyword

        # singular → plural mapping
        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"
        if self.keyword == "space":
            return "spaces"

        # default: unchanged
        return self.keyword

    def to_expression(self) -> str:
        return f"{self._generalized_keyword()}()"


class VariableKeywordNode(BaseNode):
    def __init__(self, keyword: str, varname: str, generalize: bool = False):
        self.keyword = keyword
        self.varname = varname
        self.generalize = generalize

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

    def to_expression(self) -> str:
        return f"{self._generalized_keyword()}(var-{self.varname})"
