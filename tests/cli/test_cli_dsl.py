# tests/cli/test_cli_dsl.py

from __future__ import annotations

import textwrap

from click.testing import CliRunner

from textfsm_ai.cli.top import main

_TEMPLATE = textwrap.dedent(
    r"""
    Value Required v1 (\S+)

    Start
      ^foo ${v1} -> Record
    """
).strip()

_SAMPLE = "foo abc\n"


def _write_fixtures(tmp_path, template=_TEMPLATE, sample=_SAMPLE):
    template_file = tmp_path / "template.textfsm"
    sample_file = tmp_path / "sample.txt"
    template_file.write_text(template, encoding="utf-8")
    sample_file.write_text(sample, encoding="utf-8")
    return str(template_file), str(sample_file)


def test_dsl_default_prints_canonical_template(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file])

    assert result.exit_code == 0
    assert "Value Required v1" in result.output
    assert r"^foo\s+${v1} -> Record" in result.output


def test_dsl_canonical_flag(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file, "--canonical"])

    assert result.exit_code == 0
    assert r"^foo\s+${v1} -> Record" in result.output


def test_dsl_readable_flag(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file, "--readable"])

    assert result.exit_code == 0
    assert "state Start:" in result.output
    assert "word(var-v1, options-Required)" in result.output


def test_dsl_recognizers_flag(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file, "--recognizers"])

    assert result.exit_code == 0
    assert result.output.strip() == r"^foo\s+[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"


def test_dsl_sections_flag(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file, "--sections"])

    assert result.exit_code == 0
    assert "=== CANONICAL TEMPLATE ===" in result.output
    assert "=== READABLE DSL ===" in result.output
    assert "=== RECOGNIZER PATTERNS ===" in result.output


def test_dsl_json_flag(tmp_path):
    template_file, sample_file = _write_fixtures(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file, "--json"])

    assert result.exit_code == 0

    import json

    data = json.loads(result.output)
    assert data["ready"] is True
    assert "canonical" in data
    assert "readable" in data
    assert "recognizers" in data


def test_dsl_invalid_template_raises_click_exception(tmp_path):
    """A template the real textfsm parser rejects should fail with a clear
    CLI error, not an unhandled traceback."""
    template_file, sample_file = _write_fixtures(
        tmp_path, template="Value v1 (unterminated[\n\nStart\n  ^foo ${v1} -> Record\n"
    )

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file])

    assert result.exit_code != 0
    assert "Failed to parse sample with template" in result.output


def test_dsl_no_matching_records_raises_click_exception(tmp_path):
    """A sample that never matches the template's rules should fail with a
    clear CLI error, not an unhandled traceback."""
    template_file, sample_file = _write_fixtures(tmp_path, sample="nomatch here\n")

    runner = CliRunner()
    result = runner.invoke(main, ["dsl", template_file, sample_file])

    assert result.exit_code != 0
    assert "DSL processing failed" in result.output


def test_dsl_missing_template_file():
    runner = CliRunner()
    result = runner.invoke(
        main, ["dsl", "does-not-exist.textfsm", "does-not-exist.txt"]
    )

    assert result.exit_code != 0
