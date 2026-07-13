"""Public Python API: sample -> template, records, ast, canonical/readable DSL."""

from __future__ import annotations

from typing import Dict, List

from textfsm_ai.api_models import DSLResult, LLMResult
from textfsm_ai.core.utils.template import (  # noqa: F401
    parse_to_dicts,
    parse_to_lists,
    validate_template,
)
from textfsm_ai.delivery.controller.controller import DeliveryController
from textfsm_ai.delivery.core.package import DeliveryOutput
from textfsm_ai.dsl.ast.nodes import TemplateAST
from textfsm_ai.dsl.engine import dsl_engine
from textfsm_ai.generation.controller.generation_controller import GenerationController

__all__ = [
    "DSLResult",
    "LLMResult",
    "compile_dsl",
    "generate",
    "parse_to_dicts",
    "parse_to_lists",
    "run_pipeline",
    "to_ast",
    "to_canonical",
    "to_dsl_result",
    "to_llm_handling",
    "to_llm_records",
    "to_llm_result",
    "to_llm_template",
    "to_llm_variables",
    "to_readable",
    "to_recognizers",
    "validate_template",
]


# ------------------------------------------------------------
# LLM generation step — sample -> template + records + variables + handling
#
# generate() is the verb_target: always returns the full LLMResult,
# `.ready`/`.reason` populated whether it succeeded or not, never raises.
#
# to_llm_*() are the to_target shortcuts: same parameters as generate().
# On failure, string-typed shortcuts (to_llm_template) return `.reason`;
# all others return an empty instance of their type. to_llm_result() is the
# one exception — it's just an alias for generate(), always the full object.
# ------------------------------------------------------------
def generate(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> LLMResult:
    """
    Ask an LLM to turn a sample into a template, parsed records, variable
    explanations, and handling notes. Never raises.
    """
    pipeline = GenerationController(
        provider_name=provider,
        api_key=api_key,
        model=model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
    ).run(sample, **kwargs)

    metadata = pipeline.last_stage.metadata if pipeline.last_stage else None

    return LLMResult(
        template=metadata.template if metadata else "",
        records=metadata.records if metadata else [],
        variables=metadata.variables if metadata else {},
        handling=metadata.handling if metadata else [],
        reason=pipeline.reason,
        ready=pipeline.ready,
    )


def to_llm_result(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> LLMResult:
    """Alias of generate() — the full LLM result object."""
    return generate(
        sample,
        provider,
        api_key,
        model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
        **kwargs,
    )


def to_llm_template(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> str:
    """LLM template string, or the failure reason if generation didn't succeed."""
    result = to_llm_result(
        sample,
        provider,
        api_key,
        model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
        **kwargs,
    )
    return result.template if result.ready else result.reason


def to_llm_records(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> List[Dict[str, str]]:
    """LLM-parsed records, or [] if generation didn't succeed."""
    result = to_llm_result(
        sample,
        provider,
        api_key,
        model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
        **kwargs,
    )
    return result.records if result.ready else []


def to_llm_variables(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> Dict[str, str]:
    """LLM variable explanations, or {} if generation didn't succeed."""
    result = to_llm_result(
        sample,
        provider,
        api_key,
        model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
        **kwargs,
    )
    return result.variables if result.ready else {}


def to_llm_handling(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    max_retries: int = 1,
    **kwargs,
) -> List[str]:
    """LLM handling notes, or [] if generation didn't succeed."""
    result = to_llm_result(
        sample,
        provider,
        api_key,
        model,
        endpoint=endpoint,
        api_version=api_version,
        max_retries=max_retries,
        **kwargs,
    )
    return result.handling if result.ready else []


# ------------------------------------------------------------
# DSL compile step — template + records -> ast/canonical/readable/recognizers
#
# compile_dsl() is the verb_target: always returns the full DSLResult.
# to_*() are the to_target shortcuts: same parameters as compile_dsl().
# ------------------------------------------------------------
def compile_dsl(template: str, records: List[Dict[str, str]]) -> DSLResult:
    """
    Compile a template into its ast, canonical template, readable DSL, and
    recognizers. Never raises.
    """
    result = dsl_engine.run(template, records)

    return DSLResult(
        ast=result.ast or TemplateAST(),
        canonical=result.canonical or "",
        readable=result.readable or "",
        recognizers=result.recognizers or [],
        reason=result.reason or "",
        ready=result.ready,
    )


def to_dsl_result(template: str, records: List[Dict[str, str]]) -> DSLResult:
    """Alias of compile_dsl() — the full DSL result object."""
    return compile_dsl(template, records)


def to_ast(template: str, records: List[Dict[str, str]]) -> TemplateAST:
    """AST, or an empty TemplateAST() if the template failed to compile."""
    result = to_dsl_result(template, records)
    return result.ast if result.ready else TemplateAST()


def to_canonical(template: str, records: List[Dict[str, str]]) -> str:
    """Canonical TextFSM template string, or the failure reason if compiling failed."""
    result = to_dsl_result(template, records)
    return result.canonical if result.ready else result.reason


def to_readable(template: str, records: List[Dict[str, str]]) -> str:
    """Human-readable DSL string, or the failure reason if compiling didn't succeed."""
    result = to_dsl_result(template, records)
    return result.readable if result.ready else result.reason


def to_recognizers(template: str, records: List[Dict[str, str]]) -> List[str]:
    """Recognizer regex patterns, or [] if compiling didn't succeed."""
    result = to_dsl_result(template, records)
    return result.recognizers if result.ready else []


# ------------------------------------------------------------
# End-to-end pipeline — sample -> everything, packaged
# ------------------------------------------------------------
def run_pipeline(
    sample: str,
    provider: str,
    api_key: str,
    model: str,
    *,
    endpoint: str = "",
    api_version: str = "",
    mode: str = "default",
    as_json: bool = False,
    max_tries: int = 1,
) -> DeliveryOutput:
    """
    Full pipeline: sample -> template, records, ast, canonical, readable,
    recognizers — packaged per `mode` ("quiet"/"default"/"info"/"debug").

    Never raises for a failed run: check `.passed`/`.error` on the result.
    """
    return DeliveryController(
        provider_name=provider,
        api_key=api_key,
        model=model,
        endpoint=endpoint,
        api_version=api_version,
        max_tries=max_tries,
    ).run(sample, mode=mode, as_json=as_json)
