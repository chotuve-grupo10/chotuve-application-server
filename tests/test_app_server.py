import os
import simplejson as json

def test_hello(client):
	response = client.get('/api/hello/', follow_redirects=True)
	assert response.data == b'Hello, World!'
	assert response.status_code == 200

def test_about(client):
	response = client.get('/api/about/', follow_redirects=True)
	assert response.data == b'This is Application Server for chotuve-10. Still in construction'
	assert response.status_code == 200

def test_ping_auth_server_is_down(client):
	previous_value = False
	if os.getenv("AUTH_SERVER_URL") is not None:
		old = os.environ['AUTH_SERVER_URL']
		previous_value = True
	os.environ['AUTH_SERVER_URL'] = 'https://chotuve-auth-server-production.herokuapp.com/ping/ds'
	response = client.get('/api/ping/', follow_redirects=True)
	assert json.loads(response.data) == {'App Server' : 'OK', 'Auth Server' : 'DOWN'}
	assert response.status_code == 200

	if previous_value:
		os.environ['AUTH_SERVER_URL'] = old

def test_ping_all_servers_up(client):
	response = client.get('/api/ping/', follow_redirects=True)
	assert json.loads(response.data) == {'App Server' : 'OK', 'Auth Server' : 'OK'}
	assert response.status_code == 200

def test_home(client):
	response = client.get('/', follow_redirects=True)
	assert response.data == b'<h1>Welcome to application server !</h1>'
	assert response.status_code == 200

def test_fake(client):
	response = client.get('/api/fake/', follow_redirects=True)
	assert not response.status_code == 200
	assert response.status_code == 404
