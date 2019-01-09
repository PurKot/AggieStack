# 678-18-c

# The Aggiestack CLI
Aggiestack CLI provides commands to store and read hardware, images and flavors config files.

## Getting Started
### Prerequisites:
```
Make sure the following modules are installed before executing.

* python 3.6+
* pip
* virtualenv
* mongodb, make sure mongo is up and running on localhost
```
### Installation steps:
```
optional
* $ vitualenv dir_name
* $ dir_name\Scripts\activate
```

```
# navigate to 678-18-c/P1 and run pip install
* $ pip install -e .
# or replace . with path to P1
* $ pip install -e /path/to/P1
```

### To Run
```
* $ aggiestack --help
* $ aggiestack config --hardware /path/to/hardware/config/file
* $ aggiestack config --images /path/to/images/config/file
* $ aggiestack config --flavors /path/to/flavors/config/file
* $ aggiestack show hardware
* $ aggiestack show images
* $ aggiestack show flavors
* $ aggiestack show all
* $ aggiestack admin show hardware
* $ aggiestack admin show instances
* $ aggiestack admin can_host <machine_name> <flavor>
* $ aggiestack server create --image IMAGE_NAME --flavor FLAVOR_NAME INSTANCE_NAME
* $ aggiestack server list
* $ aggiestack server delete INSTANCE_NAME
* $ aggiestack admin evacuate RACK_NAME
* $ aggiestack admin remove MACHINE
* $ aggiestack admin add –-mem MEM – disk NUM_DISKS –vcpus VCPUs  –ip IP –rack RACK_NAME MACHINE

```
### Additional implementations:
```
* $ aggiestack admin show imagecaches RACK_NAME
```

### Project structure:
```
P1
  |--aggiestack
      |--commands             #contains implementation of all commands
      |--models               #contains mongo models corresponding to rack, hardware, flavor, image collections
  |--log
      |--aggiestack-log.txt   #created at first run, logs program execution
  |--test-files               #sample config files to quick test
```
