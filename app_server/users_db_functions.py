import logging
import pymongo.errors
from bson import ObjectId

logger = logging.getLogger('gunicorn.error')

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500

def insert_new_user(data, collection):

	doc = {'email': data['email'],
		   'fullName': data['full name'],
		   'friends': [],
		   'requests': []
	}
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(doc)
		return 201
	except pymongo.errors.DuplicateKeyError:
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

def insert_new_friendship_request(user_email, new_friends_email, collection):
	# Chequeo cero: que no sea yo mismo pidiendome amistad a mí mismo. Meme de spiderman
	if user_email == new_friends_email:
		return HTTP_METHOD_NOT_ALLOWED

	# Chequeo que existan ambos usuarios
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return HTTP_NOT_FOUND

	# Primero chequeo que no sean ya amigos!
	if new_friend['_id'] in user['friends']:
		logger.error('User % requested was already submitted and is pending',
					 user_email)
		return HTTP_FORBIDDEN

	# Segundo, chequeo que la request no haya sido hecha ya
	requests = new_friend['requests']

	if user['_id'] in requests:
		logger.error('User % requested was already submitted and is pending',
					 user_email)
		return HTTP_CONFLICT

	result = collection.update_one({'_id': new_friend['_id']},
								   {'$push':{'requests': user['_id']}})
	if result.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 user_email)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('New friendship request submitted ' + user_email)
	return HTTP_CREATED

def accept_friendship_request(user_email, new_friends_email, collection):

	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return HTTP_NOT_FOUND

	#2 eliminar la request
	result = collection.update_one({'_id': user['_id']},
								   {'$pull': {'requests': new_friend['_id']}})
	if result.modified_count != 1:
		logger.error('There is no friendship request pending to respond between %s and %s',
					 user_email, new_friends_email)
		return HTTP_FORBIDDEN

	#3 agregar la amistad para ambos usuarios
	result_01 = collection.update_one({'_id': user['_id']},
						  {'$push': {'friends': new_friend['_id']}})
	result_02 = collection.update_one({'_id': new_friend['_id']},
						  {'$push': {'friends': user['_id']}})
	if result_01.modified_count != 1 or result_02.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 user_email)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('Friendship request was accepted by ' + user_email)
	return HTTP_OK

def reject_friendship(user_email, new_friends_email, collection):

	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return HTTP_NOT_FOUND

	#2 eliminar la request
	result = collection.update_one({'_id': user['_id']},
								   {'$pull': {'requests': new_friend['_id']}})
	if result.modified_count != 1:
		logger.error('There is no friendship request pending to respond between %s and %s',
					 user_email, new_friends_email)
		return HTTP_FORBIDDEN

	# 3 no agrego nada!
	logger.debug('Friendship request was denied by ' + user_email)
	return HTTP_OK

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

def delete_friendship_relationship(user_email, friends_email, collection):

	user = get_user_by_email(user_email, collection)
	friend = get_user_by_email(friends_email, collection)
	if user is None or friend is None:
		return HTTP_NOT_FOUND

	#2 eliminar la request
	result_01 = collection.update_one({'_id': user['_id']},
								   	  {'$pull': {'friends': friend['_id']}})
	result_02 = collection.update_one({'_id': friend['_id']},
								   	  {'$pull': {'friends': user['_id']}})
	if result_01.modified_count != 1 or result_02.modified_count != 1:
		logger.error('There is no friendship relationship between %s and %s',
					 user_email, friends_email)
		return HTTP_FORBIDDEN

	# 3 no agrego nada!
	logger.debug('Friendship relationship was deleted ' + user_email)
	return HTTP_OK

def get_friends_email(user, collection):
	if len(user['friends']) == 0:
		return []
	friends_email = []
	for friend_object_id in user['friends']:
		friend = get_user_by_objectid(friend_object_id, collection,
									  {'email': True})
		friends_email.append(friend['email'])

	return friends_email

def filter_videos_for_specific_user(videos_list, user_email, collection):

	user = get_user_by_email(user_email, collection)
	if user is None:
		return HTTP_NOT_FOUND

	emails_friends = get_friends_email(user, collection)

	filtered_videos = []
	for video in videos_list:
		# if video['is_private']:
		# 	if video['user'] in emails_friends:
		# 		filtered_videos.append(video)
		# else:
		filtered_videos.append(video)

	return filtered_videos