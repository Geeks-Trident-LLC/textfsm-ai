import click


@click.command(name="quota", help="Show quota and usage information for providers.")
def quota() -> None:
    click.echo("openai: ok")
    click.echo("claude: ok")
