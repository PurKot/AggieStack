import os
import click
import logging
from mongoengine import *
from aggiestack import constants
from aggiestack.cli import pass_context
from aggiestack.models.instance import Instance
from aggiestack.models.image import Image
from aggiestack.models.hardware import Hardware
from aggiestack.models.flavor import Flavor
#from aggiestack.models.hardware import Rack
from aggiestack.log_handler import logger


connect(constants.db)
my_logger = logging.getLogger()

@click.command('server')
@pass_context
@click.argument('subcommand', type = click.STRING)
@click.argument('command_args', nargs = -1)
def cli(context, subcommand, command_args):
    """
    \b
    Works with the following subcommands:
    create: creates the instance
        Argument: INSTANCE_NAME
        Options:
            --flavor Name of the flavor to be configured with the server
            --image  Name of the image  to be configured with the server
    delete: Deletes the instance
        Argument: INSTANCE_NAME
    list: Lists all the servers configured
    """
    if len(command_args)==0 and subcommand == "list" :
        list_servers()
    elif len(command_args)>=1 and subcommand == "create" :
        try:
            instance_name, flavor, image = parse_command_args_for_values(command_args)
            if not instance_name:
                logger.error("Instance name not provided with the server create command")
                logger.info(f"FAILED: COMMAND:  aggiestack server {subcommand} {command_args}")
                return
            create_server_instance(instance_name, flavor, image)
        except IOError:
            logger.error('Incorrect format of args passed')
            logger.info(f"FAILED: COMMAND:  aggiestack server {subcommand} {command_args}")
            return
    elif len(command_args)==1 and subcommand == "delete" :
        instance_name = command_args[0]
        delete_server_instance(instance_name)
    else:
        logger.error(f"Command '$> server {subcommand}' not defined")
        logger.info(f"FAILED: COMMAND:  aggiestack server {subcommand} {command_args}")

def create_server_instance(instance_name, flavor, image):
        """Creates an instance named INSTANCE_NAME to be boot from
        IMAGE and configured as indicated in FLAVOR_NAME """
        logger.info(f"Got request to create a server with configuration:")
        logger.info(f"Instance name: {instance_name}")
        logger.info(f"Flavor name:   {flavor}")
        logger.info(f"Image name:    {image}")

        alcServer = getPhyServerAllocation(instance_name,image,flavor)

        if alcServer:
                selFlavor =  Flavor.objects(flavorName=flavor).first()
                selImage = Image.objects(imageName = image).first()
                reqRam =selFlavor.ram
                reqDisks = selFlavor.numDisks
                reqvcpus = selFlavor.vcpus
                newInstance = Instance.objects(instanceName = instance_name).first()
                rckname = alcServer.rackAssigned.rackName
                if newInstance:
                        newInstance.phySerName = alcServer.phySerName
                        newInstance.imageName = image
                        newInstance.flavorName = flavor
                        newInstance.rackAssigned = rckname
                        newInstance.save()
                        logger.info(f"instance {instance_name} updated")
                else:
                        newInstance = Instance(instanceName =instance_name )
                        newInstance.phySerName = alcServer.phySerName
                        newInstance.imageName = image
                        newInstance.flavorName = flavor
                        newInstance.rackAssigned = rckname
                        newInstance.save()
                        logger.info(f"instance {instance_name} created")

                alcServer.avMem = alcServer.avMem-reqRam
                alcServer.avNumDisks = alcServer.avNumDisks-reqDisks
                alcServer.avNumCores = alcServer.avNumCores-reqvcpus
                alcServer.save()
                alcServer.update(push__instances = newInstance)
                if selImage not in alcServer.rackAssigned.imgCache:
                    alcServer.rackAssigned.update(push__imgCache = selImage)
                    alcServer.rackAssigned.update(dec__avStorage=selImage.imageSize)

                print(f"Added to server {alcServer.phySerName} (on rack {alcServer.rackAssigned.rackName}) current memmory {alcServer.mem} availble memory {alcServer.avMem})")
                logger.info(f"Added to server {alcServer.phySerName} (on rack {alcServer.rackAssigned.rackName}) current memmory {alcServer.mem} availble memory {alcServer.avMem})")
                logger.info(f"SUCCESS: COMMAND: aggiestack server create --image {image} --flavor {flavor} {instance_name}")
        else:
                logger.info(f"FAILED: COMMAND: aggiestack server create --image {image} --flavor {flavor} {instance_name}")


