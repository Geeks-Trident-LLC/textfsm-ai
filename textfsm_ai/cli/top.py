from __future__ import annotations

import click

from textfsm_ai import __version__

from .dsl_cmd import dsl
from .generate_cmd import generate
from .list_models_cmd import list_models
from .orchestrator_cmd import orchestrator_group
from .pipeline_cmd import pipeline
from .providers_cmd import providers_group
from .version_cmd import version_cmd


@click.group()
@click.version_option(__version__, message="textfsm-ai v%(version)s")
def main() -> None:
    """textfsm-ai command line interface."""
    return


# existing commands (e.g. template generation) stay here
# main.add_command(generate_group)  # example

main.add_command(providers_group)
main.add_command(orchestrator_group)
main.add_command(generate)
main.add_command(dsl)
main.add_command(pipeline)
main.add_command(list_models)
main.add_command(version_cmd)
