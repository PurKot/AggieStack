from mongoengine import *
from datetime import *


class Instance(Document):
    instanceName = StringField(primary_key = True, required=True)
    # option 1
    # phySerName = ReferenceField(Hardware) or embed document
    # flavorName = ReferenceField(Flavor)
    # imageName = ReferenceField(Image)

    ##option 2
    phySerName = StringField(required=True)
    flavorName = StringField(required=True)
    imageName = StringField(required=True)
    rackAssigned = StringField(required=True)
    date_modified = DateTimeField(default=datetime.utcnow)
