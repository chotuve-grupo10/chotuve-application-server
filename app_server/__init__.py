import os
import logging
import simplejson as json
from flasgger import Swagger
from flasgger import swag_from
from flask import Flask, request
from app_server.http_functions import *

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

	@app.route('/api/ping/', methods=['GET'])
	@swag_from('docs/ping.yml')
	def _respond():
		api_ping = "/api/ping/"
		response_auth_server = get_auth_server_ping(os.environ.get('AUTH_SERVER_URL') + api_ping)
		response_media_server = get_media_server_ping(os.environ.get('MEDIA_SERVER_URL') + api_ping)
		status = {}
		status["App Server"] = "OK"

		if response_auth_server.status_code == 200:
			data = response_auth_server.json()
			if data['Health'] == 'OK':
				status["Auth Server"] = "OK"
			else:
				status["Auth Server"] = "DOWN"
		else:
			status["Auth Server"] = "DOWN"

		if response_media_server.status_code == 200:
			data = response_media_server.json()
			if data['Health'] == 'OK':
				status["Media Server"] = "OK"
			else:
				status["Media Server"] = "DOWN"
		else:
			status["Media Server"] = "DOWN"

		return json.dumps(status)

	@app.route('/api/about/', methods=['GET'])
	@swag_from('docs/about.yml')
	def _about():
		status = {}
		status["Description"] = 'This is Application Server for chotuve-10. Still in construction'
		return json.dumps(status)


	@app.route('/')
	def _index():
		return "<h1>Welcome to application server !</h1>"

### Métodos que aún no implementaremos ###

	@app.route('/api/home/', methods=['GET'])
	@swag_from('docs/home.yml')
	def _home_page():
		return {}

	@app.route('/api/register/', methods=['POST'])
	@swag_from('docs/register.yml')
	def _register_user():
		#user_request = request.headers['AuthenticationHeader']
		#response_auth_server = post_auth_server_register(os.environ.get('AUTH_SERVER_URL'), user_request)
		return {}

	@app.route('/api/register_with_facebook/', methods=['POST'])
	@swag_from('docs/register_with_facebook.yml')
	def _register_user_using_facebook():
		return {}

	@app.route('/api/register_with_google/', methods=['POST'])
	@swag_from('docs/register_with_google.yml')
	def _register_user_using_google():
		return {}

	@app.route('/api/login/', methods=['POST'])
	@swag_from('docs/login.yml')
	def _login_user():
		return {}

	@app.route('/api/login_with_facebook/', methods=['POST'])
	@swag_from('docs/login_with_facebook.yml')
	def _login_user_using_facebook():
		return {}

	@app.route('/api/login_with_google/', methods=['POST'])
	@swag_from('docs/login_with_google.yml')
	def _login_user_using_google():
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
