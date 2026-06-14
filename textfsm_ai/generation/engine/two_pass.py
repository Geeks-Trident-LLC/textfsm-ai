# textfsm_ai/generation/engine/two_pass.py

from textfsm_ai.generation.core.models import TwoPassResult
from textfsm_ai.generation.support import extractor, llm_extractor, prompt_builder
from textfsm_ai.providers.registry import get_provider_for_model


def run(api_key: str, model: str, sample: str) -> TwoPassResult:
    provider = get_provider_for_model(model)(api_key, model)
    builder = prompt_builder.PromptBuilder()

    # -------------------------
    # PASS 1 — Free Generation
    # -------------------------
    prompt_free = builder.two_pass_prompt_a(sample)
    response_free = llm_extractor.extract(provider, model, prompt_free)

    llm_run = extractor.extract(
        provider_name=provider.name,
        model=model,
        sample=sample,
        prompt=prompt_free,
        response=response_free,
    )

    # -------------------------
    # PASS 2 — Structured Extraction
    # -------------------------
    prompt_structured = builder.two_pass_prompt_b(response_free)
    response_structured = llm_extractor.extract(provider, model, prompt_structured)

    extractor.next_extract(
        llm_run_result=llm_run,
        prompt=prompt_structured,
        response=response_structured,
    )

    # -------------------------
    # Wrap in new dataclass
    # -------------------------
    return TwoPassResult(
        prompt_free=prompt_free,
        response_free=response_free,
        prompt_structured=prompt_structured,
        response_structured=response_structured,
        model=model,
        provider=provider.name,
        metadata={"llm_run": llm_run},
    )
