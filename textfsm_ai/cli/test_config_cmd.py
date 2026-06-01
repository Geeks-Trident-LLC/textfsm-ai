# textfsm_ai/cli/test_config_cmd.py

import click

from textfsm_ai.config_loader import load_config
from textfsm_ai.provider_ping import PING_MAP


@click.command("test-config")
@click.argument("config_file", type=click.Path(exists=True))
def test_config(config_file):
    click.echo(f"Loading config: {config_file}")

    cfg = load_config(config_file)
    click.echo(f"[OK] provider = {cfg.provider}")
    click.echo(f"[OK] model    = {cfg.model}")

    if cfg.provider not in PING_MAP:
        raise click.ClickException(f"Unknown provider: {cfg.provider}")

    click.echo("Testing API key and connectivity...")

    try:
        # Corrected signature
        PING_MAP[cfg.provider](cfg.provider, cfg.model, cfg.api_key)
        click.echo("[OK] API key valid")
        click.echo("[OK] Connectivity successful")
    except Exception as e:
        raise click.ClickException(f"[ERROR] Provider test failed: {e}")
