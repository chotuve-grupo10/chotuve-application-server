import os
import logging
from flask import Blueprint, request
from flasgger import swag_from
from app_server.http_functions import *

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

@authentication_bp.route('/api/register_with_facebook/', methods=['POST'])
@swag_from('docs/register_with_facebook.yml')
def _register_user_using_facebook():
	return {}

@authentication_bp.route('/api/register_with_google/', methods=['POST'])
@swag_from('docs/register_with_google.yml')
def _register_user_using_google():
	return {}

@authentication_bp.route('/api/login/', methods=['POST'])
@swag_from('docs/login.yml')
def _login_user():

	data = request.json
	api_login = '/api/login/'
	url = os.environ.get('AUTH_SERVER_URL') + api_login

	response = post_auth_server(url, data)
	logger.debug('Finished auth server login request')

	return response.text, response.status_code

@authentication_bp.route('/api/login_with_facebook/', methods=['POST'])
@swag_from('docs/login_with_facebook.yml')
def _login_user_using_facebook():
	return {}

@authentication_bp.route('/api/login_with_google/', methods=['POST'])
@swag_from('docs/login_with_google.yml')
def _login_user_using_google():
	return {}
