# textfsm_ai/cli/config_show_cmd.py

import json
import os

import click

from textfsm_ai.user_config import load_user_config


@click.command("show")
@click.argument("config_name", type=str)
def config_show(config_name):
    """
    Show the contents of a config file.
    Supports:
      - config show default
      - config show <file-path>
    """

    # Resolve "default" → default.config in CWD
    if config_name == "default":
        path = "default.config"
    else:
        path = config_name

    if not os.path.exists(path):
        raise click.ClickException(f"Config file not found: {path}")

    try:
        cfg = load_user_config(path)
    except Exception as e:
        raise click.ClickException(f"Failed to load config: {e}")

    # Pretty-print JSON
    data = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_key": cfg.api_key,
    }

    click.echo(json.dumps(data, indent=2))
