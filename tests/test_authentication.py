from unittest.mock import patch
import simplejson as json

def test_login_fails_auth_server_returns_invalid_password(client):
	with patch('app_server.authentication.post_auth_server') as mock:

		data = {'email': 'test_email@test.com', 'password' : 'test'}

		mock.return_value.status_code = 401
		mock.return_value.json.return_value = {'Login' : 'invalid password'}

		value_expected = {'Login' : 'invalid password'}
		response = client.post('/api/login/', json=data, follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_login_fails_auth_server_returns_user_not_found(client):
	with patch('app_server.authentication.post_auth_server') as mock:

		data = {'email': 'test_email@test.com', 'password' : 'test'}

		mock.return_value.status_code = 404
		mock.return_value.json.return_value = {'Login' : 'user NOT found'}

		value_expected = {'Login' : 'user NOT found'}
		response = client.post('/api/login/', json=data, follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_login_success_returns_two_tokens(client):
	with patch('app_server.authentication.post_auth_server') as mock:

		data = {'email': 'test_email@test.com', 'password' : 'test'}

		mock.return_value.status_code = 200
		mock.return_value.json.return_value = {'Token' : '12k22l232nj3gghghg32'}

		auth_value_expected = 'Auth token'
		app_value_expected = '12k22l232nj3gghghg32'
		response = client.post('/api/login/', json=data, follow_redirects=False)
		assert mock.called
		assert auth_value_expected in json.loads(response.data)
		assert app_value_expected in json.loads(response.data)[auth_value_expected]
		