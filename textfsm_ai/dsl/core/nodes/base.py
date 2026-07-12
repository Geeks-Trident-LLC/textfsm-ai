# ------------------------------------------------------------
# Base Node
# ------------------------------------------------------------


class BaseNode:
    name: str

    def to_regex(self, include_var: bool = False) -> str:
        raise NotImplementedError

    def to_expression(self) -> str:
        raise NotImplementedError

    def __str__(self):
        return self.to_expression()
