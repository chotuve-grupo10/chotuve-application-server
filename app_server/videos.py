import os
import logging
import simplejson as json
from flask import Blueprint, request
from flasgger import swag_from
from app_server.http_functions import *

videos_bp = Blueprint('videos', __name__)
logger = logging.getLogger('gunicorn.error')

@videos_bp.route('/api/list_videos/', methods=['GET'])
@swag_from('docs/list_videos.yml')
def _list_videos():
	api_list_videos = '/api/list_videos/'
	response_media_server = get_media_server_request(os.environ.get('MEDIA_SERVER_URL') + api_list_videos)
	status = []
	if response_media_server.status_code == 200:
		logger.debug('Response from media server list videos is 200')
		#Recibe lista de videos
		data = response_media_server.json()
		status = data
	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	return json.dumps(status), response_media_server.status_code


@videos_bp.route('/api/list_videos/<user_id>', methods=['GET'])
@swag_from('docs/list_videos_for_user_id.yml')
def _list_videos_for_user(user_id):
	assert user_id == request.view_args['user_id']
	logger.debug("Requested videos from id:" + user_id)
	api_list_video_for_user = '/api/list_videos/'+ user_id
	response_media_server = get_media_server_request(os.environ.get('MEDIA_SERVER_URL') + api_list_video_for_user)
	status = []
	if response_media_server.status_code == 200:
		logger.debug('Response from media server list videos is 200')
		#Recibe lista de videos según id
		data = response_media_server.json()
		status = data
	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	return json.dumps(status), response_media_server.status_code


@videos_bp.route('/api/upload_video/', methods=['POST'])
@swag_from('docs/upload_video.yml')
def _upload_video():
	data = request.json
	api_upload_video = '/api/upload_video/'
	response_media_server = post_media_server(os.environ.get('MEDIA_SERVER_URL') + api_upload_video, data)
	status = {}
	if response_media_server.status_code == 200:
		logger.debug('Response from media server upload video is 200')
		data = response_media_server.json()
		status = data
	else:
		logger.debug('Response from media server is NOT 200')
		status['Upload Video'] = 'No response'

	return json.dumps(status), response_media_server.status_code


@videos_bp.route('/api/delete_video/<video_id>', methods=['DELETE'])
@swag_from('docs/delete_video.yml')
def _delete_video(video_id):
	logger.debug("Requested delete video with id:" + video_id)
	api_delete_video = '/api/delete_video/' + video_id
	response_media_server = delete_media_server(os.environ.get('MEDIA_SERVER_URL') + api_delete_video)
	status = {}
	if response_media_server.status_code == 200:
		logger.debug('Response from media server list videos is 200')
		data = response_media_server.json()
		status['Deleted Video'] = data
	else:
		logger.debug('Response from media server is NOT 200')
		status['Deleted Video'] = 'No response'

	return json.dumps(status), response_media_server.status_code
