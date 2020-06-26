from pymongo_inmemory import MongoClient
from app_server.videos_db_functions import *

DB = 'test_app_server'

def test_new_collection_is_empty():
	client = MongoClient()
	coll = client[DB]['videos']

	result = list(coll.find({}))
	client.close()
	assert len(result) == 0

### Insert video into db ###

def test_insert_new_video():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test'}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	result = list(collection.find({}))
	first_video = result[0]
	client.close()

	assert len(result) == 1
	assert first_video['title'] == 'test'

def test_insert_ten_videos():
	client = MongoClient()
	collection = client[DB]['videos']
	for i in range(0, 10):
		data = {
		'title': 'test_{0}'.format(i),
		'url': 'test.com',
		'user': 'test'}

		# Esto se hace porque sino el id es repetido y tira conflicto.
		_id = '5edbc9196ab5430010391c7' + str(i)
		insert_video_into_db(_id, data, collection)

	fifth_video = collection.find_one({'title': 'test_5'})
	assert fifth_video is not None
	eleventh_video = collection.find_one({'title': 'test_11'})
	assert eleventh_video is None

	result = list(collection.find({}))
	client.close()

	assert len(result) == 10
	for counter, document in enumerate(result):
		assert document['title'] == 'test_{0}'.format(counter)
