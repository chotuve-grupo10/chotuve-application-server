from pymongo_inmemory import MongoClient
from app_server.users_db_functions import *
from app_server.relationships_functions import *
from app_server.users import respond_to_friendship_request

DB = 'test_app_server'

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
	assert status_code == HTTP_CREATED

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
	assert status_code == HTTP_CREATED
	status_code = insert_new_friendship_request(data[0]['email'], data[1]['email'], collection)
	assert status_code == HTTP_CONFLICT

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
		assert status_code == HTTP_CREATED

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
	assert status_code == HTTP_CREATED
	status_code = insert_new_friendship_request(data[0]['email'], third_user, collection)
	assert status_code == HTTP_NOT_FOUND

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
	assert status_code == HTTP_NOT_FOUND

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
	assert status_code == HTTP_CREATED
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=True)

	assert status_code == HTTP_OK
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
	assert status_code == HTTP_CREATED
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=True)

	assert status_code == HTTP_FORBIDDEN
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
	assert status_code == HTTP_CREATED
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
	assert status_code == HTTP_NOT_FOUND
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
	assert status_code == HTTP_CREATED
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	result, status_code = respond_to_friendship_request(data[0]['email'],
														data[1]['email'],
														collection,
														accept=False)

	assert status_code == HTTP_OK
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
	assert status_code == HTTP_CREATED
	user = collection.find_one({'email': data[0]['email']})
	assert len(user['requests']) == 1

	# La request la tiene que aceptar el usuario 0, no el 1
	result, status_code = respond_to_friendship_request(data[1]['email'],
														data[0]['email'],
														collection,
														accept=False)

	assert status_code == HTTP_FORBIDDEN
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
	assert status_code == HTTP_CREATED
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
	assert status_code == HTTP_NOT_FOUND
	assert result == {'Reject_friendship_request':
					  'La solicitud no se pudo completar porque uno de los usuarios no existe'}

	client.close()

### Get user friendship requests ###

def test_get_user_requests():
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

	result = get_user_requests_from_db(my_user['email'], collection)
	assert len(result) == 3
	list_result = list(result)
	for i in range(0, 3):
		assert data[i]['email'] == list_result[i]['email']

	for i in range(0, 3):
		respond_to_friendship_request(my_user['email'],
									  data[i]['email'],
									  collection,
									  accept=True)

	result = get_user_requests_from_db(my_user['email'], collection)
	assert len(result) == 0

	client.close()

def test_get_user_requests_fails():
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
	result = get_user_requests_from_db(third_user, collection)
	assert result == HTTP_NOT_FOUND
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
	assert status_code == HTTP_OK

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
		assert status_code == HTTP_OK

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 0

	for i in range(0, 2):
		status_code = delete_friendship_relationship(data[2]['email'],
													 data[i]['email'],
													 collection)
		assert status_code == HTTP_FORBIDDEN #Forbidden

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
	assert status_code == HTTP_FORBIDDEN

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
	assert status_code == HTTP_OK

	third_user = 'surprisingly_inexistent@mail.call'	# Not existing
	status_code = delete_friendship_relationship(data[2]['email'],
												 third_user,
												 collection)
	assert status_code == HTTP_NOT_FOUND

	user = collection.find_one({'email': data[2]['email']})
	assert len(user['friends']) == 0

	client.close()
