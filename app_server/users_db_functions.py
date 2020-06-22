import logging
import pymongo.errors
from bson import ObjectId

logger = logging.getLogger('gunicorn.error')

def insert_new_user(data, collection):

	doc = {'email': data['email'],
		   'friends': [],
		   'requests': []
	}
	try:
		## insert_one result has no attribute modified_counts
		collection.insert_one(doc)
		return 201
	except pymongo.errors.DuplicateKeyError:
		return 500


def insert_new_friendship_request(my_user_id, new_friends_id, collection):
	# Lo primero que hay que chequear, es que no sean ya amigos!
	try:
		friends = collection.find_one({'_id': ObjectId(my_user_id)})['friends']
	except TypeError:
		return {'Friendship_request':
				'The request could not complete successfully because you appear not to be'
				'a valid user in db'}, 403	# Forbidden
	if ObjectId(new_friends_id) in friends:
		logger.error('User % requested was already submitted and is pending',
					 my_user_id)
		return {'Friendship_request':
				'This user is already your friend!'}, 409	# Conflict

	# Segundo, chequeo que la request no haya sido hecha ya
	try:
		requests = collection.find_one({'_id': ObjectId(new_friends_id)})['requests']
	except TypeError:
		return {'Friendship_request':
				'This user you are trying to make friends with does not exist in db'}, 403

	if ObjectId(my_user_id) in requests:
		logger.error('User % requested was already submitted and is pending',
					 my_user_id)
		return {'Friendship_request':
				'Friendship request was already submitted'}, 409

	result = collection.update_one({'_id': ObjectId(new_friends_id)},
								   {'$push':{'requests': ObjectId(my_user_id)}})
	if result.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 my_user_id)
		return {'Friendship_request':
				'The request could not complete successfully'}, 500

	logger.debug('New friendship request submitted ' + my_user_id)
	return {'Friendship_request':
			'Your request was completed successfully'}, 201
