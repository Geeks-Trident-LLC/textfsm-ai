# textfsm_ai/cli/config_group.py

import click

from textfsm_ai.cli.config_doctor_cmd import config_doctor
from textfsm_ai.cli.config_init_cmd import config_init
from textfsm_ai.cli.config_list_cmd import config_list
from textfsm_ai.cli.config_migrate_cmd import config_migrate
from textfsm_ai.cli.config_show_cmd import config_show


@click.group("config")
def config_group():
    """Manage textfsm-ai configuration files."""
    pass


config_group.add_command(config_init)
config_group.add_command(config_list)
config_group.add_command(config_doctor)
config_group.add_command(config_migrate)
config_group.add_command(config_show)
