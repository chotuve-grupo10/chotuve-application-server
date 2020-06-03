import os
import logging
import simplejson as json
from flasgger import Swagger
from flasgger import swag_from
from flask import Flask, request
from app_server.http_functions import *
from app_server.authentication import authentication_bp

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	# Parametro adicional que no estamos usando por ahora en app.config.from_mapping
	#DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'
	app.config.from_mapping(SECRET_KEY='dev')
	Swagger(app)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Set up del log
	# Basicamente lo que se esta haciendo es usar el handler de gunicorn para
	# que todos los logs salgan por ese canal.
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	app.logger.debug('Log configuration finished')
	app.logger.info('App server running...')

	# Registro de blueprints que encapsulan comportamiento:
	with app.app_context():
		app.register_blueprint(authentication_bp)

	@app.route('/api/ping/', methods=['GET'])
	@swag_from('docs/ping.yml')
	def _respond():
		api_ping = '/api/ping/'
		response_auth_server = get_auth_server_request(os.environ.get('AUTH_SERVER_URL') + api_ping)
		response_media_server = get_media_server_ping(os.environ.get('MEDIA_SERVER_URL') + api_ping)
		status = {}
		status['App Server'] = 'OK'

		if response_auth_server.status_code == 200:
			app.logger.debug('Response from auth server ping is 200')
			data = response_auth_server.json()
			status['Auth Server'] = data['Health']
		else:
			app.logger.debug('Response from auth server ping is NOT 200')
			status['Auth Server'] = 'DOWN'

		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server ping is 200')
			data = response_media_server.json()
			status['Media Server'] = data['Health']
		else:
			app.logger.debug('Response from media server ping is NOT 200')
			status['Media Server'] = 'DOWN'

		return json.dumps(status)

	@app.route('/api/about/', methods=['GET'])
	@swag_from('docs/about.yml')
	def _about():
		status = {}
		status['Description'] = 'This is Application Server for chotuve-10. Still in construction'
		return json.dumps(status)


	@app.route('/')
	def _index():
		return '<h1>Welcome to application server !</h1>'

### Métodos que aún no implementaremos ###

	@app.route('/api/home/', methods=['GET'])
	@swag_from('docs/home.yml')
	def _home_page():
		return {}

	# @app.route('/user/<username>')
	# def show_user_profile(username):
	#     # show the user profile for that user
	#     return 'User name is %s' % escape(username)

	# @app.route('/post/<int:post_id>')
	# def show_post(post_id):
	#     # show the post with the given id, the id is an integer
	#     return 'Post %d' % post_id

	return app

	@app.route('/api/list_videos/', methods=['GET'])
	@swag_from('docs/list_videos.yml')
	def _respond():
		api_list_videos = '/api/list_videos/'
		response_media_server = get_media_server_request("https://chotuve-media-server-dev.herokuapp.com" + api_list_videos)
		status = {}
		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server list videos is 200')
			#Recibe lista de videos
			data = response_media_server.json()
			status['List Videos'] = data
		else:
			app.logger.debug('Response from media server is NOT 200')
			status['List Videos'] = 'No response'

		return json.dumps(status)

	@app.route('/api/list_videos/:id', methods=['GET'])
	@swag_from('docs/list_videos.yml')
	def _listVideosForUser(req):
		api_list_video_for_user = '/api/list_videos/'+req.id
		response_media_server = get_media_server_request("https://chotuve-media-server-dev.herokuapp.com" + api_list_video_for_user)
		status = {}
		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server list videos is 200')
			#Recibe lista de videos según id
			data = response_media_server.json()
			status['List Videos'] = data
		else:
			app.logger.debug('Response from media server is NOT 200')
			status['List Videos'] = 'No response'

		return json.dumps(status)


	@app.route('/api/upload_video/', methods=['POST'])
	@swag_from('docs/upload_video.yml') #TODO agregar doc
	def _uploadVideo(req):
		api_upload_video = '/api/upload_video/'
		response_media_server = post_media_server("https://chotuve-media-server-dev.herokuapp.com" + api_upload_video, req.body)
		status = {}
		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server list videos is 200')
			data = response_media_server.json()
			status['Upload Video'] = data['Upload Video']
		else:
			app.logger.debug('Response from media server is NOT 200')
			status['Upload Video'] = 'No response'

		return json.dumps(status)


	@app.route('/api/delete_video/', methods=['DELETE'])
	@swag_from('docs/delete_video.yml')
	def _deleteVideo(req):
		api_delete_video = '/api/delete_video/'+req.id
		response_media_server = delete_media_server("https://chotuve-media-server-dev.herokuapp.com" + api_delete_video)
		status = {}
		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server list videos is 200')
			data = response_media_server.json()
			status['Deleted Video'] = data['Deleted Video']
		else:
			app.logger.debug('Response from media server is NOT 200')
			status['Deleted Video'] = 'No response'

		return json.dumps(status)