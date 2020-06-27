import os
import json
import logging
from flask import Blueprint
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import *

users_bp = Blueprint('users_relationships', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>',
				methods=['POST'])
@swag_from('docs/friendship_request.yml')
def _new_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = insert_new_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll])
	return response, status_code

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>/accept',
				methods=['POST'])
@swag_from('docs/friendship_accept.yml')
def _accept_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=True)
	return response, status_code

@users_bp.route('/api/users/<user_email>/friends/<new_friends_email>/reject',
				methods=['POST'])
@swag_from('docs/friendship_reject.yml')
def _reject_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=False)
	return response, status_code

@users_bp.route('/api/users/<user_email>/friends',
				methods=['GET'])
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

# @users_bp.route('/api/users?<filter>')
# @swag_from('docs/get_users_by_query.yml')
# def _get_users_by_query(filter):
# 	coll = 'users'
# 	# response = get_users_by_query(filter,
# 	# 							  client[DB][coll])
#
# 	return json.dumps(response), 200
