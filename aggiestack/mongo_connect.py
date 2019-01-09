import pymongo
from aggiestack import constants
from mongoengine import *

def connectMongo():
	url = "mongodb://" + constants.host + "/" + constants.db
	client = pymongo.MongoClient(url)
	db = client[constants.db]
	return db

aggiestack_db = connectMongo()
connect(constants.db)
