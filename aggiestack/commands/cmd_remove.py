import click
import logging
from aggiestack import utility
from aggiestack.cli import pass_context
from aggiestack.log_handler import logger
from aggiestack.models.hardware import Hardware


my_logger = logging.getLogger()

@click.command('remove')
@click.argument('machine_name')
@pass_context
def cli(context, machine_name):
    """ Remove the machine name from the view of the datacenter """

    if( not context.admin_rights):
        logger.error('Can allow this operation only in admin mode')
        logger.info(f'FAILED: COMMAND:  aggiestack remove {machine_name}')
        return

    logger.info(f"Got request to evacuate machine: {machine_name}")
    server = Hardware.objects(phySerName=machine_name).first()
    if len(server.instances) == 0:
        server.delete()
        logger.info(f"Removed machine {machine_name}")
        logger.info(f"Removed machine {machine_name}")
        logger.info(f'SUCCESS: COMMAND:  aggiestack admin remove {machine_name}')
    else:
        logger.error(f"Can't remove machine '{machine_name}', it has {len(server.instances)} instances associated with it.")
        logger.info(f'FAILED: COMMAND:  aggiestack admin remove {machine_name}')
