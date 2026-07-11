# tests/cli/test_list_models_cmd.py

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from textfsm_ai.cli.list_models_cmd import list_models
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class _NoListingProvider:
    """A provider class that does NOT implement ModelListingMixin."""

    name = "no-listing"


def _make_provider(
    curated=None, latest=None, latest_error=None, raw=None, raw_error=None
):
    """Build a fake provider class implementing ModelListingMixin with
    controllable behavior for each mode list_models supports."""

    class _FakeProvider(ModelListingMixin):
        name = "fake"

        @classmethod
        def list_models_curated(cls):
            return curated if curated is not None else {}

        @classmethod
        def from_env(cls):
            return cls()

        def classify_models(self):
            if latest_error:
                raise latest_error
            return latest if latest is not None else {}

        def fetch_latest_models(self):
            if raw_error:
                raise raw_error
            return raw if raw is not None else []

    return _FakeProvider


def _invoke(provider_cls, args):
    runner = CliRunner()
    with patch("textfsm_ai.cli.list_models_cmd.registry") as mock_registry:
        if provider_cls is None:
            mock_registry.get.side_effect = KeyError("unknown")
        else:
            mock_registry.get.return_value = provider_cls
        result = runner.invoke(list_models, args)
    return result


def test_list_models_unknown_provider():
    result = _invoke(None, ["nope"])

    assert result.exit_code == 0
    assert "Unknown provider: nope" in result.output
    assert "textfsm-ai providers list" in result.output


def test_list_models_provider_without_listing_support():
    result = _invoke(_NoListingProvider, ["no-listing"])

    assert result.exit_code == 0
    assert "does not support model listing" in result.output


def test_list_models_default_curated_no_filters_shows_all_groups():
    curated = {
        "quality-chat": ["q-model"],
        "balance-chat": ["b-model"],
        "speed-chat": ["s-model"],
        "thinking-chat": ["t-model"],
        "other": ["o-model"],
    }
    result = _invoke(_make_provider(curated=curated), ["fake"])

    assert result.exit_code == 0
    assert "Models for provider: fake" in result.output
    assert "(latest)" not in result.output
    for model in ["q-model", "b-model", "s-model", "t-model", "o-model"]:
        assert model in result.output


def test_list_models_default_curated_group_with_no_models_is_skipped():
    curated = {"quality-chat": ["q-model"], "balance-chat": []}
    result = _invoke(
        _make_provider(curated=curated), ["fake", "--quality", "--balance"]
    )

    assert result.exit_code == 0
    assert "q-model" in result.output
    assert "balance-chat:" not in result.output


def test_list_models_quality_filter():
    curated = {"quality-chat": ["q-model"], "balance-chat": ["b-model"]}
    result = _invoke(_make_provider(curated=curated), ["fake", "--quality"])

    assert result.exit_code == 0
    assert "q-model" in result.output
    assert "b-model" not in result.output


def test_list_models_balance_filter():
    curated = {"quality-chat": ["q-model"], "balance-chat": ["b-model"]}
    result = _invoke(_make_provider(curated=curated), ["fake", "--balance"])

    assert result.exit_code == 0
    assert "b-model" in result.output
    assert "q-model" not in result.output


def test_list_models_speed_filter():
    curated = {"speed-chat": ["s-model"], "quality-chat": ["q-model"]}
    result = _invoke(_make_provider(curated=curated), ["fake", "--speed"])

    assert result.exit_code == 0
    assert "s-model" in result.output
    assert "q-model" not in result.output


def test_list_models_premium_filter():
    curated = {"thinking-chat": ["t-model"], "quality-chat": ["q-model"]}
    result = _invoke(_make_provider(curated=curated), ["fake", "--premium"])

    assert result.exit_code == 0
    assert "t-model" in result.output
    assert "q-model" not in result.output


def test_list_models_no_premium_filter():
    curated = {
        "thinking-chat": ["t-model"],
        "quality-chat": ["q-model"],
        "balance-chat": ["b-model"],
        "speed-chat": ["s-model"],
    }
    result = _invoke(_make_provider(curated=curated), ["fake", "--no-premium"])

    assert result.exit_code == 0
    assert "t-model" not in result.output
    assert "q-model" in result.output
    assert "b-model" in result.output
    assert "s-model" in result.output


def test_list_models_combined_filters_union():
    curated = {
        "quality-chat": ["q-model"],
        "speed-chat": ["s-model"],
        "balance-chat": ["b-model"],
    }
    result = _invoke(_make_provider(curated=curated), ["fake", "--quality", "--speed"])

    assert result.exit_code == 0
    assert "q-model" in result.output
    assert "s-model" in result.output
    assert "b-model" not in result.output


def test_list_models_latest_success():
    latest = {"quality-chat": ["fresh-model"]}
    result = _invoke(_make_provider(latest=latest), ["fake", "--latest"])

    assert result.exit_code == 0
    assert "Fetching latest models from provider: fake" in result.output
    assert "Models for provider: fake (latest)" in result.output
    assert "fresh-model" in result.output


def test_list_models_latest_error():
    result = _invoke(
        _make_provider(latest_error=RuntimeError("api down")), ["fake", "--latest"]
    )

    assert result.exit_code == 0
    assert "Error: api down" in result.output


def test_list_models_latest_raw_success():
    result = _invoke(
        _make_provider(raw=["model-a", "model-b"]), ["fake", "--latest-raw"]
    )

    assert result.exit_code == 0
    assert "Raw model names (no classification):" in result.output
    assert "model-a" in result.output
    assert "model-b" in result.output


def test_list_models_latest_raw_error():
    result = _invoke(
        _make_provider(raw_error=RuntimeError("api down")), ["fake", "--latest-raw"]
    )

    assert result.exit_code == 0
    assert "Error: api down" in result.output


def test_list_models_latest_takes_priority_over_latest_raw():
    latest = {"quality-chat": ["fresh-model"]}
    result = _invoke(
        _make_provider(latest=latest, raw=["raw-model"]),
        ["fake", "--latest", "--latest-raw"],
    )

    assert result.exit_code == 0
    assert "fresh-model" in result.output
    assert "Raw model names" not in result.output
