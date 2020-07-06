import os
import logging
import json
import requests
from flask import Blueprint
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import get_user_by_email
from app_server.utils.http_responses import *

notifications_bp = Blueprint('push_notifications', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

FIREBASE_URL = 'https://fcm.googleapis.com/fcm/send'

@notifications_bp.route(
	'/api/users/<user_email>/notifications/<token>',
	methods=['PUT'])
@swag_from('docs/add_notifications_token_to_user.yml')
def _assign_push_notifications_token(user_email, token):
	coll = 'users'
	status_code = add_notifications_token(user_email,
										  token,
										  client[DB][coll])

	if status_code == HTTP_OK:
		logger.debug('El usuario %s ya tenía el mismo token asociado', user_email)
		message = 'La solicitud fue completada con éxito'
	if status_code == HTTP_CREATED:
		logger.debug('Nuevo token asociado a usuario %s', user_email)
		message = 'La solicitud fue completada con éxito'
	elif status_code == HTTP_NOT_FOUND:
		logger.debug('No se encontró al usuario %s', user_email)
		message = 'La solicitud no se pudo completar porque el usuario no existe'
	else: # HTTP_INTERNAL_SERVER_ERROR
		message = 'La solicitud no se pudo completar'

	return {'Notifications_token': message}, status_code


def add_notifications_token(user_email, token, collection):
	doc_to_set = {'$set': {'notifications_token': token}}

	previous_token = get_user_by_email(user_email, collection)
	if token != previous_token:
		result = collection.update_one({'email': user_email},
									   doc_to_set)
		if result.modified_count != 1:
			return HTTP_NOT_FOUND
		return HTTP_CREATED
	return HTTP_OK

def get_user_token(user_email, collection):
	user = get_user_by_email(user_email, collection)
	if user is not None:
		try:
			return user['notifications_token']
		except KeyError:
			return ''	# Token not available yet
	return None

def send_notification_to_user(user_email, title, message, collection):
	token = get_user_token(user_email, collection)
	if token is not None:

		headers = {'Content-type': 'application/json',
				   'Authorization': 'key='+ os.environ.get('FIREBASE_SERVER_KEY')}

		notification_body = {'title': title,
							 'body': message}

		body = {'notification': notification_body,
				'to': token,
				'priority': 'high'}

		response = requests.post(url=FIREBASE_URL,
								 headers=headers,
								 data=json.dumps(body))
		if response.status_code == HTTP_OK:
			logger.debug('Successfully sent notification to user %s', user_email)
		else:
			logger.error('Error %s sendind notification to user %s',
						 str(response.status_code), user_email)
