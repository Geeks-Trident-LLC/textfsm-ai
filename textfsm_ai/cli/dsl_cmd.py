# textfsm_ai/cli/dsl_cmd.py

from __future__ import annotations

import click

from textfsm_ai.core.utils.template import parse_to_dicts
from textfsm_ai.dsl.engine import dsl_engine


@click.command("dsl")
@click.argument("template_file", type=click.Path(exists=True))
@click.argument("sample_file", type=click.Path(exists=True))
@click.option(
    "--canonical", is_flag=True, help="Print only the canonical TextFSM template"
)
@click.option("--readable", is_flag=True, help="Print only the readable DSL")
@click.option("--recognizers", is_flag=True, help="Print only recognizer patterns")
@click.option(
    "--sections",
    is_flag=True,
    help="Print canonical, readable, and recognizer sections together",
)
@click.option(
    "--json", "json_output", is_flag=True, help="Print the full DSL result as JSON"
)
def dsl(
    template_file,
    sample_file,
    canonical,
    readable,
    recognizers,
    sections,
    json_output,
):
    """
    Deterministically compile a TextFSM template into its canonical form,
    readable DSL, and recognizer patterns.

    TEMPLATE_FILE is a TextFSM template. SAMPLE_FILE is raw text parsed by
    that template to infer each Value's type. No LLM call is made.
    """

    # -----------------------------
    # 1. Load template + sample
    # -----------------------------
    with open(template_file, "r", encoding="utf-8") as f:
        template = f.read()

    with open(sample_file, "r", encoding="utf-8") as f:
        sample = f.read()

    # -----------------------------
    # 2. Parse sample into records via the template itself
    # -----------------------------
    try:
        records = parse_to_dicts(template, sample)
    except Exception as ex:
        raise click.ClickException(
            f"Failed to parse sample with template: {type(ex).__name__}: {ex}"
        )

    # -----------------------------
    # 3. Run the DSL engine
    # -----------------------------
    result = dsl_engine.run(template, records)

    if not result.ready:
        raise click.ClickException(f"DSL processing failed: {result.reason}")

    # -----------------------------
    # 4. Output modes
    # -----------------------------

    # --json → full DSLParseResult JSON
    if json_output:
        import json

        click.echo(json.dumps(result.to_dict(), indent=2))
        return

    # --sections → print all 3 canonical blocks
    if sections:
        click.echo("=== CANONICAL TEMPLATE ===")
        click.echo(result.canonical)
        click.echo("")

        click.echo("=== READABLE DSL ===")
        click.echo(result.readable)
        click.echo("")

        click.echo("=== RECOGNIZER PATTERNS ===")
        for pattern in result.recognizers:
            click.echo(pattern)
        return

    # --readable → readable DSL only
    if readable:
        click.echo(result.readable)
        return

    # --recognizers → recognizer patterns only
    if recognizers:
        for pattern in result.recognizers:
            click.echo(pattern)
        return

    # --canonical (or default) → canonical template
    click.echo(result.canonical)
