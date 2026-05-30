import click


@click.command(name="providers", help="List configured AI providers and routing information.")
def providers() -> None:
    click.echo("openai")
    click.echo("claude")
    click.echo("gemini")
    click.echo("deepseek")
