import logging
from app_server.users_db_functions import *
from app_server.push_notifications import send_notification_to_user
from app_server.utils.notification_messages import *

logger = logging.getLogger('gunicorn.error')

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

	send_notification_to_user(new_friends_email,
							  NEW_FRIENDSHIP_REQUEST_TITLE,
							  NEW_FRIENDSHIP_REQUEST_BODY.format(user_email),
							  collection)
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

	send_notification_to_user(new_friends_email,
							  ACCEPT_FRIENDSHIP_REQUEST_TITLE,
							  ACCEPT_FRIENDSHIP_REQUEST_BODY.format(user_email),
							  collection)
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
