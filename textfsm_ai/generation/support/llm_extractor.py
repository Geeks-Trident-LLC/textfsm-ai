# textfsm_ai/generation/engine/llm_extractor.py


import anyask

from textfsm_ai.generation.core.models import LLMRawResponse


def extract(provider_name: str, model: str, prompt: str, **kwargs) -> LLMRawResponse:
    """
    Call `provider_name`'s `model` via `anyask.ask()` and normalize the
    result into the dict-shaped `LLMRawResponse.raw` this module has
    always produced, so downstream code (extractor.py) needs no changes.

    Any failure - unknown provider, missing credentials, a provider SDK
    error, network failure - surfaces as `anyask`'s exception types
    (`ProviderNotFoundError`/`ProviderAuthError`/`ProviderError`, all
    subclassing `Exception`) and is caught here.
    """

    try:
        response = anyask.ask(prompt, provider=provider_name, model=model, **kwargs)
    except Exception as ex:
        return LLMRawResponse(
            raw={},
            reason=f"{type(ex).__name__}: {ex}",
            ready=False,
        )

    content = response.content

    if content is None or content == "":
        return LLMRawResponse(
            raw={"content": content, "raw": response.raw},
            reason="provider returned response without content",
            ready=False,
        )

    return LLMRawResponse(
        raw={
            "content": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "raw": response.raw,
        },
        ready=True,
    )
