import click
import os
import sys
from mongoengine import *
from aggiestack.log_handler import logger
from aggiestack import constants

# mongo connection for mongo_engine
connect(constants.db)

# region Config classes
CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')

class Context(object):

    def __init__(self):
        self.admin_rights = False
        self.verbose = False


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
                    filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('aggiestack.commands.cmd_' + name, None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


# endregion


@click.group(cls=ComplexCLI, chain=True, context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose mode for enhanced logging')
@pass_context
def cli(context, verbose):
    context.admin_rights = False
    context.verbose = verbose

if __name__ == '__main__':
    cli(Context(), False)
