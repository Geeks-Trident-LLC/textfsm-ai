import click

from .generate_cmd import generate
from .providers_cmd import providers
from .quota_cmd import quota
from .version_cmd import version_cmd

from ._utils import wrap_command  # if you place wrappers in a helper file


@click.group(
    name="textfsm-ai", help="AI-powered TextFSM template generator with multi-provider routing."
)
@click.option("--time", "time_flag", is_flag=True, help="Show execution time (human mode only).")
@click.option("--json", "json_flag", is_flag=True, help="Output results in JSON format.")
@click.pass_context
def cli(ctx, time_flag, json_flag):
    ctx.ensure_object(dict)
    ctx.obj["time"] = time_flag
    ctx.obj["json"] = json_flag


# Register wrapped subcommands
cli.add_command(wrap_command(generate))
cli.add_command(wrap_command(providers))
cli.add_command(wrap_command(quota))
cli.add_command(wrap_command(version_cmd))


def main():
    cli()
