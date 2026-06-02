from __future__ import annotations

import click

from .generate_cmd import generate
from .orchestrator_cmd import orchestrator_group
from .providers_cmd import providers_group


@click.group()
def main() -> None:
    """textfsm-ai command line interface."""
    return


# existing commands (e.g. template generation) stay here
# main.add_command(generate_group)  # example

main.add_command(providers_group)
main.add_command(orchestrator_group)
main.add_command(generate)
