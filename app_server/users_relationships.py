import os
import logging
from flask import Blueprint
from flasgger import swag_from
from pymongo import MongoClient
from app_server.users_db_functions import *

users_bp = Blueprint('users_relationships', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@users_bp.route('/api/<my_user_id>/friends/<new_friends_id>',
				methods=['POST'])
@swag_from('docs/friendship_request.yml')
def _new_friendship_request(my_user_id, new_friends_id):
	coll = 'users'
	response, status_code = insert_new_friendship_request(my_user_id,
														  new_friends_id,
														  client[DB][coll])
	return response, status_code

@users_bp.route('/api/<my_user_id>/friends/<new_friends_id>/accept',
				methods=['POST'])
@swag_from('docs/accept_friendship.yml')
def _accept_friendship_request(my_user_id, new_friends_id):
	coll = 'users'
	response, status_code = respond_to_friendship_request(my_user_id,
														  new_friends_id,
														  client[DB][coll],
														  accept=True)
	return response, status_code
