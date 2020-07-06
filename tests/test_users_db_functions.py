from unittest.mock import patch
from pymongo_inmemory import MongoClient
from app_server.users_db_functions import *
from app_server.users import respond_to_friendship_request
from app_server.relationships_functions import insert_new_friendship_request

DB = 'test_app_server'

def test_new_collection_is_empty():
	client = MongoClient()
	coll = client[DB]['users']

	result = list(coll.find({}))
	client.close()
	assert len(result) == 0

### Insert users into db ###

def test_insert_new_user():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': 'test@test.com', 'full name': ''}
	insert_new_user(data, collection)

	result = list(collection.find({}))
	first_user = result[0]
	client.close()

	assert len(result) == 1
	assert first_user['email'] == 'test@test.com'

def test_insert_ten_users():
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 10):
		data = {'email': 'test_{0}@test.com'.format(i),
				'full name': ''}
		insert_new_user(data, collection)

	fifth_user = collection.find_one({'email': 'test_5@test.com'})
	assert fifth_user is not None
	eleventh_user = collection.find_one({'email': 'test_11@test.com'})
	assert eleventh_user is None

	result = list(collection.find({}))
	client.close()

	assert len(result) == 10
	for counter, document in enumerate(result):
		assert document['email'] == 'test_{0}@test.com'.format(counter)

def test_insert_firebase_user_inserts_new_user_once():
	client = MongoClient()
	collection = client[DB]['users']
	data = {'email': 'test_1@test.com',
			'name': 'No Name'}

	insert_new_firebase_user_if_not_exists(data, collection)
	insert_new_firebase_user_if_not_exists(data, collection)

	result = collection.find({})
	assert len(list(result)) == 1

	data = {'email': 'test_2@test.com',
			'name': 'No Name'}

	insert_new_firebase_user_if_not_exists(data, collection)

	result = collection.find({})
	assert len(list(result)) == 2

	client.close()

### Get user friends ###

def test_get_user_friends():
	with patch('app_server.relationships_functions.send_notification_to_user') as _mock:
		client = MongoClient()
		collection = client[DB]['users']
		data = []
		for i in range(0, 4):
			data.append({'email': 'test_{0}@test.com'.format(i),
						 'full name': '{0}'.format(i)})
			insert_new_user(data[i], collection)

		result = collection.find({})
		assert len(list(result)) == 4

		my_user = data[3]
		for i in range(0, 3):
			insert_new_friendship_request(data[i]['email'], my_user['email'], collection)
		for i in range(0, 3):
			_, status_code = respond_to_friendship_request(my_user['email'],
														   data[i]['email'],
														   collection,
														   accept=True)
			assert status_code == 200

		result = get_user_friends_from_db(my_user['email'], collection)
		assert len(result) == 3

		list_result = list(result)
		for i in range(0, 3):
			assert data[i]['email'] == list_result[i]['email']

		assert my_user not in result
		client.close()

def test_get_user_friends_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	result = collection.find({})
	assert len(list(result)) == 4

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	result = get_user_friends_from_db(third_user, collection)
	assert result == 404
	client.close()

### Filter users by string_query ###

def test_get_users_by_query_successfull():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	almost_all = get_users_by_query('test', 'test_3@test.com', collection)
	assert len(list(almost_all)) == 3

	one = get_users_by_query('3', 'test_2@test.com', collection)
	assert len(list(one)) == 1

	zero = get_users_by_query('3', 'test_3@test.com', collection)
	assert len(list(zero)) == 0

	_none = get_users_by_query('SOME_RANDOM_SHIT', 'test_3@test.com', collection)
	assert len(list(_none)) == 0

	client.close()

def test_get_users_when_filter_is_empty_gets_all_except_me():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 5):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	_all = get_users_by_query('', 'test_4@test.com', collection)
	assert len(list(_all)) == 4

	emails = [item['email'] for item in list(_all)]
	assert 'test_4@test.com' not in emails

	client.close()
