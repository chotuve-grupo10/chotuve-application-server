from unittest.mock import patch
from pymongo_inmemory import MongoClient
from app_server.videos_db_functions import *
from app_server.users_db_functions import insert_new_user
from app_server.users import respond_to_friendship_request
from app_server.relationships_functions import insert_new_friendship_request

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
	 'user': 'test',
	 'isPrivate': True}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	result = list(collection.find({}))
	first_video = result[0]
	client.close()

	assert len(result) == 1
	assert first_video['title'] == 'test'
	assert first_video['is_private']

def test_insert_ten_videos():
	client = MongoClient()
	collection = client[DB]['videos']
	for i in range(0, 10):
		data = {
		'title': 'test_{0}'.format(i),
		'url': 'test.com',
		'user': 'test',
		'isPrivate': False}

		# Esto se hace porque sino el id es repetido y tira conflicto.
		_id = '5edbc9196ab5430010391c7' + str(i)
		insert_video_into_db(_id, data, collection)

	fifth_video = collection.find_one({'title': 'test_5'})
	assert fifth_video is not None
	assert not fifth_video['is_private']
	eleventh_video = collection.find_one({'title': 'test_11'})
	assert eleventh_video is None

	result = list(collection.find({}))
	client.close()

	assert len(result) == 10
	for counter, document in enumerate(result):
		assert document['title'] == 'test_{0}'.format(counter)

def test_insert_duplicate_key_video_fails():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)
	response = insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	client.close()

	assert response == HTTP_INTERNAL_SERVER_ERROR

### Delete video tests ###

def test_delete_video_is_successful():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, data, collection)

	result = list(collection.find({}))
	assert len(result) == 1

	status = delete_video_in_db(_id, collection)
	assert status == HTTP_OK

	result = list(collection.find({}))
	assert len(result) == 0
	client.close()

def test_delete_video_not_exists():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {'title': 'test',
			'url': 'test.com',
			'user': 'test',
			'isPrivate': True
	}

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, data, collection)

	another_id = '66dbc9196ab5430010391c79'
	status = delete_video_in_db(another_id, collection)
	assert status == HTTP_NOT_FOUND

	result = list(collection.find({}))
	assert len(result) == 1
	client.close()

## Get video tests ##

def test_get_video_fails_type_error():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	result = list(collection.find({}))

	assert len(result) == 1

	video_obtained = get_video_by_objectid('test', collection)
	assert video_obtained is None

	client.close()

def test_get_video_successfully():
	client = MongoClient()
	collection = client[DB]['videos']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	result = list(collection.find({}))
	first_video = result[0]

	assert len(result) == 1

	video_obtained = get_video_by_objectid(ObjectId('5edbc9196ab5430010391c79'), collection)
	assert video_obtained == first_video

	client.close()

## Filter videos for specific user tests ##

def test_filter_videos_for_specific_user_fails_user_doesnt_exist():
	client = MongoClient()
	collection = client[DB]['videos']
	users_collection = client[DB]['users']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	insert_video_into_db('5edbc9196ab5430010391c79', data, collection)

	result = list(collection.find({}))

	assert len(result) == 1

	filtered_videos = filter_videos_for_specific_user([data], 'test', users_collection, collection)
	assert filtered_videos == []

	client.close()

def test_filter_videos_for_specific_user_successfuly_all_private_videos_non_friends():
	client = MongoClient()
	collection = client[DB]['videos']
	users_collection = client[DB]['users']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': 'test2',
	 'isPrivate': True}

	_id1 = '5edbc9196ab5430010391c79'
	_id2 = '5edbc9196ab5430010391c78'

	insert_video_into_db(_id1, data, collection)
	insert_video_into_db(_id2, data2, collection)

	data['_id'] = _id1
	data2['_id'] = _id2

	result = list(collection.find({}))

	assert len(result) == 2

	user = {'email': 'prueba@prueba.com', 'full name': 'Prueba'}
	insert_new_user(user, users_collection)

	filtered_videos = filter_videos_for_specific_user([data, data2], 'prueba@prueba.com', users_collection, collection)
	assert len(filtered_videos) == 0

	client.close()

def test_filter_videos_for_specific_user_successfuly_all_public_videos():
	client = MongoClient()
	collection = client[DB]['videos']
	users_collection = client[DB]['users']

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': False}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': 'test2',
	 'isPrivate': False}

	_id1 = '5edbc9196ab5430010391c79'
	_id2 = '5edbc9196ab5430010391c78'

	insert_video_into_db(_id1, data, collection)
	insert_video_into_db(_id2, data2, collection)

	data['_id'] = _id1
	data2['_id'] = _id2

	result = list(collection.find({}))

	assert len(result) == 2

	user = {'email': 'prueba@prueba.com', 'full name': 'Prueba'}
	insert_new_user(user, users_collection)

	filtered_videos = filter_videos_for_specific_user([data, data2], 'prueba@prueba.com', users_collection, collection)
	assert len(filtered_videos) == 2
	assert filtered_videos[0] == data
	assert filtered_videos[1] == data2

	client.close()

def test_filter_videos_for_specific_user_successfuly_all_own_videos():
	client = MongoClient()
	collection = client[DB]['videos']
	users_collection = client[DB]['users']

	user_filtering = 'test@test.com'

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': user_filtering,
	 'isPrivate': True}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': user_filtering,
	 'isPrivate': True}

	_id1 = '5edbc9196ab5430010391c79'
	_id2 = '5edbc9196ab5430010391c78'

	insert_video_into_db(_id1, data, collection)
	insert_video_into_db(_id2, data2, collection)

	data['_id'] = _id1
	data2['_id'] = _id2

	result = list(collection.find({}))

	assert len(result) == 2

	user = {'email': user_filtering, 'full name': 'Prueba'}
	insert_new_user(user, users_collection)

	filtered_videos = filter_videos_for_specific_user([data, data2], user_filtering, users_collection, collection)
	assert len(filtered_videos) == 2
	assert filtered_videos[0] == data
	assert filtered_videos[1] == data2

	client.close()

