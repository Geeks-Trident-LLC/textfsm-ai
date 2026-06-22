# textfsm_ai/delivery/assembly/builder.py

from datetime import datetime, timezone
from typing import Optional

import textfsm

import textfsm_ai
from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.generation.core.models import GenerationStage

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


def _or_empty(value, default):
    return value if value is not None else default


def build_delivery_package(
    *,
    mode: DeliveryMode,
    model: str,
    generation: Optional[GenerationStage],
    canonical: Optional[CanonicalTemplate],
    machine_dsl: Optional[MachineDSL],
    human_dsl: Optional[HumanDSL],
    recognizer: Optional[RecognizerPatterns],
    state: str = "",
    reason: str = "",
    duration_ms: int = 0,
) -> DeliveryPackage:

    created_at = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------
    # Template + Status
    # ------------------------------------------------------------
    template = DeliveryTemplate(
        canonical_template=canonical.template if canonical else "",
        human_template_dsl=human_dsl.human_dsl if human_dsl else "",
    )

    status = DeliveryStatus(
        state=state,
        warnings=[],
        errors=[reason] if reason else [],
    )

    general: Optional[DeliveryGeneral] = None
    explanation: Optional[DeliveryExplanation] = None
    usage: Optional[DeliveryUsage] = None
    debug: Optional[DeliveryDebug] = None

    metadata = generation.metadata if generation else None

    # ------------------------------------------------------------
    # DEFAULT, INFO, DEBUG
    # ------------------------------------------------------------
    if mode >= DeliveryMode.DEFAULT:
        general = DeliveryGeneral(
            textfsm_version=textfsm.__version__,
            textfsm_ai_version=textfsm_ai.__version__,
            model=model,
            created_at=created_at,
        )

        explanation = DeliveryExplanation(
            variable_definitions=metadata.variables if metadata else {},
            llm_parsing_explanation=metadata.handling if metadata else [],
            template_generation_explanation=metadata.template if metadata else "",
        )

    # ------------------------------------------------------------
    # INFO, DEBUG
    # ------------------------------------------------------------
    if mode >= DeliveryMode.INFO:
        if metadata and metadata.response:
            input_tokens = metadata.response.input_tokens or 0
            output_tokens = metadata.response.output_tokens or 0
            total_tokens = metadata.response.total_tokens or 0
            llm_duration_ms = metadata.response.duration_ms or 0
        else:
            input_tokens = output_tokens = total_tokens = 0
            llm_duration_ms = 0

        usage = DeliveryUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            llm_duration_ms=llm_duration_ms,
            estimated_cost=None,
            duration_ms=duration_ms,
        )

    # ------------------------------------------------------------
    # DEBUG
    # ------------------------------------------------------------
    if mode == DeliveryMode.DEBUG:
        debug = DeliveryDebug(
            raw_llm_output=canonical.llm_template if canonical else "",
            cleaned_template="",
            canonical_template_internal=canonical.template if canonical else "",
            machine_dsl=machine_dsl.dsl if machine_dsl else None,
            human_template_dsl_internal=human_dsl.human_dsl if human_dsl else "",
            recognizer_pattern=recognizer.patterns if recognizer else "",
            validation_log=[],
            canonicalization_log=[],
            literal_regex_trace=[],
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
