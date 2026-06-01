# textfsm_ai/cli/top.py

import click

from textfsm_ai.cli.config_group import config_group
from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.cli.ping_config_cmd import ping_config


@click.group()
def cli():
    """textfsm-ai command-line interface"""
    pass


cli.add_command(generate)
cli.add_command(ping_config)
cli.add_command(config_group)


def main():
    cli()
