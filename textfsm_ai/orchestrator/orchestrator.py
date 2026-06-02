# textfsm_ai/orchestrator/orchestrator.py
from __future__ import annotations

import time
from typing import Dict, Iterable, List, Optional

from .errors import (
    ProviderError,
    ProviderNotFoundError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from .hooks import (
    PostHook,
    PreHook,
    TraceHook,
    apply_post_hooks,
    apply_pre_hooks,
    apply_trace,
)
from .provider import Provider
from .routing import RoutingTable
from .types import OrchestratorRequest, OrchestratorResponse


class Orchestrator:
    """
    High-level AI orchestration engine with retry and fallback.
    """

    def __init__(
        self,
        providers: Iterable[Provider],
        routing_table: RoutingTable,
        pre_hooks: Optional[List[PreHook]] = None,
        post_hooks: Optional[List[PostHook]] = None,
        trace_hooks: Optional[List[TraceHook]] = None,
        max_retries: int = 2,
        backoff_base_seconds: float = 0.5,
    ) -> None:
        self._providers: Dict[str, Provider] = {p.name: p for p in providers}
        self._routing_table = routing_table
        self._pre_hooks = pre_hooks or []
        self._post_hooks = post_hooks or []
        self._trace_hooks = trace_hooks or []
        self._max_retries = max_retries
        self._backoff_base_seconds = backoff_base_seconds

    # ---------- internal helpers ----------

    def _trace(self, event: str, payload: dict) -> None:
        apply_trace(self._trace_hooks, event, payload)

    def _call_with_retry(
        self,
        provider: Provider,
        request: OrchestratorRequest,
        *,
        async_mode: bool = False,
    ):
        """
        Retry on transient provider errors (rate limit, timeout).
        """
        attempts = self._max_retries + 1

        for attempt in range(1, attempts + 1):
            self._trace(
                "provider.attempt",
                {
                    "provider": provider.name,
                    "model": request.model,
                    "attempt": attempt,
                    "max_attempts": attempts,
                    "async": async_mode,
                },
            )
            try:
                if async_mode:
                    # async path handled by caller
                    raise RuntimeError("async path must call _call_with_retry_async")
                return provider.generate(
                    prompt=request.prompt,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
            except (ProviderRateLimitError, ProviderTimeoutError) as exc:
                if attempt >= attempts:
                    self._trace(
                        "provider.retry_exhausted",
                        {"provider": provider.name, "error": type(exc).__name__},
                    )
                    raise
                delay = self._backoff_base_seconds * attempt
                self._trace(
                    "provider.retry_scheduled",
                    {
                        "provider": provider.name,
                        "delay": delay,
                        "error": type(exc).__name__,
                    },
                )
                time.sleep(delay)
            except Exception as exc:
                # non-transient provider error
                self._trace(
                    "provider.error",
                    {"provider": provider.name, "error": type(exc).__name__},
                )
                raise ProviderError(f"Provider {provider.name} failed") from exc

    async def _call_with_retry_async(
        self,
        provider: Provider,
        request: OrchestratorRequest,
    ):
        import asyncio

        attempts = self._max_retries + 1

        for attempt in range(1, attempts + 1):
            self._trace(
                "provider.attempt",
                {
                    "provider": provider.name,
                    "model": request.model,
                    "attempt": attempt,
                    "max_attempts": attempts,
                    "async": True,
                },
            )
            try:
                return await provider.generate_async(
                    prompt=request.prompt,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
            except (ProviderRateLimitError, ProviderTimeoutError) as exc:
                if attempt >= attempts:
                    self._trace(
                        "provider.retry_exhausted",
                        {"provider": provider.name, "error": type(exc).__name__},
                    )
                    raise
                delay = self._backoff_base_seconds * attempt
                self._trace(
                    "provider.retry_scheduled",
                    {
                        "provider": provider.name,
                        "delay": delay,
                        "error": type(exc).__name__,
                    },
                )
                await asyncio.sleep(delay)
            except Exception as exc:
                self._trace(
                    "provider.error",
                    {"provider": provider.name, "error": type(exc).__name__},
                )
                raise ProviderError(f"Provider {provider.name} failed (async)") from exc

    def _call_with_fallback(
        self,
        request: OrchestratorRequest,
        *,
        async_mode: bool = False,
    ):
        """
        Try primary provider, then fallback provider if configured.
        """
        primary = self._routing_table.select_provider(request, self._providers)
        self._trace(
            "routing.primary",
            {"provider": primary.name, "model": request.model},
        )

        try:
            if async_mode:
                raise RuntimeError("async path must call _call_with_fallback_async")
            raw = self._call_with_retry(primary, request, async_mode=False)
            return primary, raw
        except ProviderError as exc:
            self._trace(
                "routing.primary_failed",
                {"provider": primary.name, "error": type(exc).__name__},
            )
            fallback = self._routing_table.select_fallback_provider(
                request, self._providers, primary
            )
            if fallback is None:
                raise

            self._trace(
                "routing.fallback",
                {"provider": fallback.name, "model": request.model},
            )
            raw = self._call_with_retry(fallback, request, async_mode=False)
            return fallback, raw

    async def _call_with_fallback_async(
        self,
        request: OrchestratorRequest,
    ):
        primary = self._routing_table.select_provider(request, self._providers)
        self._trace(
            "routing.primary",
            {"provider": primary.name, "model": request.model},
        )

        try:
            raw = await self._call_with_retry_async(primary, request)
            return primary, raw
        except ProviderError as exc:
            self._trace(
                "routing.primary_failed",
                {"provider": primary.name, "error": type(exc).__name__},
            )
            fallback = self._routing_table.select_fallback_provider(
                request, self._providers, primary
            )
            if fallback is None:
                raise

            self._trace(
                "routing.fallback",
                {"provider": fallback.name, "model": request.model},
            )
            raw = await self._call_with_retry_async(fallback, request)
            return fallback, raw

    # ---------- public sync API ----------

    def run(self, request: OrchestratorRequest) -> OrchestratorResponse:
        self._trace("request.start", {"model": request.model})

        request = apply_pre_hooks(request, self._pre_hooks)

        try:
            provider, raw = self._call_with_fallback(request, async_mode=False)
        except ProviderNotFoundError:
            self._trace("routing.not_found", {"model": request.model})
            raise

        response = OrchestratorResponse(
            provider=provider.name,
            model=request.model,
            content=raw.get("content", ""),
            raw=raw,
        )

        response = apply_post_hooks(response, self._post_hooks)
        self._trace("response.end", {"provider": provider.name, "model": request.model})
        return response

    # ---------- public async API ----------

    async def run_async(self, request: OrchestratorRequest) -> OrchestratorResponse:
        self._trace("request.start", {"model": request.model, "async": True})

        request = apply_pre_hooks(request, self._pre_hooks)

        try:
            provider, raw = await self._call_with_fallback_async(request)
        except ProviderNotFoundError:
            self._trace("routing.not_found", {"model": request.model, "async": True})
            raise

        response = OrchestratorResponse(
            provider=provider.name,
            model=request.model,
            content=raw.get("content", ""),
            raw=raw,
        )

        response = apply_post_hooks(response, self._post_hooks)
        self._trace(
            "response.end",
            {"provider": provider.name, "model": request.model, "async": True},
        )
        return response
