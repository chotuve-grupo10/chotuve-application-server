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
	response, status_code = insert_new_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll])
	return response, status_code

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
				methods=['PATCH'])
@swag_from('docs/friendship_response.yml')
def _respond_to_friendship_request(user_email, new_friends_email):
	data = request.json
	try:
		accept_or_reject = data['response']
	except KeyError:
		return {'Friendship_response': 'Response was missing'}, 400

	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=accept_or_reject)
	return response, status_code


@users_bp.route('/api/users/<user_email>/friends', methods=['GET'])
@swag_from('docs/get_user_friends.yml')
def _get_user_information(user_email):
	coll = 'users'
	response = get_user_information_from_db(user_email,
											client[DB][coll])
	if response == 403:
		return {'Get_user_information':
				'The request could not complete successfully because one of the users'
				' is not valid'}, response

	return json.dumps(response), 200
#
@users_bp.route('/api/users', methods=['GET'])
@swag_from('docs/get_users_by_query.yml')
def _get_users_by_query():
	coll = 'users'
	try:
		filter_str = request.args.get('filter')
	except KeyError:
		return {'get_users_by_query': 'No filter parameter was given'}, 400

	response = get_users_by_query(filter_str,
								  client[DB][coll])

	return json.dumps(response), 200
