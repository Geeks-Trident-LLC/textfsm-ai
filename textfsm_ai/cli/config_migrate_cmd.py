# textfsm_ai/cli/config_migrate_cmd.py

import os

import click

from textfsm_ai.config_manager import save_config
from textfsm_ai.model_selector import get_model
from textfsm_ai.user_config import UserConfig

ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


@click.command("migrate")
def config_migrate():
    """
    Auto-migrate environment variables into user config files.
    Creates ~/.textfsm-ai/<provider>.config for each provider with an API key.
    """
    migrated = 0

    for provider, env_var in ENV_MAP.items():
        api_key = os.getenv(env_var)
        if not api_key:
            continue

        # Dynamically pick the best NLP model for this provider
        try:
            model = get_model(provider, api_key)
        except Exception as e:
            click.echo(f"[WARN] Could not auto-select model for {provider}: {e}")
            continue

        cfg = UserConfig(
            provider=provider,
            model=model,
            api_key=api_key,
        )

        path = save_config(provider, cfg)
        click.echo(f"[OK] Migrated {env_var} → {path}")
        migrated += 1

    if migrated == 0:
        click.echo("No environment variables found to migrate.")
    else:
        click.echo(f"Migration complete: {migrated} configs created.")
