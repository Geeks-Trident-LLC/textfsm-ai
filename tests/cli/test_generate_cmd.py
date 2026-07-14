# tests/cli/test_generate_cmd.py

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import (
    generate,
    resolve_api_key,
    resolve_api_version,
    resolve_endpoint,
    resolve_model,
    resolve_project,
    resolve_region,
)
from textfsm_ai.providers.config import OrchestratorConfig, ProviderConfig

# All provider-specific env vars the helpers under test consult. Cleared in
# every relevant test so a developer's real API keys never leak into
# assertions or change test outcomes.
_PROVIDER_ENV_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
]


@pytest.fixture(autouse=True)
def _clear_provider_env(monkeypatch):
    for var in _PROVIDER_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@contextmanager
def _mocked_generate(
    tmp_path, provider="openai", provider_params=None, input_text="hello world"
):
    """Set up load_config_from_file/env + GenerationController mocks and
    yield (runner, controller_instance, input_file) for the caller to
    configure pipeline.run.return_value before invoking the command."""
    input_file = tmp_path / "input.txt"
    input_file.write_text(input_text, encoding="utf-8")

    if provider_params is None:
        provider_params = {"api_key": "dummy", "model": "test-model"}
    fake_provider = ProviderConfig(name=provider, type=provider, params=provider_params)

    with (
        patch("textfsm_ai.cli.generate_cmd.load_config_from_file") as mock_file,
        patch("textfsm_ai.cli.generate_cmd.load_config_from_env") as mock_env,
        patch("textfsm_ai.cli.generate_cmd.GenerationController") as mock_ctrl,
    ):
        mock_file.return_value = OrchestratorConfig(providers={provider: fake_provider})
        mock_env.return_value = OrchestratorConfig(providers={})
        yield CliRunner(), mock_ctrl.return_value, input_file


def test_generate_basic_output(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    fake_provider = ProviderConfig(
        name="openai",
        type="openai",
        params={"api_key": "dummy", "model": "gpt-4o-mini"},
    )

    with (
        patch("textfsm_ai.cli.generate_cmd.load_config_from_file") as mock_file,
        patch("textfsm_ai.cli.generate_cmd.load_config_from_env") as mock_env,
        patch("textfsm_ai.cli.generate_cmd.GenerationController") as mock_ctrl,
    ):
        mock_file.return_value = OrchestratorConfig(providers={"openai": fake_provider})
        mock_env.return_value = OrchestratorConfig(providers={})

        instance = mock_ctrl.return_value
        instance.run.return_value.last_stage.template = "mocked output"
        instance.run.return_value.ready = True

        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                str(input_file),
                "--provider",
                "openai",
                "--model",
                "gpt-4o-mini",
            ],
        )

    assert result.exit_code == 0
    assert "mocked output" in result.output


def test_generate_requires_provider(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(generate, [str(input_file)])

    assert result.exit_code != 0
    assert "Missing option '--provider'" in result.output


def test_generate_unknown_provider(tmp_path):
    with _mocked_generate(tmp_path) as (runner, _instance, input_file):
        result = runner.invoke(
            generate, [str(input_file), "--provider", "not-configured"]
        )

    assert result.exit_code != 0
    assert "Unknown provider 'not-configured'" in result.output


def test_generate_pipeline_not_ready_raises(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        instance.run.return_value.ready = False
        instance.run.return_value.reason = "provider timeout"

        result = runner.invoke(generate, [str(input_file), "--provider", "openai"])

    assert result.exit_code != 0
    assert "Generation failed: provider timeout" in result.output


def test_generate_azure_missing_endpoint_raises(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="azure",
        provider_params={"api_key": "dummy", "model": "gpt-4o"},
    ) as (runner, _instance, input_file):
        result = runner.invoke(generate, [str(input_file), "--provider", "azure"])

    assert result.exit_code != 0
    assert "Azure requires an endpoint" in result.output


def test_generate_azure_missing_model_raises(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="azure",
        provider_params={"api_key": "dummy", "endpoint": "https://example.azure.com"},
    ) as (runner, _instance, input_file):
        result = runner.invoke(generate, [str(input_file), "--provider", "azure"])

    assert result.exit_code != 0
    assert "Azure requires a deployment name" in result.output


def test_generate_bedrock_missing_region_raises(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="bedrock",
        provider_params={"model": "anthropic.claude-haiku-4-5-v1:0"},
    ) as (runner, _instance, input_file):
        result = runner.invoke(generate, [str(input_file), "--provider", "bedrock"])

    assert result.exit_code != 0
    assert "Bedrock requires an AWS region" in result.output


def test_generate_bedrock_debug_output(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="bedrock",
        provider_params={
            "model": "anthropic.claude-haiku-4-5-v1:0",
            "region": "us-east-1",
        },
    ) as (runner, instance, input_file):
        instance.run.return_value.ready = True
        instance.run.return_value.last_stage.template = "tmpl"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "bedrock", "--debug"]
        )

    assert result.exit_code == 0
    assert "=== Debug Info ===" in result.output
    # Bedrock has no project-level api_key - never printed/masked like others
    assert "<not used, resolved via AWS credential chain>" in result.output
    assert "region:         us-east-1" in result.output


