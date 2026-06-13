from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..core.modes import DeliveryMode
from ..core.package import (
    DeliveryDebug,
    DeliveryExplanation,
    DeliveryGeneral,
    DeliveryPackage,
    DeliveryStatus,
    DeliveryTemplate,
    DeliveryUsage,
)


def build_delivery_package(
    *,
    mode: DeliveryMode,
    textfsm_version: str,
    textfsm_ai_version: str,
    model: str,
    canonical_template: str,
    human_template_dsl: str,
    status_state: str,
    status_warnings: Optional[List[str]] = None,
    status_errors: Optional[List[str]] = None,
    explanation_variable_definitions: Optional[str] = None,
    explanation_llm_parsing: Optional[str] = None,
    explanation_template_generation: Optional[str] = None,
    usage_input_tokens: Optional[int] = None,
    usage_output_tokens: Optional[int] = None,
    usage_estimated_cost: Optional[float] = None,
    usage_duration_ms: Optional[int] = None,
    debug_raw_llm_output: Optional[str] = None,
    debug_cleaned_template: Optional[str] = None,
    debug_canonical_template_internal: Optional[str] = None,
    debug_machine_dsl: Optional[Dict[str, Any]] = None,
    debug_human_template_dsl_internal: Optional[str] = None,
    debug_recognizer_dsl: Optional[List[str]] = None,
    debug_validation_log: Optional[List[str]] = None,
    debug_canonicalization_log: Optional[List[str]] = None,
    debug_literal_regex_trace: Optional[List[str]] = None,
) -> DeliveryPackage:
    created_at = datetime.now(timezone.utc).isoformat()

    general = None
    explanation = None
    usage = None
    debug = None

    template = DeliveryTemplate(
        canonical_template=canonical_template,
        human_template_dsl=human_template_dsl,
    )

    status = DeliveryStatus(
        state=status_state,
        warnings=status_warnings or [],
        errors=status_errors or [],
    )

    if mode in ("default", "info", "debug"):
        general = DeliveryGeneral(
            textfsm_version=textfsm_version,
            textfsm_ai_version=textfsm_ai_version,
            model=model,
            created_at=created_at,
        )

    if mode in ("default", "info", "debug"):
        explanation = DeliveryExplanation(
            variable_definitions=explanation_variable_definitions or "",
            llm_parsing_explanation=explanation_llm_parsing or "",
            template_generation_explanation=explanation_template_generation or "",
        )

    if mode in ("info", "debug") and usage_input_tokens is not None:
        usage = DeliveryUsage(
            input_tokens=usage_input_tokens,
            output_tokens=usage_output_tokens or 0,
            total_tokens=(usage_input_tokens + (usage_output_tokens or 0)),
            estimated_cost=usage_estimated_cost,
            duration_ms=usage_duration_ms,
        )

    if mode == "debug":
        debug = DeliveryDebug(
            raw_llm_output=debug_raw_llm_output,
            cleaned_template=debug_cleaned_template,
            canonical_template_internal=debug_canonical_template_internal,
            machine_dsl=debug_machine_dsl,
            human_template_dsl_internal=debug_human_template_dsl_internal,
            recognizer_dsl=debug_recognizer_dsl,
            validation_log=debug_validation_log,
            canonicalization_log=debug_canonicalization_log,
            literal_regex_trace=debug_literal_regex_trace,
        )

    return DeliveryPackage(
        mode=mode,
        general=general,
        template=template,
        explanation=explanation,
        status=status,
        usage=usage,
        debug=debug,
    )
