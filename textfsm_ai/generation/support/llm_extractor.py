# textfsm_ai/generation/engine/llm_extractor.py


from textfsm_ai.generation.core.models import LLMRawResponse
from textfsm_ai.orchestrator.provider import Provider


def extract(provider: Provider, model: str, prompt: str) -> LLMRawResponse:
    try:
        raw = provider.generate_sync(prompt, model=model) or {}
        if raw:
            return LLMRawResponse(raw=raw, ready=True)
        return LLMRawResponse(
            raw=raw, reason="received an empty LLM response", ready=False
        )
    except Exception as ex:
        return LLMRawResponse(raw={}, reason=f"{type(ex).__name__}: {ex}", ready=False)