def test_generate_vertexai_missing_region_raises(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="vertexai",
        provider_params={"model": "gemini-2.5-flash", "project": "my-project"},
    ) as (runner, _instance, input_file):
        result = runner.invoke(generate, [str(input_file), "--provider", "vertexai"])

    assert result.exit_code != 0
    assert "Vertex AI requires a GCP location" in result.output


def test_generate_vertexai_missing_project_raises(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="vertexai",
        provider_params={"model": "gemini-2.5-flash", "region": "us-central1"},
    ) as (runner, _instance, input_file):
        result = runner.invoke(generate, [str(input_file), "--provider", "vertexai"])

    assert result.exit_code != 0
    assert "Vertex AI requires a GCP project" in result.output


def test_generate_vertexai_debug_output(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="vertexai",
        provider_params={
            "model": "gemini-2.5-flash",
            "region": "us-central1",
            "project": "my-project",
        },
    ) as (runner, instance, input_file):
        instance.run.return_value.ready = True
        instance.run.return_value.last_stage.template = "tmpl"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "vertexai", "--debug"]
        )

    assert result.exit_code == 0
    assert "=== Debug Info ===" in result.output
    # Vertex AI has no project-level api_key - never printed/masked like others
    assert "<not used, resolved via GCP ADC credential chain>" in result.output
    assert "region:         us-central1" in result.output
    assert "project:        my-project" in result.output


def test_generate_debug_output(tmp_path):
    with _mocked_generate(
        tmp_path,
        provider="azure",
        provider_params={
            "api_key": "sk-secretvalue",
            "model": "gpt-4o",
            "endpoint": "https://example.azure.com",
        },
    ) as (runner, instance, input_file):
        instance.run.return_value.ready = True
        instance.run.return_value.last_stage.template = "tmpl"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "azure", "--debug"]
        )

    assert result.exit_code == 0
    assert "=== Debug Info ===" in result.output
    assert "provider:       azure" in result.output
    # api_key is masked, never printed in full
    assert "sk-secretvalue" not in result.output
    assert "sk-s...alue" in result.output
    assert "endpoint:       https://example.azure.com" in result.output
    assert "api_version:" in result.output


def test_generate_json_output(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.to_dict.return_value = {"model": "test-model", "ready": True}

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--json"]
        )

    assert result.exit_code == 0
    assert '"ready": true' in result.output


def test_generate_usage_output_with_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        meta = pipeline.last_stage.metadata
        meta.response.input_tokens = 10
        meta.response.output_tokens = 20
        meta.response.total_tokens = 30

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--usage"]
        )

    assert result.exit_code == 0
    assert "prompt_tokens: 10" in result.output
    assert "completion_tokens: 20" in result.output
    assert "total_tokens: 30" in result.output


def test_generate_usage_output_without_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--usage"]
        )

    assert result.exit_code == 0
    assert "No token usage available." in result.output


def test_generate_sections_output_full(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        stage = pipeline.last_stage
        stage.template = "TEMPLATE_BODY"
        stage.records = [{"a": "1"}]
        stage.metadata.variables = {"a": "digit"}
        stage.metadata.handling = ["step one", "step two"]

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--sections"]
        )

    assert result.exit_code == 0
    assert "=== TEXTFSM TEMPLATE ===" in result.output
    assert "TEMPLATE_BODY" in result.output
    assert "=== PARSED RECORDS ===" in result.output
    assert "=== VARIABLE EXPLANATIONS ===" in result.output
    assert "=== LLM HANDLING ===" in result.output
    assert "step one" in result.output
    assert "step two" in result.output


def test_generate_sections_output_missing_meta(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--sections"]
        )

    assert result.exit_code == 0
    assert "No variable explanations available." in result.output
    assert "No LLM handling information available." in result.output


def test_generate_template_only_output(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.template = "ONLY_TEMPLATE"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--template-only"]
        )

    assert result.exit_code == 0
    assert result.output.strip() == "ONLY_TEMPLATE"


