# textfsm_ai/generation/engine/extractor.py

import time
from datetime import datetime, timezone
from typing import Type

from textfsm_ai.generation.core.models import LLMResponse
from textfsm_ai.generation.support import llm_extractor
from textfsm_ai.orchestrator.provider import Provider


def extract(provider: Type[Provider], model: str, prompt: str) -> LLMResponse:
    sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    start = time.time()

    raw = llm_extractor.extract(provider, model=model, prompt=prompt)

    duration_ms = int((time.time() - start) * 1000)
    received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # If raw failed
    if not raw.ready:
        return LLMResponse(
            content="",
            prompt=prompt,
            provider=provider.name,
            model=model,
            duration_ms=duration_ms,
            sent_at=sent_at,
            received_at=received_at,
            raw=raw,
            reason=raw.reason,
            ready=False,
        )

    # Extract content
    content = raw.raw.get("content") or ""

    # Extract token usage
    usage = raw.raw.get("usage") or {}
    input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
    output_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
    total_tokens = usage.get("total_tokens")

    # Determine readiness
    is_ready = raw.ready and bool(content.strip())

    return LLMResponse(
        content=content,
        prompt=prompt,
        provider=provider.name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        duration_ms=duration_ms,
        sent_at=sent_at,
        received_at=received_at,
        raw=raw,
        reason="" if is_ready else "Received empty content from LLM",
        ready=is_ready,
    )
