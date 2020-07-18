import os
import logging
from pymongo import MongoClient
from bson import json_util
from flask import Blueprint, request, g
from flasgger import swag_from
from app_server.http_functions import *
from app_server.videos_db_functions import *
from app_server.videos_reactions_db_functions import *
from app_server.decorators.auth_required_decorator import auth_required

videos_reactions_bp = Blueprint('videos_reactions', __name__)
logger = logging.getLogger('gunicorn.error')

client = MongoClient(os.environ.get('DATABASE_URL'))
DB = 'app_server'

@videos_reactions_bp.route('/api/videos/<video_id>/likes', methods=['POST'])
@swag_from('docs/like_video.yml')
@auth_required
def _like_video(video_id):
	user_email = g.data['user_id']

	coll_users = 'users'
	user = get_user_by_email(user_email, client[DB][coll_users])
	if user is None:
		logger.error('El usuario %s que quiso likear un video no existe', user_email)
		return {'Like_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = like_video(video_id, user, client[DB][coll_videos])

	if status_code == HTTP_CREATED:
		video = get_video_for_response(video_id, client[DB][coll_videos])
		result = json.dumps(video, default=json_util.default)
	elif status_code == HTTP_CONFLICT:
		result = {'Like_video': 'Este video ya te gusta'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Like_video': 'No se encontró el video'}
	else:  # HTTP_INTERNAL_SERVER_ERROR
		result = {'Like_video': 'Sucedió un error'}

	return result, status_code


@videos_reactions_bp.route('/api/videos/<video_id>/likes', methods=['DELETE'])
@swag_from('docs/delete_like_to_video.yml')
@auth_required
def _delete_like_video(video_id):
	user_email = g.data['user_id']

	coll_users = 'users'
	user = get_user_by_email(user_email, client[DB][coll_users])
	if user is None:
		logger.error('El usuario %s que quiso likear un video no existe', user_email)
		return {'Delete_like_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = delete_like_video(video_id, user, client[DB][coll_videos])

	if status_code == HTTP_OK:
		video = get_video_for_response(video_id, client[DB][coll_videos])
		result = json.dumps(video, default=json_util.default)
	elif status_code == HTTP_CONFLICT:
		result = {'Delete_like_video': 'Este video no tenia tu like'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Delete_like_video': 'No se encontró el video'}
	else:  # HTTP_INTERNAL_SERVER_ERROR
		result = {'Delete_like_video': 'Sucedió un error'}

	return result, status_code


@videos_reactions_bp.route('/api/videos/<video_id>/dislikes', methods=['POST'])
@swag_from('docs/dislike_video.yml')
@auth_required
def _dislike_video(video_id):
	user_email = g.data['user_id']

	coll_users = 'users'
	user = get_user_by_email(user_email, client[DB][coll_users])
	if user is None:
		logger.error('El usuario %s que quiso dislikear un video no existe', user_email)
		return {'Dislike_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = dislike_video(video_id, user, client[DB][coll_videos])

	if status_code == HTTP_CREATED:
		video = get_video_for_response(video_id, client[DB][coll_videos])
		result = json.dumps(video, default=json_util.default)
	elif status_code == HTTP_CONFLICT:
		result = {'Dislike_video': 'Este video ya te disgusta'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Dislike_video': 'No se encontró el video'}
	else:  # HTTP_INTERNAL_SERVER_ERROR
		result = {'Dislike_video': 'Sucedió un error'}

	return result, status_code


@videos_reactions_bp.route('/api/videos/<video_id>/dislikes', methods=['DELETE'])
@swag_from('docs/delete_dislike_to_video.yml')
@auth_required
def _delete_dislike_video(video_id):
	user_email = g.data['user_id']

	coll_users = 'users'
	user = get_user_by_email(user_email, client[DB][coll_users])
	if user is None:
		logger.error('El usuario %s que quiso eliminar el dislike de un video no existe', user_email)
		return {'Delete_dislike_video': 'User not found'}, HTTP_NOT_FOUND

	coll_videos = 'videos'
	status_code = delete_dislike_video(video_id, user, client[DB][coll_videos])

	if status_code == HTTP_OK:
		video = get_video_for_response(video_id, client[DB][coll_videos])
		result = json.dumps(video, default=json_util.default)
	elif status_code == HTTP_CONFLICT:
		result = {'Delete_dislike_video': 'Este video no tenia tu dislike'}
	elif status_code == HTTP_NOT_FOUND:
		result = {'Delete_dislike_video': 'No se encontró el video'}
	else:  # HTTP_INTERNAL_SERVER_ERROR
		result = {'Delete_dislike_video': 'Sucedió un error'}

	return result, status_code