def test_generate_records_output(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.records = [{"x": "1"}, {"x": "2"}]

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--records"]
        )

    assert result.exit_code == 0
    assert "{'x': '1'}" in result.output


def test_generate_handling_output_with_meta(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata.handling = ["reasoning line"]

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--handling"]
        )

    assert result.exit_code == 0
    assert "reasoning line" in result.output


def test_generate_handling_output_without_meta(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--handling"]
        )

    assert result.exit_code == 0
    assert "No LLM handling information available." in result.output


def test_generate_sample_output_with_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata.response.prompt = "the original sample text"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--sample"]
        )

    assert result.exit_code == 0
    assert "the original sample text" in result.output


def test_generate_sample_output_without_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--sample"]
        )

    assert result.exit_code == 0
    assert "No sample available." in result.output


def test_generate_raw_output_with_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata.response.raw = "raw LLM text"

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--raw"]
        )

    assert result.exit_code == 0
    assert "raw LLM text" in result.output


def test_generate_raw_output_without_response(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--raw"]
        )

    assert result.exit_code == 0
    assert "No raw LLM output available." in result.output


def test_generate_explain_output_with_meta(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata.variables = {"v1": "word"}

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--explain"]
        )

    assert result.exit_code == 0
    assert "v1" in result.output


def test_generate_explain_output_without_meta(tmp_path):
    with _mocked_generate(tmp_path) as (runner, instance, input_file):
        pipeline = instance.run.return_value
        pipeline.ready = True
        pipeline.last_stage.metadata = None

        result = runner.invoke(
            generate, [str(input_file), "--provider", "openai", "--explain"]
        )

    assert result.exit_code == 0
    assert "No variable explanations available." in result.output


# ============================================================
# resolve_api_key
# ============================================================


def test_resolve_api_key_explicit_flag_wins():
    assert resolve_api_key("openai", "explicit-key", pconf=None) == "explicit-key"


def test_resolve_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    assert resolve_api_key("openai", None, pconf=None) == "env-key"


def test_resolve_api_key_from_pconf_fallback():
    pconf = ProviderConfig(name="openai", type="openai", params={"api_key": "yaml-key"})
    assert resolve_api_key("openai", None, pconf) == "yaml-key"


def test_resolve_api_key_raises_when_missing():
    pconf = ProviderConfig(name="openai", type="openai", params={})
    with pytest.raises(Exception, match="API key not provided"):
        resolve_api_key("openai", None, pconf)


def test_resolve_api_key_bedrock_returns_none_even_if_explicit_flag_given():
    # Bedrock has no project-level api_key concept - boto3 resolves AWS
    # credentials on its own, so this always short-circuits to None.
    assert resolve_api_key("bedrock", "ignored-explicit-key", pconf=None) is None


def test_resolve_api_key_vertexai_returns_none_even_if_explicit_flag_given():
    # Vertex AI has no project-level api_key concept either - the
    # google-genai SDK resolves GCP credentials (ADC) on its own.
    assert resolve_api_key("vertexai", "ignored-explicit-key", pconf=None) is None


# ============================================================
# resolve_model
# ============================================================


def test_resolve_model_explicit_flag_wins():
    assert resolve_model("openai", "gpt-4o", pconf=None) == "gpt-4o"


def test_resolve_model_azure_from_env_deployment(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "my-deployment")
    assert resolve_model("azure", None, pconf=None) == "my-deployment"


def test_resolve_model_azure_from_pconf():
    pconf = ProviderConfig(
        name="azure", type="azure", params={"model": "deployment-from-yaml"}
    )
    assert resolve_model("azure", None, pconf) == "deployment-from-yaml"


def test_resolve_model_azure_raises_when_missing():
    pconf = ProviderConfig(name="azure", type="azure", params={})
    with pytest.raises(Exception, match="Azure requires a deployment name"):
        resolve_model("azure", None, pconf)


def test_resolve_model_non_azure_from_pconf():
    pconf = ProviderConfig(
        name="openai", type="openai", params={"model": "gpt-4o-mini"}
    )
    assert resolve_model("openai", None, pconf) == "gpt-4o-mini"


def test_resolve_model_non_azure_raises_when_missing():
    pconf = ProviderConfig(name="openai", type="openai", params={})
    with pytest.raises(Exception, match="No model provided"):
        resolve_model("openai", None, pconf)


# ============================================================
# resolve_endpoint
# ============================================================


def test_resolve_endpoint_non_azure_returns_none():
    assert resolve_endpoint("openai", "https://ignored.example.com", pconf=None) is None


def test_resolve_endpoint_azure_explicit_flag_wins():
    assert resolve_endpoint("azure", "https://explicit.example.com", pconf=None) == (
        "https://explicit.example.com"
    )


