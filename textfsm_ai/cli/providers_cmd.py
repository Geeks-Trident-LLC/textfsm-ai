from __future__ import annotations

from typing import Optional

import anyask
import click
from anyask.registry import registry

from textfsm_ai.providers.config import (
    ProvidersConfig,
    load_config_from_env,
    load_config_from_file,
)

PROVIDER_DESCRIPTIONS = {
    "openai": "Native OpenAI API",
    "deepseek": "DeepSeek (OpenAI-compatible API)",
    "azure": "Azure AI Inference / Azure OpenAI",
    "anthropic": "Anthropic Claude models",
    "gemini": "Google Gemini models",
    "groq": "Groq (fast open-model inference, OpenAI-compatible API)",
    "xai": "xAI Grok models (OpenAI-compatible API)",
    "together": "Together AI (open-model hosting, OpenAI-compatible API)",
    "fireworks": "Fireworks AI (open-model hosting, OpenAI-compatible API)",
    "cerebras": "Cerebras (fast open-model inference, OpenAI-compatible API)",
    "perplexity": "Perplexity (search-grounded Sonar models, OpenAI-compatible API)",
    "openrouter": "OpenRouter (multi-provider model aggregator, OpenAI-compatible API)",
    "moonshot": "Moonshot AI / Kimi models (OpenAI-compatible API)",
    "mistral": "Mistral AI (native SDK)",
    "bedrock": "Amazon Bedrock (native SDK, AWS credential chain)",
    "cohere": "Cohere Command models (native SDK)",
    "vertexai": "Google Vertex AI (Gemini via GCP, ADC credential chain)",
    "oci": "Oracle Cloud Infrastructure Generative AI (Llama/Grok, config-file auth)",
}


def _load_config(config_path: Optional[str]) -> ProvidersConfig:
    if config_path:
        return load_config_from_file(config_path)
    return load_config_from_env()


@click.group(name="providers")
def providers_group() -> None:
    """Provider-related commands."""
    return


@providers_group.command("list")
def providers_list() -> None:
    """
    List all registered provider names with descriptions.
    """
    providers = registry.all()
    if not providers:
        click.echo("No providers registered.")
        return

    click.echo("NAME           DESCRIPTION")
    click.echo("-------------  ----------------------------------------")

    for name in sorted(providers):
        desc = PROVIDER_DESCRIPTIONS.get(name, "")
        click.echo(f"{name:<13}  {desc}")


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

    pcfg = cfg.providers.get(provider_name)
    if pcfg is None:
        click.echo(f"No configured provider with name '{provider_name}'.")
        return

    click.echo(f"Name: {provider_name}")
    click.echo(f"Type: {pcfg.type}")

    safe_params = {
        k: (
            "***"
            if any(s in k.lower() for s in ("key", "token", "secret", "password"))
            else v
        )
        for k, v in pcfg.params.items()
    }

    click.echo(f"Params: {safe_params}")


@providers_group.command("test")
@click.option(
    "--provider", "provider_name", required=True, help="Provider name, e.g. openai"
)
@click.option("--config", "config_path", type=click.Path(exists=True), required=False)
@click.option("--model", required=True, help="Model name, e.g. gpt-4o-mini")
@click.option("--prompt", required=True, help="Prompt to send to the provider")
def providers_test(
    provider_name: str, config_path: Optional[str], model: str, prompt: str
) -> None:
    """
    Send a test prompt directly to a provider.
    """
    cfg = _load_config(config_path)
    pcfg = cfg.providers.get(provider_name)
    params = pcfg.params if pcfg else {}

    response = anyask.ask(prompt, provider=provider_name, model=model, **params)

    click.echo(f"Provider: {response.provider}")
    click.echo(f"Model: {response.model}")
    click.echo("-" * 40)
    click.echo(response.content)
