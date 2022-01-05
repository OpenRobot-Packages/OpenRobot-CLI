import re
import click

version = ''
with open('openrobot_cli/__init__.py') as f:
    openrobot_cli_version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1) or '0.0.0'

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(f'OpenRobot-CLI Version {openrobot_cli_version}')
    ctx.exit()

@click.group("openrobot", invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def main(ctx: click.Context):
    """
    OpenRobot CLI. A shell/CLI utility for OpenRobot, ranging from OpenRobot API, Jeyy API and OpenRobot RePI API.
    """

    if ctx.invoked_subcommand is None:
        help_str = ctx.get_help()
        click.echo(help_str)
        
        ctx.exit()


# Setup OpenRobot CLI with all the subcommands

# Imports:

try:
    from .api import api_cli_setup
except:
    api_cli_setup = None

try:
    from .jeyyapi import jeyyapi_cli_setup
except:
    jeyyapi_cli_setup = None

try:
    from .repi import repi_cli_setup
except:
    repi_cli_setup = None

# Setup:

if api_cli_setup:
    api_cli_setup(main)

if jeyyapi_cli_setup:
    jeyyapi_cli_setup(main)

if repi_cli_setup:
    repi_cli_setup(main)