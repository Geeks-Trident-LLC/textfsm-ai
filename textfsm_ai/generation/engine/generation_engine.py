# textfsm_ai/generation/engine/generation_engine.py

from textfsm_ai.generation.core.models import GenerationResult
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
    return generator.generate(structured)


def run_correction_prompt(
    api_key: str, model: str, sample: str, prev_result: GenerationResult
):
    provider = get_provider_for_model(model)(api_key, model)

    prev_response = prev_result.metadata.response.content
    template = prev_result.metadata.template
    records = prev_result.metadata.records

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
    return generator.generate(structured)
