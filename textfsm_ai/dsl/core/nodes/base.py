# ------------------------------------------------------------
# Base Node
# ------------------------------------------------------------


class BaseNode:
    name: str

    def to_regex(self, include_var: bool = False) -> str:
        raise NotImplementedError

    def to_expression(self) -> str:
        raise NotImplementedError

    def to_expression_regex(self) -> str:
        return self.to_regex(include_var=False)

    # def as_keyword_expression(self):
    #     return keyword_expression_from(self.to_expression())

    def __str__(self):
        return self.to_expression()
