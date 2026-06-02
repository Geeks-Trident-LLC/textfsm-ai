# textfsm_ai/orchestrator/hooks.py
from __future__ import annotations

from typing import Protocol, List, Dict, Any

from .types import OrchestratorRequest, OrchestratorResponse


class PreHook(Protocol):
    def __call__(self, request: OrchestratorRequest) -> OrchestratorRequest:
        ...


class PostHook(Protocol):
    def __call__(self, response: OrchestratorResponse) -> OrchestratorResponse:
        ...


class TraceHook(Protocol):
    def __call__(self, event: str, payload: Dict[str, Any]) -> None:
        ...


def apply_pre_hooks(
    request: OrchestratorRequest,
    hooks: List[PreHook],
) -> OrchestratorRequest:
    for hook in hooks:
        request = hook(request)
    return request


def apply_post_hooks(
    response: OrchestratorResponse,
    hooks: List[PostHook],
) -> OrchestratorResponse:
    for hook in hooks:
        response = hook(response)
    return response


def apply_trace(
    hooks: List[TraceHook],
    event: str,
    payload: Dict[str, Any],
) -> None:
    for hook in hooks:
        hook(event, payload)
