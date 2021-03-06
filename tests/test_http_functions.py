from unittest.mock import patch
import pytest
from app_server import http_functions

def test_auth_server_ping_successfully():
	with patch('requests.get') as mock:
		mock.return_value.status_code = 200
		response = http_functions.get_auth_server_request('test')

		assert response.status_code == 200

def test_auth_server_ping_error_url_empty():
	with pytest.raises(ValueError) as error_received:
		http_functions.get_auth_server_request('')
	assert str(error_received.value) == 'URL received is empty'

def test_auth_media_ping_error_url_empty():
	with pytest.raises(ValueError) as error_received:
		http_functions.get_media_server_ping('')
	assert str(error_received.value) == 'URL received is empty'

def test_post_auth_server_error_url_empty():
	with pytest.raises(ValueError) as error_received:
		http_functions.post_auth_server('', None)
	assert str(error_received.value) == 'URL received is empty'

def test_post_auth_server_error_data_empty():
	with pytest.raises(ValueError) as error_received:
		http_functions.post_auth_server('test', None)
	assert str(error_received.value) == 'User data is None'

def test_put_auth_server_error_url_empty():
	with pytest.raises(ValueError) as error_received:
		http_functions.put_auth_server('', None)
	assert str(error_received.value) == 'URL received is empty'
