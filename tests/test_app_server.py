from unittest.mock import patch
import simplejson as json

def test_about(client):
	response = client.get('/api/about/', follow_redirects=True)
	description = 'This is Application Server for chotuve-10. Still in construction'
	assert json.loads(response.data) == {'Description' : description}
	assert response.status_code == 200

def test_home(client):
	response = client.get('/', follow_redirects=True)
	assert response.data == b'<h1>Welcome to application server !</h1>'
	assert response.status_code == 200

def test_home_page(client):
	response = client.get('/api/home/', follow_redirects=True)
	assert json.loads(response.data) == {}
	assert response.status_code == 200

def test_fake(client):
	response = client.get('/api/fake/', follow_redirects=True)
	assert not response.status_code == 200
	assert response.status_code == 404

def test_ping_successfully_to_all_servers(client):
	with patch('app_server.get_auth_server_ping') as mock_auth_ping:

		mock_auth_ping.return_value.json.return_value = {'Health' : 'OK'}
		mock_auth_ping.return_value.status_code = 200

		with patch('app_server.get_media_server_ping') as mock_media_ping:

			mock_media_ping.return_value.json.return_value = {'Health' : 'OK'}
			mock_media_ping.return_value.status_code = 200

			response = client.get('/api/ping/')

			value_expected = {}
			value_expected['App Server'] = 'OK'
			value_expected['Auth Server'] = 'OK'
			value_expected['Media Server'] = 'OK'

			assert mock_auth_ping.called
			assert mock_media_ping.called
			assert json.loads(response.data) == value_expected

def test_ping_auth_server_down(client):
	with patch('app_server.get_auth_server_ping') as mock_auth_ping:

		mock_auth_ping.return_value.status_code = 500

		with patch('app_server.get_media_server_ping') as mock_media_ping:

			mock_media_ping.return_value.json.return_value = {'Health' : 'OK'}
			mock_media_ping.return_value.status_code = 200

			response = client.get('/api/ping/')

			value_expected = {}
			value_expected['App Server'] = 'OK'
			value_expected['Auth Server'] = 'DOWN'
			value_expected['Media Server'] = 'OK'

			assert mock_auth_ping.called
			assert mock_media_ping.called
			assert json.loads(response.data) == value_expected

def test_ping_media_server_down(client):
	with patch('app_server.get_auth_server_ping') as mock_auth_ping:

		mock_auth_ping.return_value.json.return_value = {'Health' : 'OK'}
		mock_auth_ping.return_value.status_code = 200

		with patch('app_server.get_media_server_ping') as mock_media_ping:

			mock_media_ping.return_value.status_code = 500

			response = client.get('/api/ping/')

			value_expected = {}
			value_expected['App Server'] = 'OK'
			value_expected['Auth Server'] = 'OK'
			value_expected['Media Server'] = 'DOWN'

			assert mock_auth_ping.called
			assert mock_media_ping.called
			assert json.loads(response.data) == value_expected

def test_ping_media_auth_server_down(client):
	with patch('app_server.get_auth_server_ping') as mock_auth_ping:

		mock_auth_ping.return_value.status_code = 500

		with patch('app_server.get_media_server_ping') as mock_media_ping:

			mock_media_ping.return_value.status_code = 500

			response = client.get('/api/ping/')

			value_expected = {}
			value_expected['App Server'] = 'OK'
			value_expected['Auth Server'] = 'DOWN'
			value_expected['Media Server'] = 'DOWN'

			assert mock_auth_ping.called
			assert mock_media_ping.called
			assert json.loads(response.data) == value_expected
