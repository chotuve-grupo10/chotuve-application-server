from pymongo_inmemory import MongoClient
from app_server.users_db_functions import *

DB = 'test_app_server'

def test_new_collection_is_empty(client):
	client = MongoClient()
	coll = client[DB]['users']

	result = list(coll.find({}))
	client.close()
	assert len(result) == 0

def test_insert_new_user(client):
	client = MongoClient()
	collection = client[DB]['users']

	data ={'email': 'test@test.com'}
	insert_new_user(data, collection)

	result = list(collection.find({}))
	first_user = result[0]
	client.close()

	assert len(result) == 1
	assert first_user['email'] == 'test@test.com'

def test_insert_ten_users(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 10):
		data = {'email': 'test_{0}@test.com'.format(i)}
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

def test_insert_new_friendship_request_success(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 2):
		data = {'email': 'test_{0}@test.com'.format(i)}
		insert_new_user(data, collection)

	first_user_id = str(collection.find_one({'email': 'test_0@test.com'})['_id'])
	second_user_id = str(collection.find_one({'email': 'test_1@test.com'})['_id'])
	# First user requests second user to be his/her friend
	result, status_code = insert_new_friendship_request(first_user_id, second_user_id, collection)
	assert status_code == 201

	client.close()

def test_insert_new_friendship_request_twice_fails_second_time(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 2):
		data = {'email': 'test_{0}@test.com'.format(i)}
		insert_new_user(data, collection)

	first_user_id = str(collection.find_one({'email': 'test_0@test.com'})['_id'])
	second_user_id = str(collection.find_one({'email': 'test_1@test.com'})['_id'])
	# First user requests second user to be his/her friend
	insert_new_friendship_request(first_user_id, second_user_id, collection)
	# assert status_code == 201
	result, status_code = insert_new_friendship_request(first_user_id, second_user_id, collection)
	assert status_code == 409

	client.close()

def test_insert_new_friendship_request_two_users(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 3):
		data = {'email': 'test_{0}@test.com'.format(i)}
		insert_new_user(data, collection)

	first_user_id = str(collection.find_one({'email': 'test_0@test.com'})['_id'])
	for i in range(1, 3):
		email = 'test_{0}@test.com'.format(i)
		my_user_id = str(collection.find_one({'email': email})['_id'])
		result, status_code = insert_new_friendship_request(my_user_id, first_user_id, collection)
		assert status_code == 201

	requests = collection.find_one({'email': 'test_0@test.com'})['requests']
	assert len(requests) == 2

	client.close()

def test_insert_new_friendship_request_fails_friends_id_is_invalid(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 2):
		data = {'email': 'test_{0}@test.com'.format(i)}
		insert_new_user(data, collection)

	first_user_id = str(collection.find_one({'email': 'test_0@test.com'})['_id'])
	second_user_id = str(collection.find_one({'email': 'test_1@test.com'})['_id'])
	third_id = '000000000000000000000000'
	# First user requests second user to be his/her friend
	insert_new_friendship_request(first_user_id, second_user_id, collection)
	# assert status_code == 201
	result, status_code = insert_new_friendship_request(first_user_id, third_id, collection)
	assert status_code == 403
	assert result == {'Friendship_request':
		'This user you are trying to make friends with does not exist in db'}

	client.close()

def test_insert_new_friendship_request_fails_my_id_is_invalid(client):
	client = MongoClient()
	collection = client[DB]['users']
	for i in range(0, 2):
		data = {'email': 'test_{0}@test.com'.format(i)}
		insert_new_user(data, collection)

	first_user_id = str(collection.find_one({'email': 'test_0@test.com'})['_id'])
	third_id = '000000000000000000000000'
	result, status_code = insert_new_friendship_request(third_id, first_user_id, collection)
	assert status_code == 403
	assert result == {'Friendship_request':
				'The request could not complete successfully because you appear not to be'
				'a valid user in db'}

	client.close()
