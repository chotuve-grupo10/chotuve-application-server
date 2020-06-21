import logging
import datetime
from bson import ObjectId

logger = logging.getLogger('gunicorn.error')

def insert_comment_into_video(video_id, user_id, comment, collection):

	data = {'user_id': user_id,
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
