import os
import json
import logging
from flask import Blueprint, request
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import *

users_bp = Blueprint('users_relationships', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

# No logré que funcionara el yml de swagger así
# @users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
# 				methods=['POST', 'PATCH', 'DELETE'])
# @swag_from('docs/friendship_handling.yml')
# def _handle_friendships(user_email, new_friends_email):

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
				methods=['POST'])
@swag_from('docs/friendship_request.yml')
def _request_friendships(user_email, new_friends_email):
	coll = 'users'
	status_code = insert_new_friendship_request(user_email,
												new_friends_email,
												client[DB][coll])
	if status_code == HTTP_CREATED:
		message = 'Your request was completed successfully'
	elif status_code == HTTP_FORBIDDEN:
		message = 'This user is already your friend!'
	elif status_code == HTTP_NOT_FOUND:
		message = 'The request could not complete successfully because one of the users is not valid'
	elif status_code == HTTP_METHOD_NOT_ALLOWED:
		message = "You can't ask yourself for friendship. That's weird"
	elif status_code == HTTP_CONFLICT:
		message = 'Friendship request was already submitted'
	else: # HTTP_INTERNAL_SERVER_ERROR
		message = 'The request could not complete successfully'

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
			message = 'Friendship accepted successfully'
		elif status_code == HTTP_FORBIDDEN:
			message = 'There is no such friendship request pending to respond'
		elif status_code == HTTP_NOT_FOUND:
			message = 'The request could not complete successfully because one of the users is not valid'
		else: # HTTP_INTERNAL_SERVER_ERROR
			message = 'The request could not complete successfully'

		return {'Accept_friendship_request': message}, status_code

	status_code = reject_friendship(user_email, new_friends_email, collection)

	if status_code == HTTP_OK:
		message = 'Friendship rejected successfully'
	elif status_code == HTTP_FORBIDDEN:
		message = 'There is no such friendship request pending to respond'
	elif status_code == HTTP_NOT_FOUND:
		message = 'The request could not complete successfully because one of the users is not valid'
	else: 	# ?
		message = 'The request could not complete successfully'

	return {'Reject_friendship_request': message}, status_code


@users_bp.route('/api/users/<user_email>/friends', methods=['GET'])
@swag_from('docs/get_user_friends.yml')
def _get_user_information(user_email):
	coll = 'users'
	response = get_user_information_from_db(user_email,
											client[DB][coll])
	if response == HTTP_NOT_FOUND:
		return {'Get_user_information':
				'User not found'}, response

	return json.dumps(response), HTTP_OK
#
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
