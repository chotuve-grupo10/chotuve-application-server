import logging
import pymongo.errors
from bson import ObjectId
from app_server.utils.http_responses import *

logger = logging.getLogger('gunicorn.error')

DEFAULT_PROFILE_PICTURE = 'https://firebasestorage.googleapis.com/v0/b/chotuve-android-app.appspot.com/o/profile_pictures%2Fdeafult-profile-03.jpg?alt=media&token=c8dd344d-1f7f-4267-95e6-0a195ebbc5d2'

def insert_new_user(data, collection):
	logger.debug('User to insert:' + str(data))
	doc = {'email': data['email'],
		   'fullName': data['full name'],
		   'friends': [],
		   'requests': [],
		   'notifications_token': '',
		   'profilePicture': DEFAULT_PROFILE_PICTURE
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
										 {'email': 1, 'fullName': 1, 'profilePicture': 1,
										  '_id': 0})
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

def modify_user_in_database(user_email, data, collection):
	user = get_user_by_email(user_email, collection)
	if user is not None:
		info_to_set = {'fullName': data['full_name'],
					   'profilePicture': data['profile_picture']}
		collection.update_one({'email': user_email},
							  {'$set': info_to_set})
		return HTTP_OK
	return HTTP_NOT_FOUND
