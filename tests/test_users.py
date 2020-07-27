from unittest.mock import patch
import simplejson as json
from app_server.token_functions import generate_app_token

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

def test_delete_user_fails_user_doesnt_exist(client):
	with patch('app_server.users.get_user_by_email') as mock_get_user:

		mock_get_user.return_value = None

		user = 'test@test.com'

		value_expected = {'Error': 'user {0} doesnt exist'.format(user)}

		response = client.delete('/api/users/' + user,
							   follow_redirects=False)
		assert mock_get_user.called
		assert response.status_code == 404
		assert json.loads(response.data) == value_expected

def test_delete_user_successfully(client):
	with patch('app_server.users.get_user_by_email') as mock_get_user:

		mock_get_user.return_value = {'email' : 'test@test.com'}

		with patch('app_server.users.insert_complete_user') as mock_insert_user:

			mock_insert_user.return_value = 201

			with patch('app_server.users.delete_user_from_db') as mock:

				mock.return_value = 200

				user = 'test@test.com'

				value_expected = {'Delete': 'user {0} deleted'.format(user)}

				response = client.delete('/api/users/' + user,
									follow_redirects=False)
				assert mock.called
				assert response.status_code == 200
				assert json.loads(response.data) == value_expected

def test_cant_get_user_profile_user_requesting_anohter_profile(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		user_requesting = 'test@test.com'
		mock.return_value = {'Message': 'token valido para user {0}'.format(user_requesting)}, 200

		user_to_get_profile = 'test2@test.com'

		token = generate_app_token({'email': user_requesting})
		response = client.get('/api/users/' + user_to_get_profile,
							headers={'Authorization': token},
							follow_redirects=False)

		assert mock.called
		assert response.status_code == 412
		assert json.loads(response.data) == {'Error' : 'requesting profile from another user'}

def test_get_user_profile_successfully(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		user_requesting = 'test@test.com'
		mock.return_value = {'Message': 'token valido para user {0}'.format(user_requesting)}, 200

		with patch('app_server.users.get_auth_server_request') as mock_get_auth_server:

			serialized_user = {'email': 'test@test.com',
								'full name': 'Test',
								'phone number': '1234',
								'profile picture' : 'test.jpg'}

			mock_get_auth_server.return_value.status_code = 200
			mock_get_auth_server.return_value.json.return_value = serialized_user

			user_to_get_profile = 'test@test.com'

			token = generate_app_token({'email': user_requesting})

			response = client.get('/api/users/' + user_to_get_profile,
								headers={'Authorization': token},
								follow_redirects=False)

			assert mock.called
			assert response.status_code == 200
			assert json.loads(response.data) == serialized_user

def test_cant_modify_user_profile_user_requesting_anohter_profile(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		user_requesting = 'test@test.com'
		mock.return_value = {'Message': 'token valido para user {0}'.format(user_requesting)}, 200

		user_to_get_profile = 'test2@test.com'

		token = generate_app_token({'email': user_requesting})
		response = client.put('/api/users/' + user_to_get_profile,
							headers={'Authorization': token},
							follow_redirects=False)

		assert mock.called
		assert response.status_code == 412
		assert json.loads(response.data) == {'Error' : 'trying to modify profile from another user'}

def test_modify_user_profile_successfully(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		user_requesting = 'test@test.com'
		mock.return_value = {'Message': 'token valido para user {0}'.format(user_requesting)}, 200

		with patch('app_server.users.put_auth_server') as mock_put_auth_server:

			serialized_user = {'Modify': 'successfully modified user with email test@test.com'}

			mock_put_auth_server.return_value.status_code = 200
			mock_put_auth_server.return_value.json.return_value = serialized_user
			with patch('app_server.users.modify_user_in_database') as mock_modification_app_server:
				mock_modification_app_server.return_value = 200

				user_to_get_profile = 'test@test.com'

				token = generate_app_token({'email': user_requesting})

				response = client.put('/api/users/' + user_to_get_profile,
									headers={'Authorization': token},
									follow_redirects=False)

				assert mock.called
				assert response.status_code == 200
				assert json.loads(response.data) == serialized_user