def test_filter_videos_for_specific_user_successfuly_friend_video():
	client = MongoClient()
	collection = client[DB]['videos']
	users_collection = client[DB]['users']

	user1_email = 'prueba@prueba.com'
	user2_email = 'test@test.com'

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': user2_email,
	 'isPrivate': True}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': 'test2',
	 'isPrivate': True}

	_id1 = '5edbc9196ab5430010391c79'
	_id2 = '5edbc9196ab5430010391c78'

	insert_video_into_db(_id1, data, collection)
	insert_video_into_db(_id2, data2, collection)

	data['_id'] = _id1
	data2['_id'] = _id2

	result = list(collection.find({}))

	assert len(result) == 2

	user = {'email': user1_email,
			'full name': 'Prueba',
			'friends': [],
		   'requests': []
			}

	user2 = {'email': user2_email,
			'full name': 'Test',
			'friends': [],
		   'requests': []
			}

	insert_new_user(user, users_collection)
	insert_new_user(user2, users_collection)

	with patch('app_server.relationships_functions.send_notification_to_user') as _mock:

		insert_new_friendship_request(user2_email, user1_email, users_collection)
		respond_to_friendship_request(user1_email, user2_email, users_collection, accept=True)

		filtered_videos = filter_videos_for_specific_user([data, data2], 'prueba@prueba.com', users_collection, collection)
		assert len(filtered_videos) == 1
		assert filtered_videos[0] == data

		client.close()

## Filter tests ##

def test_filter_public_videos_successfully():

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': 'test2',
	 'isPrivate': False}

	videos_list = [data, data2]
	result = filter_public_videos(videos_list)
	first_video = result[0]

	assert len(result) == 1
	assert first_video['title'] == 'test2'
	assert not first_video['isPrivate']

def test_delete_keys_successfully():

	data = {
	 'title': 'test',
	 'url': 'test.com',
	 'user': 'test',
	 'isPrivate': True}

	data2 = {
	 'title': 'test2',
	 'url': 'test2.com',
	 'user': 'test2',
	 'isPrivate': False}

	videos_list = [data, data2]
	result = delete_keys_from_videos(videos_list, ['user'])
	first_video = result[0]

	value_expected = {
	 'title': 'test',
	 'url': 'test.com',
	 'isPrivate': True}

	assert len(result) == 2
	assert first_video == value_expected

### Comments test ###

def test_comment_video():
	client = MongoClient()
	collection = client[DB]['videos']

	video_data = {'title': 'test',
			'url': 'test.com',
			'user': 'test',
			'isPrivate': True,
			'comments': []
	}

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, video_data, collection)

	user = 'test_01@test.com'
	text = 'Este es un comentario de prueba'
	status_code = insert_comment_into_video(_id, user, text, collection)
	assert status_code == HTTP_CREATED

	this_video = collection.find_one({'_id': ObjectId(_id)})

	assert len(this_video['comments']) == 1
	comment = this_video['comments'][0]

	assert comment['text'] == text
	assert comment['user'] == user
	assert 'timestamp' in comment.keys()
	client.close()

def test_second_comment_video_comes_first():
	client = MongoClient()
	collection = client[DB]['videos']

	video_data = {'title': 'test',
			'url': 'test.com',
			'user': 'test',
			'isPrivate': True,
			'comments': []
	}

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, video_data, collection)

	user = 'test_01@test.com'
	text_01 = 'Este es un comentario de prueba'
	insert_comment_into_video(_id, user, text_01, collection)
	text_02 = 'Este es el segundo comentario'
	status_code = insert_comment_into_video(_id, user, text_02, collection)
	assert status_code == HTTP_CREATED

	this_video = collection.find_one({'_id': ObjectId(_id)})

	assert len(this_video['comments']) == 2
	comment = this_video['comments'][0]

	assert comment['text'] == text_02
	assert comment['user'] == user
	assert 'timestamp' in comment.keys()
	client.close()

def test_ten_comments_in_order():
	client = MongoClient()
	collection = client[DB]['videos']

	video_data = {'title': 'test',
				  'url': 'test.com',
				  'user': 'test',
				  'isPrivate': True,
				  'comments': []
				  }

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, video_data, collection)

	user = 'test_01@test.com'
	text = 'Este es el comentario numero {0}'
	for i in range(0, 10):
		text = text.format(i)
		insert_comment_into_video(_id, user, text, collection)

	this_video = collection.find_one({'_id': ObjectId(_id)})

	assert len(this_video['comments']) == 10

	for i in range(10, 0):
		comment = this_video['comments'][i]
		assert comment['text'] == text.format(i)

	client.close()

def test_comment_video_fails_video_does_not_exist():
	client = MongoClient()
	collection = client[DB]['videos']

	video_data = {'title': 'test',
			'url': 'test.com',
			'user': 'test',
			'isPrivate': True,
			'comments': []
	}

	_id = '5edbc9196ab5430010391c79'
	insert_video_into_db(_id, video_data, collection)

	user = 'test_01@test.com'
	text = 'Este es un comentario de prueba'
	__inexistent_id = '5edbc9196ab5430010391c78'
	status_code = insert_comment_into_video(__inexistent_id, user, text, collection)
	assert status_code == HTTP_INTERNAL_SERVER_ERROR

	this_video = collection.find_one({'_id': ObjectId(_id)})

	assert len(this_video['comments']) == 0
	client.close()
