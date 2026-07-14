# textfsm_ai/generation/engine/generation_engine.py


from textfsm_ai.generation.core.models import GenerationStage
from textfsm_ai.generation.support import (
    extractor,
    generator,
    prompt_builder,
    structured_extractor,
    validator,
)
from textfsm_ai.providers.registry import get_provider_by_name


def run(
    provider_name: str,
    api_key: str,
    model: str,
    sample: str,
    endpoint: str = "",
    api_version: str = "",
    region: str = "",
    project: str = "",
    compartment_id: str = "",
    **kwargs,
):
    provider_type = get_provider_by_name(provider_name)
    if provider_type.name == "azure":
        deployment = model
        provider = provider_type(api_key, endpoint, api_version, deployment)
    elif provider_type.name == "bedrock":
        provider = provider_type(region, model)
    elif provider_type.name == "vertexai":
        provider = provider_type(project, region, model)
    elif provider_type.name == "oci":
        provider = provider_type(compartment_id, region, model)
    else:
        provider = provider_type(api_key, model)

    # Build prompt
    prompt = prompt_builder.PromptBuilder().base_prompt(sample)

    response = extractor.extract(
        provider=provider, model=model, prompt=prompt, **kwargs
    )
    structured = structured_extractor.extract(response)
    result = generator.generate(structured)
    result.name = "generate-using-base-prompt"
    return result


def run_correction_prompt(
    provider_name: str,
    api_key: str,
    model: str,
    sample: str,
    prev_result: GenerationStage,
    endpoint: str = "",
    api_version: str = "",
    region: str = "",
    project: str = "",
    compartment_id: str = "",
    **kwargs,
):
    provider_type = get_provider_by_name(provider_name)
    if provider_type.name == "azure":
        provider = provider_type(api_key, endpoint, api_version, model)
    elif provider_type.name == "bedrock":
        provider = provider_type(region, model)
    elif provider_type.name == "vertexai":
        provider = provider_type(project, region, model)
    elif provider_type.name == "oci":
        provider = provider_type(compartment_id, region, model)
    else:
        provider = provider_type(api_key, model)

    metadata = prev_result.metadata

    prev_response = metadata.response.content if metadata else ""
    template = metadata.template if metadata else ""
    records = metadata.records if metadata else []

    findings = validator.find_template_issues(template, records, sample)

    # Build prompt
    prompt = prompt_builder.PromptBuilder().correction_prompt(
        sample, prev_response, findings.findings
    )

    response = extractor.extract(
        provider=provider, model=model, prompt=prompt, **kwargs
    )
    structured = structured_extractor.extract(response)
    result = generator.generate(structured)
    result.name = "generate-using-correction-prompt"
    return result
