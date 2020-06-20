import os
from pymongo import MongoClient

client = MongoClient(os.environ.get('DATABASE_URL'))

def test_database():
	db = 'appServer'
	coll = 'amistades'
	amistades = client[db][coll]
	amistades.insert_one({'this_is': 'tercera_pruebita'})