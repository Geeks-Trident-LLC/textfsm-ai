import click

from textfsm_ai.providers.model_listing_mixin import ModelListingMixin
from textfsm_ai.providers.registry import registry


@click.command("list-models")
@click.argument("provider")
@click.option(
    "--latest",
    is_flag=True,
    help="Fetch latest models from provider API and classify them using an LLM.",
)
@click.option(
    "--latest-raw",
    is_flag=True,
    help="Fetch latest models from provider API but DO NOT classify with LLM.",
)
def list_models(provider: str, latest: bool, latest_raw: bool) -> None:
    """
    List available models for a provider.

    Default: show curated hardcoded model groups.
    --latest: fetch live models and classify using LLM.
    --latest-raw: fetch live models but skip LLM classification.
    """

    # 1. Lookup provider class
    try:
        provider_cls = registry.get(provider)
    except KeyError:
        click.echo(f"Unknown provider: {provider}")
        click.echo("Use `textfsm-ai providers list` to see available providers.")
        return

    # 2. Ensure provider supports model listing
    if not issubclass(provider_cls, ModelListingMixin):
        click.echo(f"Provider '{provider}' does not support model listing.")
        return

    # -----------------------------------------
    # MODE 1: LATEST (API + LLM classification)
    # -----------------------------------------
    if latest:
        click.echo(f"Fetching latest models from provider: {provider} ...\n")

        # Lazy instantiation — only now we need API key + default model
        prov = provider_cls.from_env()

        try:
            raw_models = prov.fetch_latest_models()
            groups = prov.classify_models_with_llm(raw_models)
        except Exception as e:
            click.echo(f"Error: {e}")
            return

        _print_model_groups(provider, groups, latest=True)
        return

    # -----------------------------------------
    # MODE 2: LATEST-RAW(API only)
    # -----------------------------------------
    if latest_raw:
        click.echo(f"Fetching latest models (dry-run) from provider: {provider} ...\n")

        prov = provider_cls.from_env()

        try:
            raw_models = prov.fetch_latest_models()
        except Exception as e:
            click.echo(f"Error: {e}")
            return

        click.echo("Raw model names (no classification):")
        click.echo("----------------------------------------")
        for m in raw_models:
            click.echo(f"  {m}")
        return

    # -----------------------------------------
    # MODE 3: DEFAULT (hardcoded curated list)
    # -----------------------------------------
    groups = provider_cls.list_models_curated()
    _print_model_groups(provider, groups, latest=False)


def _print_model_groups(provider: str, groups: dict, latest: bool) -> None:
    title = f"Models for provider: {provider}"
    if latest:
        title += " (latest)"

    click.echo(title)
    click.echo("----------------------------------------\n")

    for group in [
        "quality",
        "balance",
        "fast",
        "thinking",
        "other",
    ]:
        models = groups.get(group)
        if not models:
            continue

        click.echo(f"{group}:")
        for m in models:
            click.echo(f"  {m}")
        click.echo()
