import click


@click.command(name="quota", help="Show quota and usage information for providers.")
def quota() -> None:
    """Show quota information."""
    # Placeholder: wire into quota_manager later.
    click.echo("[quota] showing quota information (placeholder)")
