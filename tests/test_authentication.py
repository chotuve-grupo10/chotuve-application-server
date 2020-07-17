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

def test_forgot_password_fails_problem_with_auth_server(client):
	with patch('app_server.authentication.post_auth_server_with_header') as mock:

		mock.return_value.status_code = 500
		mock.return_value.json.return_value = {'Error' : 'Error'}

		user_email = 'test@test.com'
		response = client.post('/api/users/' + user_email + '/reset_password_token', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == {'Error': 'there is a problem with the auth server'}

def test_forgot_password_successfully(client):
	with patch('app_server.authentication.post_auth_server_with_header') as mock:

		mock.return_value.status_code = 200
		user_email = 'test@test.com'
		value = {'Forgot password' : 'email sent to {0}'.format(user_email)}
		mock.return_value.json.return_value = value

		response = client.post('/api/users/' + user_email + '/reset_password_token', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value

def test_reset_password_fails_problem_with_auth_server(client):
	with patch('app_server.authentication.put_auth_server') as mock:

		mock.return_value.status_code = 500
		mock.return_value.json.return_value = {'Error' : 'Error'}

		user_email = 'test@test.com'
		response = client.put('/api/users/' + user_email + '/password', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == {'Error': 'there is a problem with the auth server'}

def test_reset_password_successfully(client):
	with patch('app_server.authentication.put_auth_server') as mock:

		mock.return_value.status_code = 200
		user_email = 'test@test.com'
		value = {'Reset password' : 'password updated for user {0}'.format(user_email)}
		mock.return_value.json.return_value = value

		response = client.put('/api/users/' + user_email + '/password', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value
