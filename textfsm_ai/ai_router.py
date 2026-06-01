# textfsm_ai/ai_router.py
from typing import Any, Dict

from .config_loader import load_config
from .providers import AIResponse
from .providers.claude_provider import ClaudeProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider
from .quota_manager import QuotaManager


class AIRouter:
    def __init__(self):
        self._config = load_config()
        self._quota = QuotaManager()
        self._providers: Dict[str, Any] = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "claude": ClaudeProvider(),
            "deepseek": DeepSeekProvider(),
        }

    def send(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        if not self._quota.allow():
            raise RuntimeError("Quota exceeded")

        provider_name = provider or self._config.default_provider
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider_obj = self._providers[provider_name]

        model_name = (
            model
            or self._config.provider_model(provider_name)
            or self._config.default_model
        )

        return provider_obj.send(prompt, model=model_name, **kwargs)


# Singleton-ish convenience
_router: AIRouter | None = None


def get_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
