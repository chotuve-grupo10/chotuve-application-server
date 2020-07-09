import os
import json
import logging
from flask import Blueprint, request
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import *
from app_server.relationships_functions import *

users_bp = Blueprint('users_relationships', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
				methods=['POST'])
@swag_from('docs/friendship_request.yml')
def _request_friendships(user_email, new_friends_email):
	coll = 'users'
	status_code = insert_new_friendship_request(user_email,
												new_friends_email,
												client[DB][coll])
	if status_code == HTTP_CREATED:
		message = 'La solicitud fue completada con éxito'
	elif status_code == HTTP_FORBIDDEN:
		message = 'Este usuario ya es tu amigo'
	elif status_code == HTTP_NOT_FOUND:
		message = 'La solicitud no se pudo completar porque uno de los usuarios no existe'
	elif status_code == HTTP_METHOD_NOT_ALLOWED:
		message = "No podes enviarte una solicitud de amistad a vos mismo. Eso es raro"
	elif status_code == HTTP_CONFLICT:
		message = 'La solicitud de amistad ya fue enviada y está pendiente'
	else: # HTTP_INTERNAL_SERVER_ERROR
		message = 'La solicitud no se pudo completar'

	return {'Friendship_request': message}, status_code

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
				methods=['PATCH'])
@swag_from('docs/friendship_response.yml')
def _respond_to_friendship_request(user_email, new_friends_email):
	data = request.json
	try:
		accept_or_reject = data['response']
	except KeyError:
		return {'Friendship_response': 'Response was missing'}, HTTP_BAD_REQUEST

	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=accept_or_reject)
	return response, status_code

def respond_to_friendship_request(user_email, new_friends_email, collection, accept):
	if accept:
		status_code = accept_friendship_request(user_email, new_friends_email, collection)

		if status_code == HTTP_OK:
			message = 'Solicitud de amistad aceptada con éxito'
		elif status_code == HTTP_FORBIDDEN:
			message = 'La solicitud de amistad que queres responder no existe'
		elif status_code == HTTP_NOT_FOUND:
			message = 'La solicitud no se pudo completar porque uno de los usuarios no existe'
		else: # HTTP_INTERNAL_SERVER_ERROR
			message = 'La solicitud no se pudo completar'

		return {'Accept_friendship_request': message}, status_code

	status_code = reject_friendship(user_email, new_friends_email, collection)

	if status_code == HTTP_OK:
		message = 'Solicitud de amistad rechazada con éxito'
	elif status_code == HTTP_FORBIDDEN:
		message = 'La solicitud de amistad que queres responder no existe'
	elif status_code == HTTP_NOT_FOUND:
		message = 'La solicitud no se pudo completar porque uno de los usuarios no existe'
	else: 	# ?
		message = 'La solicitud no se pudo completar'

	return {'Reject_friendship_request': message}, status_code

@users_bp.route('/api/users/<user_email>/friends/<friends_email>',
				methods=['DELETE'])
@swag_from('docs/friendship_delete.yml')
def _delete_friendship(user_email, friends_email):
	coll = 'users'
	status_code = delete_friendship_relationship(user_email,
											  	 friends_email,
											 	 client[DB][coll])
	if status_code == HTTP_OK:
		message = 'Amistad removida con éxito'
	elif status_code == HTTP_FORBIDDEN:
		message = 'Ésta relación de amistad no existe'
	elif status_code == HTTP_NOT_FOUND:
		message = 'La solicitud no se pudo completar porque uno de los usuarios no existe'
	else: 	# ?
		message = 'La solicitud no se pudo completar'

	return {'Delete_friendship_request': message}, status_code


@users_bp.route('/api/users/<user_email>/friends', methods=['GET'])
@swag_from('docs/get_user_friends.yml')
def _get_user_information(user_email):
	coll = 'users'
	response = get_user_friends_from_db(user_email,
										client[DB][coll])
	if response == HTTP_NOT_FOUND:
		return {'Get_user_information':
				'User not found'}, response

	return json.dumps(response), HTTP_OK

@users_bp.route('/api/users/<user_email>/requests', methods=['GET'])
@swag_from('docs/get_user_requests.yml')
def _get_user_requests(user_email):
	coll = 'users'
	response = get_user_requests_from_db(user_email,
								 		 client[DB][coll])
	if response == HTTP_NOT_FOUND:
		return {'Get_user_information':
				'User not found'}, response

	return json.dumps(response), HTTP_OK



@users_bp.route('/api/users', methods=['GET'])
@swag_from('docs/get_users_by_query.yml')
def _get_users_by_query():
	coll = 'users'
	try:
		filter_str = request.args.get('filter')
	except KeyError:
		return {'Users_by_query': 'No filter parameter was given'}, HTTP_BAD_REQUEST

	user_email = request.headers.get('User_email')
	response = get_users_by_query(filter_str, user_email,
								  client[DB][coll])

	return json.dumps(response), HTTP_OK

@users_bp.route('/api/users/<user_email>', methods=['DELETE'])
@swag_from('docs/delete_user.yml')
def _delete_user(user_email):

	logger.debug('Received request to delete user: ' + user_email)

	user_obtained = get_user_by_email(user_email, client[DB]['users'])
	if user_obtained is None:
		return {'Error': 'user {0} doesnt exist'.format(user_email)}, HTTP_NOT_FOUND

	user_insert_response = insert_new_user(user_obtained, client[DB]['users_deleted'])

	if user_insert_response == HTTP_INTERNAL_SERVER_ERROR:
		return {'Error': 'couldnt insert deleted user in users_delete collection'}, HTTP_INTERNAL_SERVER_ERROR

	try:
		delete_user_from_db(user_email, client[DB]['users'])
		return {'Delete': 'user {0} deleted'.format(user_email)}, HTTP_OK
	except ValueError:
		# Esto nunca deberia suceder. Pero mejor prevenir que curar
		return {'Error': 'user {0} doesnt exist'.format(user_email)}, HTTP_NOT_FOUND
