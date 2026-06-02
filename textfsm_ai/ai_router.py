# textfsm_ai/ai_router.py

from typing import Optional

from .providers.anthropic_provider import AnthropicProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider
from .quota_manager import QuotaManager


class AIRouter:
    def __init__(self):
        self._config = None
        self._quota = QuotaManager()
        self._provider_classes = {
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider,
        }

        self._providers = {}

    def send(self, prompt, provider, model, api_key, lang="en", **kwargs):
        if provider not in self._providers:
            self._providers[provider] = self._provider_classes[provider](
                api_key=api_key,
                model=model,
            )

        return self._providers[provider].send(prompt, model=model, lang=lang, **kwargs)

    # Public API used by tests and by your CLI
    def ask(self, prompt, provider, model, api_key, lang="en", **kwargs):
        return self.send(prompt, provider, model, api_key, lang="en", **kwargs)


# Singleton-ish convenience
_router: Optional[AIRouter] = None


def get_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
