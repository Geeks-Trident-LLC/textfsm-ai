# textfsm_ai/dsl/normalize.py

import re

from textfsm_ai.dsl.infer import infer_base_keyword
from textfsm_ai.dsl.nodes import BaseNode, create_node

VAR_PATTERN = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


class ExpressionNodeFactory:
    def __init__(self, var_samples=None, generalize=True):
        self.var_samples = var_samples or {}
        self.generalize = generalize

    def create(self, token: str) -> BaseNode:
        m = VAR_PATTERN.fullmatch(token)
        if m:
            varname = m.group(1)
            kw = self._infer_var_keyword(varname)
            return create_node(kw, varname, generalize=self.generalize)

        kw = infer_base_keyword([token])
        if kw is None:
            return create_node(token, literal=True)

        return create_node(kw, generalize=self.generalize)

    def _infer_var_keyword(self, varname: str) -> str:
        samples = self.var_samples.get(varname)
        if not samples:
            return "any"  # maps to r".*"
        kw = infer_base_keyword(samples)
        return kw or "any"


class ExpressionNormalizer:
    """
    Convert a line into a normalized DSL expression (string)
    by building node objects and rendering them.
    """

    def __init__(self, var_samples=None):
        self.factory = ExpressionNodeFactory(var_samples)

    def normalize(self, line: str) -> str:
        tokens = [t for t in line.split() if t]
        nodes = [self.factory.create(tok) for tok in tokens]
        return " ".join(str(n) for n in nodes)

    def normalize_to_nodes(self, line: str) -> list[BaseNode]:
        tokens = [t for t in line.split() if t]
        return [self.factory.create(tok) for tok in tokens]
