import os
import logging
import simplejson as json
from pymongo import MongoClient
from flask import Blueprint, request
from flasgger import swag_from
from app_server.http_functions import *
from app_server.videos_db_functions import *
from app_server.utils.http_responses import *
from app_server.decorators.auth_required_decorator import auth_required

videos_bp = Blueprint('videos', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@videos_bp.route('/api/users/<user_id>/videos/', methods=['GET'])
@auth_required
@swag_from('docs/list_videos_of_user.yml')
def _list_videos_of_user(user_id):
	assert user_id == request.view_args['user_id']
	logger.debug("Requested videos from id:" + user_id)
	api_list_video_of_user = '/api/list_videos/'+ user_id
	response_media_server = get_media_server_request(os.environ.get('MEDIA_SERVER_URL') + api_list_video_of_user)
	if response_media_server.status_code == HTTP_OK:
		logger.debug('Response from media server list videos is 200')
		#Recibe lista de videos según id
		status = response_media_server.json()
	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	return json.dumps(status), response_media_server.status_code

@videos_bp.route('/api/videos/<user_id>', methods=['GET'])
@swag_from('docs/list_videos.yml')
def _list_videos(user_id):
	api_list_videos = '/api/list_videos/'
	response_media_server = get_media_server_request(os.environ.get('MEDIA_SERVER_URL') + api_list_videos)
	if response_media_server.status_code == HTTP_OK:
		logger.debug('Response from media server list videos is 200')
		#Recibe lista de videos
		raw_data = response_media_server.json()
		users_coll = 'users'
		videos_coll = 'videos'
		status = filter_videos_for_specific_user(raw_data, user_id,
												 client[DB][users_coll],
												 client[DB][videos_coll])
	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	return json.dumps(status), response_media_server.status_code

@videos_bp.route('/api/videos/', methods=['POST'])
@swag_from('docs/upload_video.yml')
def _upload_video():
	data = request.json
	api_upload_video = '/api/upload_video/'
	response_media_server = post_media_server(os.environ.get('MEDIA_SERVER_URL') + api_upload_video, data)
	status = {}
	# Trate de usar el .ok de la response, pero un 500 lo toma como true.
	# Por suerte estaban los tests para hacermelo notar
	if response_media_server.status_code == HTTP_CREATED:
		logger.debug('Response from media server upload video is 201')
		coll = 'videos'
		media_server_response_data = response_media_server.json()
		status_code = insert_video_into_db(media_server_response_data['_id'], data, client[DB][coll])

		if status_code == HTTP_CREATED:
			status['Upload video'] = 'Successfully uploaded video'
		else:
			status['Upload video'] = 'Couldnt upload video'
	else:
		logger.debug('Response from media server is NOT 201')
		status['Upload Video'] = 'No response'
		status_code = response_media_server.status_code

	return json.dumps(status), status_code


@videos_bp.route('/api/videos/<video_id>', methods=['DELETE'])
@swag_from('docs/delete_video.yml')
def _delete_video(video_id):
	logger.debug("Requested delete video with id:" + video_id)
	api_delete_video = '/api/delete_video/' + video_id
	response_media_server = delete_media_server(os.environ.get('MEDIA_SERVER_URL') + api_delete_video)
	status = {}
	if response_media_server.status_code == HTTP_OK:
		logger.debug('Response from media server list videos is 200')
		data = response_media_server.json()
		videos_coll = 'videos'
		app_server_status = delete_video_in_db(video_id,
											   client[DB][videos_coll])
		if app_server_status == HTTP_NOT_FOUND:
			logger.error('App server did not found this video on its collection')

		status['Deleted Video'] = data
	else:
		logger.debug('Response from media server is NOT 200')
		status['Deleted Video'] = 'No response'

	return json.dumps(status), response_media_server.status_code

@videos_bp.route('/api/videos/<video_id>/comments', methods=['POST'])
@swag_from('docs/comment_video.yml')
def _comment_video(video_id):

	data = request.json
	coll = 'videos'
	result, status_code = insert_comment_into_video(video_id,
													data['email'],
													data['comment'],
													client[DB][coll])

	return result, status_code
