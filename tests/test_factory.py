from app_server import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    response = client.get('/hello',  follow_redirects=True)
    assert response.data == b'Hello, World!'
    assert response.status_code == 200