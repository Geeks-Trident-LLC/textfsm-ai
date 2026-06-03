from __future__ import annotations

import httpx

from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.orchestrator.types import OrchestratorResponse


class OpenAICompatProvider(Provider):
    name = "openai_compat"

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def supports(self, model_name: str) -> bool:
        return model_name == self.model

    async def generate(self, prompt: str, **kwargs) -> OrchestratorResponse:
        return await self.run(prompt, **kwargs)

    async def run(self, prompt: str, **kwargs) -> OrchestratorResponse:
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]

        return OrchestratorResponse(
            content=content,
            provider=self.name,
            model=self.model,
            raw=data,
        )

