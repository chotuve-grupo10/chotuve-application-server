import requests

def get_auth_server_ping(url_received):
	response = requests.get(url=url_received)
	return response

def get_media_server_ping(url_received):
	response = requests.get(url=url_received)
	return response

# def get_auth_server_login_response(url_received, parameters_json):
#	# puedo mandarle acá un POST al auth server y esperar su respuesta?
#	# la espera de esa respuesta es bloqueante?
#	try:
# 		response = requests.get(url=url_received)
# 		return response
#	except KeyError:
#		# log error and return None