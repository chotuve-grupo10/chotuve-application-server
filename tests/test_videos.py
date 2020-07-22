from unittest.mock import patch
import simplejson as json
from app_server.token_functions import generate_app_token

def test_upload_video_fails(client):
	with patch('app_server.videos.post_media_server') as mock:

		video_to_upload = {
			'description': 'This is a test video', 'fileName': 'HKUG2278kH',
			'isPrivate': False, 'latitude': '-27.0000', 'longitude': '-54.22',
			'title': 'Test video', 'url' : 'test', 'user' : 'test'}

		mock.return_value.status_code = 500
		## The json response doesnt matteer because the status code is not 200.
		mock.return_value.json.return_value = {'Upload' : 'video uploaded'}

		value_expected = {'Upload Video' : 'No response'}
		response = client.post('/api/videos/', json=video_to_upload, follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_upload_fails_problems_inserting_into_db(client):
	with patch('app_server.videos.post_media_server') as mock:

		video_to_upload = {
			'description': 'This is a test video', 'fileName': 'HKUG2278kH',
			'isPrivate': False, 'latitude': '-27.0000', 'longitude': '-54.22',
			'title': 'Test video', 'url' : 'test', 'user' : 'test'}

		mock.return_value.status_code = 201
		mock.return_value.json.return_value = {'_id' : '12345'}

		with patch('app_server.videos.insert_video_into_db') as mock_insert_video:

			mock_insert_video.return_value = 500

			value_expected = {'Upload video' : 'Couldnt upload video'}
			response = client.post('/api/videos/', json=video_to_upload, follow_redirects=False)

			assert mock.called
			assert mock_insert_video.called
			assert json.loads(response.data) == value_expected

def test_upload_video_successfully(client):
	with patch('app_server.videos.post_media_server') as mock:

		video_to_upload = {
			'description': 'This is a test video', 'fileName': 'HKUG2278kH',
			'isPrivate': False, 'latitude': '-27.0000', 'longitude': '-54.22',
			'title': 'Test video', 'url' : 'test', 'user' : 'test'}

		mock.return_value.status_code = 201
		mock.return_value.json.return_value = {'_id' : '12345'}

		with patch('app_server.videos.insert_video_into_db') as mock_insert_video:

			mock_insert_video.return_value = 201

			value_expected = {'Upload video' : 'Successfully uploaded video'}
			response = client.post('/api/videos/', json=video_to_upload, follow_redirects=False)

			assert mock.called
			assert mock_insert_video.called
			assert json.loads(response.data) == value_expected

def test_list_videos_sucessfully(client):
	with patch('app_server.videos.get_media_server_request') as mock:

		with patch('app_server.videos.filter_videos_for_specific_user') as mock_videos:

			mock.return_value.status_code = 200
			response_media = [{'id' : 'test', 'title' : 'test'}]
			mock.return_value.json.return_value = response_media
			mock_videos.return_value = response_media

			value_expected = response_media
			response = client.get('/api/videos/user_test@test.com', follow_redirects=False)
			assert mock.called
			assert mock_videos.called
			assert json.loads(response.data) == value_expected

def test_list_videos_fails(client):
	with patch('app_server.videos.get_media_server_request') as mock:

		mock.return_value.status_code = 500

		value_expected = []
		response = client.get('/api/videos/test_user@test.com', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_delete_video_sucessfully(client):
	with patch('app_server.videos.delete_media_server') as mock:
		with patch('app_server.videos.delete_video_in_db') as _:

			mock.return_value.status_code = 200
			response_media = {'Delete' : 'Video deleted'}
			mock.return_value.json.return_value = response_media

			value_expected = {'Deleted Video' : response_media}
			response = client.delete('/api/videos/3', follow_redirects=False)
			assert mock.called
			assert json.loads(response.data) == value_expected

def test_delete_video_fails(client):
	with patch('app_server.videos.delete_media_server') as mock:

		mock.return_value.status_code = 500

		value_expected = {'Deleted Video' : 'No response'}
		response = client.delete('/api/videos/3', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_comment_video_fails(client):
	with patch('app_server.videos.insert_comment_into_video') as mock:

		data_to_comment = {
			'email': 'email01@gmail.com',
			'comment': 'This is one hell of a fake comment'
		}
		info = {'Comment video':
				'The request could not complete successfully'}
		mock.return_value = info, 500

		value_expected = info
		response = client.post('/api/videos/01xa/comments',
							   json=data_to_comment,
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 500
		assert json.loads(response.data) == value_expected

def test_get_videos_from_specific_user_fails_invalid_token(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		mock.return_value = {'Message': 'invalid token'}, 401

		user = 'test@test.com'
		response = client.get('/api/users/' + user + '/videos/',
							   headers={'Authorization': 'FAKETOKEN'},
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 403
		assert json.loads(response.data) == {'Error' : 'invalid token'}

def test_get_videos_from_specific_user_with_users_being_friends(client):
	with patch('app_server.decorators.auth_required_decorator.validate_token') as mock:

		user_requesting = 'test@test.com'
		mock.return_value = {'Message': 'token valido para user {0}'.format(user_requesting)}, 200

		with patch('app_server.videos.get_media_server_request') as mock_get_media_server:

			mock_get_media_server.return_value.status_code = 200
			video_info = {'Video' : 'video1'}
			mock_get_media_server.return_value.json.return_value = video_info

			with patch('app_server.videos.get_user_friends_from_db') as mock_get_user_friends:

				mock_get_user_friends.return_value = [{'email': user_requesting, 'fullName': 'test'}]

				user_to_get_videos = 'test2@test.com'

				token = generate_app_token({'email': user_requesting})
				response = client.get('/api/users/' + user_to_get_videos + '/videos/',
									headers={'Authorization': token},
									follow_redirects=False)

				assert mock.called
				assert mock_get_media_server.called
				assert mock_get_user_friends.called
				assert response.status_code == 200
				assert json.loads(response.data) == video_info
