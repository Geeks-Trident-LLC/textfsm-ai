# tests/integration/test_cli_generate_anthropic.py

from __future__ import annotations

import os

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate


@pytest.mark.integration
def test_real_anthropic(tmp_path, azure_key):
    # Create a temporary input file
    input_file = tmp_path / "input.txt"
    input_file.write_text(
        "Extract hostname from this output:\nhostname Router1",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        generate,
        [
            str(input_file),
            "--provider",
            "azure",
            "--model",
            "gpt-4.1-textfsm-ai",
            "--endpoint",
            os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "--api-version",
            os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        ],
    )

    # Basic assertions
    assert result.exit_code == 0, f"Generation failed: {result.reason}"
    template = result.output.strip()

    # The model should return something TextFSM-like
    for expected in ("Value ", "\n\nStart", " ^hostname"):
        assert expected in template
