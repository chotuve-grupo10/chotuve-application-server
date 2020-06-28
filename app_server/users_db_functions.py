import logging
import pymongo.errors
from bson import ObjectId

logger = logging.getLogger('gunicorn.error')

def insert_new_user(data, collection):

	doc = {'email': data['email'],
		   'fullName': data['full Name'],
		   'friends': [],
		   'requests': []
	}
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(doc)
		return 201
	except pymongo.errors.DuplicateKeyError:
		return 500

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
	# Lo primero que hay que chequear, es que no sean ya amigos!
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return {'Friendship_request':
				'The request could not complete successfully because one of the users'
				' is not valid'}, 403	# Forbidden

	if new_friend['_id'] in user['friends']:
		logger.error('User % requested was already submitted and is pending',
					 user_email)
		return {'Friendship_request':
				'This user is already your friend!'}, 409	# Conflict

	# Segundo, chequeo que la request no haya sido hecha ya
	requests = new_friend['requests']

	if user['_id'] in requests:
		logger.error('User % requested was already submitted and is pending',
					 user_email)
		return {'Friendship_request':
				'Friendship request was already submitted'}, 409

	result = collection.update_one({'_id': new_friend['_id']},
								   {'$push':{'requests': user['_id']}})
	if result.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 user_email)
		return {'Friendship_request':
				'The request could not complete successfully'}, 500

	logger.debug('New friendship request submitted ' + user_email)
	return {'Friendship_request':
			'Your request was completed successfully'}, 201

def respond_to_friendship_request(user_email, new_friends_email, collection, accept):
	if accept:
		return accept_friendship_request(user_email, new_friends_email, collection)

	return reject_friendship(user_email, new_friends_email, collection)

def accept_friendship_request(user_email, new_friends_email, collection):
	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return {'Accept_friendship_request':
				'The request could not complete successfully because one of the users'
				' is not valid'}, 403	# Forbidden

	#2 eliminar la request
	result = collection.update_one({'_id': user['_id']},
								   {'$pull': {'requests': new_friend['_id']}})
	if result.modified_count != 1:
		logger.error('There is no friendship request pending to respond between %s and %s',
					 user_email, new_friends_email)
		return {'Accept_friendship_request':
				'There is no such friendship request pending to respond'}, 409

	#3 agregar la amistad para ambos usuarios
	result_01 = collection.update_one({'_id': user['_id']},
						  {'$push': {'friends': new_friend['_id']}})
	result_02 = collection.update_one({'_id': new_friend['_id']},
						  {'$push': {'friends': user['_id']}})
	if result_01.modified_count != 1 or result_02.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 user_email)
		return {'Accept_friendship_request':
				'The request could not complete successfully'}, 500

	logger.debug('Friendship request was accepted by ' + user_email)
	return {'Accept_friendship_request':
			'Your request was completed successfully'}, 201

def reject_friendship(user_email, new_friends_email, collection):
	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	new_friend = get_user_by_email(new_friends_email, collection)
	if user is None or new_friend is None:
		return {'Reject_friendship_request':
				'The request could not complete successfully because one of the users'
				' is not valid'}, 403	# Forbidden

	#2 eliminar la request
	result = collection.update_one({'_id': user['_id']},
								   {'$pull': {'requests': new_friend['_id']}})
	if result.modified_count != 1:
		logger.error('There is no friendship request pending to respond between %s and %s',
					 user_email, new_friends_email)
		return {'Reject_friendship_request':
				'There is no such friendship request pending to respond'}, 409

	# 3 no agrego nada!
	logger.debug('Friendship request was denied by ' + user_email)
	return {'Reject_friendship_request':
			'Your request was completed successfully'}, 201

def get_user_information_from_db(user_email, collection):
	#1 Chequear que el user exista realmente
	user = get_user_by_email(user_email, collection)
	if user is None:
		return 404	# User not found
	result = []
	for friend in user['friends']:
		this_user = get_user_by_objectid(ObjectId(friend), collection,
										 {'email': 1, 'fullName': 1, '_id': 0})
		result.append(this_user)

	return result

def get_users_by_query(filter_str, collection):

	regex_doc = {'$regex': filter_str}
	users = collection.find({'email': regex_doc},
							{'_id': False,
							 'friends': False,
							 'requests': False})

	return list(users)
