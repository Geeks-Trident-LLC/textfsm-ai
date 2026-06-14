# textfsm_ai/generation/engine/one_pass.py

from textfsm_ai.generation.core.models import OnePassResult
from textfsm_ai.generation.support import extractor, llm_extractor, prompt_builder
from textfsm_ai.providers.registry import get_provider_for_model


def run(api_key: str, model: str, sample: str) -> OnePassResult:
    provider = get_provider_for_model(model)(api_key, model)

    # Build prompt
    prompt = prompt_builder.PromptBuilder().one_pass_prompt(sample)

    # LLM call
    response = llm_extractor.extract(provider, model, prompt)

    # Wrap raw LLM run result (old extractor)
    llm_run = extractor.extract(
        provider_name=provider.name,
        model=model,
        sample=sample,
        prompt=prompt,
        response=response,
    )

    # Convert to new dataclass
    return OnePassResult(
        prompt=prompt,
        response=response,
        model=model,
        provider=provider.name,
        metadata={"llm_run": llm_run},
    )
