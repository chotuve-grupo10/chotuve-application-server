import os
import logging
from flask import Blueprint
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import HTTP_OK, HTTP_NOT_FOUND

notifications_bp = Blueprint('push_notifications', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@notifications_bp.route(
	'/api/users/<user_email>/notifications_token/<token>',
	methods=['POST'])
@swag_from('docs/assign_notifications_token_to_user.yml')
def _assign_push_notifications_token(user_email, token):
	coll = 'users'
	status_code = add_notifications_token(user_email,
										  token,
										  client[DB][coll])

	if status_code == HTTP_OK:
		message = 'La solicitud fue completada con éxito'
	elif status_code == HTTP_NOT_FOUND:
		message = 'La solicitud no se pudo completar porque uno de los usuarios no existe'
	else: # HTTP_INTERNAL_SERVER_ERROR
		message = 'La solicitud no se pudo completar'

	return {'Notifications_token': message}, status_code


def add_notifications_token(user_email, token, collection):
	doc_to_set = {'$set': {'notifications_token': token}}
	result = collection.update_one({'email': user_email},
								   doc_to_set)
	if result.modified_count != 1:
		return HTTP_NOT_FOUND

	return HTTP_OK
