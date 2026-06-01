# textfsm_ai/cli/config_init_cmd.py

import click

from textfsm_ai.config_loader import ProviderConfig
from textfsm_ai.config_manager import save_config


@click.command("init")
@click.option(
    "-o",
    "--output",
    "output_path",
    required=True,
    help="Path to write the config file.",
)
def config_init(output_path):
    """
    Create a new provider config file interactively.
    """
    provider = click.prompt("Provider name")
    model = click.prompt("Model name")
    api_key = click.prompt("API key")

    cfg = ProviderConfig(provider=provider, model=model, api_key=api_key)
    save_config(output_path.replace(".config", ""), cfg)

    click.echo(f"Config written to {output_path}")
