from __future__ import annotations

import os
from typing import Optional

import click

from textfsm_ai.providers.registry import registry
from textfsm_ai.providers.config import (
    load_config_from_file,
    load_config_from_env,
    OrchestratorConfig,
)
from textfsm_ai.orchestrator.factory import create_orchestrator_from_config
from textfsm_ai.orchestrator.types import OrchestratorRequest


def _load_config(config_path: Optional[str]) -> OrchestratorConfig:
    if config_path:
        return load_config_from_file(config_path)
    return load_config_from_env()


@click.group(name="providers")
def providers_group() -> None:
    """Provider-related commands."""
    # group only
    return


@providers_group.command("list")
def providers_list() -> None:
    """
    List all registered provider types.
    """
    providers = registry.all()
    if not providers:
        click.echo("No providers registered.")
        return

    for name, cls in providers.items():
        click.echo(f"{name:10s} ({cls.__name__})")


@providers_group.command("info")
@click.option(
    "--name", "provider_name", required=True, help="Provider name, e.g. openai"
)
@click.option("--config", "config_path", type=click.Path(exists=True), required=False)
def providers_info(provider_name: str, config_path: Optional[str]) -> None:
    """
    Show configuration-related info for a provider (safe fields only).
    """
    cfg = _load_config(config_path)
    matches = [p for p in cfg.providers if p.name == provider_name]

    if not matches:
        click.echo(f"No configured provider with name '{provider_name}'.")
        return

    pcfg = matches[0]
    click.echo(f"Name: {pcfg.name}")
    click.echo(f"Type: {pcfg.type}")
    safe_params = {
        k: ("***" if "key" in k.lower() or "token" in k.lower() else v)
        for k, v in pcfg.params.items()
    }
    click.echo(f"Params: {safe_params}")


@providers_group.command("test")
@click.option("--config", "config_path", type=click.Path(exists=True), required=False)
@click.option("--model", required=True, help="Model name, e.g. openai/gpt-4o-mini")
@click.option("--prompt", required=True, help="Prompt to send to the provider")
def providers_test(config_path: Optional[str], model: str, prompt: str) -> None:
    """
    Send a test prompt through the orchestrator to the appropriate provider.
    """
    cfg = _load_config(config_path)
    orch = create_orchestrator_from_config(cfg)

    req = OrchestratorRequest(model=model, prompt=prompt)
    resp = orch.run(req)

    click.echo(f"Provider: {resp.provider}")
    click.echo(f"Model: {resp.model}")
    click.echo("-" * 40)
    click.echo(resp.content)
