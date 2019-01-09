import click
from aggiestack.cli import pass_context



@click.command('admin', help='Club with other commands to run under administrative privileges')
@pass_context
def cli(context):
    context.admin_rights = True
