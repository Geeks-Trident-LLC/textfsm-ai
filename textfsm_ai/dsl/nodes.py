# textfsm_ai/dsl/nodes.py


class BaseNode:
    name: str  # keyword name, e.g. "mixed-word", "digits", "puncts"

    def to_expression(self) -> str:
        raise NotImplementedError

    def __str__(self):
        return self.to_expression()


class LiteralNode(BaseNode):
    def __init__(self, text: str):
        self.text = text
        self.name = "literal"  # or None if you prefer

    def to_expression(self) -> str:
        return self.text


class KeywordNode(BaseNode):
    def __init__(self, keyword: str, generalize: bool = False):
        self.keyword = keyword
        self.generalize = generalize
        self.name = self._generalized_keyword()

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
        return f"{self.name}()"


class VariableKeywordNode(BaseNode):
    def __init__(self, keyword: str, varname: str, generalize: bool = False):
        self.keyword = keyword
        self.varname = varname
        self.generalize = generalize
        self.name = self._generalized_keyword()

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
        return f"{self.name}(var-{self.varname})"
