# textfsm_ai/cli/top.py

import io
import json
import sys
import time

import click

from textfsm_ai.cli.config_group import config_group
from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.cli.ping_config_cmd import ping_config


class GlobalState:
    def __init__(self):
        self.json_output = False
        self.time_enabled = False


@click.group()
@click.option("--json", "json_output", is_flag=True)
@click.option("--time", "time_enabled", is_flag=True)
@click.pass_context
def cli(ctx, json_output, time_enabled):
    state = GlobalState()
    state.json_output = json_output
    state.time_enabled = time_enabled
    ctx.obj = state


# ------------------------------------------------------------
# Wrap ONLY the command callback, not Click's dispatch
# ------------------------------------------------------------
def wrap_command(cmd):
    """Decorator to wrap each command callback."""
    original = cmd.callback

    def wrapped(*args, **kwargs):
        ctx = click.get_current_context()
        state = ctx.obj

        # No flags → run normally
        if not state.json_output and not state.time_enabled:
            return original(*args, **kwargs)

        # Capture stdout
        buffer = io.StringIO()
        real_stdout = sys.stdout
        sys.stdout = buffer

        start = time.perf_counter()
        error = None

        try:
            original(*args, **kwargs)
        except Exception as e:
            error = e
        finally:
            sys.stdout = real_stdout

        elapsed = time.perf_counter() - start
        output_text = buffer.getvalue().rstrip("\n")

        # JSON mode
        if state.json_output:
            payload = {
                "output": output_text,
                "elapsed": f"{elapsed:.3f}s",  # ALWAYS include elapsed
            }
            if error:
                payload["error"] = str(error)
            click.echo(json.dumps(payload, indent=2))
            return

        # Normal mode
        click.echo(output_text)
        if error:
            click.echo(f"[ERROR] {error}")
        if state.time_enabled:
            click.echo(f"[time] {elapsed:.4f}s")

    cmd.callback = wrapped
    return cmd


# ------------------------------------------------------------
# Register commands with wrapping
# ------------------------------------------------------------
cli.add_command(wrap_command(generate))
cli.add_command(wrap_command(ping_config))
cli.add_command(wrap_command(config_group))


def main():
    cli()
