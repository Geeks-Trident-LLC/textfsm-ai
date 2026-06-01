# textfsm_ai/cli/config_list_cmd.py

from pathlib import Path

import click


@click.command("config-list")
def config_list():
    """
    List available config files in PWD and ~/.textfsm-ai/.
    """
    home_dir = Path.home() / ".textfsm-ai"
    pwd = Path(".")

    click.echo("Configs in current directory:")
    for f in pwd.glob("*.config"):
        click.echo(f"  - {f}")

    click.echo("\nConfigs in ~/.textfsm-ai/:")
    if home_dir.exists():
        for f in home_dir.glob("*.config"):
            click.echo(f"  - {f}")
    else:
        click.echo("  (no directory)")
