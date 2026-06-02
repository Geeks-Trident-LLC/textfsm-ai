from __future__ import annotations

from typing import Optional

import click

from textfsm_ai.providers.config import (
    load_config_from_file,
    load_config_from_env,
    OrchestratorConfig,
)
from textfsm_ai.orchestrator.factory import (
    create_orchestrator_from_config,
    create_default_routing_table,
)
from textfsm_ai.orchestrator.types import OrchestratorRequest


def _load_config(config_path: Optional[str]) -> OrchestratorConfig:
    if config_path:
        return load_config_from_file(config_path)
    return load_config_from_env()


@click.group(name="orchestrator")
def orchestrator_group() -> None:
    """Orchestrator-related commands."""
    return


@orchestrator_group.command("route")
@click.option(
    "--model", required=True, help="Model name, e.g. anthropic/claude-3-5-sonnet"
)
def orchestrator_route(model: str) -> None:
    """
    Show which provider the orchestrator would route a model to.
    """
    routing_table = create_default_routing_table()
    # dummy providers dict: only names matter for routing
    from textfsm_ai.orchestrator.provider import Provider

    class DummyProvider(Provider):
        def __init__(self, name: str) -> None:
            self.name = name

        def supports(self, model: str) -> bool:
            return True

        def generate(self, *args, **kwargs):
            raise NotImplementedError

        async def generate_async(self, *args, **kwargs):
            raise NotImplementedError

    providers = {
        "openai": DummyProvider("openai"),
        "anthropic": DummyProvider("anthropic"),
        "gemini": DummyProvider("gemini"),
        "azure": DummyProvider("azure"),
    }

    from textfsm_ai.orchestrator.types import OrchestratorRequest as OR

    req = OR(model=model, prompt="")
    provider = routing_table.select_provider(req, providers)
    click.echo(f"Model: {model}")
    click.echo(f"Routed provider: {provider.name}")


@orchestrator_group.command("run")
@click.option("--config", "config_path", type=click.Path(exists=True), required=False)
@click.option("--model", required=True, help="Model name, e.g. gemini/gemini-1.5-flash")
@click.option("--prompt", required=True, help="Prompt to send through the orchestrator")
def orchestrator_run(config_path: Optional[str], model: str, prompt: str) -> None:
    """
    Run a full orchestrator request and print the response.
    """
    cfg = _load_config(config_path)
    orch = create_orchestrator_from_config(cfg)

    req = OrchestratorRequest(model=model, prompt=prompt)
    resp = orch.run(req)

    click.echo(f"Provider: {resp.provider}")
    click.echo(f"Model: {resp.model}")
    click.echo("-" * 40)
    click.echo(resp.content)
