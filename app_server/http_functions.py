import requests

def get_auth_server_ping(url_received):
	response = requests.get(url=url_received)
	return response
    