# tests/integration/test_cli_generate_cerebras.py

from __future__ import annotations

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.models import model as MODEL


@pytest.mark.integration
def test_real_cerebras(tmp_path, cerebras_key):
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
            "cerebras",
            "--model",
            MODEL.cerebras.default,
        ],
    )

    # Basic assertions
    assert result.exit_code == 0, f"Generation failed: {result.reason}"
    template = result.output.strip()

    # The model should return something TextFSM-like
    for expected in ("Value ", "\n\nStart", " ^hostname"):
        assert expected in template
