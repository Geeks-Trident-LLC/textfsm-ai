# textfsm_ai/cli/generate_cmd.py

import click

from textfsm_ai.api import ask_ai
from textfsm_ai.user_config import load_user_config


@click.command("generate")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--config", "config_file", type=click.Path(), help="Path to config file")
@click.option("--config-default", is_flag=True, help="Load default.config from PWD")
def generate(input_file, config_file, config_default):
    if not config_file and not config_default:
        raise click.UsageError("Must specify --config=<file> or --config-default")

    if config_default:
        config_file = "default.config"

    cfg = load_user_config(config_file)

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    resp = ask_ai(
        raw_text,
        provider=cfg.provider,
        model=cfg.model,
        api_key=cfg.api_key,
    )

    click.echo(resp)
