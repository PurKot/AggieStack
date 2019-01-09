import click
import logging
from aggiestack import utility
from aggiestack.cli import pass_context
from aggiestack.log_handler import logger
from aggiestack.models.hardware import Hardware
from aggiestack.models.flavor import Flavor
from aggiestack.models.image import Image
from aggiestack.models.instance import Instance
from aggiestack.models.rack import Rack

my_logger = logging.getLogger()

@click.command('evacuate')
@click.argument('rack_name')
@pass_context
def cli(context, rack_name):
    """
    Evacuates all the machines located on the same rack
    """

    if( not context.admin_rights):
        logger.error('Can allow this operation only in admin mode')
        logger.info(f'FAILED: COMMAND:  aggiestack evacuate {rack_name}')
        return

    logger.info(f"Got request to evacuate rack: {rack_name}")
    rack = Rack.objects(rackName=rack_name).first()
    if not rack:
        logger.error(f"Rack {rack_name} doesn't exist")
        logger.info(f'FAILED: COMMAND:  aggiestack evacuate {rack_name}')
        return
    rack_servers = Hardware.objects(rackAssigned=rack_name)
    logger.info(f"rack servers: '{rack_servers.count()}'")
    new_server_names = []
    old_server_names = []
    migrated_instance_names = []
    roll_back = False
    for server in rack_servers:
        if roll_back:
            break

        for instance in server.instances:
            logger.info(f"migrating instance '{instance.instanceName}' image: '{instance.imageName}' flavor: {instance.flavorName}")
            new_server = utility.getPhyServerAllocation(instance.imageName, instance.flavorName, rack_name)
            if not new_server:
                logger.error(f"cannot migrate instance: '{instance.instanceName}' image:'{instance.imageName}'")
                roll_back = True
                break
            else:
                utility.insertInstanceOnServer(instance.instanceName, instance.flavorName, instance.imageName, new_server.phySerName)
                migrated_instance_names.append(instance.instanceName)
                old_server_names.append(server.phySerName)
                new_server_names.append(new_server.phySerName)

    if roll_back:
        logger.error(f'Cannot evacuate rack {rack_name}')
        logger.error("rolling back servers")
        for i in range(len(migrated_instance_names)-1, -1, -1):
            logger.info(f"rolling back server: '{new_server_names[i]}' for instance: '{migrated_instance_names[i]}' to its previous server: '{old_server_names[i]}'")
            # rolling back instance
            migrated_instance = Instance.objects(instanceName=migrated_instance_names[i]).first()
            migrated_instance.phySerName = old_server_names[i]
            migrated_instance.save()

            flavor = Flavor.objects(flavorName=migrated_instance.flavorName).first()
            image = Image.objects(imageName=migrated_instance.imageName).first()

            # rolling back the server to which instance it was assigned
            new_server = Hardware.objects(phySerName=new_server_names[i]).first()
            new_server.avMem += flavor.ram
            new_server.avNumDisks += flavor.numDisks
            new_server.avNumCores += flavor.vcpus
            new_server.instances.remove(migrated_instance)
            new_server.save()
        logger.info(f'FAILED: COMMAND: aggiestack admin evacuate {rack_name}')
    else:
        logger.info(f"migrated #'{len(migrated_instance_names)}' instances")
        for server in rack_servers:
            server.delete()
        logger.info(f"removed all servers from rack {rack_name}")
        rack = Rack.objects(rackName=rack_name).first()
        rack.delete()
        logger.info(f"evicted rack {rack_name}")
        logger.info(f'SUCCESS: COMMAND: aggiestack admin evacuate {rack_name}')
        logger.info(f'Successfully evacuated rack {rack_name}')
