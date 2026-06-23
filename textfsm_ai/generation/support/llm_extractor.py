# textfsm_ai/generation/engine/llm_extractor.py


from textfsm_ai.generation.core.models import LLMRawResponse
from textfsm_ai.orchestrator.provider import Provider


def extract(provider: Provider, model: str, prompt: str, **kwargs) -> LLMRawResponse:
    """
    Robust LLM extractor that gracefully handles:
    - provider overload / busy / rate limit
    - network failures
    - malformed provider responses
    - missing content
    - provider-supplied error payloads
    """

    try:
        raw = provider.generate_sync(prompt, model=model, **kwargs)

        # Provider returned None or empty
        if not raw:
            return LLMRawResponse(
                raw={},
                reason="provider returned empty or null response",
                ready=False,
            )

        # Provider returned something non-dict (bad provider implementation)
        if not isinstance(raw, dict):
            return LLMRawResponse(
                raw={"raw": raw},
                reason=f"provider returned non-dict response: {type(raw).__name__}",
                ready=False,
            )

        # ---------------------------------------------------------
        # 1. Provider returned explicit error payload: {"error": {...}}
        # ---------------------------------------------------------
        if isinstance(raw.get("error"), dict):
            err = raw["error"]
            err_type = err.get("type", "unknown")
            err_msg = err.get("message", "no-message")
            return LLMRawResponse(
                raw=raw,
                reason=f"LLM-ERROR-{err_type}-{err_msg}",
                ready=False,
            )

        # ---------------------------------------------------------
        # 2. Provider returned raw response object containing error
        #    e.g. raw["raw"].error.type / raw["raw"].error.message
        # ---------------------------------------------------------
        raw_obj = raw.get("raw")
        if raw_obj is not None:
            err_obj = getattr(raw_obj, "error", None)
            if err_obj:
                err_type = getattr(err_obj, "type", "unknown")
                err_msg = getattr(err_obj, "message", "no-message")
                return LLMRawResponse(
                    raw=raw,
                    reason=f"LLM-ERROR-{err_type}-{err_msg}",
                    ready=False,
                )

        # ---------------------------------------------------------
        # 3. Missing or empty content
        # ---------------------------------------------------------
        content = raw.get("content")
        if content is None or content == "":
            return LLMRawResponse(
                raw=raw,
                reason="provider returned response without content",
                ready=False,
            )

        # ---------------------------------------------------------
        # 4. Success
        # ---------------------------------------------------------
        return LLMRawResponse(raw=raw, ready=True)

    except Exception as ex:
        # Catch-all for overload, busy, network, provider errors
        return LLMRawResponse(
            raw={},
            reason=f"{type(ex).__name__}: {ex}",
            ready=False,
        )
