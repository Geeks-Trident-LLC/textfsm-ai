# textfsm_ai/cli/config_migrate_cmd.py

import os

import click

from textfsm_ai.config_loader import ProviderConfig
from textfsm_ai.config_manager import save_config

ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat",
}


@click.command("migrate")
def config_migrate():
    """
    Auto-migrate environment variables into config files.
    """
    migrated = 0

    for provider, env_var in ENV_MAP.items():
        key = os.getenv(env_var)
        if not key:
            continue

        cfg = ProviderConfig(
            provider=provider,
            model=DEFAULT_MODELS[provider],
            api_key=key,
        )

        path = save_config(provider, cfg)
        click.echo(f"[OK] Migrated {env_var} → {path}")
        migrated += 1

    if migrated == 0:
        click.echo("No environment variables found to migrate.")
    else:
        click.echo(f"Migration complete: {migrated} configs created.")
