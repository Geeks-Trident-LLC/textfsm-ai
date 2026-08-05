# textfsm_ai/cli/list_models_cmd.py

import anyask
import click


@click.command("list-models")
@click.argument("provider")
def list_models(provider: str) -> None:
    """
    List a provider's live models, fetched from the provider's own API.
    """

    click.echo(f"Fetching models from provider: {provider} ...\n")

    try:
        models = anyask.list_models(provider)
    except anyask.ProviderNotFoundError:
        click.echo(f"Unknown provider or unsupported model listing: {provider}")
        click.echo("Use `textfsm-ai providers list` to see available providers.")
        return
    except Exception as e:
        click.echo(f"Error: {e}")
        return

    click.echo(f"Models for provider: {provider}")
    click.echo("----------------------------------------")
    for m in models:
        click.echo(f"  {m}")
