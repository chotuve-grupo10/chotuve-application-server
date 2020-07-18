import logging
from datetime import datetime, timedelta
import jwt

# TODO: env var this!
JWT_SECRET = 'secretin'
JWT_ALGORITHM = 'HS256'

logger = logging.getLogger('gunicorn.error')

def generate_app_token(user_data):
	payload = {
        'user_id': user_data['email']
    }

	jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
	return jwt_token

def validate_token(token):
	if token:
		try:
			logger.debug("Token to decode")
			logger.debug(token)
			payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
			user = payload['user_id']
			result = {'Message': 'token valido para user {0}'.format(user)}
			status_code = 200
		except jwt.DecodeError:
			result = {'Message': 'invalid token'}
			status_code = 401
		except jwt.ExpiredSignatureError:
			result = {'Message': 'expired token'}
			status_code = 401
	return result, status_code

def get_user_from_token(token):
	payload = jwt.decode(token, 'secret', algorithms='HS256')
	return payload['user_id']
