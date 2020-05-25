import logging
from flask import Blueprint, current_app, request
from flasgger import swag_from

authentication_bp = Blueprint('authentication', __name__)
logger = logging.getLogger('gunicorn.error')

@authentication_bp.route('/api/register/', methods=['POST'])
@swag_from('docs/register.yml')
def _register_user():
    #user_request = request.headers['AuthenticationHeader']
    #response_auth_server = post_auth_server_register(os.environ.get('AUTH_SERVER_URL'), user_request)
    return {}

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
    return {}

@authentication_bp.route('/api/login_with_facebook/', methods=['POST'])
@swag_from('docs/login_with_facebook.yml')
def _login_user_using_facebook():
    return {}

@authentication_bp.route('/api/login_with_google/', methods=['POST'])
@swag_from('docs/login_with_google.yml')
def _login_user_using_google():
    return {}