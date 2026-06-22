# textfsm_ai/generation/engine/generation_engine.py


from textfsm_ai.generation.core.models import GenerationStage
from textfsm_ai.generation.support import (
    extractor,
    generator,
    prompt_builder,
    structured_extractor,
    validator,
)
from textfsm_ai.providers.registry import get_provider_for_model


def run(api_key: str, model: str, sample: str):
    provider = get_provider_for_model(model)(api_key, model)

    # Build prompt
    prompt = prompt_builder.PromptBuilder().base_prompt(sample)

    response = extractor.extract(
        provider=provider,
        model=model,
        prompt=prompt,
    )
    structured = structured_extractor.extract(response)
    result = generator.generate(structured)
    result.name = "generate-using-base-prompt"
    return result


def run_correction_prompt(
    api_key: str, model: str, sample: str, prev_result: GenerationStage
):
    provider = get_provider_for_model(model)(api_key, model)

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
        provider=provider,
        model=model,
        prompt=prompt,
    )
    structured = structured_extractor.extract(response)
    result = generator.generate(structured)
    result.name = "generate-using-correction-prompt"
    return result
