# pylint: disable=E0012
from unittest.mock import patch
import simplejson as json
from pymongo_inmemory import MongoClient
from app_server.push_notifications import add_notifications_token, HTTP_CREATED
from app_server.users_db_functions import insert_new_user
from app_server.push_notifications import get_user_token
from app_server.utils import http_responses

DB = 'test_app_server'

def test_add_notification_token():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': '@test.com', 'full name': ''}
	insert_new_user(data, collection)

	status_code = add_notifications_token('@test.com',
										  'FAKE_TOKEN', collection)

	result = list(collection.find({}))
	first_user = result[0]
	client.close()

	assert len(result) == 1
	assert first_user['email'] == '@test.com'
	assert first_user['notifications_token'] == 'FAKE_TOKEN'
	assert status_code == HTTP_CREATED

def test_add_notification_token_twice():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': '@test.com', 'full name': ''}
	insert_new_user(data, collection)

	add_notifications_token('@test.com',
							'FAKE_TOKEN', collection)
	status_code = add_notifications_token('@test.com',
										  'NEW_FAKE_TOKEN', collection)

	result = list(collection.find({}))
	first_user = result[0]
	client.close()

	assert len(result) == 1
	assert first_user['email'] == '@test.com'
	assert first_user['notifications_token'] == 'NEW_FAKE_TOKEN'
	assert status_code == HTTP_CREATED

def test_get_user_token_fails_user_doesnt_exist():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': '@test.com', 'full name': ''}
	insert_new_user(data, collection)

	result = list(collection.find({}))
	first_user = result[0]

	user_token = get_user_token('@prueba.com', collection)
	client.close()

	assert len(result) == 1
	assert first_user['email'] == '@test.com'
	assert user_token is None

def test_get_user_token_fails():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': '@test.com', 'full name': ''}
	insert_new_user(data, collection)

	result = list(collection.find({}))
	first_user = result[0]

	user_token = get_user_token('@test.com', collection)
	client.close()

	assert len(result) == 1
	assert first_user['email'] == '@test.com'
	assert user_token == ''

def test_get_user_token_successfully():
	client = MongoClient()
	collection = client[DB]['users']

	data = {'email': '@test.com', 'full name': ''}
	insert_new_user(data, collection)

	result = list(collection.find({}))
	first_user = result[0]

	status_code = add_notifications_token('@test.com',
										  'NEW_FAKE_TOKEN', collection)

	user_token = get_user_token('@test.com', collection)
	client.close()

	assert len(result) == 1
	assert first_user['email'] == '@test.com'
	assert user_token == 'NEW_FAKE_TOKEN'
	assert status_code == HTTP_CREATED

def test_notification_endpoint_fails_internal_error(client):

	with patch('app_server.push_notifications.add_notifications_token') as mock_add_notification_token:

		mock_add_notification_token.return_value = http_responses.HTTP_INTERNAL_SERVER_ERROR

		user = 'test@test.com'
		token = 'TOKEN'
		response = client.put('/api/users/' + user + '/notifications/' + token, follow_redirects=False)

		assert json.loads(response.data) == {'Notifications_token': 'La solicitud no se pudo completar'}

def test_notification_endpoint_fails_not_found(client):

	with patch('app_server.push_notifications.add_notifications_token') as mock_add_notification_token:

		mock_add_notification_token.return_value = http_responses.HTTP_NOT_FOUND

		user = 'test@test.com'
		token = 'TOKEN'
		response = client.put('/api/users/' + user + '/notifications/' + token, follow_redirects=False)

		assert json.loads(response.data) == {'Notifications_token': 'La solicitud no se pudo completar porque el usuario no existe'}

def test_notification_endpoint_successfully_new_entry(client):

	with patch('app_server.push_notifications.add_notifications_token') as mock_add_notification_token:

		mock_add_notification_token.return_value = http_responses.HTTP_CREATED

		user = 'test@test.com'
		token = 'TOKEN'
		response = client.put('/api/users/' + user + '/notifications/' + token, follow_redirects=False)

		assert json.loads(response.data) == {'Notifications_token': 'La solicitud fue completada con éxito'}

def test_notification_endpoint_successfully_existent_entry(client):

	with patch('app_server.push_notifications.add_notifications_token') as mock_add_notification_token:

		mock_add_notification_token.return_value = http_responses.HTTP_OK

		user = 'test@test.com'
		token = 'TOKEN'
		response = client.put('/api/users/' + user + '/notifications/' + token, follow_redirects=False)

		assert json.loads(response.data) == {'Notifications_token': 'La solicitud fue completada con éxito'}
