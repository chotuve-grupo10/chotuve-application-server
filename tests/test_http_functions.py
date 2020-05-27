from unittest.mock import patch
import simplejson as json
import pytest
from app_server import http_functions

def test_auth_server_ping_successfully(client):
	with patch('requests.get') as mock:
		mock.return_value.status_code = 200
		response = http_functions.get_auth_server_ping('test')

		assert response.status_code == 200

def test_auth_server_ping_error_url_empty(client):
	with pytest.raises(ValueError) as e:
		 http_functions.get_auth_server_ping('')
	assert str(e.value) == 'URL received is empty'

def test_auth_media_ping_error_url_empty(client):
	with pytest.raises(ValueError) as e:
		http_functions.get_media_server_ping('')
	assert str(e.value) == 'URL received is empty'

def test_auth_server_ping_error_url_empty(client):
	with pytest.raises(ValueError) as e:
		 http_functions.get_auth_server_ping('')
	assert str(e.value) == 'URL received is empty'

def test_post_auth_server_error_url_empty(client):
	with pytest.raises(ValueError) as e:
		http_functions.post_auth_server('', None)
	assert str(e.value) == 'URL received is empty'

def test_post_auth_server_error_data_empty(client):
	with pytest.raises(ValueError) as e:
		http_functions.post_auth_server('test', None)
	assert str(e.value) == 'User data is None'