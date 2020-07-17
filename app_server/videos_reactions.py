import os
import logging
import simplejson as json
from pymongo import MongoClient
from flask import Blueprint, request
from flasgger import swag_from
from app_server.http_functions import *
from app_server.videos_db_functions import *
from app_server.videos_reactions_db_functions import *

videos_reactions_bp = Blueprint('videos_reactions', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@videos_reactions_bp.route('/api/videos/<video_id>/likes', methods=['POST'])
@swag_from('docs/like_video.yml')
def _like_video(video_id):
	data = request.json

	coll_users = 'users'
	user = get_user_by_email(data['email'], client[DB][coll_users])
	if user is None:
		logger.error('El usuario % que quiso likear un video no existe', data['email'])
		return {'Like_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = like_video(video_id, data['email'], client[DB][coll_videos])

	if status_code == HTTP_CREATED:
		result = {'Like_video': 'Te gusta este video'}
	elif status_code == HTTP_CONFLICT:
		result = {'Like_video': 'Este video ya te gusta'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Like_video': 'No se encontró el video'}
	else: # HTTP_INTERNAL_SERVER_ERROR
		result = {'Like_video': 'Sucedió un error'}

	return result, status_code

@videos_reactions_bp.route('/api/videos/<video_id>/likes', methods=['DELETE'])
@swag_from('docs/delete_like_to_video.yml')
def _delete_like_video(video_id):
	data = request.json

	coll_users = 'users'
	user = get_user_by_email(data['email'], client[DB][coll_users])
	if user is None:
		logger.error('El usuario % que quiso likear un video no existe', data['email'])
		return {'Like_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = delete_like_video(video_id, data['email'], client[DB][coll_videos])

	if status_code == HTTP_CREATED:
		result = {'Like_video': 'Te gusta este video'}
	elif status_code == HTTP_CONFLICT:
		result = {'Like_video': 'Este video ya te gusta'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Like_video': 'No se encontró el video'}
	else: # HTTP_INTERNAL_SERVER_ERROR
		result = {'Like_video': 'Sucedió un error'}

	return result, status_code
