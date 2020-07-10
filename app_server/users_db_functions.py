import logging
import pymongo.errors
from bson import ObjectId
from app_server.utils.http_responses import *

logger = logging.getLogger('gunicorn.error')

def insert_new_user(data, collection):
	logger.debug('User to insert:' + str(data))
	doc = {'email': data['email'],
		   'fullName': data['full name'],
		   'friends': [],
		   'requests': []
	}
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(doc)
		logger.debug('User inserted')
		return 201
	except pymongo.errors.DuplicateKeyError:
		logger.error('Cant insert user. Duplicate key error')
		return 500

def insert_complete_user(user_to_insert, collection):
	logger.debug('User to insert:' + str(user_to_insert))
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(user_to_insert)
		logger.debug('User inserted')
		return 201
	except pymongo.errors.DuplicateKeyError:
		logger.error('Cant insert user. Duplicate key error')
		return 500

def insert_new_firebase_user_if_not_exists(claims, collection):

	user = get_user_by_email(claims.get('email'), collection)
	if user is not None:
		return

	doc = {'email': claims.get('email'),
		   'fullName': claims.get('name'),
		   'friends': [],
		   'requests': []
	}
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(doc)
	except pymongo.errors.DuplicateKeyError:
		pass

def get_user_by_email(user_email, collection):
	logger.debug('Looking for user with email ' + user_email)
	try:
		user = collection.find_one({'email': user_email})
		return user
	except TypeError:
		logger.error('User % is not a valid user', user_email)
		return None

def get_user_by_objectid(_id, collection, docs=None):
	try:
		if docs is None:
			user = collection.find_one({'_id': _id})
		else:
			user = collection.find_one({'_id': _id}, docs)
		return user
	except TypeError:
		logger.error('User with id % is not a valid user', _id)
		return None

def get_user_friends_from_db(user_email, collection):
	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	if user is None:
		return HTTP_NOT_FOUND	# User not found
	result = []
	for friend in user['friends']:
		this_user = get_user_by_objectid(ObjectId(friend), collection,
										 {'email': 1, 'fullName': 1, '_id': 0})
		result.append(this_user)

	return result

def get_user_requests_from_db(user_email, collection):
	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	if user is None:
		return HTTP_NOT_FOUND	# User not found
	result = []
	for friend in user['requests']:
		this_user = get_user_by_objectid(ObjectId(friend), collection,
										 {'email': 1, 'fullName': 1, '_id': 0})
		result.append(this_user)

	return result

def get_users_by_query(filter_str, user_email, collection):

	filtering = {'$regex': filter_str, '$ne': user_email}
	# Según la doc de pymongo: IMPLICIT AND
	users = collection.find({'email': filtering},
							{'_id': False,
							 'friends': False,
							 'requests': False})

	# users = [user for user in users if user['email'] is not user_email]
	return list(users)

def delete_user_from_db(user_email, collection):
	logger.debug('Deleting user with email ' + user_email)

	result = collection.delete_one({'email': user_email})
	if result.deleted_count == 0:
		logger.error('User not found. Cant delete user')
		raise ValueError('User {0} doesnt exist'.format(user_email))
	logger.debug('User deleted')
	return result
