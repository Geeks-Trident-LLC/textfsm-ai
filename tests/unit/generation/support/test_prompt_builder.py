# tests/unit/generation/support/test_prompt_builder.py

from pathlib import Path
from unittest.mock import patch

import pytest

from textfsm_ai.generation.support.prompt_builder import PromptBuilder

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------


@pytest.fixture
def fake_yaml():
    return {
        "one_pass_prompt": "ONE_PASS_BASE",
        "two_pass_prompt_a": "TWO_PASS_A_BASE",
        "two_pass_prompt_b": "TWO_PASS_B_BASE",
    }


@pytest.fixture
def builder(fake_yaml):
    with patch(
        "textfsm_ai.generation.support.prompt_builder.PromptBuilder._load_yaml",
        return_value=fake_yaml,
    ):
        yield PromptBuilder(prompts_path=Path("fake.yaml"))


# ------------------------------------------------------------
# _load_yaml tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.prompt_builder.yaml.safe_load")
@patch("textfsm_ai.generation.support.prompt_builder.Path.read_text")
@patch("textfsm_ai.generation.support.prompt_builder.Path.exists")
def test_load_yaml_success(mock_exists, mock_read, mock_yaml, fake_yaml):
    # Arrange
    mock_exists.return_value = True
    mock_read.return_value = "yaml content"
    mock_yaml.return_value = fake_yaml

    # Act
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    # Assert
    assert builder.prompts == fake_yaml
    mock_exists.assert_called_once()
    mock_read.assert_called_once()
    mock_yaml.assert_called_once_with("yaml content")


@patch("textfsm_ai.generation.support.prompt_builder.Path.exists")
def test_load_yaml_missing_file(mock_exists):
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError):
        PromptBuilder(prompts_path=Path("missing.yaml"))


# ------------------------------------------------------------
# _get tests
# ------------------------------------------------------------


def test_get_valid_key(builder):
    assert builder._get("one_pass_prompt") == "ONE_PASS_BASE"


def test_get_missing_key(builder):
    with pytest.raises(KeyError):
        builder._get("does_not_exist")


# ------------------------------------------------------------
# Prompt method tests
# ------------------------------------------------------------


def test_one_pass_prompt(builder):
    result = builder.one_pass_prompt("SAMPLE")
    assert result == "ONE_PASS_BASE\nSAMPLE"


def test_two_pass_prompt_a(builder):
    result = builder.two_pass_prompt_a("A")
    assert result == "TWO_PASS_A_BASE\nA"


def test_two_pass_prompt_b(builder):
    result = builder.two_pass_prompt_b("B")
    assert result == "TWO_PASS_B_BASE\nB"


# ------------------------------------------------------------
# Additional behavior tests
# ------------------------------------------------------------


def test_prompt_builder_caches_yaml(fake_yaml):
    with patch(
        "textfsm_ai.generation.support.prompt_builder.PromptBuilder._load_yaml",
        return_value=fake_yaml,
    ) as mock_load:
        b = PromptBuilder(prompts_path=Path("fake.yaml"))
        _ = b.one_pass_prompt("X")
        _ = b.two_pass_prompt_a("Y")

        # YAML should be loaded only once
        mock_load.assert_called_once()


def test_prompt_builder_handles_newlines(builder):
    result = builder.one_pass_prompt("LINE1\nLINE2")
    assert result == "ONE_PASS_BASE\nLINE1\nLINE2"


def test_prompt_builder_raises_on_missing_prompt_key():
    fake_yaml = {"one_pass_prompt": "OK"}  # missing two_pass_prompt_a

    with patch(
        "textfsm_ai.generation.support.prompt_builder.PromptBuilder._load_yaml",
        return_value=fake_yaml,
    ):
        b = PromptBuilder(prompts_path=Path("fake.yaml"))

        with pytest.raises(KeyError):
            b.two_pass_prompt_a("X")
