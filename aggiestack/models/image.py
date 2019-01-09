from mongoengine import *
from aggiestack import constants

connect(constants.db)

class Image(Document):
    imageName = StringField(primary_key = True, required=True)
    imageSize = IntField(required=True)
    imageLocation = StringField(Required =True)
