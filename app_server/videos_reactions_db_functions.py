import logging
from bson import ObjectId
from app_server.utils.http_responses import *
from app_server.videos_db_functions import get_video_by_objectid

logger = logging.getLogger('gunicorn.error')

def like_video(video_id, user, collection):

	logger.debug('El usuario %s quiere likear un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, filter=None)
	if video is None:
		return HTTP_NOT_FOUND

	if user['email'] in video['likes']:
		logger.debug('Este usuario ya likeo el video antes')
		return HTTP_CONFLICT
	if user['email'] in video['dislikes']:
		logger.debug('Eliminando dislike del video antes')
		result = collection.update_one({'_id': ObjectId(video_id)},
							{'$pull': {'dislikes': user['email']}})

	result = collection.update_one({'_id': ObjectId(video_id)},
							{'$push': {'likes': user['email']}})
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %s', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario %s dio like al video con éxito', user['email'])
	return HTTP_CREATED

def delete_like_video(video_id, user, collection):
	logger.debug('El usuario %s quiere sacar su like de un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, filter=None)
	if video is None:
		return HTTP_NOT_FOUND

	if user['email'] not in video['likes']:
		logger.debug('Este usuario NO likeo el video antes')
		return HTTP_CONFLICT

	result = collection.update_one({'_id': ObjectId(video_id)},
							{'$pull': {'likes': user['email']}})
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %s', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario %s quito su like del video con éxito', user['email'])
	return HTTP_OK

def dislike_video(video_id, user, collection):

	logger.debug('El usuario %s quiere dislikear un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, filter=None)
	if video is None:
		return HTTP_NOT_FOUND

	if user['email'] in video['dislikes']:
		logger.debug('Este usuario ya dislikeo el video antes')
		return HTTP_CONFLICT
	if user['email'] in video['likes']:
		logger.debug('Eliminando like del video antes')
		result = collection.update_one({'_id': ObjectId(video_id)},
							{'$pull': {'likes': user['email']}})

	result = collection.update_one({'_id': ObjectId(video_id)},
							{'$push': {'dislikes': user['email']}})
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %s', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario %s dio dislike al video con éxito', user['email'])
	return HTTP_CREATED

def delete_dislike_video(video_id, user, collection):
	logger.debug('El usuario %s quiere sacar su dislike de un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, filter=None)
	if video is None:
		return HTTP_NOT_FOUND

	if user['email'] not in video['dislikes']:
		logger.debug('Este usuario NO dislikeo el video antes')
		return HTTP_CONFLICT

	result = collection.update_one({'_id': ObjectId(video_id)},
							{'$pull': {'dislikes': user['email']}})
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %s', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario %s quito su dislike del video con éxito', user['email'])
	return HTTP_OK
