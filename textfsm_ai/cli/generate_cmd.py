import pathlib

import click

from textfsm_ai.api import ask_ai


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
def generate_cmd(prompt: tuple[str, ...], provider: str | None, model: str | None):
    """
    Generate something using an AI provider.
    """
    full_prompt = " ".join(prompt)
    resp = ask_ai(full_prompt, provider=provider, model=model)
    click.echo(resp.text)
