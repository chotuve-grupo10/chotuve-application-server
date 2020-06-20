# pylint: disable=C0103
import os
from pymongo import MongoClient

client = MongoClient(os.environ.get('DATABASE_URL'))

def test_database():
	db = 'app_server'
	coll = 'amistades'
	amistades = client[db][coll]
	amistades.insert_one({'this_is': 'primera_prueba_nueva_db'})
