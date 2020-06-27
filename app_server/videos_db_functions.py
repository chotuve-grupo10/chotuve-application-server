import logging
import datetime
from bson import ObjectId
import pymongo.errors

logger = logging.getLogger('gunicorn.error')

def insert_video_into_db(video_id, data, collection):

	doc = {'_id': ObjectId(video_id),
		   'title': data['title'],
		   'url': data['url'],
		   'user': data['user'],
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
