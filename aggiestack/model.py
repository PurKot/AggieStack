import collections

FlavorRepresenation = collections.namedtuple('FlavorRepresenation',['name','ram', 'disks', 'vcpus'])
HardwareRepresentation = collections.namedtuple('HardwareRepresentation',['name', 'ip', 'ram', 'disks', 'vcpus'])
AggregateHardwareRepresentation = collections.namedtuple('AggregateHardwareRepresentation',['ram', 'disks', 'vcpus'])
ImageRepresentation= collections.namedtuple('ImageRepresentation',['name', 'path'])
InstanceRepresentation = collections.namedtuple('InstanceRepresentation',['name', 'phyServer', 'image', 'flavor'])
