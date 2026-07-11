from .base import BaseNode
from .groups import KeywordGroup, keyword_group

# ------------------------------------------------------------
# Optional
# ------------------------------------------------------------


class OptionalNode(BaseNode):
    def __init__(self, keyword_node: BaseNode):
        self.keyword_node = keyword_node
        self.name = f"optional-{keyword_node.name}"

    def to_regex(self, include_var=False):
        base = self.keyword_node.to_regex(include_var)
        g = keyword_group(self.keyword_node.name)

        if g == KeywordGroup.ATOMIC:
            return f"{base}?"

        if g == KeywordGroup.ATOMIC_PLUS:
            return f"{base[:-1]}*"

        return f"(?:{base})?"

    def to_expression(self):
        return f"optional-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Maybe (alias for optional)
# ------------------------------------------------------------


class MaybeNode(OptionalNode):
    def __init__(self, keyword_node: BaseNode):
        super().__init__(keyword_node)
        self.name = f"maybe-{keyword_node.name}"

    def to_expression(self):
        return f"maybe-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Negative Lookahead
# ------------------------------------------------------------


class NotNode(BaseNode):
    def __init__(self, keyword_node: BaseNode):
        self.keyword_node = keyword_node
        self.name = f"not-{keyword_node.name}"

    def to_regex(self, include_var=False):
        return f"(?!{self.keyword_node.to_regex(include_var)})"

    def to_expression(self):
        return f"not-{self.keyword_node.to_expression()}"
