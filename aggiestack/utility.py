# stores utility functions like file_read, file_write, file_parser

import pickle
import os
import aggiestack
from aggiestack.models.instance import Instance
from aggiestack.models.image import Image
from aggiestack.models.hardware import Hardware
from aggiestack.models.flavor import Flavor

def file_write(data, file_path):
    file_write(data, file_path, 'a')

def file_write(data, file_path, mode):
    file  = open(file_path, mode)
    if type(data) is list:
        for e in data:
            file.write(e)
    else:
        file.write(data)

# return array of string with each element in array corresponds to particular line number
def file_read(file_path):
    file_content = []
    file = open(file_path, 'r')
    for line in file:
        file_content.append(line)
    return file_content

def file_print(file_path):
    file_content = file_read(file_path)
    print(f'{len(file_content)}')
    for e in file_content:
        print(e,end="")

def get_project_dir():
    return os.path.dirname(os.path.dirname(aggiestack.__file__))

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        print (f'creating directory at {dir_path}')
        os.makedirs(dir_path)

def get_data_dir():
    data_dir = os.path.join(get_project_dir(), 'data')
    create_dir(data_dir)
    return data_dir

def get_log_dir():
    log_dir = os.path.join(get_project_dir(), 'log')
    create_dir(log_dir)
    return log_dir

def get_hardware_info_path():
    return os.path.join(get_data_dir(), 'p_hardware_info')

def get_image_info_path():
    return os.path.join(get_data_dir(), 'p_image_info')

def get_flavor_info_path():
    return os.path.join(get_data_dir(), 'p_flavor_info')

def get_log_file_path():
    return os.path.join(get_log_dir(), 'aggiestack-log.txt')

def file_to_map(file_path, mapIndex):
    if not os.path.exists(file_path):
        return {}
    return list_to_map(file_read(file_path), mapIndex)

def list_to_map(file_content, mapIndex):
    map = {}
    for line in file_content:
        key = line.split(" ")[mapIndex]
        map[key] = line
    return map

def map_value_to_list(map1, map2):
    content = []
    for k, v in map1.items():
        if k in map2:
            del map2[k]
        content.append(v)

    for k, v in map2.items():
        content.append(v)
    return content

# return physical Server Name that can host given instance with given image, flavor config
def getPhyServerAllocation(image,flavor, rack_name=None):
        mimage = Image.objects(imageName =image).first()
        mflavor = Flavor.objects(flavorName=flavor).first()
        if(mimage and mflavor):
                reqDisks = mflavor.numDisks
                reqRam = mflavor.ram
                reqvcpus = mflavor.vcpus
                # reqImagesize = mimage.imageSize # update later based on prof input
                if not rack_name:
                    avServers = Hardware.objects(avMem__gte=reqRam,avNumDisks__gte = reqDisks, avNumCores__gte = reqvcpus).first()
                else:
                    avServers = Hardware.objects(avMem__gte=reqRam,avNumDisks__gte = reqDisks, avNumCores__gte = reqvcpus, rackAssigned__ne=rack_name).first()
                return avServers

        else:
                print("flavor or image doesnt exist")

# inserts the given instance into the given Server (this is an object)
# instance_name, flavor_name, image_name, server_name => STRING
def insertInstanceOnServer(instance_name, flavor_name, image_name, server_name):
    alcServer = Hardware.objects(phySerName=server_name).first()
    selFlavor =  Flavor.objects(flavorName=flavor_name).first()
    reqRam =selFlavor.ram
    reqDisks = selFlavor.numDisks
    reqvcpus = selFlavor.vcpus
    newInstance = Instance.objects(instanceName = instance_name).first()
    rckname = alcServer.rackAssigned.rackName
    if newInstance:
            newInstance.phySerName = alcServer.phySerName
            newInstance.imageName = image_name
            newInstance.flavorName = flavor_name
            newInstance.rackAssigned = rckname
            newInstance.save()
            print(f"instance '{instance_name}' updated")
    else:
            newInstance = Instance(instanceName =instance_name )
            newInstance.phySerName = alcServer.phySerName
            newInstance.imageName = image_name
            newInstance.flavorName = flavor_name
            newInstance.rackAssigned = rckname
            newInstance.save()
            print(f"instance '{instance_name}' created")

    alcServer.avMem = alcServer.avMem-reqRam
    alcServer.avNumDisks = alcServer.avNumDisks-reqDisks
    alcServer.avNumCores = alcServer.avNumCores-reqvcpus
    alcServer.instances = [newInstance]
    alcServer.save()
    print(f"hardware '{server_name}' on rack: '{alcServer.rackAssigned.rackName}' updated")
