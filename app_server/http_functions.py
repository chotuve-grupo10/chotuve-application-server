import requests

def get_auth_server_ping(url_received):
	response = requests.get(url=url_received)
	return response

def get_media_server_ping(url_received):
	response = requests.get(url=url_received)
	return response

def post_auth_server_register(url, user_data):
	# la espera de esta respuesta es bloqueante?
	response = requests.post(url=url, data=user_data)
	return response
