from unittest.mock import patch
import simplejson as json

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
		response = client.post('/api/upload_video/', json=video_to_upload, follow_redirects=False)
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
			response = client.post('/api/upload_video/', json=video_to_upload, follow_redirects=False)

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
			response = client.post('/api/upload_video/', json=video_to_upload, follow_redirects=False)

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

		mock.return_value.status_code = 200
		response_media = {'Delete' : 'Video deleted'}
		mock.return_value.json.return_value = response_media

		value_expected = {'Deleted Video' : response_media}
		response = client.delete('/api/delete_video/3', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_delete_video_fails(client):
	with patch('app_server.videos.delete_media_server') as mock:

		mock.return_value.status_code = 500

		value_expected = {'Deleted Video' : 'No response'}
		response = client.delete('/api/delete_video/3', follow_redirects=False)
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
		response = client.put('/api/videos/01xa/comment',
							   json=data_to_comment,
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 500
		assert json.loads(response.data) == value_expected

def test_comment_video_is_successfull(client):
	with patch('app_server.videos.insert_comment_into_video') as mock:

		data_to_comment = {
			'email': 'email01@gmail.com',
			'comment': 'This is one hell of a fake comment'
		}
		info = {'Comment video':
				'Your request was completed successfully'}
		mock.return_value = info, 201

		value_expected = info
		response = client.put('/api/videos/01xa/comment',
							   json=data_to_comment,
							   follow_redirects=False)
		assert mock.called
		assert response.status_code == 201
		assert json.loads(response.data) == value_expected
