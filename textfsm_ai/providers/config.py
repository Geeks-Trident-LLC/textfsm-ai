# textfsm_ai/providers/config.py

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass
class ProviderConfig:
    name: str
    type: str
    params: Dict[str, Any]


@dataclass
class OrchestratorConfig:
    providers: Dict[str, ProviderConfig]


def load_config_from_file(path: str = "") -> OrchestratorConfig:
    if not path:
        from textfsm_ai import BASE_DIR

        path = str(BASE_DIR / "models" / "providers.yaml")

    if not os.path.exists(path):
        return OrchestratorConfig(providers={})

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    providers_cfg: Dict[str, ProviderConfig] = {}

    raw_providers = data.get("providers") or {}

    for name, item in raw_providers.items():
        providers_cfg[name] = ProviderConfig(
            name=name,
            type=item["type"],
            params=item.get("params", {}),
        )

    return OrchestratorConfig(providers=providers_cfg)


def load_config_from_env() -> OrchestratorConfig:
    providers_cfg: Dict[str, ProviderConfig] = {}

    if os.getenv("OPENAI_API_KEY"):
        providers_cfg["openai"] = ProviderConfig(
            name="openai",
            type="openai",
            params={"api_key": os.getenv("OPENAI_API_KEY")},
        )

    if os.getenv("ANTHROPIC_API_KEY"):
        providers_cfg["anthropic"] = ProviderConfig(
            name="anthropic",
            type="anthropic",
            params={"api_key": os.getenv("ANTHROPIC_API_KEY")},
        )

    if os.getenv("GEMINI_API_KEY"):
        providers_cfg["gemini"] = ProviderConfig(
            name="gemini",
            type="gemini",
            params={"api_key": os.getenv("GEMINI_API_KEY")},
        )

    if os.getenv("DEEPSEEK_API_KEY"):
        providers_cfg["deepseek"] = ProviderConfig(
            name="deepseek",
            type="deepseek",
            params={"api_key": os.getenv("DEEPSEEK_API_KEY")},
        )

    if os.getenv("GROQ_API_KEY"):
        providers_cfg["groq"] = ProviderConfig(
            name="groq",
            type="groq",
            params={"api_key": os.getenv("GROQ_API_KEY")},
        )

    if os.getenv("XAI_API_KEY"):
        providers_cfg["xai"] = ProviderConfig(
            name="xai",
            type="xai",
            params={"api_key": os.getenv("XAI_API_KEY")},
        )

    if os.getenv("TOGETHER_API_KEY"):
        providers_cfg["together"] = ProviderConfig(
            name="together",
            type="together",
            params={"api_key": os.getenv("TOGETHER_API_KEY")},
        )

    if os.getenv("FIREWORKS_API_KEY"):
        providers_cfg["fireworks"] = ProviderConfig(
            name="fireworks",
            type="fireworks",
            params={"api_key": os.getenv("FIREWORKS_API_KEY")},
        )

    if os.getenv("CEREBRAS_API_KEY"):
        providers_cfg["cerebras"] = ProviderConfig(
            name="cerebras",
            type="cerebras",
            params={"api_key": os.getenv("CEREBRAS_API_KEY")},
        )

    if os.getenv("PERPLEXITY_API_KEY"):
        providers_cfg["perplexity"] = ProviderConfig(
            name="perplexity",
            type="perplexity",
            params={"api_key": os.getenv("PERPLEXITY_API_KEY")},
        )

    if os.getenv("OPENROUTER_API_KEY"):
        providers_cfg["openrouter"] = ProviderConfig(
            name="openrouter",
            type="openrouter",
            params={"api_key": os.getenv("OPENROUTER_API_KEY")},
        )

    if os.getenv("MOONSHOT_API_KEY"):
        providers_cfg["moonshot"] = ProviderConfig(
            name="moonshot",
            type="moonshot",
            params={"api_key": os.getenv("MOONSHOT_API_KEY")},
        )

    if os.getenv("MISTRAL_API_KEY"):
        providers_cfg["mistral"] = ProviderConfig(
            name="mistral",
            type="mistral",
            params={"api_key": os.getenv("MISTRAL_API_KEY")},
        )

    aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    if aws_region:
        providers_cfg["bedrock"] = ProviderConfig(
            name="bedrock",
            type="bedrock",
            # No api_key here - boto3 resolves AWS credentials on its own
            # (AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_SESSION_TOKEN,
            # ~/.aws/credentials, or an IAM role), so region is the only
            # Bedrock-specific param this app needs to track.
            params={"region": aws_region},
        )

    if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
        providers_cfg["azure"] = ProviderConfig(
            name="azure",
            type="azure",
            params={
                "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                "api_version": os.getenv(
                    "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
                ),
            },
        )

    return OrchestratorConfig(providers=providers_cfg)
