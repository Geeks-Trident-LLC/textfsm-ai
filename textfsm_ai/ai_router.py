# textfsm_ai/ai_router.py

from .providers.claude_provider import ClaudeProvider
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
            "claude": ClaudeProvider,
            "deepseek": DeepSeekProvider,
        }

        self._providers = {}

    def send(self, prompt, provider, model, api_key, **kwargs):
        if provider not in self._providers:
            self._providers[provider] = self._provider_classes[provider](
                api_key=api_key
            )

        return self._providers[provider].send(prompt, model=model, **kwargs)


# Singleton-ish convenience
_router: AIRouter | None = None


def get_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
