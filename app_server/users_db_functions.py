import logging
from bson import ObjectId

logger = logging.getLogger('gunicorn.error')

def insert_new_user(data, collection):

	doc = {'email': data['email'],
		   'friends': [],
		   'requests': []
	}
	result = collection.insert_one(doc)
	if result.modified_count != 1:
		return 500
	return 201


def insert_new_friendship_request(my_user_id, new_friends_id, collection):
	# Lo primero que hay que chequear, es que no sean ya amigos!
	requests = collection.find_one({'_id': ObjectId(new_friends_id)})['requests']

	if new_friends_id in requests:
		logger.error('User % requested was already submitted and is pending',
					 my_user_id)
		return {'Friendship_request':
				'Friendship request was already submitted'}, 409

	result = collection.update_one({'_id': ObjectId(my_user_id)},
								   {'$push':{'requests': new_friends_id}})
	if result.modified_count != 1:
		logger.error('Something went wrong internally with request from id ' +
					 my_user_id)
		return {'Friendship_request':
				'The request could not complete successfully'}, 500

	logger.debug('New friendship request submitted ' + my_user_id)
	return {'Friendship_request':
			'Your request was completed successfully'}, 201
