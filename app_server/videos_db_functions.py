import logging
import datetime
from bson import ObjectId
import pymongo.errors
from app_server.users_db_functions import get_user_by_email, get_user_friends_from_db

logger = logging.getLogger('gunicorn.error')

def insert_video_into_db(video_id, data, collection):

	doc = {'_id': ObjectId(video_id),
		   'title': data['title'],
		   'url': data['url'],
		   'user': data['user'],
		   'is_private': data['isPrivate'],
		   'upload_date': datetime.datetime.now(),
		   'comments': [],
		   'likes': [],
		   'dislikes': []
	}
	try:
		collection.insert_one(doc)
		logger.debug('Successfully inserted new video with id:' + video_id)
		return 201
	except pymongo.errors.DuplicateKeyError:
		logger.error('Pymongo duplicate key error')
		return 500

# def delete_video_by_object_id(video_object_id, collection):
# 	return

def insert_comment_into_video(video_id, user_email, comment, collection):

	data = {'user': user_email,
			'comment': comment,
			'timestamp': datetime.datetime.now()}
	result = collection.update_one({'_id': ObjectId(video_id)},
								   {'$push': {'comments': data}})

	if result.modified_count != 1:
		logger.error('Apparently this video does not exist for AppServer ' +
					 video_id)
		return {'Comment video':
				'The request could not complete successfully'}, 500

	return {'Comment video':
			'Your request was completed successfully'}, 201

def get_video_by_objectid(_id, collection, docs=None):
	try:
		if docs is None:
			video = collection.find_one({'_id': _id})
		else:
			video = collection.find_one({'_id': _id}, docs)
		return video
	except TypeError:
		logger.error('Video with id % is not valid', _id)
		return None

def filter_videos_for_specific_user(videos_list, user_email, user_collection, videos_collection):

	user = get_user_by_email(user_email, user_collection)
	if user is None:
		logger.error("No se listaron videos para el usuario %s porque no existe", user_email)
		return []

	friends = get_user_friends_from_db(user['email'], user_collection)
	email_friends = [friend['email'] for friend in friends]
	filtered_videos = []
	for raw_video in videos_list:
		video = get_video_by_objectid(ObjectId(raw_video['_id']),
									  videos_collection)
		if video is None:
			# acá debería pudrirse todo para mí... pero tampoco debería suceder nunca
			logger.error("Este video no existe en la base del AppServer %s", raw_video['_id'])
			continue
		if video['is_private']:
			if video['user'] in email_friends or video['user'] == user_email:
				filtered_videos.append(raw_video)
		else:
			filtered_videos.append(raw_video)

	return filtered_videos
