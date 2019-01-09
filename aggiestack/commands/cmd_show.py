import os
import click
import logging
from aggiestack.cli import pass_context
from aggiestack import constants
from aggiestack import utility
from aggiestack.log_handler import logger
from aggiestack.models.instance import Instance
from aggiestack.models.image import Image
from aggiestack.models.hardware import Hardware
from aggiestack.models.flavor import Flavor
from aggiestack.models.rack import Rack
from mongoengine import *

connect(constants.db)

my_logger = logging.getLogger()

@click.command('show')
@click.argument('command_args', nargs = -1)
@pass_context
def cli(context, command_args):
    """
    Display the available configurations

    Sub commands allowed:
        all:        Show all the arguments
        hardware:   Show all the hardware servers configured
        instances:  Show all the instances
        flavors:    Show all the flavors
        images:     Show all the images configured
        imagecaches Show the image cacehes on a rack
                    Argument:
                        rack_name name of the rack names
    """
    cmd = "aggiestack show"
    if context.admin_rights:
        my_logger.info("Enter the ADMIN!")
        cmd = "aggiestack admin show"

    if len(command_args) == 0:
        logger.error(f'no sub command added after show, $> {cmd}')
        logger.info(f"FAILED: COMMAND: {cmd}")

    if command_args[0] == 'images':
        show_images(context)
    elif command_args[0] == 'flavors':
        show_flavors(context)
    elif command_args[0] == 'hardware':
        show_hardware(context)
    elif command_args[0] == 'instances':
        show_instances(context)
    elif command_args[0] == 'imagecaches' and len(command_args) == 2:
        show_image_caches(context, command_args[1])
    elif command_args[0] == 'all':
        show_all_configs(context)
    else:
        logger.error('Unknown command signature, $> {cmd} {command_args[0]}')
        logger.info(f"FAILED: COMMAND: {cmd} {command_args[0]}")

def show_images(context):
    imageList = Image.objects({})

    if imageList.first():
        for img in imageList:
            r = []
            for rc in  Rack.objects(imgCache__in = [img.imageName]): r.append(rc.rackName)
            if r: print(f"Image Name: {img.imageName}  Size : {img.imageSize}  location {img.imageLocation} Racks image cached on: {r}")
            else: print(f"Image Name: {img.imageName}  Size : {img.imageSize}  location {img.imageLocation} Racks image cached on: No racks cached on")
        logger.info("COMMAND: aggiestack show images - SUCCESS - printed configuration on console")
    else:
        print("No images found")
        logger.info("COMMAND: aggiestack show images - No Stored image Configurations Found")


def show_flavors(context):
    flvList = Flavor.objects({})
    if flvList.first():
        for flv in flvList:
                print(f"Flavor Name: {flv.flavorName} Memory size:{flv.ram}  No of disks: {flv.numDisks} No of cores : {flv.vcpus}")
        logger.info("COMMAND: aggiestack show flavors - SUCCESS - printed configuration on console")
    else:
        print("no flavors found")
        logger.info("COMMAND: aggiestack show flavors - No Stored Flavor Configurations Found")


def show_hardware(context):
    hrdlist = Hardware.objects({})
    if hrdlist.first():
        for hrd in hrdlist:
            if context.admin_rights:
                print(f"Harware Server Name: {hrd.phySerName} Rack assigned: {hrd.rackAssigned.rackName} Available Memory size:{hrd.avMem} Available no of disks: {hrd.avNumDisks} Available no of cores : {hrd.avNumCores}")
            else:
                print(f"Harware Server Name: {hrd.phySerName} Rack assigned: {hrd.rackAssigned.rackName} Total Memory size:{hrd.mem} Total no of disks: {hrd.numDisks} Total no of cores : {hrd.numCores}")
        if context.admin_rights:
            logger.info("COMMAND: aggiestack admin show hardware - SUCCESS - printed configuration on console")
        else:
            logger.info("COMMAND: aggiestack show hardware - SUCCESS - printed configuration on console")
    else:
        print("no hardware servers found")
        if context.admin_rights:
            logger.info("COMMAND: aggiestack admin show hardware - No Stored machine Configurations Found")
        else:
            logger.info("COMMAND: aggiestack show hardware - No Stored machine Configurations Found")

def show_instances(context):
    if not context.admin_rights:
        print(" add admin to see instances or use server list command")
        logger.info("COMMAND: aggiestack show instances - INVALID COMMAND - add admin")
        return
    instanceList = Instance.objects({})
    if instanceList.first():
        for inst in instanceList:
            print(f"Instance Name: {inst.instanceName} Physical Server Running on:{inst.phySerName} Rack assigned to: {inst.rackAssigned}")
        logger.info("COMMAND: aggiestack admin show instances - SUCCESS - printed configuration on console")
    else:
        print("no instances found")
        logger.info("COMMAND: aggiestack show instances - FAILED - no instances found")

def show_all_configs(context):
    print("\n*************************HARDWARE CONFIGURATION********************************")
    show_hardware(context)
    print("\n*************************IMAGES CONFIGURATION********************************")
    show_images(context)
    print("\n*************************FLAVOR CONFIGURATION********************************")
    show_flavors(context)
    logger.info("COMMAND: aggiestack show all - SUCCESS - printed configurations on console")


def show_image_caches(context, rack_name):
    print(f'Request to show image caches in a seperate files')
    if not context.admin_rights:
        logger.error('show imagecaches allowed only in ADMIN mode')
        logger.info("COMMAND: aggiestack show imagechaces - INVALID COMMAND - add admin")
    else:
        rk = Rack.objects(rackName = rack_name).first()
        if rk:
            imageCacheList = rk.imgCache
            if imageCacheList:
                print("Images cached: ")
                for img in imageCacheList:
                   print(img.imageName)
                logger.info("COMMAND: aggiestack admin show imagechaces - SUCCESS")
                print(f"Available Storage on Rack to cache images: {rk.avStorage}")
            else:
                print("No Image caches found")
                print(f"Available Storage on Rack: {rk.avStorage}")
                logger.info("COMMAND: aggiestack admin show imagechaces - No images caches found")
        else:
            print("Invalid rack name. Enter valid rack name")
            logger.info("COMMAND: aggiestack show imagechaces - FAILED. Invalid rack name. Re-enter a valid rack name")
