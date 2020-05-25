import logging
import requests
import simplejson as json

logger = logging.getLogger('gunicorn.error')

def get_auth_server_ping(url_received):
	logger.debug('Auth server ping requested')
	#TODO: manejar error si url viene vacia
	if url_received is None:
		logger.critical("URL received is empty")
	else:
		logger.debug('URL: ' + url_received)
	response = requests.get(url=url_received)
	return response

def get_media_server_ping(url_received):
	logger.debug('Media server ping requested')
	#TODO: manejar error si url viene vacia
	if url_received is None:
		logger.critical("URL received is empty")
	else:
		logger.debug('URL: ' + url_received)
	response = requests.get(url=url_received)
	return response

def post_auth_server_register(url, user_data):
	logger.debug('Auth server register requested')
	#TODO: manejar error si url viene vacia
	if url is None:
		logger.critical("URL received is empty")
	else:
		logger.debug('URL: ' + url)
	# la espera de esta respuesta es bloqueante?
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(url=url, data=json.dumps(user_data), headers=headers)
	return response
