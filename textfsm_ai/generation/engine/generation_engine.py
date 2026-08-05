# textfsm_ai/generation/engine/generation_engine.py


from textfsm_ai.generation.core.models import GenerationStage
from textfsm_ai.generation.support import (
    extractor,
    generator,
    prompt_builder,
    structured_extractor,
    validator,
)


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
    # Build prompt
    prompt = prompt_builder.PromptBuilder().base_prompt(sample)

    response = extractor.extract(
        provider_name,
        model=model,
        prompt=prompt,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
        deployment=model,
        region=region,
        project=project,
        compartment_id=compartment_id,
        **kwargs,
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
        provider_name,
        model=model,
        prompt=prompt,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
        deployment=model,
        region=region,
        project=project,
        compartment_id=compartment_id,
        **kwargs,
    )
    structured = structured_extractor.extract(response)
    result = generator.generate(structured)
    result.name = "generate-using-correction-prompt"
    return result
