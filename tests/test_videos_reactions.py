# pylint: disable=C0411
from app_server.videos_reactions_db_functions import *
from app_server.videos_db_functions import insert_video_into_db
from pymongo_inmemory import MongoClient

DB = 'test_app_server'

empty_video_01 = {
		'title': 'test',
		'url': 'url',
		'user': 'test_user',
		'isPrivate': True,
		'upload_date': '',
		'comments': [],
		'likes': [],
		'dislikes': []
}

#### Like tests ####

def test_video_not_found_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	status_code = insert_video_into_db('5df1679ee0acd518e5cfd002', empty_video_01, collection)
	assert status_code == HTTP_CREATED

	result = list(collection.find({}))
	assert len(result) == 1

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = like_video('22222225ef1679ee0acd518e', fake_user, collection)
	assert status_code == HTTP_NOT_FOUND
	client.close()

def test_like_is_successful():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = like_video(_id, fake_user, collection)
	assert status_code == HTTP_CREATED

	video = collection.find_one({'_id': ObjectId(_id)})
	assert fake_user['email'] in video['likes']
	client.close()

def test_double_like_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	like_video(_id, fake_user, collection)
	status_code = like_video(_id, fake_user, collection)
	assert status_code == HTTP_CONFLICT

	video = collection.find_one({'_id': ObjectId(_id)})
	assert fake_user['email'] in video['likes']
	client.close()

def test_delete_like_is_successful():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = like_video(_id, fake_user, collection)
	assert status_code == HTTP_CREATED

	status_code = delete_like_video(_id, fake_user, collection)
	assert status_code == HTTP_OK

	video = collection.find_one({'_id': ObjectId(_id)})
	assert not fake_user['email'] in video['likes']
	client.close()

def test_delete_inexistent_like_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = delete_like_video(_id, fake_user, collection)
	assert status_code == HTTP_CONFLICT
	client.close()

### Dislike tests ###

def test_dislike_video_not_found_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	status_code = insert_video_into_db('5df1679ee0acd518e5cfd002', empty_video_01, collection)
	assert status_code == HTTP_CREATED

	result = list(collection.find({}))
	assert len(result) == 1

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = dislike_video('22222225ef1679ee0acd518e', fake_user, collection)
	assert status_code == HTTP_NOT_FOUND
	client.close()

def test_dislike_is_successful():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = dislike_video(_id, fake_user, collection)
	assert status_code == HTTP_CREATED

	video = collection.find_one({'_id': ObjectId(_id)})
	assert fake_user['email'] in video['dislikes']
	client.close()

def test_delete_dislike_is_successful():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = dislike_video(_id, fake_user, collection)
	assert status_code == HTTP_CREATED

	status_code = delete_dislike_video(_id, fake_user, collection)
	assert status_code == HTTP_OK

	video = collection.find_one({'_id': ObjectId(_id)})
	assert not fake_user['email'] in video['likes']
	client.close()

def test_delete_inexistent_dislike_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	_id = '5df1679ee0acd518e5cfd002'
	status_code = insert_video_into_db(_id, empty_video_01, collection)
	assert status_code == HTTP_CREATED

	fake_user = {'email': 'fake_email@gmail.com'}
	status_code = delete_like_video(_id, fake_user, collection)
	assert status_code == HTTP_CONFLICT
	client.close()

### Crossed tests ###
