# textfsm_ai/cli/generate_cmd.py

from __future__ import annotations

import asyncio

import click

from textfsm_ai.api import ask_ai


@click.command("generate")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--model",
    required=True,
    help="Model name with prefix, e.g. openai/gpt-4o-mini",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True),
    required=False,
    help="Optional YAML config file. If omitted, environment variables are used.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Return output in JSON format.",
)
def generate(input_file, model, config_path, as_json):
    """
    Generate a TextFSM template or AI output using the orchestrator.
    """

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    resp = asyncio.run(
        ask_ai(
            raw_text,
            model=model,
            config_path=config_path,
        )
    )

    if as_json:
        click.echo(resp.to_json())
    else:
        click.echo(resp.content)
