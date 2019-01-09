from mongoengine import *
from aggiestack import constants

connect(constants.db)

class Flavor(Document):
    flavorName = StringField(required=True)
    ram = IntField(required=True)
    numDisks = IntField(required=True)
    vcpus = IntField(required=True)
