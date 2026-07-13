import logging
from datetime import datetime, timezone

import pytest

from textfsm_ai.core.pricing import (
    PRICING_DATA_PATH,
    PRICING_TABLE,
    PricingResult,
    estimate_cost,
    extract_base_model,
    update_claude_sonnet_5,
)

# ---------------------------------------------------------------------------
# pricing.yaml loading
# ---------------------------------------------------------------------------


def test_pricing_data_path_exists_and_is_yaml():
    assert PRICING_DATA_PATH.exists()
    assert PRICING_DATA_PATH.name == "pricing.yaml"


def test_pricing_table_loaded_from_yaml_has_expected_providers():
    # "azure" is deliberately excluded here - it's derived at import time,
    # not present in pricing.yaml itself.
    for provider in (
        "anthropic",
        "openai",
        "deepseek",
        "gemini",
        "groq",
        "xai",
        "together",
        "fireworks",
        "cerebras",
        "perplexity",
    ):
        assert provider in PRICING_TABLE
        assert isinstance(PRICING_TABLE[provider], dict)
        assert PRICING_TABLE[provider]  # non-empty


# ---------------------------------------------------------------------------
# Model-family extraction
# ---------------------------------------------------------------------------


def test_extract_base_model_openai():
    provider = "openai"
    for model, based_model in (
        ("gpt-4o-2024-08-06", "gpt-4o"),
        ("gpt-4o-mini-2024-09-12", "gpt-4o-mini"),
        ("gpt-5.4-mini-20250101", "gpt-5.4-mini"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_anthropic():
    provider = "anthropic"
    for model, based_model in (
        ("claude-opus-3-20240229", "claude-opus-3"),
        ("claude-sonnet-3-5-20241021", "claude-sonnet-3-5"),
        ("claude-haiku-4-5-20250101", "claude-haiku-4-5"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_deepseek():
    provider = "deepseek"
    for model, based_model in (
        ("deepseek-v4-flash", "deepseek-v4-flash"),
        ("deepseek-v4-pro-20250101", "deepseek-v4-pro"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_groq():
    provider = "groq"
    for model, based_model in (
        ("llama-3.3-70b-versatile", "llama-3.3-70b-versatile"),
        ("llama-3.1-8b-instant", "llama-3.1-8b-instant"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_xai():
    provider = "xai"
    for model, based_model in (
        ("grok-4", "grok-4"),
        ("grok-3-mini", "grok-3-mini"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_together():
    provider = "together"
    for model, based_model in (
        (
            "meta-llama/Llama-3.1-8B-Instruct-Turbo",
            "meta-llama/Llama-3.1-8B-Instruct-Turbo",
        ),
        (
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
        ),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_fireworks():
    provider = "fireworks"
    for model, based_model in (
        (
            "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "accounts/fireworks/models/llama-v3p1-8b-instruct",
        ),
        (
            "accounts/fireworks/models/mixtral-8x22b-instruct",
            "accounts/fireworks/models/mixtral-8x22b-instruct",
        ),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_cerebras():
    provider = "cerebras"
    for model, based_model in (
        ("llama3.1-8b", "llama3.1-8b"),
        ("qwen-3-32b", "qwen-3-32b"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_perplexity():
    provider = "perplexity"
    for model, based_model in (
        ("sonar", "sonar"),
        ("sonar-pro", "sonar-pro"),
    ):
        assert extract_base_model(provider, model) == based_model


def test_extract_base_model_unknown_provider():
    assert extract_base_model("unknown", "gpt-4o") == ""


def test_extract_base_model_no_match():
    assert extract_base_model("openai", "nonexistent-model") == ""


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------


def test_estimate_cost_basic():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="openai",
        model="gpt-4o-2024-08-06",
    )

    assert result.provider == "openai"
    assert result.based_model == "gpt-4o"
    assert result.input_per_million == PRICING_TABLE["openai"]["gpt-4o"]["input"]
    assert result.output_per_million == PRICING_TABLE["openai"]["gpt-4o"]["output"]
    assert result.warning is None

    # Cost math
    input_cost = (1000 / 1_000_000) * result.input_per_million
    output_cost = (2000 / 1_000_000) * result.output_per_million
    other_cost = (0 / 1_000_000) * result.output_per_million
    assert result.estimated_cost == pytest.approx(input_cost + output_cost + other_cost)


def test_estimate_cost_groq():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="groq",
        model="llama-3.1-8b-instant",
    )

    assert result.provider == "groq"
    assert result.based_model == "llama-3.1-8b-instant"
    assert (
        result.input_per_million
        == PRICING_TABLE["groq"]["llama-3.1-8b-instant"]["input"]
    )
    assert (
        result.output_per_million
        == PRICING_TABLE["groq"]["llama-3.1-8b-instant"]["output"]
    )
    assert result.warning is None


def test_estimate_cost_xai():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="xai",
        model="grok-3-mini",
    )

    assert result.provider == "xai"
    assert result.based_model == "grok-3-mini"
    assert result.input_per_million == PRICING_TABLE["xai"]["grok-3-mini"]["input"]
    assert result.output_per_million == PRICING_TABLE["xai"]["grok-3-mini"]["output"]
    assert result.warning is None


def test_estimate_cost_together():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="together",
        model="meta-llama/Llama-3.1-8B-Instruct-Turbo",
    )

    assert result.provider == "together"
    assert result.based_model == "meta-llama/Llama-3.1-8B-Instruct-Turbo"
    assert (
        result.input_per_million
        == PRICING_TABLE["together"]["meta-llama/Llama-3.1-8B-Instruct-Turbo"]["input"]
    )
    assert (
        result.output_per_million
        == PRICING_TABLE["together"]["meta-llama/Llama-3.1-8B-Instruct-Turbo"]["output"]
    )
    assert result.warning is None


def test_estimate_cost_fireworks():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="fireworks",
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    )

    assert result.provider == "fireworks"
    assert result.based_model == "accounts/fireworks/models/llama-v3p1-8b-instruct"
    assert (
        result.input_per_million
        == PRICING_TABLE["fireworks"][
            "accounts/fireworks/models/llama-v3p1-8b-instruct"
        ]["input"]
    )
    assert (
        result.output_per_million
        == PRICING_TABLE["fireworks"][
            "accounts/fireworks/models/llama-v3p1-8b-instruct"
        ]["output"]
    )
    assert result.warning is None


def test_estimate_cost_cerebras():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="cerebras",
        model="llama3.1-8b",
    )

    assert result.provider == "cerebras"
    assert result.based_model == "llama3.1-8b"
    assert result.input_per_million == PRICING_TABLE["cerebras"]["llama3.1-8b"]["input"]
    assert (
        result.output_per_million == PRICING_TABLE["cerebras"]["llama3.1-8b"]["output"]
    )
    assert result.warning is None


def test_estimate_cost_perplexity():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="perplexity",
        model="sonar-pro",
    )

    assert result.provider == "perplexity"
    assert result.based_model == "sonar-pro"
    assert result.input_per_million == PRICING_TABLE["perplexity"]["sonar-pro"]["input"]
    assert (
        result.output_per_million == PRICING_TABLE["perplexity"]["sonar-pro"]["output"]
    )
    assert result.warning is None


def test_estimate_cost_with_reasoning_tokens():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=5000,  # 2000 reasoning tokens
        currency="USD",
        provider="openai",
        model="gpt-4o-mini-2024-09-12",
    )

    assert result.based_model == "gpt-4o-mini"

    other_tokens = 5000 - 1000 - 2000
    expected_cost = (
        (1000 / 1_000_000) * result.input_per_million
        + (2000 / 1_000_000) * result.output_per_million
        + (other_tokens / 1_000_000) * result.output_per_million
    )

    assert result.estimated_cost == pytest.approx(expected_cost)


def test_estimate_cost_pricing_family_not_found(monkeypatch):
    # extract_base_model() only ever returns a key that exists in
    # PRICING_TABLE[provider], so this branch is defensive; exercise it
    # directly by forcing a mismatch.
    monkeypatch.setattr(
        "textfsm_ai.core.pricing.extract_base_model",
        lambda provider, model: "nonexistent-family",
    )

    result = estimate_cost(
        input_tokens=100,
        output_tokens=100,
        total_tokens=200,
        currency="USD",
        provider="openai",
        model="whatever",
    )

    assert result.based_model == "nonexistent-family"
    assert result.input_per_million == 0.0
    assert result.output_per_million == 0.0
    assert result.estimated_cost == 0.0
    assert "not found" in result.warning.lower()


def test_estimate_cost_fallback():
    result = estimate_cost(
        input_tokens=1000,
        output_tokens=2000,
        total_tokens=3000,
        currency="USD",
        provider="openai",
        model="nonexistent-model",
    )

    assert result.based_model == "unknown"
    assert result.input_per_million == 0.0
    assert result.output_per_million == 0.0
    assert result.estimated_cost == 0.0
    assert "fallback" in result.warning.lower()


# ---------------------------------------------------------------------------
# PricingResult
# ---------------------------------------------------------------------------


def test_pricing_result_to_dict():
    result = PricingResult(
        provider="openai",
        based_model="gpt-4o",
        currency="USD",
        input_per_million=2.5,
        output_per_million=10.0,
        estimated_cost=0.0125,
        warning=None,
    )

    assert result.to_dict() == {
        "provider": "openai",
        "based_model": "gpt-4o",
        "currency": "USD",
        "input_per_million": 2.5,
        "output_per_million": 10.0,
        "estimated_cost": 0.0125,
        "warning": None,
    }


# ---------------------------------------------------------------------------
# Azure pricing inheritance
# ---------------------------------------------------------------------------


def test_azure_inherits_openai_pricing():
    azure_price = PRICING_TABLE["azure"]["gpt-4o"]
    openai_price = PRICING_TABLE["openai"]["gpt-4o"]
    assert azure_price == openai_price


def test_azure_includes_deepseek():
    assert "deepseek-v4-flash" in PRICING_TABLE["azure"]
    assert "deepseek-v4-pro" in PRICING_TABLE["azure"]


def test_azure_includes_anthropic_subset():
    assert "claude-opus-4-8" in PRICING_TABLE["azure"]
    assert "claude-haiku-4-5" in PRICING_TABLE["azure"]


# ---------------------------------------------------------------------------
# Sonnet-5 auto-update logic
# ---------------------------------------------------------------------------


def test_sonnet_5_intro_pricing_updates_after_cutoff(tmp_path, monkeypatch):
    # Force ack file into temp directory
    monkeypatch.setattr("textfsm_ai.core.pricing._ACK_FLAG_FILE", tmp_path / ".ack")

    # Intro pricing before cutoff
    before = datetime(2026, 8, 1, tzinfo=timezone.utc)
    update_claude_sonnet_5(now=before)
    assert PRICING_TABLE["anthropic"]["claude-sonnet-5"]["input"] == 2.00

    # After cutoff
    after = datetime(2026, 10, 1, tzinfo=timezone.utc)
    update_claude_sonnet_5(now=after)
    assert PRICING_TABLE["anthropic"]["claude-sonnet-5"]["input"] == 3.00
    assert PRICING_TABLE["anthropic"]["claude-sonnet-5"]["output"] == 15.00


def test_sonnet_5_already_updated_nags_once(tmp_path, monkeypatch, caplog):
    ack_file = tmp_path / ".ack"
    monkeypatch.setattr("textfsm_ai.core.pricing._ACK_FLAG_FILE", ack_file)
    monkeypatch.setitem(PRICING_TABLE["anthropic"]["claude-sonnet-5"], "input", 3.00)
    monkeypatch.setitem(PRICING_TABLE["anthropic"]["claude-sonnet-5"], "output", 15.00)

    after = datetime(2026, 10, 1, tzinfo=timezone.utc)

    assert not ack_file.exists()

    with caplog.at_level(logging.WARNING, logger="textfsm_ai.core.pricing"):
        update_claude_sonnet_5(now=after)

    assert ack_file.exists()
    assert any("dead code" in r.message for r in caplog.records)

    caplog.clear()

    # Second call: ack file already exists -> no repeat warning
    with caplog.at_level(logging.WARNING, logger="textfsm_ai.core.pricing"):
        update_claude_sonnet_5(now=after)

    assert caplog.records == []
