import pathlib
from typing import Optional

import click


@click.command(name="generate", help="Generate a TextFSM template from raw CLI output.")
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
@click.option(
    "--provider",
    "-p",
    default="openai",
    show_default=True,
    help="Provider name to use for generation.",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Optional model name override.",
)
def generate(input_file: pathlib.Path, provider: str, model: Optional[str]) -> None:
    click.echo(f"Generating template from: {input_file}")
    click.echo(f"Provider: {provider}")
    click.echo(f"Model: {model}")
    click.echo("Status: ok")
