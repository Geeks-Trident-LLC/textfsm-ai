import importlib.metadata
import click

from .generate_cmd import generate
from .providers_cmd import providers
from .quota_cmd import quota
from .version_cmd import version_cmd


@click.group(
    name="textfsm-ai", help="AI-powered TextFSM template generator with multi-provider routing."
)
@click.version_option(
    version=importlib.metadata.version("textfsm-ai"),
    prog_name="textfsm-ai",
    message="textfsm-ai v%(version)s",
)
def cli():
    """Top-level CLI group."""
    pass


cli.add_command(version_cmd)
cli.add_command(generate)
cli.add_command(providers)
cli.add_command(quota)


def main() -> None:
    """Console script entry point."""
    cli()
