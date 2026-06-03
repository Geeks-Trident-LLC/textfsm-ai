from __future__ import annotations

import os

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate


@pytest.mark.integration
def test_generate_real_openai(tmp_path):
    """
    Real integration test that exercises the full CLI + async orchestrator +
    OpenAI provider stack. Only runs when OPENAI_API_KEY and TEST_REAL=true
    are set in the environment.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("Requires OPENAI_API_KEY")

    if os.environ.get("TEST_REAL") != "true":
        pytest.skip("Requires TEST_REAL=true")

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
            "openai/gpt-4o-mini",
        ],
    )

    # Basic assertions
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0

    # The model should return something TextFSM-like
    assert "Router1" in result.output
