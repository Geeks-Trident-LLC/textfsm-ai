# textfsm_ai/dsl/engine/dsl_engine.py

from typing import Dict, List

from textfsm_ai.dsl.ast.parser import parse_textfsm
from textfsm_ai.dsl.core.models import DSLParseResult
from textfsm_ai.dsl.engine.render.readable import render_readable
from textfsm_ai.dsl.engine.render.recognizer import render_recognizer
from textfsm_ai.dsl.engine.render.template import render_template


def run(raw_template: str, records: List[Dict[str, str]]) -> DSLParseResult:
    result = DSLParseResult(
        raw_template=raw_template,
        records=records,
        ready=False,
    )
    sep = "----------------------"
    # ------------------------------------------------------------
    # Stage 1: Build AST
    # ------------------------------------------------------------
    try:
        result.name = "build-ast"
        ast = parse_textfsm(raw_template, records)
        result.ast = ast
    except Exception as ex:
        result.reason = f"BUILD-AST-ERROR\n{sep}\n{type(ex).__name__}: {ex}"
        return result

    # ------------------------------------------------------------
    # Stage 2: Canonical template
    # ------------------------------------------------------------
    try:
        result.name = "render-canonical-template"
        result.canonical = render_template(result.ast, canonicalized=True)
    except Exception as ex:
        result.reason = f"RENDER-CANONICAL-ERROR\n{sep}\n{type(ex).__name__}: {ex}"
        return result

    # ------------------------------------------------------------
    # Stage 3: Readable DSL
    # ------------------------------------------------------------
    try:
        result.name = "render-readable-dsl"
        result.readable = render_readable(result.ast)
    except Exception as ex:
        result.reason = f"RENDER-READABLE-ERROR\n{sep}\n{type(ex).__name__}: {ex}"
        return result

    # ------------------------------------------------------------
    # Stage 4: Recognizer patterns
    # ------------------------------------------------------------
    try:
        result.name = "render-recognizer-patterns"
        result.recognizers = render_recognizer(result.ast)
    except Exception as ex:
        result.reason = f"RENDER-RECOGNIZER-ERROR\n{sep}\n{type(ex).__name__}: {ex}"
        return result

    # ------------------------------------------------------------
    # Success
    # ------------------------------------------------------------
    result.ready = True
    return result
