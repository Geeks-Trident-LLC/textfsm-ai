# textfsm_ai/cli/list_models_cmd.py

import click

from textfsm_ai.providers.model_listing_mixin import ModelListingMixin
from textfsm_ai.providers.registry import registry


@click.command("list-models")
@click.argument("provider")
def list_models(provider: str) -> None:
    """
    List a provider's live models, fetched from the provider's own API.
    """

    try:
        provider_cls = registry.get(provider)
    except KeyError:
        click.echo(f"Unknown provider: {provider}")
        click.echo("Use `textfsm-ai providers list` to see available providers.")
        return

    if not issubclass(provider_cls, ModelListingMixin):
        click.echo(f"Provider '{provider}' does not support model listing.")
        return

    click.echo(f"Fetching models from provider: {provider} ...\n")
    prov = provider_cls.from_env()

    try:
        models = prov.fetch_latest_models()
    except Exception as e:
        click.echo(f"Error: {e}")
        return

    click.echo(f"Models for provider: {provider}")
    click.echo("----------------------------------------")
    for m in models:
        click.echo(f"  {m}")
