# textfsm_ai/cli/generate_cmd.py

# textfsm_ai/cli/generate_cmd.py

from __future__ import annotations

import os

import click

from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.providers.config import load_config_from_env, load_config_from_file


@click.command("generate")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--provider", required=True)
@click.option("--api-key", required=False)
@click.option("--model", required=False)
@click.option("--endpoint", required=False)
@click.option("--api-version", required=False)
@click.option("--max-retries", default=1, show_default=True)
@click.option("--raw", is_flag=True, help="Show raw LLM output")
@click.option("--json", "json_output", is_flag=True, help="Show full pipeline JSON")
@click.option("--explain", is_flag=True, help="Show variable explanations")
@click.option("--debug", is_flag=True, help="Show provider/controller resolution")
@click.option("--usage", is_flag=True, help="Show token usage")
@click.option("--sections", is_flag=True, help="Print all canonical output sections")
@click.option(
    "--template-only", is_flag=True, help="Print only the final TextFSM template"
)
@click.option("--records", is_flag=True, help="Print parsed records")
@click.option("--handling", is_flag=True, help="Print LLM reasoning/handling")
@click.option("--sample", is_flag=True, help="Print the input sample used by the LLM")
def generate(
    input_file,
    provider,
    api_key,
    model,
    endpoint,
    api_version,
    max_retries,
    raw,
    json_output,
    explain,
    debug,
    usage,
    sections,
    template_only,
    records,
    handling,
    sample,
):
    """
    Generate a TextFSM template or AI output using the orchestrator.
    """

    # -----------------------------
    # 1. Load prompt
    # -----------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        prompt = f.read()

    # -----------------------------
    # 2. Resolve provider config
    # -----------------------------
    cfg = load_config_from_file()
    env_cfg = load_config_from_env()
    providers = {**cfg.providers, **env_cfg.providers}

    if provider not in providers:
        keys = ", ".join(sorted(providers.keys()))
        raise click.ClickException(f"Unknown provider '{provider}'. Available: {keys}")

    pconf = providers[provider]
    params = pconf.params.copy()

    # Resolve each field: CLI flag > provider-specific env var > providers.yaml
    params["api_key"] = resolve_api_key(provider, api_key, pconf)
    params["model"] = resolve_model(provider, model, pconf)
    params["endpoint"] = resolve_endpoint(provider, endpoint, pconf)
    params["api_version"] = resolve_api_version(provider, api_version, pconf)

    # -----------------------------
    # 3. Debug output
    # -----------------------------

    # --debug → provider/controller resolution
    if debug and not json_output:
        click.echo("=== Debug Info ===")
        click.echo(f"provider:       {provider}")
        click.echo(f"model:          {params.get('model')}")
        click.echo(f"max_retries:    {max_retries}")

        # API key masking
        key = params.get("api_key")
        masked = key[:4] + "..." + key[-4:] if key else "<missing>"
        click.echo(f"api_key:        {masked}")

        # Azure-only fields
        if params.get("endpoint"):
            click.echo(f"endpoint:       {params.get('endpoint')}")
            click.echo(f"api_version:    {params.get('api_version')}")
        click.echo("")

    # -----------------------------
    # 4. Create controller
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
    # 5. Run pipeline
    # -----------------------------
    pipeline = controller.run(prompt)

    if not pipeline.ready:
        raise click.ClickException(f"Generation failed: {pipeline.reason}")

    # -----------------------------
    # 6. Output modes
    # -----------------------------

    stage = pipeline.last_stage
    meta = stage.metadata
    resp = meta.response if meta else None

    # --json → full pipeline JSON
    if json_output:
        import json

        click.echo(json.dumps(pipeline.to_dict(), indent=2))
        return

    # --usage → token usage
    if usage:
        click.echo("=== LLM Usage ===")
        if resp:
            click.echo(f"prompt_tokens: {resp.input_tokens}")
            click.echo(f"completion_tokens: {resp.output_tokens}")
            click.echo(f"total_tokens: {resp.total_tokens}")
        else:
            click.echo("No token usage available.")

    # --sections → print all 4 canonical blocks
    if sections:
        click.echo("=== TEXTFSM TEMPLATE ===")
        click.echo(stage.template)
        click.echo("")

        click.echo("=== PARSED RECORDS ===")
        click.echo(stage.records)
        click.echo("")

        click.echo("=== VARIABLE EXPLANATIONS ===")
        if meta and meta.variables:
            click.echo(meta.variables)
        else:
            click.echo("No variable explanations available.")
        click.echo("")

        click.echo("=== LLM HANDLING ===")
        if meta and meta.handling:
            for line in meta.handling:
                click.echo(line)
        else:
            click.echo("No LLM handling information available.")
        return

    # --template-only → explicitly print only the final template
    if template_only:
        click.echo(stage.template)
        return

    # --records → print parsed records
    if records:
        click.echo(stage.records)
        return

    # --handling → print LLM reasoning
    if handling:
        if meta and meta.handling:
            for line in meta.handling:
                click.echo(line)
        else:
            click.echo("No LLM handling information available.")
        return

    # --sample → print the input sample
    if sample:
        if resp:
            click.echo(resp.prompt)
        else:
            click.echo("No sample available.")
        return

    # --raw → raw LLM output
    if raw:
        if resp and resp.raw:
            click.echo(resp.raw)
        else:
            click.echo("No raw LLM output available.")
        return

    # --explain → variable explanations
    if explain:
        if meta and meta.variables:
            click.echo(meta.variables)
        else:
            click.echo("No variable explanations available.")
        return

    # -----------------------------
    # 7. Default output → final template
    # -----------------------------
    click.echo(stage.template)


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
        "gemini": "GEMINI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "xai": "XAI_API_KEY",
        "together": "TOGETHER_API_KEY",
    }

    env_var = env_map.get(provider)
    if env_var:
        key = os.getenv(env_var)
        if key:
            return key

    # providers.yaml fallback
    if pconf and pconf.params.get("api_key"):
        return pconf.params["api_key"]

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
