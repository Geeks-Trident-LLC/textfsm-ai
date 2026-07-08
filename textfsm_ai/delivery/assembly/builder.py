# textfsm_ai/delivery/assembly/builder.py

from textfsm_ai.core.pricing import estimate_cost
from textfsm_ai.delivery.core.package import (
    Debug,
    Default,
    DeliveryPackage,
    Info,
    LLMInfo,
    LLMResponse,
    LLMStructuredResponse,
    Output,
    Quiet,
    Status,
    Usage,
    Version,
)
from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline


def build_delivery_package(
    *,
    model_info: dict,
    generation_pipeline: GenerationPipeline,
    dsl_pipeline: DSLPipeline,
    duration_ms: int = 0,
) -> DeliveryPackage:

    llm_info = LLMInfo(**model_info)

    gp_stage = generation_pipeline.last_stage
    metadata = getattr(gp_stage, "metadata", None)
    response = getattr(metadata, "response", None)

    llm_response = LLMResponse(
        max_retries=getattr(generation_pipeline, "max_retries", 1),
        duration_ms=getattr(response, "duration_ms", 0),
        raw=getattr(getattr(response, "raw", None), "raw", {}),
    )

    if not llm_info.model and llm_response.raw:
        raw = llm_response.raw.get("raw", None)
        if raw and getattr(raw, "model"):
            llm_info.model = raw.model

    llm_structured_response = LLMStructuredResponse(
        template=getattr(metadata, "template", ""),
        records=getattr(metadata, "records", []),
        variables=getattr(metadata, "variables", {}),
        handling=getattr(metadata, "handling", []),
    )

    input_tokens = getattr(response, "input_tokens", 0)
    output_tokens = getattr(response, "output_tokens", 0)
    total_tokens = getattr(response, "total_tokens", 0)
    cost_result = estimate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        currency="dollar",
        provider=llm_info.provider_name,
        model=llm_info.model,
    )

    usage = Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        llm_duration_ms=getattr(response, "duration_ms", 0),
        currency="dollar",
        input_per_million=cost_result.input_per_million,
        output_per_million=cost_result.output_per_million,
        estimated_cost=cost_result.estimated_cost,
        warning=cost_result.warning or "",
    )

    dsl = dsl_pipeline.dsl or None

    output = Output(
        raw_template=getattr(dsl, "raw_template", ""),
        template=dsl.canonical or "" if dsl else "",
        readable_dsl=getattr(dsl, "readable", ""),
        recognizers=getattr(dsl, "recognizers", []),
    )

    errors = []

    if dsl and dsl.reason:
        errors.append(dsl.reason)
    if gp_stage and gp_stage.reason:
        errors.append(gp_stage.reason)

    status = Status(
        state=dsl.name if dsl else gp_stage.name if gp_stage else "",
        errors=errors,
        passed=False if not dsl else dsl.ready,
    )

    quiet = Quiet(
        template=(
            dsl.canonical or dsl.raw_template
            if dsl
            else metadata.template if metadata else ""
        ),
        status=status,
    )

    default = Default(output=output, status=status)

    version = Version()

    info = Info(
        version=version,
        llm_info=llm_info,
        usage=usage,
        llm_structured_response=llm_structured_response,
        output=output,
        status=status,
    )

    debug = Debug(
        llm_info=llm_info,
        llm_response=llm_response,
        usage=usage,
        generation_pipeline=generation_pipeline,
        dsl_pipeline=dsl_pipeline,
        version=version,
        status=status,
        duration_ms=duration_ms,
    )

    return DeliveryPackage(
        quiet=quiet,
        default=default,
        info=info,
        debug=debug,
    )
