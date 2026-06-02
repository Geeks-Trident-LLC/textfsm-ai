# textfsm_ai/orchestrator/factory.py
from __future__ import annotations

from typing import List, Optional

from textfsm_ai.providers.config import OrchestratorConfig
from textfsm_ai.providers.factory import create_providers_from_config

from .hooks import PostHook, PreHook, TraceHook
from .orchestrator import Orchestrator
from .provider import Provider
from .routing import RoutingRule, RoutingTable


def create_default_routing_table() -> RoutingTable:
    rules = [
        RoutingRule(model_prefix="openai/", provider_name="openai"),
        RoutingRule(model_prefix="anthropic/", provider_name="anthropic"),
        RoutingRule(model_prefix="gemini/", provider_name="gemini"),
        RoutingRule(model_prefix="azure/", provider_name="azure"),
    ]
    return RoutingTable(rules=rules)


def create_orchestrator_from_config(
    config: OrchestratorConfig,
    pre_hooks: Optional[List[PreHook]] = None,
    post_hooks: Optional[List[PostHook]] = None,
    trace_hooks: Optional[List[TraceHook]] = None,
) -> Orchestrator:
    providers = create_providers_from_config(config)
    routing_table = create_default_routing_table()
    return Orchestrator(
        providers=providers,
        routing_table=routing_table,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        trace_hooks=trace_hooks,
    )


def create_orchestrator(
    providers: List[Provider],
    pre_hooks: Optional[List[PreHook]] = None,
    post_hooks: Optional[List[PostHook]] = None,
    trace_hooks: Optional[List[TraceHook]] = None,
) -> Orchestrator:
    routing_table = create_default_routing_table()
    return Orchestrator(
        providers=providers,
        routing_table=routing_table,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        trace_hooks=trace_hooks,
    )
