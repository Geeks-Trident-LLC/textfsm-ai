# tests/cli/test_list_models_cmd.py

from __future__ import annotations

from unittest.mock import patch

import anyask
from click.testing import CliRunner

from textfsm_ai.cli.list_models_cmd import list_models


def _invoke(args, **anyask_list_models_kwargs):
    runner = CliRunner()
    with patch(
        "textfsm_ai.cli.list_models_cmd.anyask.list_models", **anyask_list_models_kwargs
    ) as mock_list_models:
        result = runner.invoke(list_models, args)
    return result, mock_list_models


def test_list_models_unknown_provider():
    result, _ = _invoke(
        ["nope"], side_effect=anyask.ProviderNotFoundError("Unknown provider: nope")
    )

    assert result.exit_code == 0
    assert "Unknown provider or unsupported model listing: nope" in result.output
    assert "textfsm-ai providers list" in result.output


def test_list_models_provider_without_listing_support():
    result, _ = _invoke(
        ["no-listing"],
        side_effect=anyask.ProviderNotFoundError(
            "Provider 'no-listing' does not support model listing"
        ),
    )

    assert result.exit_code == 0
    assert "Unknown provider or unsupported model listing: no-listing" in result.output


def test_list_models_success():
    result, mock_list_models = _invoke(["fake"], return_value=["model-a", "model-b"])

    assert result.exit_code == 0
    assert "Fetching models from provider: fake" in result.output
    assert "Models for provider: fake" in result.output
    assert "model-a" in result.output
    assert "model-b" in result.output
    mock_list_models.assert_called_once_with("fake")


def test_list_models_error():
    result, _ = _invoke(["fake"], side_effect=RuntimeError("api down"))

    assert result.exit_code == 0
    assert "Error: api down" in result.output
