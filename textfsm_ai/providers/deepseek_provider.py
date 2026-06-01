# textfsm_ai/providers/deepseek_provider.py

import os
from typing import Any

import click
from openai import APIError, OpenAI  # DeepSeek uses the openai SDK


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self, api_key: str | None = None, model: str = ""):
        self._client = OpenAI(
            api_key=api_key or os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self._default_model = model

    def send(self, prompt: str, **kwargs: Any) -> str:
        model = kwargs.get("model", self._default_model)

        try:
            resp = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1024),
            )
        except APIError as e:
            raise click.ClickException(f"[ERROR] DeepSeek request failed: {e}") from e

        return resp.choices[0].message.content


def list_deepseek_models(api_key: str) -> list[str]:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    models = client.models.list()
    return [m.id for m in models.data]
