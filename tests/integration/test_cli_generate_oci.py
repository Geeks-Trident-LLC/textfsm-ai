# tests/integration/test_cli_generate_oci.py

from __future__ import annotations

import pytest
from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.models import model as MODEL


@pytest.mark.integration
def test_real_oci(tmp_path, oci_compartment_id, oci_region):
    # Create a temporary input file
    input_file = tmp_path / "input.txt"
    input_file.write_text(
        "Extract hostname from this output:\nhostname Router1",
        encoding="utf-8",
    )
    runner = CliRunner()
    args = [
        str(input_file),
        "--provider",
        "oci",
        "--model",
        MODEL.oci.default,
        "--compartment-id",
        oci_compartment_id,
    ]
    if oci_region:
        args += ["--region", oci_region]

    result = runner.invoke(generate, args)

    # Basic assertions
    assert result.exit_code == 0, f"Generation failed: {result.reason}"
    template = result.output.strip()

    # The model should return something TextFSM-like
    for expected in ("Value ", "\n\nStart", " ^hostname"):
        assert expected in template
