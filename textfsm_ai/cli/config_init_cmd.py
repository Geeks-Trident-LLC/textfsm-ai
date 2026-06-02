# textfsm_ai/cli/config_init_cmd.py

import os

import click

from textfsm_ai.model_selector import is_chat_model, list_models
from textfsm_ai.user_config import UserConfig, save_user_config

PROVIDERS = ["openai", "anthropic", "gemini", "deepseek"]


@click.command("init")
@click.option(
    "--output", default="default.config", help="Where to save the config file"
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing config file")
@click.option(
    "--create-empty",
    "empty_path",
    default=None,
    help="Create an empty config file and skip all prompts",
)
def config_init(output, overwrite, empty_path):
    """
    Initialize a new config file.
    Supports interactive mode or --create-empty for non-interactive creation.
    """

    # ------------------------------------------------------------
    # 0. Handle --create-empty (non-interactive mode)
    # ------------------------------------------------------------
    if empty_path is not None:
        # If user passed --create-empty=default, convert to default.config
        if empty_path == "default":
            empty_path = "default.config"

        if os.path.exists(empty_path) and not overwrite:
            raise click.ClickException(
                f"Config file '{empty_path}' already exists. "
                f"Use --overwrite to replace it."
            )

        empty_cfg = UserConfig(provider="", model="", api_key="")
        save_user_config(empty_path, empty_cfg)

        click.echo(f"[OK] Empty config created at {empty_path}")
        return

    # ------------------------------------------------------------
    # 1. Normal interactive workflow
    # ------------------------------------------------------------
    click.echo("=== TextFSM-AI Config Init ===")

    # Overwrite check
    if os.path.exists(output) and not overwrite:
        raise click.ClickException(
            f"Config file '{output}' already exists. Use --overwrite to replace it."
        )

    # -----------------------------
    # Provider selection
    # -----------------------------
    click.echo("\nSelect provider:")
    for idx, p in enumerate(PROVIDERS, start=1):
        click.echo(f"  {idx}. {p}")

    provider_input = (
        click.prompt("Enter provider name or number", type=str).strip().lower()
    )

    if provider_input.isdigit():
        provider_idx = int(provider_input)
        if not (1 <= provider_idx <= len(PROVIDERS)):
            raise click.ClickException("Invalid provider number")
        provider = PROVIDERS[provider_idx - 1]
    else:
        if provider_input not in PROVIDERS:
            raise click.ClickException(f"Unknown provider: {provider_input}")
        provider = provider_input

    click.echo(f"[OK] Provider selected: {provider}")

    # -----------------------------
    # API key
    # -----------------------------
    api_key = click.prompt("Enter API key", hide_input=True)
    if not api_key:
        raise click.ClickException("API key cannot be empty")

    # -----------------------------
    # List latest NLP models
    # -----------------------------
    click.echo("\nFetching available models...")

    try:
        all_models = list_models(provider, api_key)
    except Exception as e:
        raise click.ClickException(f"Failed to list models: {e}")

    all_models = [m.split("/")[-1] for m in all_models]
    nlp_models = [m for m in all_models if is_chat_model(provider, m)]

    if not nlp_models:
        click.echo("[WARN] No NLP models detected for this provider.")
        model = click.prompt("Enter model name manually")
    else:
        nlp_models = sorted(nlp_models, reverse=True)
        top_models = nlp_models[:3]

        click.echo("\nSelect a model:")
        for idx, m in enumerate(top_models, start=1):
            click.echo(f"  {idx}. {m}")
        click.echo(f"  {len(top_models) + 1}. Other (enter manually)")

        model_input = click.prompt("Enter model name or number").strip()

        if model_input.isdigit():
            model_idx = int(model_input)
            if 1 <= model_idx <= len(top_models):
                model = top_models[model_idx - 1]
            elif model_idx == len(top_models) + 1:
                model = click.prompt("Enter model name manually")
            else:
                raise click.ClickException("Invalid model number")
        else:
            model = model_input

    click.echo(f"[OK] Model selected: {model}")

    # -----------------------------
    # Save config
    # -----------------------------
    cfg = UserConfig(provider=provider, model=model, api_key=api_key)
    save_user_config(output, cfg)

    click.echo(f"\nConfig saved to {output}")
    click.echo("Done.")
