from app_server import create_app

def test_hello(client):
    response = client.get('/hello',  follow_redirects=True)
    assert response.data == b'Hello, World!'
    assert response.status_code == 200

def test_abort(client):
	response = client.get('/about/', follow_redirects=True)
	assert response.data == b'This is Application Server for chotuve-10. Still in construction'
	assert response.status_code == 200

def test_fake(client):
	response = client.get('/fake/', follow_redirects=True)
	assert not response.status_code == 200
	assert response.status_code == 404