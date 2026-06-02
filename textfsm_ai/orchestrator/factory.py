# textfsm_ai/orchestrator/factory.py
from __future__ import annotations

from typing import List, Optional

from .orchestrator import Orchestrator
from .routing import RoutingTable, RoutingRule
from .hooks import PreHook, PostHook, TraceHook
from .provider import Provider


def create_default_routing_table() -> RoutingTable:
    rules = [
        RoutingRule(model_prefix="openai/", provider_name="openai"),
        RoutingRule(model_prefix="azure/", provider_name="azure_openai"),
    ]
    return RoutingTable(rules=rules)


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
