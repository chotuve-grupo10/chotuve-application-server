import logging
import datetime
from bson import ObjectId
import pymongo.errors
from app_server.utils.http_responses import *
from app_server.videos_db_functions import get_video_by_objectid

logger = logging.getLogger('gunicorn.error')

def like_video(video_id, user, collection):

	logger.debug('El usuario %s quiere likear un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, docs=None)
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
	logger.debug('Realicé el update!')
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario % dio like al video con éxito', user['email'])
	return HTTP_CREATED

def delete_like_video(video_id, user, collection):
	logger.debug('El usuario %s quiere sacar su like de un video', user['email'])
	video = get_video_by_objectid(ObjectId(video_id), collection, docs=None)
	if video is None:
		return HTTP_NOT_FOUND

	if user['email'] not in video['likes']:
		logger.debug('Este usuario NO likeo el video antes')
		return HTTP_CONFLICT

	result = collection.update_one({'_id': ObjectId(video_id)},
							{'$pull': {'likes': user['email']}})
	logger.debug('Realicé el update!')
	if result.modified_count != 1:
		logger.debug('Error queriendo modificar el video de id %', video_id)
		return HTTP_INTERNAL_SERVER_ERROR

	logger.debug('El usuario % quitó su like del video con éxito', user['email'])
	return HTTP_OK
