# textfsm_ai/dsl/engine/render/recognizer.py

from __future__ import annotations

import re
from typing import List

from textfsm_ai.dsl.ast.nodes import TemplateAST


def render_recognizer(ast: TemplateAST) -> List[str]:
    parts: List[str] = []

    for state in ast.states:
        for rule in state.rules:
            pat = "".join(item.regex for item in rule.pattern.items)
            re.compile(pat)
            if pat not in parts:
                parts.append(pat)

    return parts
