# textfsm_ai/generation/engine/two_pass.py

from textfsm_ai.generation.support import prompt_builder
from textfsm_ai.providers.registry import get_provider_for_model

from ..support import extractor, llm_extractor


def run(api_key: str, model: str, sample: str):
    provider = get_provider_for_model(model)(api_key, model)
    builder = prompt_builder.PromptBuilder()

    # PASS 1 — Free Generation
    prompt1 = builder.two_pass_prompt_a(sample)
    response1 = llm_extractor.extract(provider, model, prompt1)

    # Wrap first pass result
    llm_run_result = extractor.extract(
        provider_name=provider.name,
        model=model,
        sample=sample,
        prompt=prompt1,
        response=response1,
    )

    # PASS 2 — Structured Extraction
    prompt2 = builder.two_pass_prompt_b(response1)
    response2 = llm_extractor.extract(provider, model, prompt2)

    # Attach second pass result
    extractor.next_extract(
        llm_run_result=llm_run_result,
        prompt=prompt2,
        response=response2,
    )

    return llm_run_result
