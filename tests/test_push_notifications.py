# pylint: disable=E0012
from pymongo_inmemory import MongoClient
from app_server.push_notifications import add_notifications_token, HTTP_OK, HTTP_CREATED
from app_server.users_db_functions import insert_new_user

DB = 'test_app_server'

def test_add_notification():
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

def test_add_notification_twice():
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
