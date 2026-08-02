# tests/cli/test_list_models_cmd.py

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from textfsm_ai.cli.list_models_cmd import list_models
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class _NoListingProvider:
    """A provider class that does NOT implement ModelListingMixin."""

    name = "no-listing"


def _make_provider(raw=None, raw_error=None):
    """Build a fake provider class implementing ModelListingMixin with
    controllable fetch_latest_models() behavior."""

    class _FakeProvider(ModelListingMixin):
        name = "fake"

        @classmethod
        def from_env(cls):
            return cls()

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


def test_list_models_success():
    result = _invoke(_make_provider(raw=["model-a", "model-b"]), ["fake"])

    assert result.exit_code == 0
    assert "Fetching models from provider: fake" in result.output
    assert "Models for provider: fake" in result.output
    assert "model-a" in result.output
    assert "model-b" in result.output


def test_list_models_error():
    result = _invoke(_make_provider(raw_error=RuntimeError("api down")), ["fake"])

    assert result.exit_code == 0
    assert "Error: api down" in result.output
