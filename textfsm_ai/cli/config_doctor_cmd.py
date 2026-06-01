# textfsm_ai/cli/config_doctor_cmd.py

import click

from textfsm_ai.provider_ping import PING_MAP
from textfsm_ai.user_config import load_user_config


@click.command("doctor")
@click.argument("config_file", type=click.Path(exists=True))
def config_doctor(config_file):
    """
    Validate config file, provider, model, API key, and connectivity.
    """
    click.echo(f"Loading config: {config_file}")

    cfg = load_user_config(config_file)

    click.echo(f"[OK] provider = {cfg.provider}")
    click.echo(f"[OK] model    = {cfg.model}")

    if cfg.provider not in PING_MAP:
        raise click.ClickException(f"[ERROR] Unknown provider: {cfg.provider}")

    click.echo("Testing provider connectivity...")

    try:
        PING_MAP[cfg.provider](cfg.api_key, cfg.model)
        click.echo("[OK] API key valid")
        click.echo("[OK] Connectivity successful")
    except Exception as e:
        raise click.ClickException(f"[ERROR] Provider test failed: {e}")
