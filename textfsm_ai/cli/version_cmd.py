import click
from textfsm_ai import __version__


@click.command(name="version", help="Show the textfsm-ai package version.")
def version_cmd():
    click.echo(f"textfsm-ai v{__version__}")
