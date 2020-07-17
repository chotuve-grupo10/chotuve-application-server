from pymongo_inmemory import MongoClient
from app_server.videos_reactions import *

DB = 'test_app_server'

empty_video_01 = {
		'title': 'test',
		'url': 'url',
		'user': 'test_user',
		'isPrivate': True,
		'upload_date': '',
		'comments': [],
		'likes': [],
		'dislikes': []
}

fake_user = {'email': 'fake_email@gmail.com'}

def test_video_not_found_fails():
	client = MongoClient()
	coll = client[DB]['videos']

	id = '5ef1679ee0acd518e5cfd0f2'
	status_code = insert_video_into_db(id, empty_video_01, coll)
	assert status_code == HTTP_CREATED

	result = list(coll.find({}))
	assert len(result) == 1

	status_code = like_video('22222225ef1679ee0acd518e', fake_user, coll)
	assert status_code == HTTP_NOT_FOUND
	client.close()
