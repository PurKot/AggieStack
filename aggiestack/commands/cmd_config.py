import click
import re
import socket
import logging
from mongoengine import *
from aggiestack import utility
from aggiestack import constants
from aggiestack.cli import pass_context
from aggiestack.log_handler import logger
from aggiestack.models.flavor import Flavor
from aggiestack.models.image import Image
from aggiestack.models.hardware import Rack
from aggiestack.models.hardware import Hardware

R_NUMBER = r"^[0-9]+$"

my_logger = logging.getLogger()
connect(constants.db)

@click.command('config', help='Configure the setup')
@click.option('--hardware', type=click.Path(exists=True), help='Path to hardware configuration file')
@click.option('--images', type=click.Path(exists=True), help='Path to images configuration file')
@click.option('--flavors', type=click.Path(exists=True), help='Path to flavors configuration file')
@pass_context
def cli(context, hardware, images, flavors):
    if hardware:
        check = check_hardware_pattern(open(hardware, 'r'))
        if check:
            logger.error("COMMAND: aggiestack config --hardware '%s' : %s",hardware,check)
            logger.info(f"FAILED: COMMAND:  aggiestack config --hardware {hardware}")
            return
        else:
            input_content = utility.file_read(hardware)
            arg_hardware = hardware
            # reading rack information
            # handle update or duplicates!
            for i in range(1, int(input_content[0])+1):
                attrs = input_content[i].split(" ")
                logger.info("Racks parsed -- '%s'", attrs)
                rack = Rack.objects(rackName=attrs[0]).first()
                if not rack:
                    rack = Rack(rackName = attrs[0],
                                storageCapacity = attrs[1],
                                avStorage = attrs[1]).save()
                    logger.info("Inserted Rack: '%s'", attrs)
                else:
                    rack.avStorage += int(attrs[1]) - rack.storageCapacity
                    rack.storageCapacity = attrs[1]
                    rack.save()
                    logger.info("Updated Rack: '%s'", attrs)
            # reading hardware information
            # fails when no hardware is present after rack info
            for line in input_content[int(input_content[0])+2:]:
                attrs = line.split(" ")
                logger.info("Hardware parsed -- '%s'", attrs)
                rack = Rack.objects(rackName=attrs[1]).first()
                if rack:
                    hardware = Hardware.objects(phySerName=attrs[0]).first()
                    if not hardware:
                        hardware = Hardware(phySerName=attrs[0],
                                            rackAssigned=Rack.objects.get(rackName =attrs[1]),
                                            ipAddress=attrs[2],
                                            mem=attrs[3],
                                            numDisks=attrs[4],
                                            numCores=attrs[5],
                                            avMem =attrs[3],
                                            avNumDisks = attrs[4],
                                            avNumCores = attrs[5])
                        hardware.save()
                        logger.info("Inserted Hardware: '%s'", attrs)
                    else:
                        hardware.phySerName = attrs[0]
                        hardware.rackAssigned = Rack.objects.get(rackName=attrs[1])
                        hardware.avMem += int(attrs[3]) - hardware.mem
                        hardware.avNumDisks += int(attrs[4]) - hardware.numDisks
                        hardware.avNumCores += int(attrs[5]) - hardware.numCores
                        hardware.mem = attrs[3]
                        hardware.numDisks = attrs[4]
                        hardware.numCores = attrs[5]
                        hardware.save()
                        logger.info("Updated Hardware: '%s'", attrs)
            logger.info("SUCCESS: COMMAND: aggiestack config --hardware %s",arg_hardware)

    elif images:
        # todo modify check function
        # check = check_image_pattern(open(images, 'r'))
        # remove this and below line after modifying check
        check = None
        if check:
            logger.error("COMMAND: aggiestack config --images '%s' : %s",images,check)
            logger.info(f"FAILED: COMMAND:  aggiestack config --images {image}")
        else:
            input_content = utility.file_read(images)
            arg_image = images
            # write to mongo
            # handle update
            for line in input_content[1:]:
                attrs = line.split(" ")
                logger.info("Images parsed -- '%s'", attrs)
                image = Image.objects(imageName=attrs[0]).first()
                # confirm with dileep
                if not image:
                    image = Image(imageName=attrs[0],
                                    imageSize=attrs[1],
                                    imageLocation=attrs[2]).save()
                    logger.info("Inserted Image: '%s'", attrs)
                else:
                    image.imageSize = attrs[1]
                    image.imageLocation = attrs[2]
                    image.save()
                    logger.info("Updated Image: '%s'", attrs)
            logger.info("SUCCESS:  COMMAND: aggiestack config --images %s",arg_image)

    elif flavors:
        check = check_flavor_pattern(open(flavors, 'r'))
        if check:
            logger.error("COMMAND: aggiestack config --flavor '%s' : %s",flavors,check)
            logger.error(f"FAILED: COMMAND:  aggiestack config --flavor {flavor}")
        else:
            input_content = utility.file_read(flavors)
            arg_flavor = flavors
            # write to mongo
            # handle update, dont duplicate record
            for line in input_content[1:]:
                attrs = line.split(" ")
                logger.info("Flavor parsed -- '%s'", attrs)
                flavor = Flavor.objects(flavorName=attrs[0]).first()
                if not flavor:
                    flavor = Flavor(flavorName=attrs[0],
                                    ram=attrs[1],
                                    numDisks=attrs[2],
                                    vcpus=attrs[3]).save()
                    logger.info("Inserted Flavor: '%s'", attrs)
                else:
                    flavor.ram = attrs[1]
                    flavor.numDisks = attrs[2]
                    flavor.vcpus = attrs[3]
                    flavor.save()
                    logger.info("Updated Flavor: '%s'", attrs)
            logger.info("SUCCESS: COMMAND: aggiestack config --flavors %s",arg_flavor)
    else:
        my_logger.error('You must enter an argument with the config command. Check with --help for available options')


