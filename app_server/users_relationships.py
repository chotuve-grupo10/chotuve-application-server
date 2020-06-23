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

@users_bp.route('/api/<user_email>/friends/<new_friends_email>',
				methods=['POST'])
@swag_from('docs/friendship_request.yml')
def _new_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = insert_new_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll])
	return response, status_code

@users_bp.route('/api/<user_email>/friends/<new_friends_email>/accept',
				methods=['POST'])
@swag_from('docs/accept_friendship.yml')
def _accept_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=True)
	return response, status_code

@users_bp.route('/api/<user_email>/friends/<new_friends_email>/reject',
				methods=['POST'])
@swag_from('docs/reject_friendship.yml')
def _reject_friendship_request(user_email, new_friends_email):
	coll = 'users'
	response, status_code = respond_to_friendship_request(user_email,
														  new_friends_email,
														  client[DB][coll],
														  accept=False)
	return response, status_code
