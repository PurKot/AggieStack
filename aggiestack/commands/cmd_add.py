import click
import logging
from aggiestack import utility
from aggiestack.cli import pass_context
from aggiestack.log_handler import logger
from aggiestack.models.hardware import Rack
from aggiestack.models.hardware import Hardware


my_logger = logging.getLogger()

@click.command('add')
@click.option('--mem',   type= click.INT,   help= "Memory of the machine to add")
@click.option('--disk',  type= click.INT,   help= "Number of disks in the machine to add")
@click.option('--vcpus', type= click.INT,   help='Number of vcpus in the machine to add')
@click.option('--ip',    type= click.STRING, help='IP of the machine to add')
@click.option('--rack', type = click.STRING, help='Name of the rack the machine belongs to')
@click.argument('machine_name')
@pass_context
def cli(context, mem, disk, vcpus, ip, rack, machine_name):
    """Add the machine to the system so that it may receive new instances.
    This is usually invoked when a "sick" server was fixed, and it is ready to work again.
    Argument: MACHINE_NAME"""

    if( not context.admin_rights):
        logger.error('Can allow this operation only in admin mode')
        logger.info(f'FAILED: COMMAND: aggiestack adming add --mem  {mem} --disk {disk} --vcpus {vcpus} --ip {ip} --rack {rack} {machine_name}')
        return

    logger.info("Machine to be added with configuration: \n")
    logger.info(f"Name: {machine_name}")
    logger.info(f"Mem: {mem}")
    logger.info(f"Disk: {disk}")
    logger.info(f"Vpus: {vcpus}")
    logger.info(f"Ip: {ip}")
    logger.info(f"Rack Name: {rack}")

    rack = Rack.objects(rackName=rack).first()
    if not rack:
        logger.error(f"Rack '{rack}' doesn't exist")
        logger.info(f'FAILED: COMMAND: aggiestack adming add --mem  {mem} --disk {disk} --vcpus {vcpus} --ip {ip} --rack {rack} {machine_name}')
        return
    else:
        hardware = Hardware.objects(ipAddress=ip).first()
        if hardware:
            logger.error(f"IP '{ip}' is already taken. Use different IP")
            logger.info(f'FAILED: COMMAND: aggiestack adming add --mem  {mem} --disk {disk} --vcpus {vcpus} --ip {ip} --rack {rack} {machine_name}')
            return

        hardware = Hardware.objects(phySerName=machine_name).first()
        if hardware:
            logger.error(f"Machine '{machine_name}' already exists.")
            logger.info(f'FAILED: COMMAND: aggiestack adming add --mem  {mem} --disk {disk} --vcpus {vcpus} --ip {ip} --rack {rack} {machine_name}')
            return

        hardware = Hardware(phySerName=machine_name,
                            rackAssigned=rack,
                            ipAddress=ip,
                            mem=mem,
                            numDisks=disk,
                            numCores=vcpus,
                            avMem=mem,
                            avNumDisks=disk,
                            avNumCores=vcpus)
        hardware.save()
        logger.info(f"Inserted Server: '{machine_name}' into rack '{rack.rackName}'")
        logger.info(f'SUCCESS: COMMAND: aggiestack adming add --mem  {mem} --disk {disk} --vcpus {vcpus} --ip {ip} --rack {rack} {machine_name}')
