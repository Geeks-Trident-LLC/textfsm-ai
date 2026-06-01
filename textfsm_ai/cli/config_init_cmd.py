# textfsm_ai/cli/config_init_cmd.py

from pathlib import Path

import click


@click.command("config-init")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="default.config",
    help="Where to write the generated config file",
)
def config_init(output):
    """
    Interactively create a provider config file.
    """
    provider = click.prompt("Provider (openai, anthropic, gemini, deepseek)")
    model = click.prompt("Model name")
    api_key = click.prompt("API key", hide_input=True)

    cfg_path = Path(output)

    content = f'provider = "{provider}"\nmodel = "{model}"\napi_key = "{api_key}"\n'

    cfg_path.write_text(content, encoding="utf-8")

    click.echo(f"Config written to {cfg_path}")
