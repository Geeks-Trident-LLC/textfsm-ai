from textfsm_ai.config_loader import load_config
from textfsm_ai.providers.openai_provider import OpenAIProvider
from textfsm_ai.providers.claude_provider import ClaudeProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.deepseek_provider import DeepSeekProvider


class MultiProviderRouter:
    def __init__(self):
        cfg = load_config()

        p = cfg["providers"]

        self.openai = OpenAIProvider(
            p["openai"]["api_key"],
            p["openai"]["model"],
            p["openai"]["daily_limit"],
            p["openai"]["monthly_limit"],
        )

        self.claude = ClaudeProvider(
            p["claude"]["api_key"],
            p["claude"]["model"],
            p["claude"]["daily_limit"],
            p["claude"]["monthly_limit"],
        )

        self.gemini = GeminiProvider(
            p["gemini"]["api_key"],
            p["gemini"]["model"],
            p["gemini"]["daily_limit"],
            p["gemini"]["monthly_limit"],
        )

        self.deepseek = DeepSeekProvider(
            p["deepseek"]["api_key"],
            p["deepseek"]["model"],
            p["deepseek"]["daily_limit"],
            p["deepseek"]["monthly_limit"],
        )

        self.providers = [
            self.gemini,
            self.deepseek,
            self.openai,
            self.claude,
            self.local,
        ]

    def generate(self, prompt: str) -> str:
        for provider in self.providers:
            try:
                return provider.generate(prompt)
            except Exception:
                continue

        raise RuntimeError("All providers failed")
