# textfsm_ai/provider_ping.py

from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.deepseek_provider import DeepSeekProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider


def ping_openai(api_key: str, model: str):
    client = OpenAIProvider(api_key=api_key, model=model)
    client.send("ping", model=model)


def ping_deepseek(api_key: str, model: str):
    client = DeepSeekProvider(api_key=api_key, model=model)
    client.send("ping", model=model)


def ping_anthropic(api_key: str, model: str):
    client = AnthropicProvider(api_key=api_key, model=model)
    client.send("ping", model=model)


def ping_gemini(api_key: str, model: str):
    client = GeminiProvider(api_key=api_key, model=model)
    client.send("ping", model=model)


PING_MAP = {
    "openai": ping_openai,
    "deepseek": ping_deepseek,
    "anthropic": ping_anthropic,
    "gemini": ping_gemini,
}