# algorithm for finding the available h/w server
def getPhyServerAllocation(instancename,image,flavor):
        mimage = Image.objects(imageName=image).first()
        mflavor = Flavor.objects(flavorName=flavor).first()
        if(mimage and mflavor):
                reqDisks = mflavor.numDisks
                reqRam = mflavor.ram
                reqvcpus = mflavor.vcpus
                # reqImagesize = mimage.imageSize # update later based on prof input
                avServers = Hardware.objects(avMem__gte=reqRam,
                                            avNumDisks__gte = reqDisks,
                                            avNumCores__gte = reqvcpus,
                                            )
                if avServers.count() == 0:
                    logger.error(f"Insufficient storage on servers to host instance {instancename} with image {image} and flavor {flavor}")
                for hrd in avServers:
                    if (mimage in hrd.rackAssigned.imgCache):
                        return hrd
                max_size = 0
                hw_with_max_size = None
                for hrd in avServers:
                    if hrd.rackAssigned.avStorage >= max_size :
                        max_size = hrd.rackAssigned.avStorage
                        hw_with_max_size = hrd
                #logger.info(f"max_size: {max_size}, hw_with_max_size: {hw_with_max_size.rackAssigned.avStorage}")
                if hw_with_max_size:
                    if max_size < mimage.imageSize:
                        imagelist = hw_with_max_size.rackAssigned.imgCache
                        logger.info(f"evicting images from rack {hw_with_max_size.rackAssigned.rackName}")
                        #evict
                        logger.info("evicting images: [ ")
                        for image in imagelist:
                            logger.info(image.imageName, end=" ")
                            max_size += image.imageSize
                            hw_with_max_size.rackAssigned.avStorage += image.imageSize
                            hw_with_max_size.rackAssigned.imgCache.remove(image)
                            if max_size >= mimage.imageSize:
                                break
                        logger.info("]")
                    hw_with_max_size.rackAssigned.save()
                    return  hw_with_max_size
                #return avServers
        elif not mimage and not mflavor:
                logger.error(f"image {image} and flavor {flavor} doesn't exist")
        elif not mimage:
                logger.error(f"image {image} doesn't exist")
        else:
                logger.error(f"flavor {flavor} doesn't exist")

def parse_command_args_for_values(command_args):
    instance_name = None
    flavor_name = None
    image_name = None

    number_of_args = len(command_args)

    if number_of_args not in [1,3,5]:
        raise IOError("Incorrect args")
    instance_name = command_args[number_of_args-1]
    i=0
    while i<(number_of_args-2):
        if command_args[i] not in ['--flavor', '--image']:
            raise IOError('Incorrect args')
        if command_args[i] == '--flavor':
            flavor_name = command_args[i+1]
        if command_args[i] == '--image':
            image_name = command_args[i+1]
        i += 2

    return instance_name, flavor_name, image_name

def list_servers():
        logger.info(f"Got request to list all servers")
        instanceList = Instance.objects({})
        if instanceList.first():
                for inst in instanceList:
                        logger.info(f"Instance Name: {inst.instanceName} Image Name: {inst.imageName} Flavor Name: {inst.flavorName}")

        else:
                logger.error("no instances found")
        logger.info("SUCCESS: COMMAND:  aggiestack server list")


def  delete_server_instance(instance_name):
    logger.info(f"got request to delete instance {instance_name}")
    delInstance = Instance.objects(instanceName = instance_name).first()
    alcServer = Hardware.objects(phySerName= delInstance.phySerName).first()
    alcFlav = Flavor.objects(flavorName = delInstance.flavorName ).first()
    if delInstance:
        logger.info("deleted instance {instance_name}")
        alcServer.avMem += alcFlav.ram
        alcServer.avNumDisks += alcFlav.numDisks
        alcServer.avNumCores +=alcFlav.vcpus
        alcServer.save()
        alcServer.update(pull__instances=delInstance)
        delInstance.delete()
        logger.info(f" hardware server :{alcServer.phySerName} updated")
        logger.info(f"SUCCESS: COMMAND: aggiestack server delete {instance_name}")
    else:
        logger.error("Instance doesn't exist. Enter a valid instance name to delete. Execute \"aggiestack server list\" for the list of instances ")
        logger.info(f"FAILED: COMMAND: aggiestack server delete {instance_name}")
