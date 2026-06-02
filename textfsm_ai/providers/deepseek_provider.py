# textfsm_ai/providers/deepseek_provider.py

import os
from typing import Any, Optional

import click
from openai import APIError, OpenAI  # DeepSeek uses the openai SDK


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self._client = OpenAI(
            api_key=api_key or os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self._default_model = model

    def send(self, prompt: str, lang: str = "en", **kwargs: Any) -> str:
        """
        Send a prompt to DeepSeek with language control.
        Default language is English.
        """
        model = kwargs.get("model", self._default_model)

        # Language‑aware system prompt
        system_prompt = {
            "en": "You are an English-only assistant. Always respond in English.",
            "zh": "你是一个中文助手。请始终使用中文回答。",
            "vi": "Bạn là trợ lý chỉ dùng tiếng Việt. Hãy luôn trả "
            "lời bằng tiếng Việt.",
        }.get(lang, "You are an English-only assistant. Always respond in English.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            resp = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1024),
            )
        except APIError as e:
            raise click.ClickException(f"[ERROR] DeepSeek request failed: {e}") from e

        return resp.choices[0].message.content


def list_deepseek_models(api_key: str) -> list[str]:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    models = client.models.list()
    return [m.id for m in models.data]
