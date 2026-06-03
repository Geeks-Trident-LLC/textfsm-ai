from __future__ import annotations

import httpx

from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.orchestrator.types import OrchestratorResponse


class AzureOpenAIProvider(Provider):
    name = "azure"

    def __init__(self, api_key: str, endpoint: str, model: str):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.model = model

    async def run(self, prompt: str, **kwargs) -> OrchestratorResponse:
        url = (
            f"{self.endpoint}/openai/deployments/"
            f"{self.model}/chat/completions?api-version=2024-02-15-preview"
        )

        payload = {
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"api-key": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return OrchestratorResponse(content=content)
