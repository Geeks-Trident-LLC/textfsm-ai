from pathlib import Path
from unittest.mock import patch

import pytest

from textfsm_ai.generation.prompt_builder import PromptBuilder

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

FAKE_YAML = {
    "one_pass_prompt": "ONE_PASS_BASE",
    "two_pass_prompt_a": "TWO_PASS_A_BASE",
    "two_pass_prompt_b": "TWO_PASS_B_BASE",
}


# ------------------------------------------------------------
# _load_yaml tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.prompt_builder.yaml.safe_load")
@patch("textfsm_ai.generation.prompt_builder.Path.read_text")
@patch("textfsm_ai.generation.prompt_builder.Path.exists")
def test_load_yaml_success(mock_exists, mock_read, mock_yaml):
    mock_exists.return_value = True
    mock_read.return_value = "yaml content"
    mock_yaml.return_value = FAKE_YAML

    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    assert builder.prompts == FAKE_YAML
    mock_exists.assert_called_once()
    mock_read.assert_called_once()
    mock_yaml.assert_called_once_with("yaml content")


@patch("textfsm_ai.generation.prompt_builder.Path.exists")
def test_load_yaml_missing_file(mock_exists):
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError):
        PromptBuilder(prompts_path=Path("missing.yaml"))


# ------------------------------------------------------------
# _get tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.prompt_builder.PromptBuilder._load_yaml")
def test_get_valid_key(mock_load):
    mock_load.return_value = FAKE_YAML
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    assert builder._get("one_pass_prompt") == "ONE_PASS_BASE"


@patch("textfsm_ai.generation.prompt_builder.PromptBuilder._load_yaml")
def test_get_missing_key(mock_load):
    mock_load.return_value = FAKE_YAML
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    with pytest.raises(KeyError):
        builder._get("nonexistent_key")


# ------------------------------------------------------------
# one_pass_prompt tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.prompt_builder.PromptBuilder._load_yaml")
def test_one_pass_prompt(mock_load):
    mock_load.return_value = FAKE_YAML
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    result = builder.one_pass_prompt("SAMPLE")
    assert result == "ONE_PASS_BASE\nSAMPLE"


# ------------------------------------------------------------
# two_pass_prompt_a tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.prompt_builder.PromptBuilder._load_yaml")
def test_two_pass_prompt_a(mock_load):
    mock_load.return_value = FAKE_YAML
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    result = builder.two_pass_prompt_a("SAMPLE_A")
    assert result == "TWO_PASS_A_BASE\nSAMPLE_A"


# ------------------------------------------------------------
# two_pass_prompt_b tests
# ------------------------------------------------------------


@patch("textfsm_ai.generation.prompt_builder.PromptBuilder._load_yaml")
def test_two_pass_prompt_b(mock_load):
    mock_load.return_value = FAKE_YAML
    builder = PromptBuilder(prompts_path=Path("fake.yaml"))

    result = builder.two_pass_prompt_b("SECTIONS_TEXT")
    assert result == "TWO_PASS_B_BASE\nSECTIONS_TEXT"
