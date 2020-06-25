from unittest.mock import patch
import simplejson as json

def test_insert_new_friendship_request_was_already_submitted(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		info = {'Friendship_request':
				'Friendship request was already submitted'}
		mock.return_value = info, 409

		value_expected = info
		response = client.post('/api/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 409
		assert json.loads(response.data) == value_expected

def test_insert_new_friendship_request_failed(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		info = {'Friendship_request':
				'The request could not complete successfully'}
		mock.return_value = info, 500

		value_expected = info

		response = client.post('/api/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 500
		assert json.loads(response.data) == value_expected

def test_insert_new_friendship_request_is_successfull(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		info = {'Friendship_request': 'Your request was completed successfully'}
		mock.return_value = info, 201

		value_expected = info

		response = client.post('/api/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 201
		assert json.loads(response.data) == value_expected
