import os
import logging
import operator
import simplejson as json
from pymongo import MongoClient
from flask import Blueprint, request, g
from flasgger import swag_from
from app_server.http_functions import *
from app_server.videos_db_functions import *
from app_server.utils.http_responses import *
from app_server import rules
from app_server.decorators.auth_required_decorator import auth_required
from app_server.users_db_functions import get_user_friends_from_db
from app_server.users_db_functions import get_user_by_email

videos_bp = Blueprint('videos', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@videos_bp.route('/api/users/videos/', methods=['GET'])
@auth_required
@swag_from('docs/list_videos_of_user.yml')
def _list_videos_of_user():

	user_id = request.args.get('user_id')
	user_requesting_videos_id = g.data['user_id']
	logger.debug("The user requesting the videos is:" + user_requesting_videos_id)

	logger.debug("Requested videos from id:" + user_id)
	api_list_video_of_user = '/api/videos/?user_name=' + user_id
	response_media_server = get_media_server_request(os.environ.get('MEDIA_SERVER_URL') + api_list_video_of_user)

	if response_media_server.status_code == HTTP_OK:
		logger.debug('Response from media server list videos is 200')

		if user_requesting_videos_id == user_id:
			logger.debug('User requesting own videos')
			videos_collection = client[DB]['videos']
			status = append_data_to_videos(response_media_server.json(), videos_collection)

		else:
			videos_collection = client[DB]['videos']
			videos_list = delete_keys_from_videos(response_media_server.json(), KEYS_TO_DELETE)
			videos_list = append_data_to_videos(videos_list, videos_collection)
			user_friends = get_user_friends_from_db(user_id, client[DB]['users'])
			friends_list = [friend['email'] for friend in user_friends]

			if user_requesting_videos_id in friends_list:
				logger.debug('Users are friends. Showing all videos')
				status = videos_list

			else:
				logger.debug('Users are not friends. Showing public videos only')
				status = filter_public_videos(videos_list)

	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	if len(status) != 0:
		for video in status:
			rules.set_importance(video, rules.ruleset)
		status = sorted(status, key=operator.itemgetter('importance'), reverse=True)

	return json.dumps(status), response_media_server.status_code

@videos_bp.route('/api/videos/<user_id>', methods=['GET'])
@swag_from('docs/list_videos.yml')
def _list_videos(user_id):
	api_list_videos = '/api/videos/'
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
		for video in status:
			rules.set_importance(video, rules.ruleset)
		status = sorted(status, key=operator.itemgetter('importance'), reverse=True)
	else:
		logger.debug('Response from media server is NOT 200')
		status = []

	return json.dumps(status), response_media_server.status_code

@videos_bp.route('/api/videos/', methods=['POST'])
@swag_from('docs/upload_video.yml')
def _upload_video():
	data = request.json
	api_upload_video = '/api/videos/'
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
	api_delete_video = '/api/videos/' + video_id
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
@auth_required
@swag_from('docs/comment_video.yml')
def _comment_video(video_id):
	user_email = g.data['user_id']

	data = request.json
	coll = 'videos'
	status_code = insert_comment_into_video(video_id,
											user_email,
											data['text'],
											client[DB][coll])

	if status_code == HTTP_CREATED:
		video = get_video_for_response(video_id, client[DB][coll])
		result = json.dumps(video)
	else: # HTTP_INTERNAL_SERVER_ERROR
		result = {'Comment video': 'The request could not complete successfully'}

	return result, status_code
