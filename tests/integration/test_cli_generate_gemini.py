# tests/integration/test_cli_generate_gemini.py

from __future__ import annotations

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.models import model as MODEL


@pytest.mark.integration
def test_real_gemini(tmp_path, gemini_key):
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
            "--model",
            MODEL.gemini.default,
        ],
    )

    # Basic assertions
    assert result.exit_code == 0
    assert result.output.strip()

    # The model should return something TextFSM-like
    assert "Router1" in result.output
