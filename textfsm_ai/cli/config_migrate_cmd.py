# textfsm_ai/cli/config_migrate_cmd.py

import os

import click

from textfsm_ai.config_manager import save_config
from textfsm_ai.model_selector import get_model
from textfsm_ai.user_config import UserConfig


@click.command("migrate")
@click.option(
    "--tier",
    type=click.Choice(
        [
            "quality",
            "balance",
            "fast",
            "quality-reasoning",
            "balance-reasoning",
            "fast-reasoning",
        ]
    ),
    default="quality",
    show_default=True,
    help="Select model tier for each provider.",
)
def config_migrate(tier):
    """
    Migrate environment variables into ~/.textfsm-ai/*.config
    """
    providers = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }

    created = 0

    for provider, env_var in providers.items():
        api_key = os.getenv(env_var)
        if not api_key:
            continue

        model = get_model(provider, api_key, tier)
        cfg = UserConfig(provider, model, api_key)
        save_config(provider, cfg)

        click.echo(f"[OK] {provider}: {model}")
        created += 1

    click.echo(f"Migration complete: {created} configs created.")