def is_num(listitem):
    return bool(re.search(R_NUMBER, listitem))

def get_number(stream):
    chunk = stream.readline()
    m = re.search(R_NUMBER, chunk)
    return int(m[0])

def get_row_items(stream):
    chunk = stream.readline()
    return re.findall(r'\S+', chunk)

# function to check the hardware file format. returns the error message if any error or None if no errors.
def check_hardware_pattern(filestream):
    num_of_racks = get_number(filestream)
    if num_of_racks <= 0:
        return "invalid no. of racks: Wrong format of file"
    y = 1
    while y<= num_of_racks:
        attr = get_row_items(filestream)
        num_rack_attr = len(attr)
        if num_rack_attr != 2:
             return "Invalid/Missing attributes of rack specs: INVALID file format"
        if not bool(re.search(r'[a-zA-Z0-9]+', attr[0])):
            return "invalid rack name: Invalid config file "
        if not is_num(attr[1]):
            return "Invalid rack memory size: INVALID config file"
        y = y+1

    num_of_machines = get_number(filestream)
    if num_of_machines <= 0:
        return "Invalid no . of machines: Wrong format of file"
    x = 1
    while x <= num_of_machines:
        attrs = get_row_items(filestream)
        num_of_attributes = len(attrs)
        if num_of_attributes != 6:
            return "Invalid/Missing attributes of machine specs: INVALID file format"
        if not bool(re.search(r'[a-zA-Z0-9]+', attrs[0])):
            return "invalid machine name: Invalid config file "
        if not bool(re.search(r'[a-zA-Z0-9]+', attrs[1])):
            return "invalid machine name: Invalid config file "
        try:
            ip_address = socket.inet_aton(attrs[2])
        except socket.error:
            return "Invalid IP Address: INVALID config file"
        if not is_num(attrs[3]):
            return "Invalid memory size: INVALID config file"
        if not is_num(attrs[4]):
            return "Invalid disk size: INVALID config file"
        if not is_num(attrs[5]):
            return "Invalid vcpus size: INVALID config file"
        x = x + 1
    chunk = filestream.readline()
    if chunk:
        return "Excess machine configurations given: Invalid file format"
    else:
        return None


# function to check the images file format. returns the error message if any error or None if no errors.
def check_image_pattern(filestream):
    noOfImg = get_number(filestream)
    if noOfImg <= 0: return "Invalid no . of images: INVALID format of file"
    x = 1
    while x <= noOfImg:
        attrs = get_row_items(filestream)
        num_of_attributes = len(attrs)
        if num_of_attributes != 3:
            return "Invalid/Missing attributes for a image : INVALID file format"
        if not attrs[0]:
            return "Invalid machine name: INVALID config file "
        if not is_num(attrs[1]):
             return "Invalid memory size: INVALID config file "
        if not bool(
            re.search(r'([/|.|\w|\s|-])*\.(?:img)', attrs[2])):
            return "Invalid image file path: INVALID config file"
        x += 1
    chunk = filestream.readline()
    if chunk:
        return "Excess image configurations given: INVALID file format"
    else:
        return None


# function to check the flavors file format. returns the error message if any error or None if no errors.
def check_flavor_pattern(filestream):
    num_of_flavors = get_number(filestream)
    if num_of_flavors <= 0: return "Invalid no . of flavors: INVALID format of file"
    x = 1
    while x <= num_of_flavors:
        attrs = get_row_items(filestream)
        num_of_attributes = len(attrs)
        if num_of_attributes != 4:
            return "Invalid/Missing attributes for a flavor: INVALID file format"
        if not bool(re.search(r'[a-zA-Z0-9]+', attrs[0])):
            return "Invalid Flavor name: INVALID config file "
        if not is_num(attrs[1]):
            return "Invalid memory size: INVALID config file"
        if not is_num(attrs[2]):
            return "Invalid disk size: INVALID config file"
        if not is_num(attrs[3]):
            return "Invalid vcpus size: INVALID config file"
        x += 1
    chunk = filestream.readline()
    if chunk:
        return "Excess flavor configurations given: INVALID file format"
    else:
        return None
