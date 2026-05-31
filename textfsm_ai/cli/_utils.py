import contextlib
import functools
import io
import json
import time

import click


def run_with_capture(ctx, func, *args, **kwargs):
    """Execute a subcommand, capture stdout, and wrap in JSON if requested.

    Behavior:
    - Default: print human-readable output.
    - --time: append human-readable timing.
    - --json: wrap stdout + elapsed_sec in JSON (always include elapsed_sec).
    """
    use_json = ctx.obj.get("json", False)
    use_time = ctx.obj.get("time", False)

    buffer = io.StringIO()

    start = time.perf_counter()
    with contextlib.redirect_stdout(buffer):
        func(*args, **kwargs)
    elapsed = time.perf_counter() - start

    output = buffer.getvalue()

    if use_json:
        payload = {
            "output": output,
            "elapsed_sec": round(elapsed, 6),
        }
        click.echo(json.dumps(payload, indent=2))
        return

    # Human-readable mode
    click.echo(output, nl=False)
    if use_time:
        click.echo(f"[time] {elapsed:.6f}s")


def wrap_command(cmd):
    """Wrap a Click command so we can intercept execution with run_with_capture()."""

    @functools.wraps(cmd.callback)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        return run_with_capture(ctx, cmd.callback, *args, **kwargs)

    return click.Command(
        name=cmd.name,
        callback=wrapper,
        params=cmd.params,
        help=cmd.help,
        short_help=cmd.short_help,
        epilog=cmd.epilog,
        options_metavar=cmd.options_metavar,
        add_help_option=cmd.add_help_option,
    )
