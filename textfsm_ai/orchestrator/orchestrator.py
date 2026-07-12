# textfsm_ai/orchestrator/orchestrator.py

from __future__ import annotations

import asyncio
from typing import Dict, Optional

from .errors import ProviderRateLimitError, ProviderTimeoutError
from .provider import Provider
from .routing import RoutingTable
from .types import OrchestratorRequest, OrchestratorResponse


class Orchestrator:
    def __init__(
        self,
        providers: Dict[str, Provider],
        routing_table: RoutingTable,
        max_retries: int = 1,
        retry_delay: float = 0.1,
    ) -> None:
        self._providers = providers
        self._routing_table = routing_table
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    async def run(self, req: OrchestratorRequest) -> OrchestratorResponse:
        """
        Async-first entrypoint: route the request, call the provider with retries,
        and wrap the provider's raw output into OrchestratorResponse.
        """
        provider_name = self._routing_table.route(req.model)
        primary = self._providers[provider_name]

        candidates: list[Provider] = [primary] + [
            p
            for name, p in self._providers.items()
            if name != provider_name and p.supports(req.model)
        ]

        last_exc: Optional[Exception] = None

        for provider in candidates:
            for attempt in range(self._max_retries + 1):
                try:
                    raw = await provider.generate(
                        req.prompt,
                        model=req.model,
                        temperature=req.temperature,
                        max_tokens=req.max_tokens,
                    )
                    return OrchestratorResponse(
                        provider=provider.name,
                        model=req.model,
                        raw=raw,
                    )
                except (ProviderRateLimitError, ProviderTimeoutError) as exc:
                    last_exc = exc
                    if attempt == self._max_retries:
                        break
                    await asyncio.sleep(self._retry_delay)
                except Exception as exc:
                    last_exc = exc
                    continue

        assert last_exc is not None
        raise last_exc
