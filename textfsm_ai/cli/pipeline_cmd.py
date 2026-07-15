# textfsm_ai/cli/pipeline_cmd.py

from __future__ import annotations

import click

from textfsm_ai.cli.generate_cmd import (
    resolve_api_key,
    resolve_api_version,
    resolve_compartment_id,
    resolve_endpoint,
    resolve_model,
    resolve_project,
    resolve_region,
)
from textfsm_ai.delivery.controller.controller import DeliveryController
from textfsm_ai.providers.config import load_config_from_env, load_config_from_file


@click.command("pipeline")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--provider",
    required=True,
    help="Provider name, e.g. openai, anthropic, azure (see `providers list`)",
)
@click.option(
    "--api-key",
    required=False,
    help="Override the resolved API key (ignored for bedrock/vertexai/oci)",
)
@click.option(
    "--model", required=False, help="Model name (or Azure deployment name for azure)"
)
@click.option("--endpoint", required=False, help="Azure endpoint URL (azure only)")
@click.option("--api-version", required=False, help="Azure API version (azure only)")
@click.option(
    "--region",
    required=False,
    help=(
        "AWS region (Bedrock), GCP location (Vertex AI), or OCI region "
        "(OCI, optional)"
    ),
)
@click.option("--project", required=False, help="GCP project (Vertex AI only)")
@click.option(
    "--compartment-id", required=False, help="OCI compartment OCID (OCI only)"
)
@click.option("--max-retries", default=1, show_default=True)
@click.option(
    "--mode",
    type=click.Choice(["quiet", "default", "info", "debug"]),
    default="default",
    show_default=True,
    help="Output verbosity",
)
@click.option(
    "--json", "json_output", is_flag=True, help="Emit the mode's output as JSON"
)
def pipeline(
    input_file,
    provider,
    api_key,
    model,
    endpoint,
    api_version,
    region,
    project,
    compartment_id,
    max_retries,
    mode,
    json_output,
):
    """
    Run the full pipeline: sample -> LLM-generated template -> DSL compile,
    packaged per --mode.
    """

    # -----------------------------
    # 1. Load sample
    # -----------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        sample = f.read()

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

    resolved_api_key = resolve_api_key(provider, api_key, pconf)
    resolved_model = resolve_model(provider, model, pconf)
    resolved_endpoint = resolve_endpoint(provider, endpoint, pconf)
    resolved_api_version = resolve_api_version(provider, api_version, pconf)
    resolved_region = resolve_region(provider, region, pconf)
    resolved_project = resolve_project(provider, project, pconf)
    resolved_compartment_id = resolve_compartment_id(provider, compartment_id, pconf)

    # -----------------------------
    # 3. Run the full pipeline
    # -----------------------------
    controller = DeliveryController(
        provider_name=provider,
        api_key=resolved_api_key,
        model=resolved_model,
        endpoint=resolved_endpoint,
        api_version=resolved_api_version,
        region=resolved_region,
        project=resolved_project,
        compartment_id=resolved_compartment_id,
        max_tries=max_retries,
    )

    result = controller.run(sample, mode=mode, as_json=json_output)

    # -----------------------------
    # 4. Output
    # -----------------------------
    click.echo(result.output)

    if not result.passed:
        raise SystemExit(result.exit_code)