def test_resolve_endpoint_azure_from_env(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://env.example.com")
    assert resolve_endpoint("azure", None, pconf=None) == "https://env.example.com"


def test_resolve_endpoint_azure_from_pconf():
    pconf = ProviderConfig(
        name="azure", type="azure", params={"endpoint": "https://yaml.example.com"}
    )
    assert resolve_endpoint("azure", None, pconf) == "https://yaml.example.com"


def test_resolve_endpoint_azure_raises_when_missing():
    pconf = ProviderConfig(name="azure", type="azure", params={})
    with pytest.raises(Exception, match="Azure requires an endpoint"):
        resolve_endpoint("azure", None, pconf)


# ============================================================
# resolve_api_version
# ============================================================


def test_resolve_api_version_non_azure_returns_none():
    assert resolve_api_version("openai", "2024-01-01", pconf=None) is None


def test_resolve_api_version_azure_explicit_flag_wins():
    assert resolve_api_version("azure", "2024-06-01", pconf=None) == "2024-06-01"


def test_resolve_api_version_azure_from_env(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-05-01")
    assert resolve_api_version("azure", None, pconf=None) == "2024-05-01"


def test_resolve_api_version_azure_from_pconf():
    pconf = ProviderConfig(
        name="azure", type="azure", params={"api_version": "2024-03-01"}
    )
    assert resolve_api_version("azure", None, pconf) == "2024-03-01"


def test_resolve_api_version_azure_defaults_when_missing():
    pconf = ProviderConfig(name="azure", type="azure", params={})
    assert resolve_api_version("azure", None, pconf) == "2024-02-15-preview"


# ============================================================
# resolve_region
# ============================================================


def test_resolve_region_non_bedrock_returns_none():
    assert resolve_region("openai", "us-east-1", pconf=None) is None


def test_resolve_region_bedrock_explicit_flag_wins():
    assert resolve_region("bedrock", "eu-central-1", pconf=None) == "eu-central-1"


def test_resolve_region_bedrock_from_aws_region_env(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    assert resolve_region("bedrock", None, pconf=None) == "us-east-1"


def test_resolve_region_bedrock_from_aws_default_region_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    assert resolve_region("bedrock", None, pconf=None) == "eu-west-1"


def test_resolve_region_bedrock_from_pconf():
    pconf = ProviderConfig(
        name="bedrock", type="bedrock", params={"region": "ap-south-1"}
    )
    assert resolve_region("bedrock", None, pconf) == "ap-south-1"


def test_resolve_region_bedrock_raises_when_missing():
    pconf = ProviderConfig(name="bedrock", type="bedrock", params={})
    with pytest.raises(Exception, match="Bedrock requires an AWS region"):
        resolve_region("bedrock", None, pconf)


def test_resolve_region_vertexai_explicit_flag_wins():
    assert resolve_region("vertexai", "europe-west4", pconf=None) == "europe-west4"


def test_resolve_region_vertexai_from_google_cloud_location_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    assert resolve_region("vertexai", None, pconf=None) == "us-central1"


def test_resolve_region_vertexai_from_pconf():
    pconf = ProviderConfig(
        name="vertexai", type="vertexai", params={"region": "asia-northeast1"}
    )
    assert resolve_region("vertexai", None, pconf) == "asia-northeast1"


def test_resolve_region_vertexai_raises_when_missing():
    pconf = ProviderConfig(name="vertexai", type="vertexai", params={})
    with pytest.raises(Exception, match="Vertex AI requires a GCP location"):
        resolve_region("vertexai", None, pconf)


# ============================================================
# resolve_project
# ============================================================


def test_resolve_project_non_vertexai_returns_none():
    assert resolve_project("openai", "ignored-project", pconf=None) is None


def test_resolve_project_vertexai_explicit_flag_wins():
    assert resolve_project("vertexai", "explicit-project", pconf=None) == (
        "explicit-project"
    )


def test_resolve_project_vertexai_from_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "env-project")
    assert resolve_project("vertexai", None, pconf=None) == "env-project"


def test_resolve_project_vertexai_from_pconf():
    pconf = ProviderConfig(
        name="vertexai", type="vertexai", params={"project": "yaml-project"}
    )
    assert resolve_project("vertexai", None, pconf) == "yaml-project"


def test_resolve_project_vertexai_raises_when_missing():
    pconf = ProviderConfig(name="vertexai", type="vertexai", params={})
    with pytest.raises(Exception, match="Vertex AI requires a GCP project"):
        resolve_project("vertexai", None, pconf)
