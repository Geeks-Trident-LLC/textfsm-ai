# textfsm_ai/api.py
from typing import Any

from .ai_router import get_router
from .providers import AIResponse


def ask_ai(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
    **kwargs: Any,
) -> AIResponse:
    """
    High-level API to send a prompt to an AI provider and get a normalized response.
    """
    router = get_router()
    return router.send(prompt, provider=provider, model=model, **kwargs)
