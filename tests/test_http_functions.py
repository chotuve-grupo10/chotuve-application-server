from unittest.mock import patch
import simplejson as json
from app_server import http_functions

def test_auth_server_ping_successfully(client):
	with patch('requests.get') as mock:
		mock.return_value.status_code = 200
		response = http_functions.get_auth_server_ping('test')

		assert response.status_code == 200