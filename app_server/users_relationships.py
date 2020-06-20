import os
import logging
from flask import Blueprint
from pymongo import MongoClient
from app_server.users_db_functions import *

users_bp = Blueprint('users_relationships', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@users_bp.route('/api/new_friendship_request/<my_user_id>/<new_friends_id>', methods=['POST'])
def _new_friendship_request(my_user_id, new_friends_id):
	coll = 'friendships'
	response, status_code = insert_new_friendship_request(my_user_id,
														  new_friends_id,
														  client[DB][coll])
	return response, status_code
