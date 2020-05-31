import logging
import requests
import simplejson as json

logger = logging.getLogger('gunicorn.error')

def get_auth_server_request(url_received, headers_received=None):
	logger.debug('Auth server get request')
	if not url_received:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	logger.debug('URL: ' + url_received)

	if headers_received is None:
		response = requests.get(url=url_received)
	else:
		response = requests.get(url=url_received, headers=headers_received)
	return response

def get_media_server_ping(url_received):
	logger.debug('Media server ping requested')
	if not url_received:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	logger.debug('URL: ' + url_received)
	response = requests.get(url=url_received)
	return response

def post_auth_server(url, user_data):
	logger.debug('Auth server register requested')
	if not url:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')
	if user_data is None:
		logger.critical("User data is None")
		raise ValueError("User data is None")

	logger.debug('URL: ' + url)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(url=url, data=json.dumps(user_data), headers=headers)
	return response
