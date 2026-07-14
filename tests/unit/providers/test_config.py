import pytest

from textfsm_ai.providers.config import load_config_from_env, load_config_from_file

_ENV_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "GROQ_API_KEY",
    "XAI_API_KEY",
    "TOGETHER_API_KEY",
    "FIREWORKS_API_KEY",
    "CEREBRAS_API_KEY",
    "PERPLEXITY_API_KEY",
    "OPENROUTER_API_KEY",
    "MOONSHOT_API_KEY",
    "MISTRAL_API_KEY",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "COHERE_API_KEY",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_API_VERSION",
    "OCI_COMPARTMENT_ID",
    "OCI_REGION",
]


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for var in _ENV_VARS:
        monkeypatch.delenv(var, raising=False)


# ============================================================
# load_config_from_file
# ============================================================


def test_load_config_from_file_nonexistent_path_returns_empty():
    cfg = load_config_from_file("does/not/exist.yaml")
    assert cfg.providers == {}


def test_load_config_from_file_parses_providers(tmp_path):
    yaml_file = tmp_path / "providers.yaml"
    yaml_file.write_text(
        """
providers:
  openai:
    type: openai
    params:
      api_key: sk-abc
      model: gpt-4o-mini
  anthropic:
    type: anthropic
    params: {}
""",
        encoding="utf-8",
    )

    cfg = load_config_from_file(str(yaml_file))

    assert set(cfg.providers.keys()) == {"openai", "anthropic"}
    assert cfg.providers["openai"].type == "openai"
    assert cfg.providers["openai"].params == {
        "api_key": "sk-abc",
        "model": "gpt-4o-mini",
    }
    assert cfg.providers["anthropic"].params == {}


def test_load_config_from_file_empty_yaml(tmp_path):
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("", encoding="utf-8")

    cfg = load_config_from_file(str(yaml_file))
    assert cfg.providers == {}


def test_load_config_from_file_no_providers_key(tmp_path):
    yaml_file = tmp_path / "no_providers.yaml"
    yaml_file.write_text("other_key: value\n", encoding="utf-8")

    cfg = load_config_from_file(str(yaml_file))
    assert cfg.providers == {}


def test_load_config_from_file_default_path_uses_real_providers_yaml():
    # No explicit path -> resolves to BASE_DIR / models / providers.yaml.
    # Just confirm it doesn't blow up and returns a config object.
    cfg = load_config_from_file()
    assert cfg.providers is not None


# ============================================================
# load_config_from_env
# ============================================================


def test_load_config_from_env_no_vars_set_returns_empty():
    cfg = load_config_from_env()
    assert cfg.providers == {}


def test_load_config_from_env_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"openai"}
    assert cfg.providers["openai"].type == "openai"
    assert cfg.providers["openai"].params == {"api_key": "sk-openai"}


def test_load_config_from_env_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"anthropic"}
    assert cfg.providers["anthropic"].params == {"api_key": "sk-anthropic"}


def test_load_config_from_env_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "sk-gemini")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"gemini"}
    assert cfg.providers["gemini"].params == {"api_key": "sk-gemini"}


def test_load_config_from_env_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"deepseek"}
    assert cfg.providers["deepseek"].params == {"api_key": "sk-deepseek"}


def test_load_config_from_env_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "sk-groq")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"groq"}
    assert cfg.providers["groq"].params == {"api_key": "sk-groq"}


def test_load_config_from_env_xai(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "sk-xai")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"xai"}
    assert cfg.providers["xai"].params == {"api_key": "sk-xai"}


def test_load_config_from_env_together(monkeypatch):
    monkeypatch.setenv("TOGETHER_API_KEY", "sk-together")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"together"}
    assert cfg.providers["together"].params == {"api_key": "sk-together"}


def test_load_config_from_env_fireworks(monkeypatch):
    monkeypatch.setenv("FIREWORKS_API_KEY", "sk-fireworks")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"fireworks"}
    assert cfg.providers["fireworks"].params == {"api_key": "sk-fireworks"}


def test_load_config_from_env_cerebras(monkeypatch):
    monkeypatch.setenv("CEREBRAS_API_KEY", "sk-cerebras")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"cerebras"}
    assert cfg.providers["cerebras"].params == {"api_key": "sk-cerebras"}


def test_load_config_from_env_perplexity(monkeypatch):
    monkeypatch.setenv("PERPLEXITY_API_KEY", "sk-perplexity")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"perplexity"}
    assert cfg.providers["perplexity"].params == {"api_key": "sk-perplexity"}


