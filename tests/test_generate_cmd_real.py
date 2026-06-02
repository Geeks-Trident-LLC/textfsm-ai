from __future__ import annotations

import json
import os
from click.testing import CliRunner

import pytest

from textfsm_ai.cli.generate_cmd import generate


@pytest.mark.integration
@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="Requires OPENAI_API_KEY in environment",
)
def test_generate_real_openai(tmp_path):
    """
    Real integration test:
    - Calls the real generate command
    - Uses the real orchestrator
    - Sends a real request to OpenAI
    """

    # Create a temporary input file
    input_file = tmp_path / "input.txt"
    input_file.write_text(
        "Extract hostname from this output:\nhostname Router1", encoding="utf-8"
    )

    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            str(input_file),
            "--model",
            "openai/gpt-4o-mini",
        ],
    )

    # Basic assertions
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0

    # The model should return something TextFSM-like
    assert "Router1" in result.output
