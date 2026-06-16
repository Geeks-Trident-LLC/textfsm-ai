# textfsm_ai/delivery/assembly/builder.py

from datetime import datetime, timezone

from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.generation.core.models import GenerationResult

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
    generation: GenerationResult,
    canonical: CanonicalTemplate,
    machine_dsl: MachineDSL,
    human_dsl: HumanDSL,
    recognizer: RecognizerPatterns,
    duration_ms: int = 0,
) -> DeliveryPackage:

    created_at = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------
    # Template + Status (always included)
    # ------------------------------------------------------------
    template = DeliveryTemplate(
        canonical_template=canonical.template,
        human_template_dsl=human_dsl.dsl_text,
    )

    status = DeliveryStatus(
        state=generation.status,
        warnings="",
        errors="",
        # warnings=_or_empty(status_warnings, []),
        # errors=_or_empty(status_errors, []),
    )

    general = None
    explanation = None
    usage = None
    debug = None

    # ------------------------------------------------------------
    # DEFAULT, INFO, DEBUG
    # ------------------------------------------------------------
    if mode >= DeliveryMode.DEFAULT:
        import textfsm

        import textfsm_ai

        general = DeliveryGeneral(
            textfsm_version=textfsm.__version__,
            textfsm_ai_version=textfsm_ai.__version__,
            model=model,
            created_at=created_at,
        )

        explanation = DeliveryExplanation(
            variable_definitions=_or_empty("", ""),
            llm_parsing_explanation=_or_empty("", ""),
            template_generation_explanation=_or_empty("", ""),
        )

    # ------------------------------------------------------------
    # INFO, DEBUG
    # ------------------------------------------------------------
    usage_input_tokens = None
    usage_output_tokens = None
    usage_estimated_cost = None
    usage_duration_ms = None
    if mode >= DeliveryMode.INFO and usage_input_tokens is not None:
        usage = DeliveryUsage(
            input_tokens=0,
            output_tokens=0 or 0,
            total_tokens=usage_input_tokens + (usage_output_tokens or 0),
            estimated_cost=usage_estimated_cost,
            duration_ms=usage_duration_ms,
        )

    # ------------------------------------------------------------
    # DEBUG
    # ------------------------------------------------------------
    if mode == DeliveryMode.DEBUG:
        debug = DeliveryDebug(
            raw_llm_output="",
            cleaned_template="",
            canonical_template_internal="",
            machine_dsl=_or_empty("", {}),
            human_template_dsl_internal="",
            recognizer_dsl=_or_empty("", []),
            validation_log=_or_empty("", []),
            canonicalization_log=_or_empty("", []),
            literal_regex_trace=_or_empty("", []),
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
