# textfsm_ai/provider_ping.py

from textfsm_ai.api import ask_ai


def ping_provider(provider: str, model: str, api_key: str) -> None:
    """
    Send a tiny 'ping' request through the router to validate provider + key.
    """
    ask_ai("ping", provider=provider, model=model, api_key=api_key)


PING_MAP = {
    "openai": ping_provider,
    "anthropic": ping_provider,
    "gemini": ping_provider,
    "deepseek": ping_provider,
}
