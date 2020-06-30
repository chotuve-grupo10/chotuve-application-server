from unittest.mock import patch
import simplejson as json

def test_insert_new_friendship_request_was_already_submitted(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		mock.return_value = 409

		value_expected = {'Friendship_request':
				'La solicitud de amistad ya fue enviada y está pendiente'}
		response = client.post('/api/users/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 409
		assert json.loads(response.data) == value_expected

def test_insert_new_friendship_request_failed(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		mock.return_value = 500

		value_expected = {'Friendship_request':
				'La solicitud no se pudo completar'}

		response = client.post('/api/users/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 500
		assert json.loads(response.data) == value_expected

def test_insert_new_friendship_request_is_successfull(client):
	with patch('app_server.users.insert_new_friendship_request') as mock:

		mock.return_value = 201

		value_expected = {'Friendship_request': 'La solicitud fue completada con éxito'}

		response = client.post('/api/users/01xa/friends/01xb',
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 201
		assert json.loads(response.data) == value_expected
