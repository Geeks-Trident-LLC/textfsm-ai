import importlib.metadata
import click


@click.command(name="version", help="Show the textfsm-ai package version.")
def version_cmd():
    version = importlib.metadata.version("textfsm-ai")
    click.echo(f"textfsm-ai v{version}")
