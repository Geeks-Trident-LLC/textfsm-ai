# tests/unit/generation/support/test_prompt_builder.py

from pathlib import Path

import pytest

from textfsm_ai.generation.support.prompt_builder import PromptBuilder


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
@pytest.fixture
def tmp_prompts(tmp_path: Path):
    """
    Creates a temporary prompts.yaml file with minimal valid content.
    """
    yaml_content = """
base: |
  BASE_PROMPT

correction: |
  {base}

  PREV:
  {prev_response}

  FINDINGS:
  {finding}

  SAMPLE:
  {sample}
"""
    p = tmp_path / "prompts.yaml"
    p.write_text(yaml_content)
    return p


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
def test_load_yaml_success(tmp_prompts):
    builder = PromptBuilder(prompts_path=tmp_prompts)
    assert "base" in builder.prompts
    assert "correction" in builder.prompts


def test_load_yaml_missing_file(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        PromptBuilder(prompts_path=missing)


def test_get_success(tmp_prompts):
    builder = PromptBuilder(prompts_path=tmp_prompts)
    assert builder._get("base").startswith("BASE_PROMPT")


def test_get_missing_key(tmp_prompts):
    builder = PromptBuilder(prompts_path=tmp_prompts)
    with pytest.raises(KeyError):
        builder._get("does_not_exist")


def test_base_prompt(tmp_prompts):
    builder = PromptBuilder(prompts_path=tmp_prompts)
    sample = "interface Gi0/1"

    out = builder.base_prompt(sample)

    assert "BASE_PROMPT" in out
    assert "Sample" in out
    assert "interface Gi0/1" in out
    assert "=============================" in out


def test_correction_prompt(tmp_prompts):
    builder = PromptBuilder(prompts_path=tmp_prompts)

    sample = "show version"
    prev = '{"template": "..."}'
    findings = ["error1", "error2"]

    out = builder.correction_prompt(sample, prev, findings)

    # Base prompt included
    assert "BASE_PROMPT" in out

    # Previous response included
    assert "PREV:" in out
    assert prev in out

    # Findings included
    assert "FINDINGS:" in out
    assert "error1" in out
    assert "error2" in out

    # Sample included
    assert "SAMPLE:" in out
    assert sample in out
