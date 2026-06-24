# textfsm_ai/cli/generate_cmd.py

# textfsm_ai/cli/generate_cmd.py

from __future__ import annotations

import os

import click

from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.providers.config import load_config_from_env, load_config_from_file


@click.command("generate")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--provider",
    required=True,
    help="Provider name (azure, openai, gemini, anthropic, deepseek)",
)
@click.option("--api-key", required=False, help="Override API key")
@click.option("--model", required=False, help="Model or deployment name")
@click.option("--endpoint", required=False, help="Endpoint URL (Azure only)")
@click.option("--api-version", required=False, help="API version (Azure only)")
@click.option("--max-retries", default=1, show_default=True)
def generate(input_file, provider, api_key, model, endpoint, api_version, max_retries):
    """
    Generate a TextFSM template or AI output using the orchestrator.
    """

    # -----------------------------
    # 1. Load config (file → env)
    # -----------------------------
    from textfsm_ai import BASE_DIR

    cfg = load_config_from_file(BASE_DIR / "models" / "providers.yaml")
    env_cfg = load_config_from_env()

    # Merge env providers on top of file providers
    providers = {**cfg.providers, **env_cfg.providers}

    if provider not in providers:
        keys = ", ".join(sorted(providers.keys()))
        raise click.ClickException(f"Unknown provider '{provider}'. Available: {keys}")

    pconf = providers[provider]  # ProviderConfig

    # -----------------------------
    # 2. Resolve parameters
    # -----------------------------
    params = pconf.params.copy()

    # CLI overrides config
    if api_key:
        params["api_key"] = api_key
    if model:
        params["model"] = model
    if endpoint:
        params["endpoint"] = endpoint
    if api_version:
        params["api_version"] = api_version

    # -----------------------------
    # 3. Validate required params
    # -----------------------------
    if "api_key" not in params or not params["api_key"]:
        raise click.ClickException(
            f"Provider '{provider}' requires an API key. "
            f"Use --api-key or set it in providers.yaml or environment."
        )

    # Azure-specific validation
    if provider == "azure":
        if "endpoint" not in params or not params["endpoint"]:
            raise click.ClickException(
                "Azure requires an endpoint. Use --endpoint or "
                "set AZURE_OPENAI_ENDPOINT."
            )
        if "model" not in params or not params["model"]:
            raise click.ClickException(
                "Azure requires a deployment name. Use --model or "
                "set AZURE_OPENAI_DEPLOYMENT."
            )
        params.setdefault("api_version", "2024-02-15-preview")

    # Non-Azure providers: model optional (fallback to config)
    else:
        params.setdefault("model", pconf.params.get("model"))

    # -----------------------------
    # 4. Read prompt
    # -----------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        prompt = f.read()

    # -----------------------------
    # 5. Create controller
    # -----------------------------
    controller = GenerationController(
        provider_name=provider,
        api_key=params.get("api_key"),
        model=params.get("model"),
        endpoint=params.get("endpoint"),
        api_version=params.get("api_version"),
        max_retries=max_retries,
    )

    # -----------------------------
    # 6. Run generation
    # -----------------------------
    pipeline = controller.run(prompt)

    if not pipeline.ready:
        raise click.ClickException(f"Generation failed: {pipeline.reason}")

    click.echo(pipeline.last_stage.template)


# ============================================================
# Helper functions
# ============================================================


def resolve_api_key(provider, api_key, pconf):
    if api_key:
        return api_key

    # Provider-specific env vars
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
    }

    env_var = env_map.get(provider)
    if env_var:
        key = os.getenv(env_var)
        if key:
            return key

    # providers.yaml fallback
    if pconf and pconf.api_key:
        return pconf.api_key

    raise click.ClickException(
        f"API key not provided. Use --api-key or set {env_var} or providers.yaml"
    )


def resolve_model(provider, model, pconf):
    if model:
        return model

    if provider == "azure":
        # Azure uses deployment names, not model names
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if deployment:
            return deployment

        # DO NOT read Azure model from providers.yaml
        if pconf and "model" in pconf.params:
            return pconf.params["model"]

        raise click.ClickException(
            "Azure requires a deployment name. Use --model or "
            "set AZURE_OPENAI_DEPLOYMENT."
        )

    # Non-Azure providers use providers.yaml
    if pconf and "model" in pconf.params:
        return pconf.params["model"]

    raise click.ClickException(
        f"No model provided and no default model found for provider '{provider}'."
    )


def resolve_endpoint(provider, endpoint, pconf):
    if provider != "azure":
        return None

    if endpoint:
        return endpoint

    env = os.getenv("AZURE_OPENAI_ENDPOINT")
    if env:
        return env

    if pconf and "endpoint" in pconf.params:
        return pconf.params["endpoint"]

    raise click.ClickException(
        "Azure requires an endpoint. Use --endpoint or set AZURE_OPENAI_ENDPOINT."
    )


def resolve_api_version(provider, api_version, pconf):
    if provider != "azure":
        return None

    if api_version:
        return api_version

    env = os.getenv("AZURE_OPENAI_API_VERSION")
    if env:
        return env

    if pconf and "api_version" in pconf.params:
        return pconf.params["api_version"]

    return "2024-02-15-preview"
