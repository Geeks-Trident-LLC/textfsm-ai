# textfsm_ai/cli/list_models_cmd.py

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
@click.option(
    "--premium",
    is_flag=True,
    help="Show premium reasoning models (thinking-chat).",
)
@click.option(
    "--no-premium",
    is_flag=True,
    help="Hide premium reasoning models (thinking-chat).",
)
@click.option(
    "--quality",
    is_flag=True,
    help="Show quality-chat models.",
)
@click.option(
    "--balance",
    is_flag=True,
    help="Show balance-chat models.",
)
@click.option(
    "--speed",
    is_flag=True,
    help="Show speed-chat models.",
)
def list_models(
    provider: str,
    latest: bool,
    latest_raw: bool,
    premium: bool,
    no_premium: bool,
    quality: bool,
    balance: bool,
    speed: bool,
) -> None:
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
        prov = provider_cls.from_env()

        try:
            groups = prov.classify_models()
        except Exception as e:
            click.echo(f"Error: {e}")
            return

        _print_model_groups(
            provider,
            groups,
            latest=True,
            no_premium=no_premium,
            premium=premium,
            quality=quality,
            balance=balance,
            speed=speed,
        )
        return

    # -----------------------------------------
    # MODE 2: LATEST-RAW (API only)
    # -----------------------------------------
    if latest_raw:
        click.echo(f"Fetching latest models from provider: {provider} ...\n")
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
    _print_model_groups(
        provider,
        groups,
        latest=False,
        no_premium=no_premium,
        premium=premium,
        quality=quality,
        balance=balance,
        speed=speed,
    )


def _print_model_groups(
    provider: str,
    groups: dict,
    latest: bool,
    no_premium: bool,
    premium: bool,
    quality: bool,
    balance: bool,
    speed: bool,
) -> None:
    groups = groups.copy()

    s = set()
    pairs = (
        (no_premium, ["quality-chat", "balance-chat", "speed-chat"]),
        (premium, ["thinking-chat"]),
        (quality, ["quality-chat"]),
        (balance, ["balance-chat"]),
        (speed, ["speed-chat"]),
    )
    for option, value in pairs:
        if option:
            s.update(value)

    filtered = list(s)
    if not filtered:
        filtered = [
            "quality-chat",
            "balance-chat",
            "speed-chat",
            "thinking-chat",
            "other",
        ]

    # Print
    title = f"Models for provider: {provider}"
    if latest:
        title += " (latest)"

    click.echo(title)
    click.echo("----------------------------------------\n")

    for group in filtered:
        models = groups.get(group)
        if not models:
            continue

        click.echo(f"{group}:")
        for m in models:
            click.echo(f"  {m}")
        click.echo()
