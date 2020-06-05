from unittest.mock import patch
import simplejson as json

def test_upload_video_fails(client):
	with patch('app_server.videos.post_media_server') as mock:

		video_to_upload = {'title': 'Test video', 'url' : 'test', 'user' : 'test'}

		mock.return_value.status_code = 500
		## The json response doesnt matteer because the status code is not 200.
		mock.return_value.json.return_value = {'Upload' : 'video uploaded'}

		value_expected = {'Upload Video' : 'No response'}
		response = client.post('/api/upload_video/', json=video_to_upload, follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_upload_video_successfully(client):
	with patch('app_server.videos.post_media_server') as mock:

		video_to_upload = {'title': 'Test video', 'url' : 'test', 'user' : 'test'}

		mock.return_value.status_code = 200
		mock.return_value.json.return_value = {'Upload' : 'video uploaded'}

		value_expected = {'Upload' : 'video uploaded'}
		response = client.post('/api/upload_video/', json=video_to_upload, follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_list_videos_sucessfully(client):
	with patch('app_server.videos.get_media_server_request') as mock:

		mock.return_value.status_code = 200
		response_media = {'id' : 'test', 'title' : 'test'}
		mock.return_value.json.return_value = response_media

		value_expected = {'List Videos' : response_media}
		response = client.get('/api/list_videos/', follow_redirects=False)
		assert mock.called
		assert json.loads(response.data) == value_expected

def test_list_videos_fails(client):
	with patch('app_server.videos.get_media_server_request') as mock:

		mock.return_value.status_code = 500

		value_expected = {'List Videos' : 'No response'}
		response = client.get('/api/list_videos/', follow_redirects=False)
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