def test_load_config_from_env_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-openrouter")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"openrouter"}
    assert cfg.providers["openrouter"].params == {"api_key": "sk-openrouter"}


def test_load_config_from_env_moonshot(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-moonshot")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"moonshot"}
    assert cfg.providers["moonshot"].params == {"api_key": "sk-moonshot"}


def test_load_config_from_env_mistral(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "sk-mistral")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"mistral"}
    assert cfg.providers["mistral"].params == {"api_key": "sk-mistral"}


def test_load_config_from_env_bedrock_aws_region(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"bedrock"}
    assert cfg.providers["bedrock"].params == {"region": "us-east-1"}


def test_load_config_from_env_bedrock_aws_default_region(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-central-1")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"bedrock"}
    assert cfg.providers["bedrock"].params == {"region": "eu-central-1"}


def test_load_config_from_env_cohere(monkeypatch):
    monkeypatch.setenv("COHERE_API_KEY", "sk-cohere")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"cohere"}
    assert cfg.providers["cohere"].params == {"api_key": "sk-cohere"}


def test_load_config_from_env_vertexai_requires_both_project_and_location(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    # location missing -> vertexai should NOT appear
    cfg = load_config_from_env()
    assert "vertexai" not in cfg.providers


def test_load_config_from_env_vertexai_with_both_vars(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"vertexai"}
    assert cfg.providers["vertexai"].params == {
        "project": "my-project",
        "region": "us-central1",
    }


def test_load_config_from_env_oci_requires_compartment_id(monkeypatch):
    monkeypatch.setenv("OCI_REGION", "us-chicago-1")
    # compartment id missing -> oci should NOT appear
    cfg = load_config_from_env()
    assert "oci" not in cfg.providers


def test_load_config_from_env_oci_compartment_id_only(monkeypatch):
    monkeypatch.setenv("OCI_COMPARTMENT_ID", "ocid1.compartment.oc1..fake")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"oci"}
    assert cfg.providers["oci"].params == {
        "compartment_id": "ocid1.compartment.oc1..fake"
    }


def test_load_config_from_env_oci_with_region(monkeypatch):
    monkeypatch.setenv("OCI_COMPARTMENT_ID", "ocid1.compartment.oc1..fake")
    monkeypatch.setenv("OCI_REGION", "us-chicago-1")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"oci"}
    assert cfg.providers["oci"].params == {
        "compartment_id": "ocid1.compartment.oc1..fake",
        "region": "us-chicago-1",
    }


def test_load_config_from_env_azure_requires_both_endpoint_and_key(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.azure.com")
    # api key missing -> azure should NOT appear
    cfg = load_config_from_env()
    assert "azure" not in cfg.providers


def test_load_config_from_env_azure_with_both_vars(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "sk-azure")
    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {"azure"}
    assert cfg.providers["azure"].params == {
        "endpoint": "https://example.azure.com",
        "api_key": "sk-azure",
        "api_version": "2024-02-15-preview",
    }


def test_load_config_from_env_azure_custom_api_version(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "sk-azure")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    cfg = load_config_from_env()

    assert cfg.providers["azure"].params["api_version"] == "2024-06-01"


def test_load_config_from_env_all_providers_at_once(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k2")
    monkeypatch.setenv("GEMINI_API_KEY", "k3")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k4")
    monkeypatch.setenv("GROQ_API_KEY", "k6")
    monkeypatch.setenv("XAI_API_KEY", "k7")
    monkeypatch.setenv("TOGETHER_API_KEY", "k8")
    monkeypatch.setenv("FIREWORKS_API_KEY", "k9")
    monkeypatch.setenv("CEREBRAS_API_KEY", "k10")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "k11")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k12")
    monkeypatch.setenv("MOONSHOT_API_KEY", "k13")
    monkeypatch.setenv("MISTRAL_API_KEY", "k14")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("COHERE_API_KEY", "k15")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "k5")
    monkeypatch.setenv("OCI_COMPARTMENT_ID", "ocid1.compartment.oc1..fake")

    cfg = load_config_from_env()

    assert set(cfg.providers.keys()) == {
        "openai",
        "anthropic",
        "gemini",
        "deepseek",
        "groq",
        "xai",
        "together",
        "fireworks",
        "cerebras",
        "perplexity",
        "openrouter",
        "moonshot",
        "mistral",
        "bedrock",
        "cohere",
        "vertexai",
        "azure",
        "oci",
    }
