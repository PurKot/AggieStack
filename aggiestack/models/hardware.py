from mongoengine import *
from aggiestack.models.instance import Instance
from aggiestack.models.rack import Rack
from datetime import *


class Hardware(Document):
    #phySerName = StringField(required=True)
    phySerName = StringField(primary_key =True, required=True)
    rackAssigned = ReferenceField(Rack)
    #ipAddress = StringField(required=True)
    ipAddress = StringField(required =True, unique_with = 'phySerName')
    mem = IntField(required=True)
    numDisks = IntField(required=True)
    numCores = IntField(required=True)
    avMem = IntField()
    avNumDisks = IntField()
    avNumCores = IntField()
    instances = ListField(ReferenceField(Instance)) # list of instances assigned to the server
    date_modified = DateTimeField(default=datetime.utcnow)