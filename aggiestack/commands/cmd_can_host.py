import click
import logging
from aggiestack.model import FlavorRepresenation
from aggiestack.model import AggregateHardwareRepresentation
from aggiestack.model import HardwareRepresentation
from aggiestack.cli import pass_context
from aggiestack import utility
from mongoengine import *
from aggiestack.models.hardware import Hardware
from aggiestack.models.flavor import Flavor
from aggiestack import constants

connect(constants.db)

my_logger= logging.getLogger()

@click.command('can_host')
@click.argument('machine_name')
@click.argument('flavor')
@pass_context
def cli(context, machine_name, flavor):
    """Check if a machine can be hosted with a particular flavour'.
    Pass the machine name and flavour to check against as argument."""

    if( not context.admin_rights):
        my_logger.error('Can allow this operation only in admin mode')
        my_logger.info(f'FAILED: COMMAND:  aggiestack can_host {machine_name} {flavor}')
        return

    flavor_rep  = Flavor.objects(flavorName = flavor).first()
    if flavor_rep is None:
        my_logger.error(f'Flavor with name {flavor} not found in configuration')
        my_logger.info(f'FAILED: COMMAND:  aggiestack admin can_host {machine_name} {flavor}')
        return
    total_hardware_available = Hardware.objects({})
    if total_hardware_available is None:
        my_logger.error('Hardware not configured')
        my_logger.info(f'FAILED: COMMAND:  aggiestack admin can_host {machine_name} {flavor}')
        return
    reqDisks = flavor_rep.numDisks
    reqRam = flavor_rep.ram
    reqvcpus = flavor_rep.vcpus
    hardware_available = Hardware.objects(avMem__gt=reqRam,avNumDisks__gt = reqDisks, avNumCores__gt = reqvcpus).first()
    if(hardware_available):
        print(f'Yes, you can host {machine_name} machine with the {flavor} flavor')
        my_logger.info("SUCCESS: COMMAND : aggiestack admin can_host %s %s", machine_name, flavor)
        return
    else:
        my_logger.error(f'Not enough server capacity to host {flavor}')
        my_logger.info(f'FAILED: COMMAND:  aggiestack admin can_host {machine_name} {flavor}')
        return


#function to check the hardware configuration availability
def get_available_hardware():

    file_path = utility.get_hardware_info_path()
    if file_path is None:
        return None

    try:
        f = open(file_path)

        ram_available = 0
        vcpus_available = 0
        disks_available = 0

        for line in f.readlines():
            ram_available += int(line.split(' ')[2])
            disks_available += int(line.split(' ')[3])
            vcpus_available += int(line.split(' ')[4])

        f.close()

        return AggregateHardwareRepresentation(ram = ram_available,
                                                disks = disks_available,
                                                vcpus = vcpus_available)
    except FileNotFoundError:
        return None

#function to check the flavor configuration availability
def get_flavor_info(flavor_name):
    file_path = utility.get_flavor_info_path()
    if file_path is None:
        return None

    f = None
    try:
        f = open(file_path)
        for line in f.readlines():
            config_entries = line.split(' ')
            if config_entries[0].lower() == flavor_name.lower():
                f.close()
                return FlavorRepresenation( name = flavor_name,
                                            ram = int(config_entries[1]),
                                            disks = int(config_entries[2]),
                                            vcpus = int(config_entries[3]))
        f.close()
        return None
    except FileNotFoundError:
        return None

# function to check the harware availability
def is_hardware_sufficient_to_hold_flavor(total_hardware_available, flavor_rep):
    return (flavor_rep.ram <= total_hardware_available.ram
            and flavor_rep.vcpus <= total_hardware_available.vcpus
            and flavor_rep.disks <= total_hardware_available.disks)
