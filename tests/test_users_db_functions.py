from pymongo_inmemory import MongoClient
from app_server.users_db_functions import *

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

	data = {'email': 'test@test.com', 'full Name': ''}
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
				'full Name': ''}
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

### Send friendship requests ###

def test_insert_new_friendship_request_success():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	# First user requests second user to be his/her friend
	_, status_code = insert_new_friendship_request(data[0]['email'],
												   data[1]['email'],
												   collection)
	assert status_code == 201

	client.close()

def test_insert_new_friendship_request_twice_fails_second_time():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	# First user requests second user to be his/her friend
	_, status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 201
	_, status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 409

	client.close()

def test_insert_new_friendship_request_two_users():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	for i in range(1, 3):
		_, status_code = insert_new_friendship_request(data[i]['email'], data[0]['email'], collection)
		assert status_code == 201

	requests = collection.find_one({'email': data[0]['email']})['requests']
	assert len(requests) == 2

	client.close()

def test_insert_new_friendship_request_fails_friends_email_is_invalid():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	# First user requests second user to be his/her friend
	_, status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 201
	result, status_code = insert_new_friendship_request(data[0]['email'], third_user, collection)
	assert status_code == 403
	assert result == {'Friendship_request':
				'The request could not complete successfully because one of the users'
				' is not valid'}

	client.close()
#
def test_insert_new_friendship_request_fails_my_id_is_invalid():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	result, status_code = insert_new_friendship_request(third_user, data[0]['email'], collection)
	assert status_code == 403
	assert result == {'Friendship_request':
				'The request could not complete successfully because one of the users'
				' is not valid'}

	client.close()

### Accept friendship request ###

def test_accept_friendship_request_successfully():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=True)

	assert status_code == 201
	assert result == {'Accept_friendship_request':
			'Your request was completed successfully'}

	client.close()


def test_accept_friendship_request_successfully_appends_friends_to_user_in_db():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)

	respond_to_friendship_request(data[0]['email'],
								  data[1]['email'],
								  collection,
								  accept=True)

	user_0 = collection.find_one({'email': data[0]['email']})
	assert len(user_0['friends']) == 1
	user_1 = collection.find_one({'email': data[1]['email']})
	assert len(user_1['friends']) == 1
	client.close()

def test_accept_friendship_non_existing_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=True)

	assert status_code == 409
	assert result == {'Accept_friendship_request':
		'There is no such friendship request pending to respond'}

	user_0 = collection.find_one({'email': data[0]['email']})
	assert len(user_0['friends']) == 0
	user_1 = collection.find_one({'email': data[1]['email']})
	assert len(user_1['friends']) == 0

	client.close()

def test_accept_friendship_non_existing_user_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	respond_to_friendship_request(data[0]['email'],
								  data[1]['email'],
								  collection,
								  accept=True)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	result, status_code = respond_to_friendship_request(data[0]['email'],
														third_user,
														collection,
														accept=True)
	assert status_code == 403
	assert result == {'Accept_friendship_request':
					  'The request could not complete successfully because one of the users'
					  ' is not valid'
					  }

	client.close()

### Reject friendship request ###

def test_reject_friendship_request_successfully():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=False)

	assert status_code == 201
	assert result == {'Reject_friendship_request':
			'Your request was completed successfully'}

	client.close()

def test_reject_friendship_non_existing_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=False)

	assert status_code == 409
	assert result == {'Reject_friendship_request':
		'There is no such friendship request pending to respond'}

	client.close()

def test_reject_friendship_non_existing_user_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': ''})
		insert_new_user(data[i], collection)

	_, status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	respond_to_friendship_request(data[0]['email'],
								  data[1]['email'],
								  collection,
								  accept=True)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	result, status_code = respond_to_friendship_request(data[0]['email'],
														third_user,
														collection,
														accept=False)
	assert status_code == 403
	assert result == {'Reject_friendship_request':
					  'The request could not complete successfully because one of the users'
					  ' is not valid'
					  }

	client.close()

### Get user information (for now, friends) ###

def test_get_user_information():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': '{0}'.format(i)})
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
		assert status_code == 201

	result = get_user_information_from_db(my_user['email'], collection)
	assert len(result) == 3

	list_result = list(result)
	for i in range(0, 3):
		assert data[i]['email'] == list_result[i]['email']

	assert my_user not in result
	client.close()

def test_get_user_information_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	result = collection.find({})
	assert len(list(result)) == 4

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	result = get_user_information_from_db(third_user, collection)
	assert result == 404
	client.close()

### Filter users by string_query ###
def test_get_users_by_query_successfull():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	_all = get_users_by_query('test', collection)
	assert len(list(_all)) == 4

	one = get_users_by_query('3', collection)
	assert len(list(one)) == 1

	_none = get_users_by_query('SOME_RANDOM_SHIT', collection)
	assert len(list(_none)) == 0

	client.close()

def test_get_users_when_filter_is_empty_gets_all():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 4):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full Name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	_all = get_users_by_query('', collection)
	assert len(list(_all)) == 4

	client.close()
