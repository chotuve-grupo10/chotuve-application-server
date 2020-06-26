import os
import logging
from flask import Blueprint, request
from flasgger import swag_from
from app_server.http_functions import *
from app_server.token_functions import *

authentication_bp = Blueprint('authentication', __name__)
logger = logging.getLogger('gunicorn.error')

@authentication_bp.route('/api/register/', methods=['POST'])
@swag_from('docs/register.yml')
def _register_user():

	data = request.json
	api_register = '/api/register/'
	url = os.environ.get('AUTH_SERVER_URL') + api_register

	response = post_auth_server(url, data)
	logger.debug('Finished auth server register request')

	return response.text, response.status_code

@authentication_bp.route('/api/validate_token/', methods=['GET'])
@swag_from('docs/validate_token.yml')
def _validate_token():
	jwt_token = request.headers.get('authorization', None)
	result, status_code = validate_token(jwt_token)
	return result, status_code

@authentication_bp.route('/api/validate_auth_token/', methods=['GET'])
@swag_from('docs/validate_auth_token.yml')
def _validate_auth_token():
	jwt_token = request.headers.get('authorization', None)

	api_validate_token = '/api/validate_token/'
	url = os.environ.get('AUTH_SERVER_URL') + api_validate_token

	headers = {'Content-Type': 'application/json', 'authorization': jwt_token}
	response = get_auth_server_request(url, headers)
	logger.debug('Finished auth server register request')

	return response.json(), response.status_code

@authentication_bp.route('/api/register_with_firebase/', methods=['POST'])
@swag_from('docs/register_with_firebase.yml')
def _register_user_using_firebase():
	jwt_token = request.headers.get('authorization', None)

	api_register_with_firebase = '/api/register_with_firebase/'
	url = os.environ.get('AUTH_SERVER_URL') + api_register_with_firebase

	headers = {'Content-Type': 'application/json', 'authorization': jwt_token}
	response = post_auth_server_with_header(url, headers)
	logger.debug('Finished auth server register with firebase request')

	return response.json(), response.status_code

@authentication_bp.route('/api/login/', methods=['POST'])
@swag_from('docs/login.yml')
def _login_user():

	data = request.json
	api_login = '/api/login/'
	url = os.environ.get('AUTH_SERVER_URL') + api_login

	response = post_auth_server(url, data)
	logger.debug('Finished auth server login request')

	if response.status_code == 200:
		logger.debug('Login request returned successful status code')
		json_response = response.json()
		app_token = generate_app_token(data)
		text = {'Auth token' : json_response['Token'], 'App token' : app_token}
	else:
		logger.debug('Login request returned failure status code')
		text = response.json()

	return text, response.status_code

@authentication_bp.route('/api/login_with_firebase/', methods=['POST'])
@swag_from('docs/login_with_firebase.yml')
def _login_user_using_firebase():
	jwt_token = request.headers.get('authorization', None)

	api_login_with_firebase = '/api/login_with_firebase/'
	url = os.environ.get('AUTH_SERVER_URL') + api_login_with_firebase

	headers = {'Content-Type': 'application/json', 'authorization': jwt_token}
	response = post_auth_server_with_header(url, headers)
	logger.debug('Finished auth server register with firebase request')

	if response.status_code == 200:
		logger.debug('Login request returned successful status code')
		json_response = response.json()
		app_token = generate_app_token(data)
		text = {'Auth token' : json_response['Token'], 'App token' : app_token}
	else:
		logger.debug('Login request returned failure status code')
		text = response.json()

	return text, response.status_code
