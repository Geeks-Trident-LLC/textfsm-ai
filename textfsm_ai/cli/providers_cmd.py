import click


@click.command(name="providers", help="List configured AI providers and routing information.")
def providers() -> None:
    """List available providers."""
    # Placeholder: wire into config_loader + ai_router later.
    click.echo("[providers] listing configured providers (placeholder)")
