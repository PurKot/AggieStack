from mongoengine import *
from datetime import *
from aggiestack.models.image import Image

class Rack(Document):
    rackName = StringField(primary_key =True, required=True)
    storageCapacity = IntField(Required =True)
    avStorage = IntField()
    imgCache = ListField(ReferenceField(Image))
