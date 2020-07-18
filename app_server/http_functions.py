import os
import logging
import requests
import simplejson as json

logger = logging.getLogger('gunicorn.error')

APP_SERVER_TOKEN_HEADER = 'AppServerToken'

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
	header = {APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_MEDIA_SERVER')}
	response = requests.get(url=url_received, headers=header)
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
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain', APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_AUTH_SERVER')}
	response = requests.post(url=url, data=json.dumps(user_data), headers=headers)
	return response

## Esto esta mal pero ya estoy quemado
def post_auth_server_with_header(url, headers):
	logger.debug('Auth server register requested')
	if not url:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	headers[APP_SERVER_TOKEN_HEADER] = os.environ.get('APP_SERVER_TOKEN_FOR_AUTH_SERVER')
	logger.debug('URL: ' + url)
	response = requests.post(url=url, headers=headers)
	return response

def get_media_server_request(url_received, headers_received=None):
	logger.debug('Media server get request')
	if not url_received:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	logger.debug('URL: ' + url_received)
	headers_to_use = {}
	if headers_received is None:
		headers_to_use = {APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_MEDIA_SERVER')}
	else:
		headers_to_use = headers_received
		headers_to_use[APP_SERVER_TOKEN_HEADER] = os.environ.get('APP_SERVER_TOKEN_FOR_MEDIA_SERVER')

	response = requests.get(url=url_received, headers=headers_to_use)
	return response


def put_auth_server(url, data):
	logger.debug('Auth server put reques')
	if not url:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	logger.debug('URL: ' + url)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain', APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_AUTH_SERVER')}

	if data is None:
		response = requests.put(url=url, headers=headers)
	else:
		response = requests.put(url=url, data=json.dumps(data), headers=headers)

	return response

def post_media_server(url, user_data):
	logger.debug('Media server upload video requested')
	if not url:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')
	if user_data is None:
		logger.critical("Video data is None")
		raise ValueError("Video data is None")

	logger.debug('URL: ' + url)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain', APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_MEDIA_SERVER')}
	response = requests.post(url=url, data=json.dumps(user_data), headers=headers)
	return response

def delete_media_server(url):
	logger.debug('Media server delete video requested')
	if not url:
		logger.critical("URL received is empty")
		raise ValueError('URL received is empty')

	logger.debug('URL: ' + url)
	header = {APP_SERVER_TOKEN_HEADER : os.environ.get('APP_SERVER_TOKEN_FOR_MEDIA_SERVER')}
	response = requests.delete(url, headers=header)
	return response
