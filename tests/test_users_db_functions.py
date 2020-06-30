from pymongo_inmemory import MongoClient
from app_server.users_db_functions import *
from app_server.users import respond_to_friendship_request

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


### Send friendship requests ###

def test_insert_new_friendship_request_success():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	# First user requests second user to be his/her friend
	status_code = insert_new_friendship_request(data[0]['email'],
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
					 'full name': ''})
		insert_new_user(data[i], collection)

	# First user requests second user to be his/her friend
	status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 201
	status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 409

	client.close()

def test_insert_new_friendship_request_two_users():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	for i in range(1, 3):
		status_code = insert_new_friendship_request(data[i]['email'], data[0]['email'], collection)
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
					 'full name': ''})
		insert_new_user(data[i], collection)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	# First user requests second user to be his/her friend
	status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == 201
	status_code = insert_new_friendship_request(data[0]['email'], third_user, collection)
	assert status_code == 404

	client.close()
#
def test_insert_new_friendship_request_fails_my_id_is_invalid():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	status_code = insert_new_friendship_request(third_user, data[0]['email'], collection)
	assert status_code == 404

	client.close()

### Accept friendship request ###

def test_accept_friendship_request_successfully():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=True)

	assert status_code == 200
	assert result == {'Accept_friendship_request':
			'Solicitud de amistad aceptada con éxito'}

	client.close()


def test_accept_friendship_request_successfully_appends_friends_to_user_in_db():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
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
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=True)

	assert status_code == 403
	assert result == {'Accept_friendship_request':
		'La solicitud de amistad que queres responder no existe'}

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
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
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
	assert status_code == 404
	assert result == {'Accept_friendship_request':
					  'La solicitud no se pudo completar porque uno de los usuarios no existe'}

	client.close()

### Reject friendship request ###

def test_reject_friendship_request_successfully():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=False)

	assert status_code == 200
	assert result == {'Reject_friendship_request':
			'Solicitud de amistad rechazada con éxito'}

	client.close()

def test_reject_friendship_non_existing_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
	assert status_code == 201
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=False)

	assert status_code == 403
	assert result == {'Reject_friendship_request':
		'La solicitud de amistad que queres responder no existe'}

	client.close()

def test_reject_friendship_non_existing_user_fails():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 2):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': ''})
		insert_new_user(data[i], collection)

	status_code = insert_new_friendship_request(data[1]['email'], data[0]['email'], collection)
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
	assert status_code == 404
	assert result == {'Reject_friendship_request':
					  'La solicitud no se pudo completar porque uno de los usuarios no existe'}

	client.close()

### Get user information (for now, friends) ###

def test_get_user_information():
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
					 'full name': '{0}'.format(i)})
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

### Delete friendship relationship ###

def test_delete_friendship_relationship_is_successful():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	for i in range(0, 2):
		insert_new_friendship_request(data[i]['email'], data[2]['email'], collection)
		respond_to_friendship_request(data[2]['email'], data[i]['email'],
									  collection, accept=True)

	user_02 = collection.find_one({'email': data[2]['email']})
	assert len(user_02['friends']) == 2
	user_00 = collection.find_one({'email': data[0]['email']})
	assert len(user_00['friends']) == 1
	user_01 = collection.find_one({'email': data[1]['email']})
	assert len(user_01['friends']) == 1

	status_code = delete_friendship_relationship(data[2]['email'],
												 data[0]['email'],
												 collection)
	assert status_code == 200

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 1
	client.close()

def test_delete_friendship_relationship_twice_fails_second_time():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	for i in range(0, 2):
		insert_new_friendship_request(data[i]['email'], data[2]['email'], collection)
		respond_to_friendship_request(data[2]['email'], data[i]['email'],
									  collection, accept=True)

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 2

	for i in range(0, 2):
		status_code = delete_friendship_relationship(data[i]['email'],
													 data[2]['email'],
													 collection)
		assert status_code == 200

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 0

	for i in range(0, 2):
		status_code = delete_friendship_relationship(data[2]['email'],
													 data[i]['email'],
													 collection)
		assert status_code == 403 #Forbidden

	client.close()

def test_delete_friendship_relationship_fails_when_friendship_does_not_exist():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	for i in range(0, 1):
		insert_new_friendship_request(data[i]['email'], data[2]['email'], collection)
		respond_to_friendship_request(data[2]['email'], data[i]['email'],
									  collection, accept=True)

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 1

	status_code = delete_friendship_relationship(data[2]['email'],
												 data[1]['email'],
												 collection)
	assert status_code == 403

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 1
	client.close()

def test_delete_friendship_relationship_fails_when_user_is_not_found():
	client = MongoClient()
	collection = client[DB]['users']
	data = []
	for i in range(0, 3):
		data.append({'email': 'test_{0}@test.com'.format(i),
					 'full name': '{0}'.format(i)})
		insert_new_user(data[i], collection)

	for i in range(0, 1):
		insert_new_friendship_request(data[i]['email'], data[2]['email'], collection)
		respond_to_friendship_request(data[2]['email'], data[i]['email'],
									  collection, accept=True)

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 1

	status_code = delete_friendship_relationship(data[2]['email'],
												 data[0]['email'],
												 collection)
	assert status_code == 200

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	status_code = delete_friendship_relationship(data[2]['email'],
												 third_user,
												 collection)
	assert status_code == 404

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 0

	client.close()
